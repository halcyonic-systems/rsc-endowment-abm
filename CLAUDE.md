# RSC Decentralized Endowment ABM - Claude Context

## Project Identity

This is the **Endowment** model matching ResearchHub's actual 2026 mechanism:

```
Hold RSC in RH account → Passive yield (dilution-based) → Deploy credits to Research Proposals
```

**Real mechanism**: No lockups. RSC in account auto-earns yield.
`Yield = (your RSC / total RH RSC) × annual_emission`
`Emission: E(t) = 9,500,000 / 2^(t/64)` (halves every 64 years)
No time-weight multipliers, no burn-from-principal (both available as Design Lab toggles).

**Primary question**: What participation rate (% of circulating RSC) does the market equilibrate to?

**Not to be confused with**: `rsc-process-fidelity-abm` (complex model with panel voting, slashing, etc.)

## Current State

**v4 Observatory live at `endowment.halcyonic.systems/`** (v3 archived at `/v3`).
Password-gated via `DASHBOARD_PASSWORD` env var (Railway + GitHub Actions secret).

**Endowment launched April 10, 2026.** Pool currently ~8.5M RSC at 6.3% participation, ~112% APY. Model predicted 30% — divergence is 23.7pp. Price ~$0.075. Shared with Jeff Koury (RH Foundation president) 2026-05-09.

**Three operating modes:**
- **Synthetic** — v3 behavior, unchanged, default for `/api/init`
- **Forecast** — `EndowmentModel.from_chain_data()` inits from live chain data (Blockscout + CoinGecko), runs forward with anchored + synthetic agents. Endpoint: `POST /api/forecast`
- **Replay** — not yet implemented (needs accumulated daily snapshots, see GitHub issue #1)

**Infrastructure:**
- **Data layer**: Blockscout + CoinGecko (keyless; Dune Sim retired at its 2026-08-01 sunset) → SQLite (`/data/endowment.db` on Railway volume) → Flask API → frontend
- **Daily snapshot cron**: GitHub Actions workflow (`.github/workflows/daily-snapshot.yml`), fires noon UTC, persists pool + treasury balances. Started 2026-05-09.
- **Railway volume**: `rsc-endowment-abm-volume` mounted at `/data` — SQLite survives redeployments
- **4 stress scenarios**: whale exit, foundation flood, cascade exit, mint event (`src/scenarios.py`)
- **13 mechanism tests**: `tests/test_mechanism.py`

Full design spec: `docs/v4-design-notes.md`. Roadmap: `docs/ROADMAP.md`.

## Python Environment

```bash
# Always activate venv before running
source venv/bin/activate
python server.py
# or: venv/bin/python3 server.py
```

## Key Files

| File | Purpose |
|------|---------|
| `src/model.py` | EndowmentModel: emissions, participation, `from_chain_data()` forecast init |
| `src/agents.py` | EndowmentHolder, AnchoredHolder (real depositors), EndowmentProposal |
| `src/constants.py` | EMISSION_PARAMS, ARCHETYPES, DEFAULT_PARAMS (burn/multiplier toggles) |
| `src/scenarios.py` | StressScenario: whale exit, foundation flood, cascade exit, mint event |
| `src/data/chain_client.py` | Chain data client (Blockscout + CoinGecko) — balances, transfers, depositor tracing |
| `src/data/store.py` | SQLite persistence — pool_snapshots, treasury_snapshots |
| `src/data/snapshot.py` | Orchestrator: take_snapshot(), get_latest_snapshot() |
| `server.py` | Flask REST API (25+ endpoints including /api/forecast, /api/chain/*) |
| `templates/v4-kpi-prototype.html` | v4 Observatory dashboard (served at root `/`) |
| `templates/index.html` | v3 simulator (archived at `/v3`) |
| `tests/test_mechanism.py` | 13 tests: mechanism correctness, scenarios, API |
| `.github/workflows/daily-snapshot.yml` | Daily chain snapshot cron (noon UTC) |
| `docs/endowment-live-tracking.md` | Wallet forensics, depositor data, market timeline |
| `docs/v4-design-notes.md` | v4 architecture spec (three modes, data layer, anchored agents) |
| `docs/v4-backend-contracts.md` | API data shapes for frontend |
| `docs/ROADMAP.md` | Full project roadmap v1→v4 |
| `docs/chain-data-calibration-plan.md` | Data pipeline spec, calibration targets |

## Deployment Infrastructure

| Component | Detail |
|-----------|--------|
| **Host** | Railway (Hobby plan) |
| **URL** | `endowment.halcyonic.systems/` (v4), `/v3` (archived) |
| **Auth** | HTTP Basic Auth via `DASHBOARD_PASSWORD` env var |
| **Volume** | `rsc-endowment-abm-volume` mounted at `/data` — SQLite persists across redeploys |
| **Cron** | `.github/workflows/daily-snapshot.yml` — noon UTC daily, calls `POST /api/chain/snapshot` |
| **Env vars (Railway)** | `DASHBOARD_PASSWORD`, `FLASK_DEBUG=false` (`DUNE_SIM_API_KEY` obsolete, safe to delete) |
| **Secrets (GitHub)** | `DASHBOARD_PASSWORD` (for cron auth) |
| **API key (local)** | none — Blockscout and CoinGecko are keyless |

## On-Chain Infrastructure

| Label | Address | Chain |
|---|---|---|
| Hot Wallet | `0x7F57d306a9422ee8175aDc25898B1b2EBF1010cb` | Both |
| Second Wallet | `0x467564DCCE90FB21153adfa69c48A3Be235d66D3` | Base |
| Foundation Treasury | `0x5222ff25f4dfc02d173c2cbd2055ee1d35f291f1` | Ethereum |
| Team Treasury | `0xe3648e99b6e68a09e28428790d12b357f081dbe0` | Ethereum |
| Foundation Community | `0xc4cfa2bdae08416312faa0b72758e1f3750f81e3` | Ethereum |
| Base Treasury | `0xb280f00e70f28e8ce38c40826270de7e1b327e21` | Base |
| RSC (Ethereum) | `0xd101dcc414f310268c37eeb4cd376ccfa507f571` | Ethereum |
| RSC (Base) | `0xfbb75a59193a3525a8825bebe7d4b56899e2f7e1` | Base |

**API keys:** none required — Blockscout and CoinGecko free tiers are keyless. (Dune Sim sunset 2026-08-01; ground-truth parity fixture at `tests/fixtures/sim_ground_truth_2026-07-30.json`.)

## Watch List

When doing any RSC-related work (price checks, on-chain queries, data pipeline runs), always check these:

| Address | Why | Check |
|---|---|---|
| `0x3e3ff36273df89400946eb840175eda5e17a7161` | Holding 1.29M RSC from Foundation Community disbursement (Apr 23). If sold on exchange, ~40% price impact. | Any outbound RSC transfers |
| `0xc4cfa2bdae08416312faa0b72758e1f3750f81e3` | Foundation Community wallet (7.09M RSC). Primary active source of sell-side supply. | New disbursements |

## Dashboard Layout

**Sidebar sections:**
- **Parameters**: Yield Threshold, Deploy Rate, Proposal Success, Holders (Apply & Reset + Defaults)
- **Archetype Mix**: Linked sliders (sum=100%, min 5% each) + stacked bar + behavioral hints
- **Time-Weight Multipliers**: Distribution bar (New/Holder/LongTerm)
- **Advanced** (collapsed): Burn Rate, Credit Expiry, Failure Mode
- **Scenarios** (collapsed): Save/Compare runs side-by-side
- **How It Works** (collapsed): Mechanism explanation, self-balancing, step breakdown

**Main area tabs:** Agent Field | Yield Dynamics | Time Series | Proposals & Funding | Agent Inspector

**Pinned KPIs:** Participation Rate, Current APY, Exited

## Parameter Mapping (Slider → Backend)

| Slider | ID | Backend param | Section |
|--------|----|---------------|---------|
| Yield Threshold | `slider-yield` | `yield_threshold_mean` (/ 100) | Parameters |
| Deploy Rate | `slider-deploy` | `deploy_probability` (/ 100) | Parameters |
| Proposal Success | `slider-success` | `success_rate` (/ 100) | Parameters |
| Holders | `slider-stakers` | `num_holders` (int) | Parameters |
| Burn Rate | `slider-burn` | `burn_rate` (/ 100) | Advanced |

Archetype sliders: `slider-believer`, `slider-yield_seeker`, `slider-institution`, `slider-speculator` → `archetype_mix` dict (values / 100).

## Model Parameters

```python
EndowmentModel(
    num_holders=100,
    num_proposals=10,
    burn_rate=0.02,               # 2% burn on credit deployment
    success_rate=0.80,            # 80% proposal completion rate
    deploy_probability=0.3,       # Scales behavioral deployment
    yield_threshold_mean=0.08,    # Average APY below which agents exit
    initial_participation_rate=0.30,  # Aspirational starting point
    archetype_mix={
        "believer": 0.25,
        "yield_seeker": 0.30,
        "institution": 0.20,
        "speculator": 0.25,
    },
    # Advanced / Design Lab
    credit_expiry_enabled=False,
    credit_expiry_weeks=8,
    failure_mode="nothing",       # nothing | partial_refund | satisfaction_only
    seed=None,
)
```

## Behavioral Model

**B = f(P, E)**: Person attributes × Environment → Behavior

Person attributes per holder:
- `mission_alignment` (0–1): cares about research quality vs. just yield
- `engagement` (0–1): how actively they deploy credits
- `price_sensitivity` (0–1): how quickly APY changes drive exit decisions
- `hold_horizon` (0–1): tendency toward long-term holding (dampens exits)
- `yield_threshold`: personal minimum APY to stay (mean + archetype offset ± noise)

## Time-Weight Multipliers

| Label | Duration | Multiplier |
|-------|----------|-----------|
| New | < 4 weeks | 1.00x |
| Holder | 4 weeks – 1 year | 1.15x |
| LongTerm | > 1 year | 1.20x |

Continuous holding (not lockup). Effective share = `(RSC × multiplier) / total_effective_RSC`.

## Self-Balancing Mechanic

1. High APY → new entrants (yield seekers spawned) → total RSC rises → APY falls
2. Low APY (below threshold) → exits → total RSC falls → APY rises
3. Equilibrium emerges at the participation rate where exits ≈ entrants

## API Quick Reference

```bash
# Initialize
curl -X POST localhost:5000/api/init \
  -d '{"num_holders": 100, "yield_threshold_mean": 0.08, "initial_participation_rate": 0.30}'

# Run 52 steps (1 year)
curl -X POST localhost:5000/api/run -d '{"steps": 52}'

# Key outputs
curl localhost:5000/api/participation   # participation rate + reference scenarios
curl localhost:5000/api/state           # full model state
curl localhost:5000/api/multipliers     # time-weight tier breakdown
```

## Difference from Process Fidelity Model

| Feature | Endowment (this) | Process Fidelity |
|---------|------------------|------------------|
| Yield mechanism | Dilution-based (passive) | Fixed APY |
| Lockups | None | Hard tiers |
| Credits | Yes | No |
| Panel voting | No | Yes (5 stakers) |
| Slashing | No | Yes |
| Primary question | Participation equilibrium | Process integrity |

## Reference Scenarios (from RH Yield Model CSV)

| Participation | Year 0 APY | Description |
|---|---|---|
| 15% | ~47% | Underparticipation — high yield signal |
| 30% | ~24% | Moderate equilibrium |
| 70% | ~10% | High participation — diluted yield |

These appear as dashed reference lines in the Yield Dynamics tab.

## Real-World Observed Data (Apr 10-24, 2026)

| Metric | Value |
|---|---|
| Circulating supply | ~220M RSC |
| Endowment TVL | ~11.2M RSC (5.1% participation) |
| Current APY (implied) | ~187% (compressing as pool grows) |
| Daily emission | 26,027 credits |
| RSC price range | $0.063 (entry) → $0.138 (peak) → $0.096 (current) |
| Known depositors | ~15 addresses traced |
| Credit-implied vs on-chain gap | ~7.9M RSC in undiscovered wallets |

See `docs/endowment-live-tracking.md` for full data, systems decomposition, treasury audit, and price action analysis.
