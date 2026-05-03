# RSC Endowment ABM — Roadmap

*Last updated: 2026-04-11*

---

## Completed

### v1-v3: Synthetic Simulator (Jan 2026)
- [x] Mesa model with 4 archetypes (Believer, Yield Seeker, Institution, Speculator)
- [x] Emission formula calibrated to RH product doc: E(t) = 9,500,000 / 2^(t/64)
- [x] Self-balancing participation dynamics
- [x] Flask API + single-page dashboard
- [x] Railway deployment (live demo)
- [x] 3 reference scenarios from RH yield model CSV (15%, 30%, 70%)
- [x] B=f(P,E) behavioral framework per agent

### Community engagement (Jan 2026)
- [x] Process fidelity staking ABM shared in Discord → positive team reception
- [x] Token Talk session — convergence with RH's endowment direction
- [x] Coordination with Tyler on mechanism design

---

## Current: Chain Data Calibration

*Triggered by endowment launch on 2026-04-10*

### Phase 1: Data Pipeline (target: April W16)
- [ ] `src/data/` module — CoinGecko price feed, Etherscan/BaseScan balance queries
- [ ] Daily append to local CSV/SQLite
- [ ] Track RSC deposits to RH platform addresses (both chains)
- [ ] Track Uniswap + Aerodrome pool depth

### Phase 2: Replay Mode (target: April W17-18)
- [ ] Feed actual daily data as environment inputs to model
- [ ] Agents react to real price/participation instead of synthetic
- [ ] New endpoint: `POST /api/replay`

### Phase 3: Sim vs Reality Dashboard (target: May W18-19)
- [ ] New "Model vs Market" tab
- [ ] Overlay: simulated vs actual participation rate
- [ ] Overlay: simulated vs actual APY
- [ ] Overlay: simulated vs actual price
- [ ] Divergence metrics

### Phase 4: Archetype Calibration (target: May W20+)
- [ ] Cluster real depositors by behavior
- [ ] Fit archetype_mix to observed patterns
- [ ] Sensitivity analysis on key parameters
- [ ] Publish calibration findings

See [chain-data-calibration-plan.md](chain-data-calibration-plan.md) for full technical spec.

---

## v4: Data-Assimilated ABM (post-defense)

The big architectural shift: from pure synthetic simulation to a model that ingests real on-chain data, calibrates itself, and projects forward from observed state.

See [v4-design-notes.md](v4-design-notes.md) for full architecture.

### Three operating modes
- **Synthetic** — v3 behavior preserved, no data dependency
- **Replay** — feed historical chain data, compare agent behavior against reality
- **Forecast** — initialize from current on-chain state, project forward with calibrated params

### P0: Data layer + feeds
- [ ] `src/data/` module: Blockscout feed, CoinGecko feed, SQLite store
- [ ] Wallet balance snapshots (hot wallet + second wallet)
- [ ] Transfer tracking (deposits, withdrawals, burns)
- [ ] Price/volume history

### P1: Replay mode + anchored agents + stress scenarios
- [ ] `AnchoredHolder` class — agents initialized from real on-chain depositors
- [ ] Environment state injection from historical data
- [ ] Replay API endpoint
- [ ] "Model vs Market" dashboard tab
- [ ] **Stress scenarios module** — whale exit, foundation flood, cascade exit, mint event
- [ ] **Price-linked exit behavior** — agents exit on price crash, not just APY (enables cascade modeling)
- [ ] **Concentration-aware initialization** — real holder distribution (Foundation 473M, Team 298M, etc.)

### P2: Calibration + forecasting
- [ ] `ArchetypeCalibrator` — automated parameter fitting against observed behavior
- [ ] Forecast mode — init from real state, project forward
- [ ] "Live State" dashboard tab — real-time on-chain monitoring
- [ ] Endogenous price model calibration
- [ ] Dune Sim webhook subscriptions for real-time data push

### P3: Community + governance tools
- [ ] **"Stress Test" dashboard tab** — scenario selector, parameter sliders, survivability scoring
- [ ] Forecast scenario builder (what-if tools for RIP proposals)
- [ ] Share calibrated model with RH community
- [ ] Export reports for governance discussions

### Future: Integration with process fidelity model
- [ ] Layer process fidelity staking on top of endowment base
- [ ] Combined model: endowment creates lock-up, process fidelity evaluates funded proposals
- [ ] Unified dashboard across both ABMs

---

## Context

- **Endowment launched**: 2026-04-10
- **Key finding from launch day**: Exchanges drained within hours. Coinbase rationing RSC by order book depth. Aerodrome 18.76% price impact on 15 ETH. Supply squeeze in progress.
- **Confirmed with RH leadership**: Researchers receive USD, not RSC. Credits are non-transferable. Net effect on liquid supply is deflationary.
- **Personal position**: 432,675 RSC deposited (~$27K). Anchor depositor alongside Jeffrey Koury (~477K). Earning ~18-44% of all emissions depending on week.
- **Week 1 validation**: 3 of 6 ABM predictions confirmed (yield seeker entry, self-balancing APY compression, deflation via burns). 3 pending (whale behavior, equilibrium rate, exit dynamics).
- **Live tracking**: See [endowment-live-tracking.md](endowment-live-tracking.md) for comprehensive on-chain data.
- **Background doc**: See `rsc-staking-project-background.md` for full project history.
