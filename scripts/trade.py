"""Order execution and validation for the trading agent.

Usage:
    python3 scripts/trade.py status
    python3 scripts/trade.py order SYMBOL QTY SIDE [LIMIT_PRICE]
"""
import os
import sys
import json

import requests

ALPACA_KEY = os.getenv("APCA_API_KEY_ID")
ALPACA_SECRET = os.getenv("APCA_API_SECRET_KEY")
BASE_URL = os.getenv("APCA_BASE_URL", "https://paper-api.alpaca.markets")


def _headers(json_body=False):
    h = {
        "APCA-API-KEY-ID": ALPACA_KEY,
        "APCA-API-SECRET-KEY": ALPACA_SECRET,
    }
    if json_body:
        h["Content-Type"] = "application/json"
    return h


def place_order(symbol, qty, side, limit_price=None):
    """Place a buy or sell order. Defaults to a day limit order."""
    order_data = {
        "symbol": symbol,
        "qty": qty,
        "side": side,
        "type": "limit" if limit_price else "market",
        "time_in_force": "day",
    }
    if limit_price:
        order_data["limit_price"] = str(limit_price)

    url = f"{BASE_URL}/v2/orders"
    response = requests.post(url, headers=_headers(json_body=True), json=order_data)
    return response.json()


def validate_order(symbol, qty, side, current_price, account_value, current_positions):
    """Pre-flight validation before order placement."""
    order_value = qty * current_price
    allocation_pct = (order_value / account_value) * 100

    if allocation_pct > 10:
        return False, f"Exceeds 10% allocation: {allocation_pct:.1f}%"

    total_invested = sum(float(p["market_value"]) for p in current_positions)
    if (total_invested + order_value) / account_value > 0.80:
        return False, "Violates 20% cash reserve requirement"

    return True, "Order validated"


def get_market_status():
    """Check if the market is open."""
    url = f"{BASE_URL}/v2/clock"
    response = requests.get(url, headers=_headers())
    return response.json()


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "status"

    if action == "status":
        print(json.dumps(get_market_status()))
    elif action == "order":
        symbol = sys.argv[2]
        qty = sys.argv[3]
        side = sys.argv[4]
        limit_price = sys.argv[5] if len(sys.argv) > 5 else None
        print(json.dumps(place_order(symbol, qty, side, limit_price)))
    else:
        print(json.dumps({"error": f"unknown action: {action}"}))
