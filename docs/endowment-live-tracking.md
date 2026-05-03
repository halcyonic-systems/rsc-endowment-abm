# RSC Endowment — Live Tracking

*Created 2026-04-16 | Endowment launched 2026-04-10*

Comprehensive record of on-chain activity, known depositors, wallet infrastructure, credit distributions, and market observations since the endowment went live.

---

## Token Fundamentals

| Attribute | Value |
|---|---|
| Token | ResearchCoin (RSC), ERC-20 MiniMeToken |
| Total supply | 1,000,000,000 RSC |
| Circulating supply | ~220,159,506 RSC (CoinGecko, Apr 23) |
| Price at endowment launch | ~$0.063 |
| Price as of Apr 23 | ~$0.138 (+119% from entry) |
| ATH | $1.48 (Jan 2025, Coinbase listing) |
| ATL | ~$0.004 (Nov 2022) |
| Daily volume (normal) | $300-500K |
| Top 10 holders | 93.66% of supply |
| Estimated free float | ~220M circulating, ~14M actively traded |
| Permanently burned | ~126,591 RSC (available supply 999,873,409 vs 1B) |

### Supply Breakdown (CoinGecko, Apr 23)

| Component | Address | RSC | % of Total |
|---|---|---|---|
| Available supply | — | 999,873,409 | 100% |
| Team Funds | `0xE3648e99B6E68A09e28428790D12B357f081dBe0` | -297,948,483 | 29.8% |
| Founder | `0x1288...` | -8,090,686 | 0.8% |
| Foundation Funds | `0x5222FF25F4DFC02d173C2cbd2055EE1D35f291F1` | -473,674,732 | 47.4% |
| **Est. Circulating** | — | **220,159,506** | **22.0%** |

**Key insight:** 78% of all RSC is in insider wallets (team + founder + foundation). The Foundation alone holds 473.7M — if they deposit even 10% into the endowment, it would 4x the current platform TVL. The Team treasury holds 297.9M. These are the whales that haven't moved yet.

### Token Contracts

| Network | Address | Explorer |
|---|---|---|
| Ethereum Mainnet | `0xd101dcc414f310268c37eeb4cd376ccfa507f571` | [Etherscan](https://etherscan.io/token/0xd101dcc414f310268c37eeb4cd376ccfa507f571) |
| Base L2 | `0xfbb75a59193a3525a8825bebe7d4b56899e2f7e1` | [BaseScan](https://basescan.org/token/0xfbb75a59193a3525a8825bebe7d4b56899e2f7e1) |

---

## Endowment Mechanism

| Parameter | Value |
|---|---|
| Emission formula | E(t) = 9,500,000 / 2^(t/64) |
| Year 1 emission | 9,500,000 RSC as non-transferable Funding Credits |
| Daily emission | ~26,027 credits (split proportionally) |
| Halving period | 64 years |
| Distribution cadence | Daily |
| Lock-up | None — principal revocable anytime |
| Credit type | Non-transferable, funding-only |
| Researcher payouts | **USD** (confirmed with RH leadership) |
| Deposit support | Base and Ethereum |
| Processing time | 10-20 minutes |

**Key insight:** Credits never enter circulation as tradeable RSC. Researchers get USD. No downstream sell pressure from yield. Net effect on liquid supply is deflationary.

---

## Systems Decomposition

### System Diagram

```
╔══════════════════════════════════════════════════════════════════════╗
║  ENVIRONMENT (exogenous)                                            ║
║  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐              ║
║  │ BTC/ETH     │  │ Press/       │  │ Exchange      │              ║
║  │ market beta │  │ Narrative    │  │ Listings      │              ║
║  └──────┬──────┘  └──────┬───────┘  └───────┬───────┘              ║
║         │                │                   │                      ║
║ ════════╪════════════════╪═══════════════════╪═══════ BOUNDARY ═══  ║
║         ▼                ▼                   ▼                      ║
║  ┌─────────────────────────────────────────────────┐                ║
║  │              EXCHANGE ORDER BOOKS               │ ◄── INTERFACE  ║
║  │   Coinbase · Gate.io · Aerodrome · Uniswap      │                ║
║  └────┬──────────────────────────────────────┬─────┘                ║
║       │ buy pressure                  sell pressure                 ║
║       ▼                                      ▲                      ║
║  ┌─────────┐    deposit    ┌──────────────┐  │  ┌────────────────┐  ║
║  │ HOLDERS │──────────────►│  ENDOWMENT   │  │  │  TREASURIES    │  ║
║  │         │◄──────────────│  POOL        │  │  │  Foundation    │  ║
║  │ Shingai │   withdraw    │  (~11.2M RSC)│  │  │  473M          │  ║
║  │ Koury   │               └──────┬───────┘  │  │  Team 298M     │  ║
║  │ Whale   │                      │ daily    │  │  Community 7M  │  ║
║  │ Retail  │                      │ emission │  │                │  ║
║  └─────────┘                      ▼          │  └───────┬────────┘  ║
║                            ┌──────────────┐  │     disbursements    ║
║                            │   CREDITS    │  │    (contributor pay, ║
║                            │  (non-       │  │     grants, ops)     ║
║                            │  transferable)│  │          │          ║
║                            └──────┬───────┘  │          ▼          ║
║                                   │ fund     │   ┌────────────┐    ║
║                                   ▼          │   │ RECIPIENTS │    ║
║                            ┌──────────────┐  │   │ (sell for  │    ║
║                            │  PROPOSALS   │  │   │  expenses) │    ║
║                            │  (research)  │  │   └─────┬──────┘    ║
║                            └──────┬───────┘  │         │           ║
║                                   │          └─────────┘           ║
║                                   ▼                                 ║
║                            ┌──────────────┐     ┌──────────┐       ║
║                            │ RESEARCHERS  │     │  BURNS   │       ║
║                            │ (receive USD)│     │  2% fee  │       ║
║                            └──────────────┘     │ permanent│       ║
║                                                 └──────────┘       ║
╚══════════════════════════════════════════════════════════════════════╝
```

### Inputs

| Input | Source | Rate | Character |
|---|---|---|---|
| RSC deposits | Holders → Endowment pool | Bursty (3 doubling events in 13 days) | Stock accumulation |
| New money | Buyers → Exchange order books | Driven by catalysts + narrative | Flow |
| Emission schedule | Protocol rule: E(t) = 9.5M / 2^(t/64) | 26,027 credits/day, monotonically decreasing | Exogenous clock |
| External catalysts | Press, listings, BTC rallies | Irregular, unpredictable | Impulse shocks |
| Treasury disbursements | Foundation Community (7M), Team vesting | Irregular (monthly contributor pay, ad hoc grants) | Impulse supply shocks |

### Outputs

| Output | Destination | Rate | Character |
|---|---|---|---|
| Funding Credits | → Proposals → Researchers (as USD) | 26,027/day split proportionally | **Leaves system as USD. Never re-enters as tradeable RSC.** |
| Burns | → Zero address (permanent) | ~266-322/day (accelerating) | Permanent supply destruction |
| Price signal | → All participants (information) | Continuous | Emergent from order book |
| Sell pressure | Treasury recipients → exchanges | Irregular | **Primary source of downward price shocks** |

### Components

| Component | State Variable | Role |
|---|---|---|
| **Endowment Pool** | total_platform_rsc (~11.2M) | Accumulator. Removes RSC from trading float. |
| **Credit System** | daily_emission (26,027), proportional_share | Distributor. Splits emission by deposit weight × time. |
| **Treasury Wallets** | Foundation 473M, Team 298M, Community 7M | Stored potential energy. Dormant = stable. Active = shocks. |
| **Burn Mechanism** | 2% per platform transaction | Entropy sink. Permanently destroys supply. |
| **Holder Agents** | rsc_held, deposit_date, archetype | Decision-makers. B=f(P,E) — deposit/hold/withdraw based on APY, price, risk tolerance. |

### Exchange Microstructure (decomposed)

The systems diagram shows "Exchange Order Books" as one box. In reality it is five distinct actor classes with different mechanics, motivations, and volumes. Most RSC volume is **infrastructure**, not humans making decisions.

```
                    EXCHANGE ORDER BOOKS (decomposed)
 ┌──────────────────────────────────────────────────────────────┐
 │                                                              │
 │  ┌─────────────────┐     ┌──────────────────┐               │
 │  │  AMM POOLS       │     │  CEX MARKET       │              │
 │  │  (Aerodrome,     │     │  MAKERS            │             │
 │  │   Uniswap)       │     │  (Gate.io, MEXC)   │             │
 │  │                  │     │                    │              │
 │  │  Algo: x·y = k  │     │  Algo: bid/ask     │             │
 │  │  No intent —     │     │  spread capture    │             │
 │  │  pure math       │     │  Inventory-neutral │             │
 │  │  ~30-50% of vol  │     │  ~20-40% of vol    │             │
 │  └────────┬─────────┘     └────────┬───────────┘             │
 │           │                        │                         │
 │  ┌────────▼────────────────────────▼───────────┐             │
 │  │          VISIBLE PRICE / VOLUME              │             │
 │  │  ($2M/day reported — but mostly internal)    │             │
 │  └────────▲────────────────────────▲───────────┘             │
 │           │                        │                         │
 │  ┌────────┴─────────┐     ┌────────┴───────────┐            │
 │  │  WASH TRADING     │     │  RETAIL + OTC       │           │
 │  │                   │     │                     │            │
 │  │  Self-dealing,    │     │  Discord community, │           │
 │  │  inflates volume  │     │  OTC desks,         │           │
 │  │  Zero real flow   │     │  intermediaries     │           │
 │  │  ~10-30% of vol   │     │  ~5-20% of vol      │           │
 │  └───────────────────┘     └─────────────────────┘           │
 │                                                              │
 │  REAL DIRECTIONAL FLOW: ~$100-200K of the $2M               │
 │  Everything else is intermediation and noise.                │
 └──────────────────────────────────────────────────────────────┘
```

| Actor | Type | Mechanism | RSC Source | Motivation | Est. Volume Share |
|---|---|---|---|---|---|
| **AMM Pools** (Aerodrome, Uniswap) | Algorithmic | Constant-product (x·y=k). Sell RSC as price rises, buy as price falls. No intent — pure math. | Liquidity providers deposit RSC+ETH pairs. Pool rebalances mechanically. | None — no actor "decides." LPs earn swap fees. | 30-50% |
| **CEX Market Makers** (Gate.io, MEXC, Coinbase) | Algorithmic | Place bid/ask orders around mid-price. Capture spread. Inventory-neutral over time. | Source RSC from other venues (arb), OTC, or existing inventory. | Spread profit. Will exit if inventory risk exceeds spread revenue. | 20-40% |
| **Wash Trading** | Noise | Entity trades with itself. Buy at $0.107, sell at $0.107. Volume inflated, no price impact. | Same RSC recycled. No net flow. | Inflate volume metrics to attract real traders. Common on MEXC. | 10-30% |
| **OTC / Intermediaries** | Opaque | Off-exchange negotiated trades. Insider RSC (team vesting, contributor pay) sold through desks. | Team vesting (73K/quarter), contributor payouts, Foundation Community disbursements. | USD for operations/living expenses. | 5-15% |
| **Retail Participants** | Discretionary | Discord community, Twitter followers. Human decisions — buy on narrative, sell on fear. | Personal holdings, Coinbase purchases. Typical position 5K-50K RSC. | Profit, belief in DeSci, yield farming. | 5-15% |

**Key structural insight:** The Discord community — the only actors visible to a participant — represents perhaps 5-15% of daily volume. The market is primarily infrastructure (AMMs + MMs providing ~50-80% of volume) and noise (wash trading inflating the rest). A single $50-100K directional buy from one invisible actor can move price 10-15% because it exhausts the real inventory behind the infrastructure's algorithmic quotes.

**What this means for price discovery:** RSC price is NOT set by community consensus or retail supply/demand. It is set by the interaction between a thin layer of real directional flow and the algorithmic response of infrastructure that has limited RSC inventory to offer. When an infrastructure actor's inventory depletes (AMM pool drains, MM runs out of RSC to sell), price gaps up until new RSC enters the system (treasury disbursement, endowment withdrawal, or new LP deposit).

### Feedback Loops

**Loop 1 — Supply Squeeze (positive, reinforcing):**
```
More deposits → less trading float → thinner order book →
  same buy pressure moves price more → price up →
  credit value up (denominated in RSC at higher price) →
  yield looks better → more deposits → ...
```
*Currently active. Bull case.*

**Loop 2 — Self-Balancing APY (negative, stabilizing):**
```
High APY → attracts depositors → total pool grows →
  each depositor's share shrinks → effective APY drops →
  fewer new depositors → APY stabilizes
```
*Working. Shingai share: 44% → 3.87% in 13 days.*

**Loop 3 — Profit-Taking Reversion (negative, stabilizing):**
```
Price spikes → early holders see +100% → sell into thin bids →
  price drops → buy pressure rebuilds → price recovers partially
```
*Observed Apr 23→24. The -39% crash on flat BTC.*

**Loop 4 — Cascade Exit (positive, destabilizing — NOT YET OBSERVED):**
```
Whale withdraws from endowment → sells on exchange →
  price crashes → other holders see USD value collapse →
  exit endowment despite high APY → more sells → death spiral
```
*Bear case. The v4 ABM stress scenario module models this.*

### Critical Interfaces

| Interface | What Crosses It | Why It Matters |
|---|---|---|
| **Holder ↔ Endowment** | RSC in (deposit), RSC out (withdraw) | No lock-up = zero friction exit. Enables Loop 4. |
| **Endowment → Credits** | Proportional daily emission | One-way valve. Credits can never become tradeable RSC. The deflationary core. |
| **Credits → Proposals → USD** | Funding decisions, USD payouts | RSC value exits the token economy entirely. No downstream sell pressure from yield. |
| **Treasury → Market** | Disbursements to contributors/ops | **The sell-pressure spigot.** 7M RSC in Community wallet. Each disbursement is an impulse shock to a thin book. |
| **Exchange ↔ External** | Buy/sell orders, new capital, listings | Where endogenous RSC dynamics meet exogenous crypto market. Amplifier for both catalysts and crashes. |
| **Real Flow ↔ Infrastructure** | Directional buys/sells vs algorithmic responses | ~$100-200K of real flow drives price. ~$1.8M of infrastructure volume intermediates it. The visible market ($2M volume) is mostly machinery, not signal. |

### One-Sentence Model

RSC deposits flow into a one-way deflationary valve (credits → USD → gone), creating a supply squeeze that amplifies any buy-side catalyst through thin order books, while treasury disbursements and zero-friction withdrawals create symmetric downside shocks — and the only structural asymmetry favoring bulls is that **burned RSC never comes back**. The visible market ($2M/day volume) is mostly algorithmic infrastructure (AMMs, market makers) and noise (wash trading) — real directional flow is perhaps $100-200K/day, meaning one motivated buyer or seller can move price 10%+ because the infrastructure has limited RSC inventory to buffer the impact.

---

## Platform Wallet Infrastructure

### Known RH-controlled wallets

| Label | Address | Type | Chain | Role |
|---|---|---|---|---|
| **Hot Wallet (primary)** | `0x7F57d306a9422ee8175aDc25898B1b2EBF1010cb` | EOA | Both | Main pooled deposit wallet |
| **Second deposit wallet** | `0x467564DCCE90FB21153adfa69c48A3Be235d66D3` | EOA | Base | Secondary collection address (discovered via trace) |
| Treasury 1 (Foundation) | `0x5222ff25f4dfc02d173c2cbd2055ee1d35f291f1` | — | Ethereum | Foundation |
| Treasury 2 (Team) | `0xe3648e99b6e68a09e28428790d12b357f081dbe0` | — | Ethereum | Team |
| Treasury 3 (Foundation Community) | `0xc4cfa2bdae08416312faa0b72758e1f3750f81e3` | — | Ethereum | Foundation Community |
| Treasury (Base) | `0xb280f00e70f28e8ce38c40826270de7e1b327e21` | — | Base | Foundation Community |

**Explorer links (primary monitoring):**
- Hot wallet ETH: https://etherscan.io/address/0x7f57d306a9422ee8175adc25898b1b2ebf1010cb
- Hot wallet Base: https://basescan.org/address/0x7f57d306a9422ee8175adc25898b1b2ebf1010cb
- Second wallet Base: https://basescan.org/address/0x467564DCCE90FB21153adfa69c48A3Be235d66D3

**Custody note:** Hot wallet is an EOA (single private key, not multisig). This is the primary custody risk — a single key controls all pooled user deposits.

**API for monitoring (Blockscout, no API key needed):**
```
# Hot wallet Base RSC transfers
https://base.blockscout.com/api/v2/addresses/0x7F57d306a9422ee8175aDc25898B1b2EBF1010cb/token-transfers?type=ERC-20&token=0xfbb75a59193a3525a8825bebe7d4b56899e2f7e1

# Second wallet Base RSC transfers  
https://base.blockscout.com/api/v2/addresses/0x467564DCCE90FB21153adfa69c48A3Be235d66D3/token-transfers?type=ERC-20&token=0xfbb75a59193a3525a8825bebe7d4b56899e2f7e1
```

---

## Known Depositors

### 🐋 ResearchHub Foundation Treasury (Apr 16 — NEW)

**The biggest signal since launch.** RH Foundation deposited 769,130 RSC from their treasury on Apr 16, 2026. This means the Foundation is dogfooding the endowment — staking their own treasury into the mechanism they designed.

| Field | Value |
|---|---|
| Source wallet | `0xb280F00e70F28e8ce38c40826270de7e1b327e21` (RH Treasury Base / Foundation Community) |
| Account abstraction proxy | `0xA03bdb65C71119d2Aa0ef7C2E3E2a6f88C2fb9ff` |
| Total deposited | 769,130 RSC (~$56,000 at $0.073) |
| Chain | Base |
| Destination | Second wallet `0x467564DCCE90...` |

**Deposit sequence (test-then-send pattern):**

| Time (Apr 16) | Action |
|---|---|
| 21:16:31 | Treasury → proxy: 100 RSC test |
| 21:20:25 | Proxy → hot wallet: 100 RSC test |
| 21:37:19 | Treasury → proxy: **769,130 RSC** |
| 21:40:11 | Proxy → second wallet: **769,130 RSC** |

**Strategic implications:**
- Foundation is not just marketing — they're committing capital
- Creates strong signal for fiduciary-obligated institutional depositors to follow
- At current burn rate (845 RSC/burn event), their 769K stake generates ~$56/day in funding credits for science
- This deposit alone accounts for ~25% of the Apr 15→16 platform growth (~2.9M total)

### Shingai (you)

| Field | Value |
|---|---|
| Deposit address | `0xa7234ea40958F5A811D63a9A87eF69a44aD3e75e` |
| Address type | ERC1967Proxy → SingleOwnerMSCA (account abstraction) |
| Total deposited | 432,675 RSC (~$27,366) |
| Deposit date | Apr 10-12, 2026 |
| Share of platform (launch) | ~44% of emissions |
| Share of platform (Apr 15) | ~18.4% of emissions |
| Share of platform (Apr 16) | **~8.25% of emissions** |

**Deposit history:**

| Date | Amount | Chain | Source | Destination |
|---|---|---|---|---|
| Apr 10 | 3,298 RSC | Ethereum | `0x77b175d1...` | Hot wallet |
| Apr 10 | 192,984 RSC | Base | `0x739120Ad...` (Coinbase-originated) | Second wallet `0x467564...` |
| Apr 12 | 135,350 RSC | Ethereum | `0x97d7298C...` | Hot wallet |
| Apr 12 | 101,043 RSC | Base | `0x1985EA6E...` (Coinbase Hot Wallet) | Hot wallet |

### Jeffrey Koury (RH Foundation President)

| Field | Value |
|---|---|
| Deposit address | `0xe81c64f3B501Df1a222F4ecAEbf868CcBF532fA0` |
| Address type | ERC1967Proxy → SingleOwnerMSCA |
| Farcaster wallet | `0x29E46015cCFe13cfe8dC96D75760a6290dF311Ee` (linked to warpcast.com/jeffreykoury) |
| Accumulation wallet | `0x26b610a059dE2488ebe3e0EDa02Ae17907917419` |
| Total deposited | ~477,354 RSC |
| Activity | Testing since Mar 3; major deposit on launch day; no new deposits since Apr 10 |

**Deposit history:**

| Date | Amount | Source | Destination |
|---|---|---|---|
| Mar 3 | 98 RSC | Farcaster/Koury wallet | Hot wallet |
| Mar 3 | 197 RSC | Coinbase | Hot wallet |
| Mar 4 | 196 RSC | `0x0581FA...` | Hot wallet |
| Mar 17 | 75,064 RSC | Farcaster/Koury wallet | Hot wallet |
| Apr 10 | 23,337 RSC | Farcaster/Koury wallet | Hot wallet |
| Apr 10 | 378,659 RSC | `0x26b610a...` (accumulation wallet) | Second wallet |

**Note:** Koury was testing deposits in March with tiny amounts (98-197 RSC) weeks before public launch. The Mar 17 deposit of 75K was a pre-launch positioning move.

### Other identified depositors (Apr 14-16)

| Address | Total Deposited | Dates | Notes |
|---|---|---|---|
| `0x7C6DD803115A...` | ~22K RSC | Apr 14, 16 | Multiple small deposits (15, 5,276, 16,672, 19 RSC) |
| `0xF965cDf1FC21...` | ~16K RSC | Apr 14 | Single deposit |
| `0xa0de3E1087B1...` | ~55K RSC | Apr 15 | Two deposits (1,434 + 54,000). Largest new depositor post-launch |
| `0xBE645050439f...` | ~8K RSC | Apr 16 | Single deposit |

These are the yield seekers arriving — mid-size holders responding to the high early APY signal.

### Growing depositors (Apr 16-23)

**Repeat depositors (accumulating aggressively):**

| Address | Lifetime Total | Deposits | Notes |
|---|---|---|---|
| `0xa0de3E1087B1...` | ~205K RSC | 1,434 + 54K + 46K + 50K + 50K | Steady accumulator since Apr 15. ~$28K at current price. |
| `0x20e43F866130...` | ~200K RSC | 50K + 97.6K + 50K + 2.6K | Largest single deposit 97.6K on Apr 20. |
| `0x973342adf59A...` | ~67K RSC | 30K + 37.5K | Two deposits on Apr 17. |

**New depositors (Apr 17-23):**

| Address | Amount | Date | Notes |
|---|---|---|---|
| `0xDd8A8aD1A7dC...` | 25,000 RSC | Apr 20 | Single deposit |
| `0x99e9d3B16A99...` | 34,613 RSC | Apr 22 | Single deposit |
| `0xFd6E47a9C36D...` | 6,419 RSC | Apr 22 | Small |

**Untraced whale (Apr 20):** ~5M RSC deposited through unknown collection wallets. Largest single-day deposit event. Not visible through monitored addresses. Credit-implied platform RSC doubled from ~5.3M to ~10.5M overnight.

**RH Foundation Treasury** (Apr 16): 769,130 RSC (see Foundation section above).

### Identified withdrawals (Apr 13-16)

| Date | To | Amount | Notes |
|---|---|---|---|
| Apr 13 | `0x000000000000...` | 845.78 RSC | **BURN** (2% platform fee) |
| Apr 13 | `0xc35D46d4...` | 1,861 RSC | User withdrawal |
| Apr 13 | `0x99f9D543...` | 1,865 RSC | User withdrawal |
| Apr 13 | `0x7165DC61...` | 200 RSC | User withdrawal |
| Apr 14 | `0x6FFdA9Cf...` | 2,500 RSC | User withdrawal |
| Apr 14 | `0x1C8FD3c9...` | 2,500 RSC | User withdrawal |
| Apr 14 | `0xaC005954...` | 2,500 RSC | User withdrawal |
| Apr 14 | `0x544E4311...` | 5,003 RSC | User withdrawal |
| Apr 14 | `0xD2eAFC03...` | 7,507 RSC | User withdrawal |
| Apr 14 | `0xaF58cFD7...` | 4,996 RSC | User withdrawal |
| Apr 15 | `0xc35D46d4...` | 5,001 RSC | User withdrawal (repeat address) |
| Apr 15 | `0x7165DC61...` | 4,810 RSC | User withdrawal (repeat address) |
| Apr 16 | `0x519D4Fba...` | 8,311 RSC | User withdrawal |

**Net flow:** Inflows (~100K+) significantly exceed outflows (~48K). Platform is growing.

---

## Hot Wallet Balance History

| Date | Ethereum | Base | Second Wallet (Base) | Total Known | Credit-Implied Total | Gap |
|---|---|---|---|---|---|---|
| Apr 13 | 630,705 | 512,665 | 542,984 | 1,686,354 | ~1,898,000 | 212K |
| Apr 16 (midday) | 628,196 | 569,362 | 542,984 | 1,740,542 | ~2,352,000 | 612K |
| Apr 16 (post-Foundation) | 628,196 | 787,010 | 1,312,114 | ~2,727,320 | ~5,245,000 | 2.5M |
| Apr 19 (Sim) | 625,979 | 687,051 | 2,440,773 | 3,753,803 | ~5,270,000 | 1.5M |
| **Apr 23 (Sim)** | **630,184** | **945,433** | **1,690,773** | **3,266,390** | **~11,180,000** | **7.9M** |

**The gap is now massive and growing.** Known wallets show 3.27M but credit-implied total is 11.18M. ~7.9M RSC is flowing through deposit infrastructure we cannot see. This confirms multiple undiscovered collection wallets or a direct-to-protocol deposit mechanism.

**Second wallet balance dropped** from 2.44M (Apr 19) to 1.69M (Apr 23) — ~750K moved out. Likely internal rebalancing to an unseen wallet, not a user withdrawal.

**Note:** Apr 19 and Apr 23 balances queried via Dune Sim API (more reliable than Blockscout for real-time balances).

---

## Credit Distribution Log (Shingai)

| Date | Credits Earned | Your Share | Implied Platform RSC | Effective APY |
|---|---|---|---|---|
| Apr 11 | 4,625.68 | 23.7% | ~827K | ~1,148% |
| Apr 12 | 6,194.66 | 23.8% | ~1,818K | ~1,148% |
| Apr 13 | 5,940.39 | 22.8% | ~1,898K | ~1,103% |
| Apr 14 | 5,764.66 | 22.1% | ~1,958K | ~1,070% |
| Apr 15 | 4,781.83 | 18.4% | ~2,352K | ~888% |
| Apr 16 | 2,147.27 | 8.25% | ~5,245K | ~400% |
| Apr 17 | 2,120.28 | 8.15% | ~5,310K | ~394% |
| Apr 18 | 2,100.71 | 8.07% | ~5,360K | ~390% |
| Apr 19 | 2,137.04 | 8.21% | ~5,270K | ~397% |
| **Apr 20** | **1,077.31** | **4.14%** | **~10,450K** | **~200%** |
| Apr 21 | 1,081.50 | 4.16% | ~10,400K | ~201% |
| **Apr 22** | **1,008.03** | **3.87%** | **~11,180K** | **~187%** |
| **Total** | **~36,859** | — | — | — |

**Phase transitions:** Three distinct doublings of platform RSC:
1. Apr 11-12: ~827K → ~1.8M (initial depositor wave)
2. Apr 15-16: ~2.35M → ~5.24M (RH Foundation Treasury 769K + others)
3. **Apr 19-20: ~5.27M → ~10.45M (unknown whale — ~5M RSC in one day, largest single deposit event)**

**Apr 20 whale:** ~5M RSC deposited in a single day — 6.5x larger than Foundation's deposit. Not visible through known wallets. Credit-implied total (~11.2M) exceeds known wallet balances (~3.27M) by ~7.9M. Multiple undiscovered collection wallets likely.

**Steady-state comparison:** At 30% participation (23.6% APY), 13 days would earn ~3,640 credits. Actual earned: ~36,859. **Early-mover earned ~10x steady-state rate.**

**Credit value at various RSC prices:**

| RSC Price | 36,859 Credits Value | 30-day Projected Credits | 30-day Value |
|---|---|---|---|
| $0.063 (entry) | $2,322 | ~30,000 (at 4% share) | $1,890 |
| $0.138 (Apr 23) | $5,087 | ~30,000 | $4,140 |
| $0.24 (2025 settling) | $8,846 | ~30,000 | $7,200 |
| $1.00 | $36,859 | ~30,000 | $30,000 |

**Position summary (Apr 30):**

| Metric | At entry (Apr 10) | Peak (Apr 23) | Now (Apr 30) | Change from entry |
|---|---|---|---|---|
| RSC price | $0.063 | $0.138 | $0.107 | +70% |
| Principal value | $27,259 | $59,709 | $46,296 | +70% |
| Credits banked | 0 | ~36,859 ($5,087) | ~44,000 est ($4,708) | — |
| Platform share | 44% | 3.87% | ~3.87% est | -91% |
| Total position value | $27,259 | ~$64,796 | ~$51,004 | **+87%** |

**Recovery from Apr 24 crash.** Principal +70% from entry. ~20 days of credits banked (~$4.7K).

---

## Market Context Timeline

| Date | Event | RSC Price |
|---|---|---|
| Mar 28-Apr 1 | Price bottom | $0.056 |
| Apr 5 | Pump (likely insider accumulation) | $0.067 |
| Apr 6-7 | Crash back down | $0.058-0.062 |
| Apr 10 | **Endowment launches.** Exchanges drain within hours. Coinbase rationing RSC. Aerodrome 18.76% price impact. | $0.062 |
| Apr 10 | Shingai deposits 196K RSC. Koury deposits 477K RSC. | $0.063 |
| Apr 12 | Shingai deposits additional 236K RSC (total 432K). | $0.063 |
| Apr 13 | First burn observed (845 RSC to zero address). | $0.065 |
| Apr 14-15 | New mid-size depositors arrive (~100K RSC). Yield seekers entering. | $0.065-0.068 |
| **Apr 16** | **RH Foundation deposits 769K RSC from treasury. Platform doubles to ~5.24M.** | **$0.073** |
| Apr 17-19 | Steady drip: `0x973342...` (67K), `0x20e43F...` (50K), mid-size yield seekers. Platform stable ~5.3M. | $0.073-0.14 |
| **Apr 20** | **Unknown whale deposits ~5M RSC. Platform doubles AGAIN to ~10.5M. Shingai share drops 8% → 4%.** | ~$0.14 |
| Apr 20 | Second burn observed: 1,020 RSC to zero address. | — |
| Apr 20-22 | `0x20e43F...` adds 97.6K, `0xa0de3E...` adds 100K, steady mid-size inflow. | $0.138 |
| **Apr 23** | RSC at $0.138 (+119% from entry). Exchanges still dry — Coinbase ~$1K limits, Uniswap 20% slippage on $1K. ~5.1% of circulating locked in endowment (~80% of estimated active trading float). | **$0.138** |
| **Apr 23** | Foundation Community wallet (`0xc4cf...`) disburses 1,294,018 RSC to new address `0x6B87...be6` (100 RSC test tx, then full amount). Two-hop: forwarded within 43min to `0x3e3f...7161` where it sits idle. | $0.138 |
| **Apr 24** | **Price crashes to $0.096 (-39% in 24h).** Volume spikes to $2.95M (6-10x normal). BTC flat at $77.5K, ETH flat at $2,314 — RSC move is entirely idiosyncratic. Thin book amplifies both directions. | **$0.096** |
| Apr 24-29 | Recovery. Price grinds back up while BTC/ETH drift sideways-to-down (BTC -1.3%, ETH -2.3%). No new Foundation disbursements. `0x3e3f` still holding (now ~1.71M RSC — had prior 2025 inflows). | $0.096→$0.107 |
| **Apr 30** | **RSC $0.107 (+13.5% 24h, +27% 7d).** Volume $2.04M (4-6x normal). BTC $76.5K (flat), ETH $2,267 (flat). Independent move — no correlated macro driver. | **$0.107** |

---

## Treasury Wallet Audit (Apr 24)

On-chain audit of all known RH-controlled wallets. Primary question: where does new sell-side supply come from?

| Wallet | RSC Balance | Last Outflow | Activity Level |
|---|---|---|---|
| **Foundation** (`0x5222...`) | 473,670,000 | Mar 6 (1M → hot wallet) | **Dormant 7 weeks** |
| **Team** (`0xe364...`) | 297,950,000 | Feb 16 (146K vesting) | **Dormant (vesting drip only)** |
| **Foundation Community ETH** (`0xc4cf...`) | 7,092,043 | **Apr 23 (1.29M → new addr)** | **Active — just disbursed** |
| **Base Treasury** (`0xb280...`) | 1,262 | Apr 16 (769K → endowment) | **Nearly empty** |

**Key finding:** The big treasuries (Foundation 473M, Team 298M) are NOT selling. The active supply source is the Foundation Community wallet (7M RSC), which disbursed 1.29M on the peak day.

### Foundation Community Disbursement Trace (Apr 23)

```
Foundation Community (0xc4cf...) → 100 RSC test tx → 0x6B87c4fD959d924E3d9fBE072a065AA8533D3be6
Foundation Community (0xc4cf...) → 1,294,018 RSC → 0x6B87...
  → 43 minutes later:
    0x6B87 → 666 RSC → 0x3e3ff36273df89400946eb840175eda5e17a7161
    0x6B87 → 1,293,452 RSC → 0x3e3f...7161
```

**0x6B87** is a Foundation operational wallet (previously received ~$100K USDC, interacted with MetaMask Swap Router). The RSC was forwarded immediately.

**0x3e3f...7161** is the final destination — an EOA with no prior RSC activity (only spam token airdrops). As of Apr 24, the ~1.294M RSC **has not been sold**. It sits idle.

**Assessment:** This is either treasury reorganization, staging for a future operation (grant, partnership, OTC deal), or pre-positioned sell-side supply. Not the direct cause of the Apr 24 crash, but a loaded gun — 1.29M RSC on a thin order book could crash price 40%+ if sold.

### Supply Sources Pipeline

```
Active sell pressure sources:
  Foundation Community (7.09M RSC) → periodic disbursements to unknown addrs
  Base Treasury contributor payouts (5K-35K/month/person, ~8-10 recipients)
  Team vesting disbursements (~73K/quarter to 0x8eC6...)
  Endowment withdrawals → sell on exchange

Dormant (not currently selling):
  Foundation Treasury (473.7M RSC) — no outflows since Mar 6
  Team Treasury (297.9M RSC) — no outflows since Feb 16
  Top 10 private holders (~200M RSC aggregate)
```

---

## Exchange Liquidity Observations

| Venue | Apr 10 | Apr 23 |
|---|---|---|
| **Coinbase** | ~$1,452/fill. Rationing by depth. | Still ~$1K/fill. No improvement despite 2x price. |
| **Uniswap (Ethereum)** | Huge spreads. | 20% slippage on $1K buys. Worse. |
| **Aerodrome (Base)** | 18.76% impact on 15 ETH. | Not retested but likely similar. |
| **Gate.io** | Not tested | Unknown |

### Liquidity Paradox

**Liquidity has not improved despite price doubling.** The endowment is vacuuming supply faster than market makers can replenish. ~5.1% of circulating (11.2M / 220M) is locked in endowment deposits. If the actively-traded float is ~14M (estimated from pre-endowment volume patterns), that's ~80% of liquid supply absorbed. Remaining actively-traded supply: ~3M RSC across all venues (estimated, not verified).

### What Would Make Order Books Thick

The endowment mechanism **structurally works against deep liquidity.** Every RSC deposited is one fewer RSC available for market makers to trade. The supply squeeze that drives the bull case is the same force that keeps the book thin. You cannot have both a depleted float and deep liquidity — they are directly opposed.

**Prerequisites for thick books:**

| Requirement | Current State | Gap |
|---|---|---|
| **Sustained volume ($5-10M+/day)** | $300-500K normal, $2.95M spike | 10-20x below threshold for professional market makers |
| **Binance listing** | Not listed | Binance brings its own MM infrastructure; step-change event |
| **Sourceable inventory** | ~3M RSC actively traded | Market makers can't fill both sides of the book without inventory |
| **Lower concentration risk** | Top 10 hold 93.66% | No MM wants exposure where one wallet can wipe their position |
| **Higher per-token dollar value** | $0.096 → 3M float = $288K total | At $1.00, same 3M float = $3M — minimally viable for a small desk |

**Resolution path:** Price must rise first, liquidity follows. At $1.00+, the dollar value of the remaining float becomes large enough for market makers to justify inventory risk. At $0.10, the entire actively-traded supply is worth less than a single MM's daily risk budget.

**Implication for depositors:** Thin books are the medium-term normal. Volatility (both up and down) will remain 5-10x that of majors. Price discovery is dominated by impulse events (treasury disbursements, whale deposits, catalysts), not continuous trading. Accept this as the operating environment.

### Volume Source Puzzle (Apr 30)

$2M daily volume at $0.107 = ~18.7M RSC changing hands per day. But Discord retail community is mostly small fish (5K-50K RSC positions). Foundation isn't selling. `0x3e3f` hasn't sold. Where is $2M of two-sided volume coming from?

**Hypothesis: most of the volume is NOT retail participants visible in Discord.**

Likely sources of the sell-side (meeting the buy demand):

| Source | Estimated Contribution | Evidence |
|---|---|---|
| **Automated market makers (AMMs)** | 30-50% | Aerodrome/Uniswap pools provide liquidity algorithmically. They sell RSC as price rises (constant-product rebalancing). This is passive, not discretionary. |
| **CEX market makers (Gate.io, MEXC)** | 20-40% | Professional desks provide liquidity on centralized order books. They buy low / sell high mechanically. Not community members. |
| **Wash trading / self-dealing** | 10-30% | Common on MEXC especially. Inflates volume without real supply/demand. One entity trading with themselves. |
| **OTC / non-public holders** | 10-20% | The 779M RSC in insider wallets. Some may be selling small amounts via OTC desks or through intermediaries that don't show up as Foundation wallet moves. |
| **Actual retail profit-takers** | 5-15% | Discord small fish selling 5K-50K RSC into the pump. Real but tiny relative to total volume. |

**Key insight:** The Discord community is not the market. Most volume is **infrastructure** (AMMs, market makers) and **noise** (wash trading), not humans making decisions. The actual directional supply/demand imbalance — the thing that moves price — might be only $100-200K of the $2M volume. Everything else is intermediation.

**Why price moves on so little real flow:** In a thin-book market with most volume being market-making infrastructure, a single $50K directional buy exhausts the real ask-side supply (the AMMs and MMs adjust, but there's no new RSC to replenish their inventory). The "demand" that's pumping RSC might be one or two entities buying $50-100K/day into a market where no one with real size is selling back.

---

## Architectural Notes

### User deposit flow (traced on-chain)

```
User sends RSC to personal deposit address (ERC1967Proxy → SingleOwnerMSCA)
  → handleOps routes to either:
    → Hot Wallet (0x7F57d3...) — primary collection
    → Second Wallet (0x467564...) — secondary collection (discovered Apr 10)
  → Routing logic unclear — same user can hit different wallets on different deposits
```

### Account abstraction

All user deposit addresses are ERC1967Proxy contracts implementing `SingleOwnerMSCA` (Modular Smart Contract Account). Implementation address: `0xD206aC7fEf53d83ED4563E770b28Dba90D0D9eC8`. Deposits trigger `handleOps` calls, not simple transfers.

### Burn mechanism

Burns go to `0x000000000000...` (zero address). This is the 2% platform fee burn operating in real time.

**Observed burns:**

| Date | Amount | Source |
|---|---|---|
| Apr 13 | 845.78 RSC | Hot wallet on-chain trace |
| Apr 20 | 1,020.19 RSC | Hot wallet on-chain trace |

**Aggregate burn data (from rscstats.pages.dev, Apr 23):**

| Window | RSC Burned | Daily Average |
|---|---|---|
| Total (lifetime) | 126,590 | — |
| 90-day | 28,989 | ~322/day |
| 30-day | 7,989 | ~266/day |

Cross-validated: CoinGecko shows available supply of 999,873,409 vs 1B total = ~126,591 burned. Matches rscstats within 1 RSC.

**Burns are accelerating.** Pre-endowment average was ~693/day (from Jan 2026 burn data in background doc). 30-day average now at 266/day may seem lower, but note the 30-day window (Mar 24 - Apr 23) includes the low-activity pre-endowment period. Post-endowment burns should accelerate further as more credits are deployed to fund proposals, each triggering 2% burns.

**External tracker:** https://rscstats.pages.dev/ — daily midnight UTC updates, maintained by D'Elia (RH community member). Useful for cross-validation.

---

## Price Action Analysis

### Jan 2025 ATH ($1.51) — Mechanism

The prior ATH was a compound catalyst, not a single event:

| Date | Catalyst | RSC Price | BTC Price |
|---|---|---|---|
| Nov 29, 2024 | **Gate.io listing** (first major CEX). RSC/USDT pair opened. | ~$0.10 | ~$97K |
| Dec 11, 2024 | **Nature magazine feature** — RSC +23% in 24h. World's most-cited journal covering RH's paid peer review model. | ~$0.30 | ~$100K |
| Dec-Jan | DeSci narrative momentum. Brian Armstrong (Coinbase CEO) backing RH amplified by press coverage. | $0.30-$1.04 | $94K-$100K |
| Jan 3-5, 2025 | **ATH: $1.44-$1.51.** 15x from Nov. Concentrated on CEX pairs (MEXC highest volume). | **$1.51** | $94K |
| Jan 31, 2025 | **Crash to $0.62** (-58% from ATH in 4 weeks). Classic CEX listing dump. | $0.62 | $102K |
| Feb 28, 2025 | Continued bleed to $0.34 (-77% from ATH). | $0.34 | — |
| Jul 31, 2025 | **Coinbase listing** — separate event, +70-100% pump. (NOT the Jan ATH catalyst.) | — | — |

**Pattern:** CEX listing → narrative catalyst (Nature) → thin-float parabolic → -77% retracement over 8 weeks. RSC's 15x massively outperformed BTC's +9% over the same period — confirming the move was idiosyncratic.

### BTC/ETH Correlation (Apr 2026)

RSC demonstrates **weak-to-negligible correlation** with majors during its endowment-era moves:

| Date | RSC | BTC | ETH | Correlated? |
|---|---|---|---|---|
| Apr 10 (launch) | $0.063 | $72,204 | $2,218 | No — RSC moved on endowment news |
| Apr 20-23 (spike) | $0.063→$0.138 (+119%) | $75K→$78K (+4%) | $2,318→$2,314 (flat) | **No — RSC 30x BTC's move** |
| Apr 24 (crash) | $0.138→$0.096 (-39%) | $77,500 (flat) | $2,314 (flat) | **No — RSC crashed alone** |

30-day ranges: BTC +12.5% ($68.9K→$77.5K), ETH +15% ($2,014→$2,314), RSC +72% ($0.056→$0.096) with 119% peak and -39% single-day crash. RSC volatility is 5-10x majors.

**Structural interpretation:** RSC moves independently in bursts driven by RSC-specific catalysts (listings, press, endowment). Between bursts, it has mild BTC beta (rising tide effect in altcoin rallies). The endowment mechanism creates a new class of idiosyncratic catalyst — supply-side structural change — that did not exist during the Jan 2025 pump.

### How RSC Gets Back to $1.00+ (Mechanism)

The Jan 2025 playbook was: **CEX listing + press catalyst + thin float = parabolic**. The post-endowment setup has the same ingredients amplified:

**What's the same:**
- Thin float (~220M circulating, ~14M actively traded)
- CEX fragmentation (Coinbase, Gate.io, MEXC — no Binance yet)
- DeSci narrative cycles
- Brian Armstrong connection

**What's structurally different (stronger):**
- **Endowment removes supply from active trading** — ~11.2M RSC locked (5.1% of circulating, but possibly ~80% of the ~14M estimated active trading float). Jan 2025 had no lock-up mechanism.
- **Deflationary credits** — researchers get USD, credits never re-enter circulation. Burns accelerate with platform usage.
- **Self-reinforcing loop** — price up → credit value up → more depositors → less float → price up further. This flywheel didn't exist in Jan 2025.
- **Foundation is a depositor** — alignment signal that didn't exist pre-endowment.

**Specific catalysts that could trigger next parabolic:**

| Catalyst | Probability | Price Impact | Mechanism |
|---|---|---|---|
| **Binance listing** | Low-medium | 5-15x | New demand channel into depleted order book. Gate.io listing alone did 15x. |
| **DeSci narrative cycle** | Medium | 2-5x | If DeSci pumps broadly, RSC is better positioned with yield narrative. |
| **BTC supercycle ($100K+)** | Medium-high | 1.5-3x | Rising tide lifts micro-caps. RSC beta to BTC during bull runs. |
| **Major press (Nature-tier)** | Low | 3-10x | Nature did +23% in 1 day. Similar coverage of endowment model could be larger with locked supply. |
| **Foundation/Team treasury deposit** | Medium | 2-5x | If Foundation deposits 50M RSC (10% of treasury), circulating supply collapses. |
| **Endowment hits critical mass** | High | Gradual 2-3x | If 30%+ of circulating locks up, free float approaches exhaustion. Market makers can't fill orders. |
| **RH marketing push** | Medium-high | 1.5-3x | RH hasn't actively marketed the yield yet. Once they do, retail inflows into Coinbase. |

**The math on float exhaustion:**
```
Current circulating: ~220M RSC
Currently locked in endowment: ~11.2M (5.1%)
Insider-held (Foundation+Team+Founder): ~779.7M (not circulating)
Estimated actively traded: ~14M

If endowment grows to 30M RSC locked → free float drops to ~190M → actively traded drops to ~3M
At $0.10/RSC, buying 3M RSC costs $300K — one whale could exhaust the entire float.
```

**The danger:** The same thin-float mechanics that enable 15x pumps also enable -77% crashes. Foundation Community wallet (7M RSC) + contributor payouts are a constant drip of sell pressure. Any insider disbursement during a low-volume period crashes price. The dump mechanism is symmetrical to the pump.

---

## Open Questions

1. **Third collection wallet (enlarged gap)?** Credit-implied platform RSC (~5.24M) now exceeds known wallet balances (~2.7M) by ~2.5M. The gap grew significantly on Apr 16. Either a third wallet exists, an Ethereum-side collection wallet mirrors the second one, or there's a direct-to-protocol deposit mechanism.
2. **Who are the other Apr 16 large depositors?** Beyond RH Foundation's 769K, another ~2.1M entered. Need to trace these.
3. **What triggers routing to second wallet vs hot wallet?** Same user (Shingai) hit both on different deposits.
4. **Where does USD for researcher payouts come from?** Likely RH treasury sells RSC, but unconfirmed on-chain.
5. **When will private whales deposit?** Top 10 private holders still hold ~200M RSC. Foundation's self-deposit changes fiduciary calculus — institutional holders may follow.
6. **Internal accounting transactions?** Apr 16 showed 67,829 RSC transfers from hot wallet to itself (×2). Purpose unclear — possibly internal rebalancing or snapshot-related.
7. **What happens to the 1.29M RSC at `0x3e3f...7161`?** Foundation Community disbursement from Apr 23, currently idle. If sold on exchange, ~40% price impact. Watch this address.
8. **What caused the Apr 24 crash (-39%)?** Not the 1.29M disbursement (still idle). Likely retail profit-taking + bot arbitrage hitting thin bids after the 119% run. Volume 6-10x normal ($2.95M) suggests active churn, possibly wash trading.

---

## ABM Validation Notes

| ABM Prediction | Reality (Week 1-2) | Match? |
|---|---|---|
| High early APY attracts yield seekers | Yes — continuous new depositors Apr 14-23, accelerating | ✓ |
| Self-balancing: high APY → entrants → APY compression | Yes — Shingai share dropped 44% → 3.87% in 13 days | ✓ |
| "House always wins" via deflation | Two burns confirmed (845 RSC Apr 13, 1,020 RSC Apr 20). Credits non-sellable. Price +119%. | ✓ |
| Whale concentration risk | Three whale events: Foundation 769K (Apr 16), unknown ~5M (Apr 20), mid-size repeat depositors (~200K each). Single deposit doubled platform RSC twice. | ✓ |
| Supply squeeze → price appreciation | **RSC $0.063 → $0.138 (+119%) while exchanges remain dry.** 5.1% of circulating locked, but most of actively-traded float absorbed. | ✓ |
| Participation equilibrium at 25-35% | Currently at ~5.2% (11.2M / 215M) — growing fast but still far from equilibrium | Pending |
| Yield seekers exit when APY drops | No exits from early depositors observed despite APY compression from 1,148% → 187% | Pending |
| Mechanism designer aligned with depositors | Foundation deposited own treasury (Apr 16) | ✓ |

**Model accuracy: 6/8 predictions confirmed in 13 days.** Two remaining (equilibrium rate, exit behavior) require more time to observe.

---

*Last updated: 2026-04-30*
*Companion docs: [chain-data-calibration-plan.md](chain-data-calibration-plan.md) | [ROADMAP.md](ROADMAP.md) | [v4-design-notes.md](v4-design-notes.md)*
