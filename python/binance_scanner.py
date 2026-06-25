#!/usr/bin/env python3
"""
Binance USDT Scanner — Scan all pairs for setup signals.
Author: Fian Dev | fiverr.com/mrxx_25

Usage:
    python binance_scanner.py --interval 15m --top 10
    python binance_scanner.py --interval 1h --score 70
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


class BinanceScanner:
    """Scan all USDT perpetual pairs on Binance for trading signals."""

    BASE_URL = "https://fapi.binance.com/fapi/v1"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def get_usdt_symbols(self) -> list[str]:
        """Fetch all USDT perpetual symbols."""
        resp = self.session.get(f"{self.BASE_URL}/exchangeInfo")
        info = resp.json()
        return [
            s["symbol"] for s in info.get("symbols", [])
            if s["symbol"].endswith("USDT") and s["status"] == "TRADING"
        ]

    def get_klines(self, symbol: str, interval: str, limit: int = 100) -> list:
        """Fetch kline/candlestick data."""
        resp = self.session.get(
            f"{self.BASE_URL}/klines",
            params={"symbol": symbol, "interval": interval, "limit": limit}
        )
        return resp.json()

    def analyze_pair(self, symbol: str, interval: str) -> Optional[dict]:
        """Analyze a single pair for signal opportunities."""
        klines = self.get_klines(symbol, interval, limit=100)
        if not klines or len(klines) < 50:
            return None

        closes = [float(k[4]) for k in klines]
        volumes = [float(k[5]) for k in klines]
        highs = [float(k[2]) for k in klines]
        lows = [float(k[3]) for k in klines]

        current = closes[-1]
        prev = closes[-2] if len(closes) > 1 else current
        change_24h = ((current - closes[0]) / closes[0]) * 100 if closes[0] else 0

        # Volume surge detection
        avg_vol = sum(volumes[:-1]) / max(len(volumes) - 1, 1)
        current_vol = volumes[-1]
        vol_ratio = current_vol / avg_vol if avg_vol > 0 else 0

        # Simple momentum
        ma20 = sum(closes[-20:]) / 20
        ma50 = sum(closes[-50:]) / 50
        momentum = ((current - ma20) / ma20) * 100

        # ATR for volatility
        tr_list = []
        for i in range(1, min(15, len(klines))):
            tr = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i-1]),
                abs(lows[i] - closes[i-1])
            )
            tr_list.append(tr)
        atr = sum(tr_list) / len(tr_list) if tr_list else 0
        volatility = (atr / current) * 100 if current else 0

        # Score calculation (0-100)
        score = 0
        score += min(vol_ratio * 10, 30)     # Volume: 0-30
        score += min(abs(momentum) * 5, 20)  # Momentum: 0-20
        score += min(volatility * 10, 20)    # Volatility: 0-20
        if ma20 > ma50:
            score += 15                       # Trend alignment: +15
        if abs(change_24h) > 2:
            score += 15                       # Significant move: +15

        return {
            "symbol": symbol,
            "price": current,
            "change_24h": round(change_24h, 2),
            "vol_ratio": round(vol_ratio, 2),
            "momentum": round(momentum, 2),
            "volatility": round(volatility, 2),
            "score": round(min(score, 100), 1),
            "signal": "BULLISH" if momentum > 0 else "BEARISH",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def scan(self, interval: str = "15m", top: int = 10, min_score: float = 50) -> list[dict]:
        """Scan all USDT pairs and return top signals."""
        symbols = self.get_usdt_symbols()
        print(f"🔍 Scanning {len(symbols)} pairs on {interval}...")

        results = []
        for i, symbol in enumerate(symbols):
            if i % 50 == 0:
                print(f"  Progress: {i}/{len(symbols)}")
            try:
                analysis = self.analyze_pair(symbol, interval)
                if analysis and analysis["score"] >= min_score:
                    results.append(analysis)
            except Exception as e:
                continue
            time.sleep(0.05)  # Rate limit

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top]


def main():
    parser = argparse.ArgumentParser(description="Binance Futures Scanner")
    parser.add_argument("--interval", default="15m", help="Kline interval (1m,5m,15m,1h,4h,1d)")
    parser.add_argument("--top", type=int, default=10, help="Top N results to show")
    parser.add_argument("--score", type=float, default=50, help="Minimum signal score")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    scanner = BinanceScanner()
    results = scanner.scan(args.interval, args.top, args.score)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"\n{'─' * 70}")
        print(f"  TOP {len(results)} SIGNALS — {args.interval} — Score ≥ {args.score}")
        print(f"{'─' * 70}")
        print(f"{'#':<4}{'Symbol':<14}{'Price':<12}{'24h%':<8}{'Vol':<8}{'Score':<8}{'Signal'}")
        print(f"{'─' * 70}")
        for i, r in enumerate(results, 1):
            emoji = "🟢" if r["signal"] == "BULLISH" else "🔴"
            print(f"{i:<4}{r['symbol']:<14}{r['price']:<12.4f}{r['change_24h']:<8.1f}%"
                  f"{r['vol_ratio']:<8.1f}x{r['score']:<8.1f}{emoji} {r['signal']}")
        print(f"{'─' * 70}")


if __name__ == "__main__":
    main()
