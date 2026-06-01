"""Market data retrieval utilities for the trading agent.

Usage:
    python3 scripts/research.py account
    python3 scripts/research.py positions
    python3 scripts/research.py bars SYMBOL
    python3 scripts/research.py news SYMBOL
"""
import os
import sys
import json
from datetime import datetime, timedelta, timezone

import requests

ALPACA_KEY = os.getenv("APCA_API_KEY_ID")
ALPACA_SECRET = os.getenv("APCA_API_SECRET_KEY")
BASE_URL = os.getenv("APCA_BASE_URL", "https://paper-api.alpaca.markets")
DATA_URL = "https://data.alpaca.markets"


def _headers():
    return {
        "APCA-API-KEY-ID": ALPACA_KEY,
        "APCA-API-SECRET-KEY": ALPACA_SECRET,
    }


def get_bars(symbol, timeframe="1Day", limit=120):
    """Fetch historical price bars for a symbol.

    Alpaca defaults the window to the current day when `start` is omitted, which
    returns only a single bar. We pass an explicit `start` ~180 calendar days back
    so there are enough trading days (>=50) to compute the moving averages.
    """
    start = (datetime.now(timezone.utc) - timedelta(days=180)).strftime("%Y-%m-%d")
    url = f"{DATA_URL}/v2/stocks/{symbol}/bars"
    params = {
        "timeframe": timeframe,
        "start": start,
        "limit": limit,
        "adjustment": "raw",
        "sort": "asc",
    }
    response = requests.get(url, headers=_headers(), params=params)
    return response.json()


def get_account():
    """Get current portfolio status."""
    url = f"{BASE_URL}/v2/account"
    response = requests.get(url, headers=_headers())
    return response.json()


def get_positions():
    """Get all open positions."""
    url = f"{BASE_URL}/v2/positions"
    response = requests.get(url, headers=_headers())
    return response.json()


def get_news(symbol):
    """Get recent news for a symbol."""
    url = f"{DATA_URL}/v1beta1/news"
    params = {"symbols": symbol, "limit": 5, "sort": "desc"}
    response = requests.get(url, headers=_headers(), params=params)
    return response.json()


def moving_average(bars_json, window):
    """Compute a simple moving average from a bars response."""
    bars = bars_json.get("bars", []) if isinstance(bars_json, dict) else []
    closes = [b["c"] for b in bars][-window:]
    if len(closes) < window:
        return None
    return round(sum(closes) / window, 2)


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "account"
    symbol = sys.argv[2] if len(sys.argv) > 2 else None

    if action == "bars" and symbol:
        data = get_bars(symbol)
        out = {
            "bars": data,
            "ma_20": moving_average(data, 20),
            "ma_50": moving_average(data, 50),
        }
        print(json.dumps(out))
    elif action == "news" and symbol:
        print(json.dumps(get_news(symbol)))
    elif action == "positions":
        print(json.dumps(get_positions()))
    else:
        print(json.dumps(get_account()))
