# v4 Design Notes — Real-Data-Informed Endowment ABM

*2026-04-16 | Post-defense build target*

---

## Design Philosophy

v3 is a pure synthetic simulator — it generates agents, runs them through the mechanism, and outputs equilibrium predictions. It answered "what might happen?" before the endowment existed.

v4 answers a different question: **"is what's happening what we predicted, and what happens next?"**

The core shift is from **generative** to **data-assimilated** simulation. The model ingests real on-chain data, calibrates itself, and projects forward from observed state rather than assumed initial conditions.

---

## Three Operating Modes

### Mode 1: Synthetic (v3 behavior, preserved)
- Same as today. Useful for what-if scenarios and parameter exploration.
- No external data dependency.

### Mode 2: Replay
- Feed historical on-chain data as environment inputs.
- Agents react to real price, real participation, real APY.
- Compare agent behavior against what actually happened.
- Primary use: calibration. Tune archetype_mix and behavioral params until sim matches observed entry/exit patterns.

### Mode 3: Forecast
- Initialize from current on-chain state (real wallet balances, real participation rate, real price).
- Run forward with calibrated agents.
- "Given what we see today, where does this go?"
- Primary use: prediction. What happens when whales deposit? When does APY equilibrate?

---

## Architectural Changes

### 1. Data Layer (`src/data/`)

New module that the model optionally depends on. Synthetic mode ignores it entirely.

```
src/data/
├── feeds.py          # Abstract DataFeed interface + FeedRegistry
├── dune_sim.py       # Dune Sim API — wallet balances, transfers, prices (PRIMARY)
├── blockscout.py     # Blockscout API — fallback / free-tier alternative
├── store.py          # Local SQLite for caching + time series
└── snapshot.py       # Point-in-time state capture (for Forecast mode init)
```

**Primary data source: Dune Sim API** (https://docs.sim.dune.com/)

Sim is a real-time blockchain data API by Dune that collapses what was previously two separate clients (Blockscout + CoinGecko) into a single unified feed:

- Single API key, single client → wallet balances, token transfers, transaction history, prices
- 60+ EVM chains + Solana — covers both Ethereum mainnet and Base natively
- Normalized data with enriched metadata and pricing included in responses
- **Webhook subscriptions** — push deposit/withdrawal events to our server in real time (eliminates polling)

This replaces the original two-client architecture:
```
Before: blockscout.py (balances, transfers) + coingecko.py (prices) → 2 APIs, 2 rate limits, manual pagination
After:  dune_sim.py (balances + transfers + prices in one call) → 1 API, normalized responses, webhook option
```

**Blockscout retained as fallback** — free, no API key, useful for development/testing and if Sim quota is exceeded. The `FeedRegistry` tries Sim first, falls back to Blockscout.

**Key design decision:** The data layer is a **feed**, not a database. The model pulls from it each step. In Replay mode, it pulls historical data for that step's timestamp. In Forecast mode, it pulls the latest snapshot once at init, then runs synthetically forward.

### 2. Real Agents vs Synthetic Agents

v3 has only synthetic agents with sampled behavioral params. v4 adds the concept of **anchored agents** — agents initialized from real on-chain depositors.

```python
class AnchoredHolder(EndowmentHolder):
    """Agent initialized from real on-chain data."""
    
    def __init__(self, model, address, rsc_held, deposit_date, chain, ...):
        # Real deposit amount, not sampled
        # Real deposit date → accurate weeks_held → correct time-weight tier
        # Archetype INFERRED from behavior, not assigned
        super().__init__(model, rsc_held=rsc_held, ...)
        self.address = address      # On-chain address (for tracking)
        self.deposit_date = deposit_date
        self.chain = chain          # 'ethereum' | 'base'
        self.anchored = True        # Flag: this agent represents a real depositor
```

In Replay mode, anchored agents enter/exit at the times their real counterparts did. Synthetic agents fill the gap between known depositors and total platform RSC.

In Forecast mode, anchored agents are initialized from current state; the model then projects their behavior forward using calibrated behavioral params.

### 3. Environment State Object

v3 computes environment (APY, participation) internally from agent state. v4 adds an explicit Environment that can be either computed OR injected from real data.

```python
class Environment:
    """Observable market state — either computed from agents or injected from data."""
    
    rsc_price: float              # USD per RSC
    total_platform_rsc: float     # Total RSC on RH
    participation_rate: float     # platform_rsc / circulating
    current_apy: float            # Computed from participation
    circulating_supply: float     # Updated for emissions + burns
    exchange_depth: float         # NEW: how much RSC available on exchanges
    volume_24h: float             # NEW: market activity signal
    
    # Wallet-level observables (new)
    hot_wallet_balance: float
    known_wallet_balances: dict   # {address: balance}
    recent_deposits: list         # Last N deposits with amounts + timestamps
    recent_withdrawals: list      # Last N withdrawals
    recent_burns: float           # RSC burned since last step
```

Agents make B=f(P,E) decisions against this Environment. In Synthetic mode, E is computed. In Replay, E is injected from historical data. In Forecast, E starts from real data then evolves.

### 4. Price Model Upgrade

v3 has a simplified directional price model. v4 should have two options:

**Option A: Exogenous price (Replay mode)**
- Price comes from Dune Sim (enriched metadata includes pricing). No modeling needed.

**Option B: Endogenous price (Synthetic + Forecast modes)**  
- Model price as function of:
  - Net deposit flow (RSC moving to/from platform = removed from/added to exchange float)
  - Exchange depth (thinner book = larger price impact per unit flow)
  - External demand baseline (crypto market beta)
  - Burns (permanent supply reduction)
- Calibrate coefficients from Replay mode observations.

### 5. Stress Scenarios Module (Concentration Risk)

**Gap in v3:** The model has no representation of the real RSC power-law distribution (93% held by top 10 wallets, Foundation holds 473M, team holds 298M). Agent exit decisions are purely APY-driven — no price-linked exits, no correlated withdrawal events, no minting risk. This means v3 literally cannot model the most dangerous failure modes.

**v4 adds a `StressScenario` system** that injects exogenous shocks into any operating mode:

```python
class StressScenario:
    """Exogenous shock injected into the model at a specific step."""
    trigger_step: int           # When the shock fires
    scenario_type: str          # 'whale_exit' | 'foundation_flood' | 'cascade' | 'mint_event'
    params: dict                # Scenario-specific parameters

STRESS_SCENARIOS = {
    "whale_exit": {
        "description": "Single large holder withdraws from endowment and sells on exchange",
        "params": {
            "exit_size_rsc": 5_000_000,       # RSC withdrawn from platform
            "sell_fraction": 0.8,              # % dumped on exchange immediately
            "price_impact_per_million": 0.15,  # 15% price drop per 1M RSC sold (thin book)
        }
    },
    "foundation_flood": {
        "description": "Foundation releases treasury RSC to market (mint or unlock)",
        "params": {
            "release_amount": 50_000_000,      # 10% of Foundation's 473M
            "release_schedule": "instant",      # 'instant' | 'weekly_over_N'
            "reason": "operational_funding",    # Context for the release
        }
    },
    "cascade_exit": {
        "description": "Whale exit triggers price crash, price crash triggers yield seeker exits, feedback loop",
        "params": {
            "initial_exit_rsc": 2_000_000,
            "price_crash_threshold": 0.30,     # 30% price drop triggers cascade
            "exit_acceleration": 1.5,          # Multiplier on exit probability during cascade
        }
    },
    "mint_event": {
        "description": "MiniMeToken controller mints new RSC (no hardcoded cap prevents this)",
        "params": {
            "mint_amount": 100_000_000,        # New RSC created
            "dilution_target": "circulating",  # Hits circulating supply, crashes price
        }
    },
}
```

**Critical behavioral change — price-linked exits:**

v3 agents only exit when `APY < yield_threshold`. In reality, a 50% price crash triggers exits regardless of APY. v4 adds a second exit channel:

```python
def _consider_exit(self):
    # Channel 1: APY-driven exit (v3 behavior, preserved)
    if current_apy < self.yield_threshold:
        # ... existing stochastic exit logic ...
    
    # Channel 2: Price-driven exit (NEW)
    if self.model.env.rsc_price < self._entry_price * (1 - self.price_crash_tolerance):
        crash_exit_prob = self.price_sensitivity * 0.25  # Up to 25%/step during crash
        if random.random() < crash_exit_prob:
            self.active = False
```

This creates the **cascade feedback loop** that the real system is vulnerable to:
```
Whale exits platform → sells on exchange → price drops →
  yield seekers see USD value collapse → exit despite high APY →
  more RSC hits exchange → more price drop → death spiral
```

**Concentration-aware initialization:**

Instead of lognormal RSC distributions, v4 can initialize from the real holder distribution:

```python
REAL_HOLDER_DISTRIBUTION = {
    "top_1":  [473_674_732],           # Foundation
    "top_2":  [297_948_483],           # Team
    "top_10": [8_090_686],             # Founder + others
    "endowment_depositors": 11_180_000, # Current platform RSC
    "retail_float": 8_980_000,          # Remaining circulating
}
```

This makes whale exit scenarios feel real — when the Foundation agent exits, it's 473M RSC, not a lognormal sample of 50K.

**Dashboard: "Stress Test" tab**
- Scenario selector (whale exit / foundation flood / cascade / mint)
- Parameter sliders for each scenario
- Before/after comparison charts: price, participation, APY, holder count
- "Survivability score": does the endowment recover within 12 weeks or death spiral?

### 6. Archetype Calibration Engine

New module that runs Replay mode repeatedly with different archetype_mix values and scores each run against observed behavior.

```python
class ArchetypeCalibrator:
    """Find the archetype_mix that best explains observed deposit/exit patterns."""
    
    def calibrate(self, historical_data, n_trials=100):
        # For each trial:
        #   1. Sample archetype_mix
        #   2. Run Replay with those params
        #   3. Score: how well do sim entry/exit times match real entry/exit times?
        # Return best-fit archetype_mix + confidence intervals
```

Scoring metrics:
- Entry timing correlation (when do sim agents enter vs real depositors?)
- Exit timing correlation  
- Deposit size distribution match (KS test against real deposit sizes)
- Participation rate trajectory (MSE between sim and observed)

### 6. Dashboard Changes

**Existing tabs** (preserved):
- Agent Field, Yield Dynamics, Time Series, Proposals & Funding, Agent Inspector

**New tabs:**

**"Live State"** — Current on-chain state at a glance:
- Hot wallet balance (auto-refreshed)
- Known depositors table (address, amount, date, inferred archetype)
- Recent deposits/withdrawals feed
- Current participation rate + APY (computed from real data)
- Your position: credits earned, share of emissions, effective APY

**"Model vs Market"** — Overlay sim predictions against reality:
- Participation rate: sim curve vs observed data points
- APY: sim curve vs computed-from-real
- Price: sim trajectory vs CoinGecko
- Divergence heatmap: where is the model wrong?

**"Forecast"** — Forward projection from current state:
- Initialize from real data, project 4/12/52 weeks forward
- Scenario selector: "what if 10M RSC deposits tomorrow?" / "what if whale exits?"
- Confidence bands from Monte Carlo runs with calibrated params

---

## Data Collection Strategy

### Automated — Dune Sim (primary)

| Data | Sim Endpoint | Frequency |
|---|---|---|
| RSC price + volume + market cap | Token metadata / balance queries (enriched) | Daily or real-time via webhook |
| Wallet balances (all monitored wallets, both chains) | Wallet balance API (multichain) | Daily or real-time |
| Recent transfers (deposits/withdrawals/burns) | Transaction history API | Daily or real-time via webhook |

**Webhook mode (P2+):** Sim supports real-time webhook subscriptions that push events to our server. Once configured, the Live State tab updates automatically — no polling needed. This replaces the cron-based approach entirely.

### Automated — Blockscout (fallback / dev)

| Data | Source | Method | Frequency |
|---|---|---|---|
| Wallet balances | Blockscout REST API (no key) | On-demand | Daily |
| Token transfers | Blockscout token-transfers endpoint | Paginated | Daily |
| Burns | Transfers to zero address | Filtered | Weekly |

Used during development (no API key needed) and as fallback if Sim quota exceeded.

### Manual (from RH app)

| Data | Source | Frequency |
|---|---|---|
| Credit distributions | Screenshot / manual entry | Per distribution |
| Funded proposals count | RH platform | Weekly |
| Endowment page stats (if RH adds them) | RH platform | As available |

### Storage

SQLite database with tables (unchanged — data source agnostic):
- `price_history` (date, price, volume, market_cap)
- `wallet_snapshots` (date, address, chain, balance)
- `transfers` (date, from, to, amount, type: deposit/withdrawal/burn)
- `distributions` (date, credits_earned, implied_share, implied_platform_rsc)
- `calibration_runs` (date, archetype_mix, score, params)

---

## Implementation Priority

| Priority | Feature | Why |
|---|---|---|
| **P0** | Data layer + SQLite store | Foundation for everything else |
| **P0** | Dune Sim feed (balances + transfers + prices, multichain) | Single API replaces Blockscout + CoinGecko |
| **P0** | Blockscout fallback feed | Free-tier dev/test, no API key needed |
| **P1** | Replay mode | Calibration depends on this |
| **P1** | AnchoredHolder class | Real depositors in the sim |
| **P1** | Model vs Market dashboard tab | Visualize fit quality |
| **P1** | Stress scenarios module | Whale exit, foundation flood, cascade, mint — models the risks the current ABM can't |
| **P1** | Price-linked exit behavior | Agents exit on price crash, not just APY — enables cascade modeling |
| **P2** | Sim webhook subscriptions | Real-time event push → Live State tab without polling |
| **P2** | Archetype calibration engine | Automated parameter fitting |
| **P2** | Forecast mode | Forward projection from real state |
| **P2** | Live State dashboard tab | Real-time monitoring (powered by webhooks) |
| **P3** | Endogenous price model calibration | Requires weeks of price data |
| **P3** | Forecast scenario builder + Stress Test tab | What-if tools for governance, survivability scoring |

---

## What This Enables

1. **For you:** Track your position, monitor whale entry, project credit accumulation trajectory.
2. **For RH governance:** Evidence-based parameter discussions. "If we change emission rate to X, the calibrated model predicts Y."
3. **For the community:** Share a tool that shows real endowment health, not just marketing numbers.
4. **For the ABM field:** A case study of a live-calibrated agent-based model tracking a real tokenomic mechanism from launch. Rare in academic literature.

---

## Key Risks

- **Sim API pricing/quota:** Free tier details TBD. If insufficient, Blockscout fallback covers core needs (balances + transfers) without cost. Price data could fall back to the CoinGecko free tier or the existing `rsc-usd-max.csv` on desktop.
- **Data staleness:** FeedRegistry implements graceful degradation — Sim → Blockscout → SQLite cache. Dashboard shows "last updated" timestamp so stale data is visible.
- **Overfitting:** Calibrating to <2 weeks of data from ~10 depositors is fragile. Need minimum data thresholds before trusting calibration. Flag results as "preliminary" when N < 30 observations.
- **Scope creep:** The forecast tools could become arbitrarily complex. Keep the core question simple: "what participation rate does the market equilibrate to?"
- **Webhook infrastructure:** Sim webhooks require a publicly accessible endpoint. Railway deployment handles this, but local dev needs a tunnel (ngrok or similar). Not a blocker — webhook is P2, polling works for P0-P1.

---

*Companion docs: [endowment-live-tracking.md](endowment-live-tracking.md) | [chain-data-calibration-plan.md](chain-data-calibration-plan.md) | [ROADMAP.md](ROADMAP.md)*
