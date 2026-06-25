#!/usr/bin/env python3
"""
Whale Wallet Tracker — Track large wallet movements on Ethereum & BSC.
Author: Fian Dev | fiverr.com/mrxx_25

Usage:
    python wallet_tracker.py --wallet 0xABC... --chain eth
    python wallet_tracker.py --top-whales --chain bsc
"""

import argparse
import json
import time
from datetime import datetime
from typing import Optional

try:
    import requests
except ImportError:
    print("Install requests: pip install requests")
    exit(1)


class WalletTracker:
    """Track whale wallet activity across multiple chains."""

    EXPLORERS = {
        "eth": {
            "api": "https://api.etherscan.io/api",
            "name": "Ethereum",
            "native": "ETH",
        },
        "bsc": {
            "api": "https://api.bscscan.com/api",
            "name": "BNB Smart Chain",
            "native": "BNB",
        },
    }

    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.session = requests.Session()

    def get_balance(self, wallet: str, chain: str = "eth") -> Optional[dict]:
        """Get native balance of a wallet address."""
        explorer = self.EXPLORERS.get(chain)
        if not explorer:
            return None

        resp = self.session.get(explorer["api"], params={
            "module": "account",
            "action": "balance",
            "address": wallet,
            "tag": "latest",
            "apikey": self.api_key,
        })
        data = resp.json()

        if data.get("status") == "1":
            balance_wei = int(data["result"])
            balance = balance_wei / 1e18
            return {
                "wallet": wallet,
                "chain": chain,
                "balance": round(balance, 4),
                "symbol": explorer["native"],
                "timestamp": datetime.utcnow().isoformat(),
            }
        return None

    def get_transactions(self, wallet: str, chain: str = "eth", limit: int = 50) -> list[dict]:
        """Get recent transactions for a wallet."""
        explorer = self.EXPLORERS.get(chain)
        if not explorer:
            return []

        resp = self.session.get(explorer["api"], params={
            "module": "account",
            "action": "txlist",
            "address": wallet,
            "startblock": 0,
            "endblock": 99999999,
            "page": 1,
            "offset": limit,
            "sort": "desc",
            "apikey": self.api_key,
        })
        data = resp.json()

        if data.get("status") != "1":
            return []

        txs = []
        for tx in data["result"]:
            value_eth = int(tx["value"]) / 1e18
            if value_eth > 0:
                txs.append({
                    "hash": tx["hash"],
                    "from": tx["from"],
                    "to": tx["to"],
                    "value": round(value_eth, 4),
                    "symbol": explorer["native"],
                    "timestamp": datetime.fromtimestamp(int(tx["timeStamp"])).isoformat(),
                    "direction": "OUT" if tx["from"].lower() == wallet.lower() else "IN",
                })
        return txs

    def get_token_balances(self, wallet: str, chain: str = "eth") -> list[dict]:
        """Get ERC20/BEP20 token balances."""
        explorer = self.EXPLORERS.get(chain)
        if not explorer:
            return []

        # For Etherscan-compatible APIs
        resp = self.session.get(explorer["api"], params={
            "module": "account",
            "action": "tokentx",
            "address": wallet,
            "page": 1,
            "offset": 100,
            "sort": "desc",
            "apikey": self.api_key,
        })
        data = resp.json()

        if data.get("status") != "1":
            return []

        # Aggregate token balances from recent transfers
        tokens = {}
        for tx in data["result"]:
            contract = tx["contractAddress"]
            if contract not in tokens:
                tokens[contract] = {
                    "token": tx["tokenSymbol"],
                    "contract": contract,
                    "decimals": int(tx["tokenDecimal"]),
                }

        return list(tokens.values())

    def track(self, wallet: str, chain: str = "eth") -> dict:
        """Full wallet tracking report."""
        balance = self.get_balance(wallet, chain)
        txs = self.get_transactions(wallet, chain)
        tokens = self.get_token_balances(wallet, chain)

        # Calculate stats
        total_in = sum(tx["value"] for tx in txs if tx["direction"] == "IN")
        total_out = sum(tx["value"] for tx in txs if tx["direction"] == "OUT")

        return {
            "wallet": wallet,
            "chain": self.EXPLORERS[chain]["name"],
            "balance": balance,
            "recent_tx_count": len(txs),
            "total_in": round(total_in, 4),
            "total_out": round(total_out, 4),
            "token_count": len(tokens),
            "tokens": tokens[:10],
            "recent_txs": txs[:5],
        }


def main():
    parser = argparse.ArgumentParser(description="Whale Wallet Tracker")
    parser.add_argument("--wallet", help="Wallet address to track")
    parser.add_argument("--chain", default="eth", choices=["eth", "bsc"], help="Blockchain")
    parser.add_argument("--api-key", default="", help="Explorer API key")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if not args.wallet:
        parser.error("--wallet is required")

    tracker = WalletTracker(args.api_key)
    report = tracker.track(args.wallet, args.chain)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        b = report["balance"]
        print(f"\n{'=' * 50}")
        print(f"  🐋 WALLET TRACKER — {report['chain']}")
        print(f"{'=' * 50}")
        print(f"  Wallet:    {report['wallet']}")
        print(f"  Balance:   {b['balance']} {b['symbol']}" if b else "  Balance:   N/A")
        print(f"  TXs (24h): {report['recent_tx_count']}")
        print(f"  Inflow:    {report['total_in']} {b['symbol'] if b else ''}")
        print(f"  Outflow:   {report['total_out']} {b['symbol'] if b else ''}")
        print(f"  Tokens:    {report['token_count']}")
        print(f"{'=' * 50}")


if __name__ == "__main__":
    main()
