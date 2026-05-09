"""
SQLite store for chain data snapshots.

Daily snapshots of pool state, treasury balances, and prices.
Append-only — each row is a point-in-time observation.
"""

import sqlite3
import json
import os
from datetime import datetime

DEFAULT_DB = os.path.join(os.path.dirname(__file__), "..", "..", "data", "endowment.db")


class DataStore:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DEFAULT_DB
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()

    def _init_tables(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS pool_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                total_rsc REAL NOT NULL,
                price_usd REAL,
                value_usd REAL,
                chains_json TEXT,
                UNIQUE(timestamp)
            );

            CREATE TABLE IF NOT EXISTS treasury_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                label TEXT NOT NULL,
                address TEXT NOT NULL,
                total_rsc REAL NOT NULL,
                chains_json TEXT,
                UNIQUE(timestamp, label)
            );
        """)
        self.conn.commit()

    def save_pool_snapshot(self, snapshot: dict):
        ts = snapshot.get("timestamp", datetime.utcnow().isoformat())
        self.conn.execute(
            """INSERT OR REPLACE INTO pool_snapshots
               (timestamp, total_rsc, price_usd, value_usd, chains_json)
               VALUES (?, ?, ?, ?, ?)""",
            (
                ts,
                snapshot["total_rsc"],
                snapshot.get("price_usd", 0),
                snapshot.get("total_usd", 0),
                json.dumps(snapshot.get("chains", {})),
            ),
        )
        self.conn.commit()

    def save_treasury_snapshot(self, snapshot: dict):
        ts = snapshot.get("timestamp", datetime.utcnow().isoformat())
        self.conn.execute(
            """INSERT OR REPLACE INTO treasury_snapshots
               (timestamp, label, address, total_rsc, chains_json)
               VALUES (?, ?, ?, ?, ?)""",
            (
                ts,
                snapshot["label"],
                snapshot["address"],
                snapshot.get("total_rsc", 0),
                json.dumps(snapshot.get("chains", {})),
            ),
        )
        self.conn.commit()

    def get_pool_history(self, limit: int = 90) -> list:
        rows = self.conn.execute(
            "SELECT * FROM pool_snapshots ORDER BY timestamp DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in reversed(rows)]

    def get_latest_pool(self) -> dict | None:
        row = self.conn.execute(
            "SELECT * FROM pool_snapshots ORDER BY timestamp DESC LIMIT 1"
        ).fetchone()
        return dict(row) if row else None

    def get_latest_treasury(self) -> list:
        rows = self.conn.execute(
            """SELECT t1.* FROM treasury_snapshots t1
               INNER JOIN (
                   SELECT label, MAX(timestamp) as max_ts
                   FROM treasury_snapshots GROUP BY label
               ) t2 ON t1.label = t2.label AND t1.timestamp = t2.max_ts"""
        ).fetchall()
        return [dict(r) for r in rows]

    def close(self):
        self.conn.close()
