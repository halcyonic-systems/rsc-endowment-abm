"""
Snapshot orchestrator — pulls chain data and persists to SQLite.

Call take_snapshot() daily (manually or via cron) to capture
pool state, treasury balances, and RSC price.
"""

from .dune_sim import DuneSimClient
from .store import DataStore


def take_snapshot(db_path: str = None, api_key: str = None) -> dict:
    """Pull live chain data and save to store. Returns the pool snapshot."""
    client = DuneSimClient(api_key=api_key)
    store = DataStore(db_path=db_path)

    pool = client.get_pool_snapshot()
    store.save_pool_snapshot(pool)

    treasuries = client.get_treasury_balances()
    for t in treasuries:
        if "error" not in t:
            store.save_treasury_snapshot(t)

    store.close()

    return {
        "pool": pool,
        "treasuries": treasuries,
    }


def get_latest_snapshot(db_path: str = None) -> dict:
    """Read the most recent snapshot from the store."""
    store = DataStore(db_path=db_path)
    pool = store.get_latest_pool()
    treasury = store.get_latest_treasury()
    history = store.get_pool_history()
    store.close()

    return {
        "pool": pool,
        "treasury": treasury,
        "history": history,
    }
