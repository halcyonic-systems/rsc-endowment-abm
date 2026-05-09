# v4 Backend Contracts — Design-Implied Data Shapes

*2026-05-03 | Derived from frontend prototype decisions*

These contracts are implied by design decisions made in the v4 frontend. Lock them in before writing endpoints.

---

## Tensions to Resolve Before Writing Code

Two architectural tensions emerged from today's frontend work that need conscious resolution before the first endpoint:

### 1. SQLite vs Postgres

**Origin:** `docs/v4-design-notes.md` (written Apr 16) specifies SQLite in `src/data/store.py` — simple, no server, single-file, works on Railway free tier. Today's frontend design session introduced a live bar that pulses "LIVE" with ≤30s polling, concurrent dashboard reads while an indexer writes, and SSE as a future path. The Chrome extension feedback explicitly said "don't ship a green pulse on stale data."

**The tension:** SQLite handles concurrent reads fine but struggles with concurrent writes from an indexer process while the API serves requests. If the indexer and Flask API are separate processes (which this doc recommends), SQLite's write lock becomes a bottleneck at 30s polling with multiple dashboard viewers.

**Decision options:**
- **SQLite for v1** — simpler, one process (indexer runs inside Flask on a background thread), defer scaling. Matches the existing v4-design-notes spec. Honest tradeoff: limits you to one writer, so the live bar can't truly be <30s without contention.
- **Postgres** — proper concurrent access, indexer and API fully independent, SSE/websockets trivial later. Slightly more setup (Railway Postgres addon or external). Matches the architecture diagram in this doc.
- **SQLite now, Postgres migration later** — use SQLAlchemy so the swap is a connection string change. Ship fast, upgrade when you need concurrent writes.

**Recommendation:** Option 3. Start SQLite (matches existing spec, zero setup), but use SQLAlchemy Core so the migration is mechanical. Change the live bar from pulsing "LIVE" to "Refreshed 14:18 UTC" until you move to Postgres + real-time indexer.

**Indexer cadence: start daily.** Dune Sim API handles daily polling trivially — one call gets wallet balances + transfers + prices across both chains. Barely touches quota. Webhooks available when ready for real-time later, but daily snapshots are the right v1 granularity.

### 2. Feed Pattern vs Persisted Store

**Origin:** `docs/v4-design-notes.md` says "the data layer is a feed, not a database — the model pulls from it each step." Today's frontend work created a dashboard that needs a persisted store the API reads from (depositor table, treasury watch, pool growth chart all need historical data, not just the latest feed response).

**The tension:** The feed pattern (model pulls live data per simulation step) and the dashboard pattern (API serves historical time series from a store) are two different access patterns on the same underlying data.

**Resolution — they coexist:**
- **For the dashboard (Tracker tab):** Indexer writes to the store on a schedule. API reads from store. This is the pattern in this doc. Serves historical charts, depositor tables, treasury watch.
- **For the ABM engine (Simulation tab):** Model pulls from the feed (Dune Sim API) during replay/forecast runs. The feed is live, ephemeral, per-step. Results of simulation runs get written back to the store as `model_outputs`.

**Practical implication:** `src/data/feeds.py` (live API clients) and `src/data/store.py` (persistence) are peers, not alternatives. The indexer uses feeds to populate the store. The ABM engine uses feeds directly during runs. The API serves from the store only.

```
feeds.py → (indexer cron) → store.py → (API reads) → frontend Tracker
feeds.py → (ABM engine)  → model_outputs → store.py → frontend Simulation
```

This is already consistent with both docs — just not stated explicitly until now.

---

---

## Core Principle: Every Value Has an Epistemic Status

```json
{
  "name": "pool_size",
  "value": 11200000,
  "unit": "RSC",
  "epistemic_status": "observed",
  "source": "base:0xRSC_ENDOWMENT",
  "block": 21438221,
  "as_of": "2026-04-23T14:18:00Z"
}
```

vs.

```json
{
  "name": "pool_size_30d",
  "value": 12800000,
  "unit": "RSC",
  "epistemic_status": "predicted",
  "ci_lower": 11400000,
  "ci_upper": 14900000,
  "ci_level": 0.80,
  "model_version": "v0.4.2",
  "n_runs": 500,
  "as_of": "2026-04-23T14:18:00Z"
}
```

Frontend renders slate for `observed`, cobalt for `predicted`. Zero ambiguity.

---

## Two Clocks on Every Payload

```json
{
  "ledger_time": { "chain": "base", "block": 21438221, "block_ts": "2026-04-23T14:00:00Z" },
  "wall_time": { "synced_at": "2026-04-23T14:18:00Z", "model_calibrated_at": "2026-04-22T03:00:00Z" }
}
```

- Ledger time = deterministic, block-anchored
- Wall time = when indexer synced, when model last calibrated
- "synced 2h ago" in live bar reads from `wall_time.synced_at`
- "Updated 2h ago" in section meta reads from same

---

## Caching / Freshness Policy

| Component | Cache TTL | Design Promise |
|-----------|-----------|----------------|
| Live bar (block, pool, APY) | ≤30s | Pulsing green dot = "live" |
| Hero KPIs + deltas | ~1 min | Rolling-window, recompute hourly |
| Depositors table + Treasury Watch | 10–15 min | Heavy queries (Blockscout + Dune) |
| Model outputs | Nightly or on-demand | Display calibration timestamp |

Every response includes `cache_ttl_seconds` and `next_refresh_at`.

**Critical**: Don't ship a green pulse on stale data. Gate the LIVE dot on `/api/health`.

---

## Key Endpoints

### `GET /api/state` — Single full-page payload

```
GET /api/state                          → live (latest block)
GET /api/state?at_block=21380000        → replay mode
GET /api/state?at_block=21500000&forecast=true  → forecast mode
```

One state shape, parameterized by block. Don't build three APIs for three modes.

### `GET /api/chart/model-vs-reality` — Three series, one grid

```json
{
  "grid": ["2026-04-10", "...", "2026-04-23"],
  "observed":  [0, "...", 11200000],
  "predicted": [0, "...", 12800000],
  "ci_lower":  [0, "...", 11400000],
  "ci_upper":  [0, "...", 14900000],
  "model_version": "v0.4.2",
  "calibrated_at_block": 21380000,
  "mae": 0.018
}
```

Single endpoint, server-side join. Don't make frontend align separate series.

### `GET /api/depositors` — With reconciliation

```json
{
  "depositors": [
    { "entity": "RH Foundation", "address": "0xb280...", "amount": 769130, "share": 0.069, "date": "2026-04-16", "type": "aligned" }
  ],
  "traced_total": 3300000,
  "untraced": 7900000,
  "pool_size": 11200000,
  "traced_share": 0.61,
  "method": "Blockscout transfer tracing + Dune Sim balance queries"
}
```

**Invariant**: `traced_total + untraced === pool_size`. Assert in tests.

### `GET /api/treasury/watch` — With impact projection

```json
{
  "wallets": [
    {
      "label": "0x3e3f...7161",
      "balance": 1710000,
      "risk_level": "high",
      "impact_if_sold": "~40% price impact on current book depth",
      "status": "idle",
      "last_activity": "2026-04-23"
    }
  ]
}
```

Decision needed: ship v1 with `balance + classification` or compute `impact_if_sold` from order book depth?

### `GET /api/model/diagnostics`

```json
{
  "mae": 0.018,
  "mape": 0.024,
  "model_version": "v0.4.2",
  "last_calibrated_at": "2026-04-22T03:00:00Z",
  "calibrated_at_block": 21380000,
  "n_runs": 500,
  "drift_warning": false
}
```

Teal model badge reads from this. When MAE > 5%, badge turns amber.

### `GET /api/health`

```json
{
  "status": "ok",
  "indexer": { "status": "ok", "last_block": 21438221, "lag_seconds": 45 },
  "model": { "status": "calibrated", "drift": false },
  "sources": {
    "base_rpc": "up",
    "dune_sim": "up",
    "blockscout": "up"
  }
}
```

Gates the green LIVE dot. Degraded → amber dot + inline note.

### `GET /api/meta`

```json
{
  "publisher": "Halcyonic Systems",
  "launched_at": "2026-04-10",
  "model_version": "v0.4.2",
  "schema_version": "1.0.0",
  "last_deploy": "2026-05-03T15:00:00Z"
}
```

---

## Architecture

```
┌──────────────┐     writes     ┌──────────┐     reads     ┌─────────┐
│   Indexer    │ ──────────────► │ Postgres │ ◄──────────── │   API   │
│ (cron/batch) │                 │          │               │ (Flask) │
└──────────────┘                 └──────────┘               └─────────┘
       │                                                         │
       ▼                                                         ▼
  Blockscout API                                          Frontend (HTML)
  Dune Sim API                                            SSE/polling ≤30s
```

- Indexer writes to Postgres on schedule (cron, not Celery for v1)
- API reads from Postgres, never calls Blockscout synchronously
- One table per entity: `pool_state_snapshots`, `depositors`, `model_outputs`, `events`
- All block-indexed

---

## Tomorrow's Sequencing

1. **Schema first** — sketch full JSON envelopes on paper
2. **Postgres tables** — one per entity, block-indexed
3. **Single `/api/state` endpoint** — returns full tracker view in one shot
4. **Indexer** — separate process, writes to Postgres on cron
5. **Health + meta endpoints** — last, smallest
6. **Hold simulator backend** — separate session after tracker is end-to-end
