# 🛠️ Crypto Trading Toolkit

> Production-ready Pine Script indicators & Python trading utilities. Built for traders, by traders.

[![Pine Script](https://img.shields.io/badge/Pine_Script-v6-00D4AA?logo=tradingview)](https://www.tradingview.com/pine-script-docs/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📊 What's Inside

### Pine Script Indicators (v5/v6)
| Indicator | Description | Type |
|-----------|-------------|------|
| `Supertrend Multi` | Multi-timeframe Supertrend with alerts | Trend |
| `Liquidity Zones` | Auto-detect buy/sell-side liquidity levels | S/R |
| `Order Blocks` | ICT-style bullish/bearish order blocks | SMC |
| `Market Structure` | BOS/CHoCH detection with trend mapping | Structure |
| `Volume Pulse` | Anomalous volume detection with signal scoring | Volume |

### Python Utilities
| Tool | Description |
|------|-------------|
| `binance_scanner.py` | Scan all USDT pairs for setup signals |
| `wallet_tracker.py` | Track whale wallets via Etherscan/BscScan |

## 🚀 Quick Start

### Pine Script
1. Open TradingView Chart
2. Pine Editor → Paste any `.pine` file
3. Add to chart → Adjust settings

### Python Scanner
```bash
pip install -r requirements.txt
python python/binance_scanner.py --interval 15m --top 10
```

## 📈 Sample Signals

```
BTC/USDT 15m — Supertrend FLIP to BULLISH
ETH/USDT 1h  — Liquidity SWEEP at $3,450
SOL/USDT 4h  — Bullish Order Block formed
```

## 🔧 Requirements

- TradingView account (free) for Pine Script
- Python 3.10+ for scanner tools
- Binance API key (optional, for live data)

## 📝 License

MIT — use freely, attribution appreciated.

## 👤 Author

**Fian Dev** — [Fiverr](https://fiverr.com/mrxx_25) | [Telegram](https://t.me/smartdevtrade)

*Need custom indicators or trading bots? [Hire me on Fiverr](https://fiverr.com/mrxx_25)*
