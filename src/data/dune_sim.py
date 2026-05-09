"""
Dune Sim API client for RSC endowment chain data.

Single API for wallet balances, transactions, and prices across
Ethereum and Base. Replaces Blockscout + CoinGecko.

Docs: https://docs.sim.dune.com/
"""

import os
import requests
from datetime import datetime

API_BASE = "https://api.sim.dune.com/v1/evm"

RSC_CONTRACTS = {
    "ethereum": "0xd101dcc414f310268c37eeb4cd376ccfa507f571",
    "base": "0xfbb75a59193a3525a8825bebe7d4b56899e2f7e1",
}

WATCHED_WALLETS = {
    "hot_wallet": "0x7F57d306a9422ee8175aDc25898B1b2EBF1010cb",
    "second_wallet": "0x467564DCCE90FB21153adfa69c48A3Be235d66D3",
    "foundation_treasury": "0x5222ff25f4dfc02d173c2cbd2055ee1d35f291f1",
    "team_treasury": "0xe3648e99b6e68a09e28428790d12b357f081dbe0",
    "foundation_community": "0xc4cfa2bdae08416312faa0b72758e1f3750f81e3",
    "base_treasury": "0xb280f00e70f28e8ce38c40826270de7e1b327e21",
}


class DuneSimClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("DUNE_SIM_API_KEY", "")
        if not self.api_key:
            raise ValueError("DUNE_SIM_API_KEY not set")
        self.session = requests.Session()
        self.session.headers["X-Sim-Api-Key"] = self.api_key

    def _get(self, path: str, params: dict = None) -> dict:
        url = f"{API_BASE}/{path}"
        r = self.session.get(url, params=params or {}, timeout=30)
        r.raise_for_status()
        return r.json()

    def get_balances(self, address: str, chain_ids: str = "1,8453") -> dict:
        return self._get(f"balances/{address}", {"chain_ids": chain_ids})

    def get_rsc_balance(self, address: str) -> dict:
        """Get RSC balances across both chains for a wallet."""
        data = self.get_balances(address)
        result = {"address": address, "timestamp": datetime.utcnow().isoformat(), "chains": {}}

        for b in data.get("balances", []):
            if b.get("symbol") == "RSC":
                chain = b["chain"]
                raw = int(b["amount"])
                decimals = b.get("decimals", 18)
                amount = raw / (10 ** decimals)
                result["chains"][chain] = {
                    "amount": amount,
                    "price_usd": b.get("price_usd", 0),
                    "value_usd": b.get("value_usd", 0),
                }

        result["total_rsc"] = sum(c["amount"] for c in result["chains"].values())
        result["total_usd"] = sum(c["value_usd"] for c in result["chains"].values())
        prices = [c["price_usd"] for c in result["chains"].values() if c["price_usd"] > 0]
        result["price_usd"] = sum(prices) / len(prices) if prices else 0

        return result

    def get_pool_snapshot(self) -> dict:
        """Get total RSC across deposit wallets (hot wallet + second wallet)."""
        hot = self.get_rsc_balance(WATCHED_WALLETS["hot_wallet"])
        second = self.get_rsc_balance(WATCHED_WALLETS["second_wallet"])

        combined = {
            "address": "pool_combined",
            "timestamp": hot["timestamp"],
            "chains": {},
            "wallets": {
                "hot_wallet": hot,
                "second_wallet": second,
            },
        }
        all_chains = set(list(hot["chains"].keys()) + list(second["chains"].keys()))
        for chain in all_chains:
            h = hot["chains"].get(chain, {"amount": 0, "price_usd": 0, "value_usd": 0})
            s = second["chains"].get(chain, {"amount": 0, "price_usd": 0, "value_usd": 0})
            combined["chains"][chain] = {
                "amount": h["amount"] + s["amount"],
                "price_usd": h["price_usd"] or s["price_usd"],
                "value_usd": h["value_usd"] + s["value_usd"],
            }
        combined["total_rsc"] = hot["total_rsc"] + second["total_rsc"]
        combined["total_usd"] = hot["total_usd"] + second["total_usd"]
        combined["price_usd"] = hot["price_usd"] or second["price_usd"]

        return combined

    def get_treasury_balances(self) -> list:
        """Get RSC balances for all watched treasury wallets."""
        results = []
        for label, address in WATCHED_WALLETS.items():
            if label == "hot_wallet":
                continue
            try:
                bal = self.get_rsc_balance(address)
                bal["label"] = label
                results.append(bal)
            except Exception as e:
                results.append({"label": label, "address": address, "error": str(e)})
        return results

    def get_transactions(self, address: str, chain_id: int = 8453, limit: int = 20) -> dict:
        return self._get(
            f"transactions/{address}",
            {"chain_ids": str(chain_id), "limit": str(limit)},
        )
