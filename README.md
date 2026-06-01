# Trading Agent (Alpaca Paper Trading)

An autonomous paper-trading agent driven by Claude Code. It researches market data, executes
limit orders via the Alpaca **paper** API, and journals every decision. Trades fake money only.

## Layout
```
trading-agent/
  CLAUDE.md              # Agent instructions + risk rules + decision framework
  watchlist.json         # Monitored symbols and per-symbol allocation caps
  requirements.txt       # Python deps
  .env.example           # Copy to .env and add your paper keys
  journal/               # Daily journal entries (YYYY-MM-DD.md) + TEMPLATE.md
  scripts/
    research.py          # account / positions / bars (+MAs) / news
    trade.py             # market clock + order placement + validation
    notify.py            # optional email digest
  .claude/routines.json  # Scheduled routines (research / trade / journal)
```

## Setup
1. **Get paper keys:** sign up at https://alpaca.markets, switch to the **Paper** account,
   and generate an API key + secret.
2. **Configure env:** `cp .env.example .env` and fill in the three `APCA_*` values.
   Keep `APCA_BASE_URL=https://paper-api.alpaca.markets`.
3. **Install deps:** `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
4. **Load env + test:** `set -a && source .env && set +a` then
   `python3 scripts/trade.py status`.

## Manual use
```bash
set -a && source .env && set +a
python3 scripts/research.py account
python3 scripts/research.py positions
python3 scripts/research.py bars NVDA
python3 scripts/research.py news NVDA
python3 scripts/trade.py status
python3 scripts/trade.py order NVDA 1 buy 100.00   # limit buy 1 share @ $100
```

## Autonomous use
Open this folder in Claude Code and let it read `CLAUDE.md`. The routines in
`.claude/routines.json` describe the 09:45 / 10:00 / 16:15 ET schedule; register them with
Claude Code's scheduler (the `/schedule` skill) to run hands-free on weekdays.

## Safety
- Paper account only — `CLAUDE.md` requires verifying the paper URL before any order.
- Risk rules: ≤5% per new position, limit orders only, 8% stop-loss, 20% cash reserve.
- `.env` is gitignored. Never commit real credentials.
