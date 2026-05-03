# Chain Data Calibration Plan

*Created 2026-04-11 — Endowment launched 2026-04-10*

The endowment is live. The ABM now has a real-world counterpart to validate against. This plan augments the simulator with on-chain and platform data so we can compare modeled dynamics against actual market behavior.

---

## Motivation

The ABM currently runs on synthetic agents with assumed behavioral parameters. Now that real deposits, real yields, and real price action exist, we can:

1. **Validate** — Does the sim's equilibrium participation rate match reality?
2. **Calibrate** — Fit archetype_mix and yield_threshold_mean to observed entry/exit patterns
3. **Predict** — Use calibrated model to project TVL, APY, and price trajectories

---

## Data Sources

### On-chain (query directly via API)

| Data point | Source | Frequency |
|---|---|---|
| RSC balance at RH deposit addresses | Etherscan / BaseScan API | Daily |
| Uniswap mainnet pool depth (RSC/WETH) | Uniswap v3 subgraph | Daily |
| Aerodrome Base pool depth (RSC pairs) | Aerodrome subgraph or API | Daily |
| Weekly burn transactions | Etherscan (RH burn address) | Weekly |
| Top holder distribution | Etherscan token holders API | Weekly |

**Key addresses:**
- Mainnet RSC token: `0xd101dcc414f310268c37eeb4cd376ccfa507f571`
- Base RSC token: `0xfbb75a59193a3525a8825bebe7d4b56899e2f7e1`
- RH Treasury (Base): `0xb280f00e70f28e8ce38c40826270de7e1b327e21`
- **RH Hot Wallet (pooled deposits):** `0x7F57d306a9422ee8175aDc25898B1b2EBF1010cb`
  - This is the primary observable for total platform TVL
  - EOA (single private key, not multisig — custody risk)
  - Holds deposits on both chains: Ethereum + Base
  - Etherscan: https://etherscan.io/address/0x7f57d306a9422ee8175adc25898b1b2ebf1010cb
  - BaseScan: https://basescan.org/address/0x7f57d306a9422ee8175adc25898b1b2ebf1010cb
- Shingai deposit address: `0xa7234ea40958F5A811D63a9A87eF69a44aD3e75e` (routes to hot wallet)

**Baseline observation (2026-04-13):**

| Chain | RSC in Hot Wallet |
|---|---|
| Ethereum | 630,705 RSC |
| Base | 512,665 RSC |
| **Total** | **1,143,370 RSC** |

This represents ~0.53% of circulating supply (215M). For context:
- RH docs "low participation" scenario = 15% (~20M RSC)
- No top-10 whale has deposited yet (they hold ~200M collectively)
- Shingai holds ~432K RSC = ~37.8% of all platform deposits
- Effective APY at this participation level: ~1,148%
- Daily emission per Shingai's share: ~11,400 credits/day (~44% of emissions)

### Market data (CoinGecko / CSV)

| Data point | Source | Frequency |
|---|---|---|
| RSC price (USD) | CoinGecko API / rsc-usd-max.csv | Daily |
| Daily volume | CoinGecko API | Daily |
| Market cap | CoinGecko API | Daily |

### Platform observables (manual or RH API if available)

| Data point | Source | Frequency |
|---|---|---|
| Number of funded proposals | ResearchHub platform | Weekly |
| Total credits deployed | RH API (if exposed) | Weekly |
| New depositor count | On-chain new transfers to RH addresses | Weekly |

---

## Implementation Phases

### Phase 1: Data Pipeline (Week 1)

Build `src/data/` module to collect and store real-world data.

```
src/data/
├── coingecko.py      # Price, volume, market cap (daily append to CSV)
├── onchain.py        # Etherscan/BaseScan balance queries
├── dex.py            # Uniswap + Aerodrome pool depth
└── store.py          # Local SQLite or CSV storage
```

- CoinGecko free API: `/api/v3/coins/researchcoin/market_chart`
- Etherscan API: `?module=account&action=tokenbalance&contractaddress=...&address=...`
- Cron job or manual daily run to append data

### Phase 2: Replay Mode (Week 2-3)

Add a "replay" mode to the model that feeds actual daily data as environment inputs instead of synthetic generation.

- Real price → agents react to actual market conditions
- Real participation (inferred from on-chain deposit totals) → validate agent entry/exit behavior
- Real APY (computed from actual platform RSC / emissions) → compare against sim APY curve

New API endpoint: `POST /api/replay {"start_date": "2026-04-10", "end_date": "2026-05-10"}`

### Phase 3: Sim vs Reality Dashboard Tab (Week 3-4)

New tab in the dashboard: **"Model vs Market"**

- Overlay charts: simulated participation rate vs actual (from on-chain deposit tracking)
- Overlay charts: simulated APY vs actual (computed from real platform RSC)
- Overlay charts: simulated price trajectory vs actual CoinGecko price
- Divergence metric: where is the model wrong and by how much?

### Phase 4: Archetype Calibration (Week 4+)

Use observed entry/exit patterns to reverse-engineer the real archetype_mix.

- Cluster depositors by behavior: hold duration, deposit size, exit timing relative to APY changes
- Map clusters to model archetypes (Believer, Yield Seeker, Institution, Speculator)
- Fit behavioral parameters (yield_threshold, hold_horizon, price_sensitivity) to match observed patterns
- Run sensitivity analysis: which parameters most affect model-reality divergence?

---

## Calibration Targets

| Model parameter | How to calibrate | Observable |
|---|---|---|
| `initial_participation_rate` | Directly measured | Total platform RSC / circulating supply |
| `yield_threshold_mean` | Fit to exit timing | When do depositors withdraw relative to APY drops? |
| `archetype_mix` | Cluster analysis | Deposit size × hold duration × exit behavior |
| `deploy_probability` | Count funded proposals | Credits deployed / credits earned ratio |
| `burn_rate` | Directly measured | Weekly burn tx amounts |
| Price model coefficients | Regression | Actual price vs modeled supply/demand |

---

## Key Questions to Answer

1. **What participation rate does the market actually equilibrate to?** (ABM predicts 25-35%)
2. **How fast do yield seekers enter/exit?** (ABM assumes weekly decisions — reality may be faster)
3. **Does the "house always wins" dynamic hold?** (Passive holders should benefit from deflation)
4. **Is the liquidity drain permanent or temporary?** (Do exchange pools refill after the initial rush?)
5. **How does the 93% whale concentration interact with the endowment?** (One whale depositing changes everything)

---

## Success Criteria

The calibrated model is useful when:
- Simulated participation rate tracks actual within ±5% after 4 weeks of data
- Simulated APY matches actual within ±2% at steady state
- Price direction (not magnitude) matches in 3 of 4 rolling 2-week windows
- Archetype distribution produces emergent behavior that matches observed entry/exit patterns

---

## References

- [ResearchHub Endowment — Official Docs](rh-reference/researchhub-endowment-official-docs.md) (captured 2026-04-11)
- [ResearchHub Endowment Product Doc](rh-reference/ResearchHub%20Endowment%20-%20Product%20Doc%20%5BRHF%20Community%5D.docx.md)
- [ResearchHub Endowments Community Doc](rh-reference/ResearchHub%20Endowments%20%5BRHF%20Community%5D.docx.md)
- [RH Yield Model CSV](rh-reference/ResearchHub%20Endowment%20Yield%20Model%20%5BRHF%20Community%5D%20-%20Yearly%20returns%20over%2010%20years.csv)
- Source URL: https://docs.researchhub.com/researchhub/product-features/fund/researchhub-endowment

*This plan lives alongside the ABM. Update as real data reveals model gaps.*
