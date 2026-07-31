"""
Backfill historical Base-chain RSC balances in endowment.db.

The retired Dune Sim API under-reported Base balances (and corrupted
price_usd) for every snapshot before 2026-07-31. This script recomputes
each snapshot's Base amounts from archival balanceOf calls against the
Base public RPC, and rebuilds price_usd / value_usd from CoinGecko's
daily price series.

Ethereum amounts are left untouched (verified accurate against RPC).

Usage:
    python scripts/backfill_base_history.py            # dry run
    python scripts/backfill_base_history.py --apply    # write changes

Run on Railway via: railway ssh -- python scripts/backfill_base_history.py
Back up first:      railway ssh -- cp /data/endowment.db /data/endowment.pre-backfill.db
"""

import argparse
import json
import sqlite3
import sys
import time
from datetime import datetime, timezone

import requests

# Both serve archival state (mainnet.base.org is load-balanced across
# archive and pruned nodes, so retries against it are meaningful).
BASE_RPCS = [
    "https://base.drpc.org",
    "https://mainnet.base.org",
]
RSC_BASE = "0xfbb75a59193a3525a8825bebe7d4b56899e2f7e1"
COINGECKO_CHART = "https://api.coingecko.com/api/v3/coins/researchcoin/market_chart"

WALLETS = {
    "hot_wallet": "0x7F57d306a9422ee8175aDc25898B1b2EBF1010cb",
    "second_wallet": "0x467564DCCE90FB21153adfa69c48A3Be235d66D3",
    "base_treasury": "0xb280f00e70f28e8ce38c40826270de7e1b327e21",
}

session = requests.Session()


def rpc(method, params):
    last_err = None
    for attempt in range(12):
        url = BASE_RPCS[attempt % len(BASE_RPCS)]
        try:
            r = session.post(url, json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params}, timeout=30)
            r.raise_for_status()
            data = r.json()
            if "result" in data and data["result"] is not None:
                return data["result"]
            last_err = data.get("error")
        except requests.RequestException as e:
            last_err = e
        time.sleep(0.5 if attempt < 6 else 4)
    raise RuntimeError(f"RPC {method} failed after retries: {last_err}")


def block_timestamp(block: int) -> int:
    blk = rpc("eth_getBlockByNumber", [hex(block), False])
    return int(blk["timestamp"], 16)


def block_at(target_ts: int, latest_block: int, latest_ts: int) -> int:
    """Base mints a block every 2s; estimate then correct until within one block."""
    if target_ts >= latest_ts:
        return latest_block
    block = latest_block - (latest_ts - target_ts) // 2
    for _ in range(8):
        block = max(1, min(block, latest_block))
        ts = block_timestamp(block)
        delta = target_ts - ts
        if -2 <= delta <= 2:
            return block
        block += delta // 2
    return block


def balance_at(address: str, block: int) -> float:
    data = "0x70a08231" + address.lower().replace("0x", "").rjust(64, "0")
    result = rpc("eth_call", [{"to": RSC_BASE, "data": data}, hex(block)])
    return int(result, 16) / 1e18


def daily_prices() -> dict:
    """Map YYYY-MM-DD -> USD price from CoinGecko daily series."""
    r = session.get(COINGECKO_CHART, params={"vs_currency": "usd", "days": 365, "interval": "daily"}, timeout=30)
    r.raise_for_status()
    out = {}
    for ms, price in r.json()["prices"]:
        day = datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
        out[day] = price
    return out


def parse_ts(iso: str) -> int:
    dt = datetime.fromisoformat(iso)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=None)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    if args.db:
        db_path = args.db
    else:
        sys.path.insert(0, ".")
        from src.data.store import DEFAULT_DB
        db_path = DEFAULT_DB

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    latest_block = int(rpc("eth_blockNumber", []), 16)
    latest_ts = block_timestamp(latest_block)
    prices = daily_prices()
    print(f"db={db_path}  latest base block={latest_block}  {'APPLY' if args.apply else 'DRY RUN'}")

    balance_cache = {}

    def base_balance(label: str, ts: int) -> float:
        block = block_at(ts, latest_block, latest_ts)
        key = (label, block)
        if key not in balance_cache:
            balance_cache[key] = balance_at(WALLETS[label], block)
        return balance_cache[key]

    def price_for(ts: int, fallback: float) -> float:
        day = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
        return prices.get(day, fallback)

    pool_updates = []
    for row in conn.execute("SELECT * FROM pool_snapshots ORDER BY timestamp"):
        ts = parse_ts(row["timestamp"])
        chains = json.loads(row["chains_json"] or "{}")
        eth_amt = chains.get("ethereum", {}).get("amount", 0)
        new_base = base_balance("hot_wallet", ts) + base_balance("second_wallet", ts)
        price = price_for(ts, row["price_usd"])
        total = eth_amt + new_base
        chains["ethereum"] = {"amount": eth_amt, "price_usd": price, "value_usd": eth_amt * price}
        chains["base"] = {"amount": new_base, "price_usd": price, "value_usd": new_base * price}
        pool_updates.append((row["id"], row["timestamp"], row["total_rsc"], total, row["price_usd"], price, json.dumps(chains)))
        print(f"pool {row['timestamp'][:19]}  rsc {row['total_rsc']:>14.2f} -> {total:>14.2f}   price {row['price_usd']:.4f} -> {price:.4f}")

    treasury_updates = []
    for row in conn.execute("SELECT * FROM treasury_snapshots WHERE label IN ('second_wallet','base_treasury') ORDER BY timestamp"):
        ts = parse_ts(row["timestamp"])
        chains = json.loads(row["chains_json"] or "{}")
        eth_amt = chains.get("ethereum", {}).get("amount", 0)
        new_base = base_balance(row["label"], ts)
        price = price_for(ts, 0)
        total = eth_amt + new_base
        if eth_amt:
            chains["ethereum"] = {"amount": eth_amt, "price_usd": price, "value_usd": eth_amt * price}
        chains["base"] = {"amount": new_base, "price_usd": price, "value_usd": new_base * price}
        treasury_updates.append((row["id"], total, json.dumps(chains)))
        print(f"treasury {row['label']:<14} {row['timestamp'][:19]}  rsc {row['total_rsc']:>14.2f} -> {total:>14.2f}")

    if not args.apply:
        print(f"\nDry run: {len(pool_updates)} pool rows, {len(treasury_updates)} treasury rows would change. Re-run with --apply.")
        return

    for rid, _, _, total, _, price, chains_json in pool_updates:
        conn.execute(
            "UPDATE pool_snapshots SET total_rsc=?, price_usd=?, value_usd=?, chains_json=? WHERE id=?",
            (total, price, total * price, chains_json, rid),
        )
    for rid, total, chains_json in treasury_updates:
        conn.execute(
            "UPDATE treasury_snapshots SET total_rsc=?, chains_json=? WHERE id=?",
            (total, chains_json, rid),
        )
    conn.commit()
    conn.close()
    print(f"\nApplied: {len(pool_updates)} pool rows, {len(treasury_updates)} treasury rows updated.")


if __name__ == "__main__":
    main()
