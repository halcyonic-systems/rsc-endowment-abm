"""
Chain data client for RSC endowment — Blockscout + CoinGecko.

Replaces the Dune Sim client (sim.dune.com sunset 2026-08-01).
Balances and transfers come from public Blockscout instances on
Ethereum and Base; USD price comes from CoinGecko. No API keys.
"""

import time
import requests
from datetime import datetime

BLOCKSCOUT = {
    "ethereum": "https://eth.blockscout.com",
    "base": "https://base.blockscout.com",
}

COINGECKO_PRICE = "https://api.coingecko.com/api/v3/simple/price"
RSC_COINGECKO_ID = "researchcoin"

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


class ChainClient:
    """Same public interface as the retired DuneSimClient."""

    def __init__(self, api_key: str = None):
        # api_key accepted and ignored for call-site compatibility
        self.session = requests.Session()
        self.session.headers["User-Agent"] = "rsc-endowment-abm/1.0"
        self._price_cache = None
        self._price_cache_time = 0

    def _get(self, url: str, params: dict = None, retries: int = 3) -> dict:
        last_err = None
        for attempt in range(retries):
            try:
                r = self.session.get(url, params=params or {}, timeout=30)
                if r.status_code == 404:
                    return {}
                if r.status_code == 429:
                    time.sleep(2 ** attempt)
                    continue
                r.raise_for_status()
                return r.json()
            except requests.RequestException as e:
                last_err = e
                time.sleep(2 ** attempt)
        raise last_err

    def get_rsc_price(self) -> float:
        """RSC price in USD from CoinGecko, cached for 5 minutes."""
        if self._price_cache is not None and time.time() - self._price_cache_time < 300:
            return self._price_cache
        data = self._get(
            COINGECKO_PRICE,
            {"ids": RSC_COINGECKO_ID, "vs_currencies": "usd"},
        )
        price = float(data.get(RSC_COINGECKO_ID, {}).get("usd", 0))
        if price > 0:
            self._price_cache = price
            self._price_cache_time = time.time()
        return price

    def get_rsc_balance(self, address: str) -> dict:
        """Get RSC balances across both chains for a wallet."""
        price = self.get_rsc_price()
        result = {"address": address, "timestamp": datetime.utcnow().isoformat(), "chains": {}}

        for chain, base_url in BLOCKSCOUT.items():
            rsc_addr = RSC_CONTRACTS[chain].lower()
            data = self._get(f"{base_url}/api/v2/addresses/{address}/token-balances")
            balances = data if isinstance(data, list) else []
            for b in balances:
                token = b.get("token", {})
                if token.get("address_hash", "").lower() != rsc_addr:
                    continue
                decimals = int(token.get("decimals") or 18)
                amount = int(b["value"]) / (10 ** decimals)
                result["chains"][chain] = {
                    "amount": amount,
                    "price_usd": price,
                    "value_usd": amount * price,
                }

        result["total_rsc"] = sum(c["amount"] for c in result["chains"].values())
        result["total_usd"] = sum(c["value_usd"] for c in result["chains"].values())
        result["price_usd"] = price

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

    def get_rsc_depositors(self, limit: int = 100) -> list:
        """
        Identify individual depositors from incoming RSC transfers to
        the hot wallet and second wallet across both chains.
        """
        depositors = {}

        for wallet_label in ["hot_wallet", "second_wallet"]:
            address = WATCHED_WALLETS[wallet_label].lower()
            for chain, base_url in BLOCKSCOUT.items():
                try:
                    transfers = self._get_token_transfers(
                        base_url, address, RSC_CONTRACTS[chain], limit
                    )
                except Exception:
                    continue
                for t in transfers:
                    sender = t["from"]["hash"].lower()
                    if sender == address:
                        continue
                    total = t.get("total") or {}
                    decimals = int(total.get("decimals") or 18)
                    amount = int(total.get("value") or 0) / (10 ** decimals)
                    ts = t.get("timestamp", "")

                    if sender not in depositors:
                        depositors[sender] = {
                            "address": sender,
                            "total_rsc": 0,
                            "tx_count": 0,
                            "first_deposit": ts,
                            "last_deposit": ts,
                        }
                    depositors[sender]["total_rsc"] += amount
                    depositors[sender]["tx_count"] += 1
                    if ts < depositors[sender]["first_deposit"]:
                        depositors[sender]["first_deposit"] = ts
                    if ts > depositors[sender]["last_deposit"]:
                        depositors[sender]["last_deposit"] = ts

        return sorted(depositors.values(), key=lambda d: d["total_rsc"], reverse=True)

    def _get_token_transfers(self, base_url: str, address: str, token: str, limit: int) -> list:
        """Incoming token transfers, following pagination up to `limit`."""
        transfers = []
        params = {"token": token, "filter": "to"}
        url = f"{base_url}/api/v2/addresses/{address}/token-transfers"
        while len(transfers) < limit:
            data = self._get(url, params)
            items = data.get("items", [])
            if not items:
                break
            transfers.extend(items)
            next_params = data.get("next_page_params")
            if not next_params:
                break
            params = {"token": token, "filter": "to", **next_params}
        return transfers[:limit]
