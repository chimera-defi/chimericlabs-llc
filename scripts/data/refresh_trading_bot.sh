#!/bin/bash
# One command: re-run the read-only profit sweep, rebuild data.json and the trading-bot page.
# usage: scripts/data/refresh_trading_bot.sh [ONCHAIN_DIR]   (default: ~/workspace/mev-bot-0x51c728-explained/onchain)
# END=<block> moves the sweep's last block; it must be 26,416,999 + n x 7,200 (multiday.py checks). Old windows are kept, so a refresh fetches only new days.
# Read-only RPC and explorer calls. Sends no transaction and touches no wallet.
set -euo pipefail
ON="${1:-$HOME/workspace/mev-bot-0x51c728-explained/onchain}"
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ON"
python3 multiday.py fetch     # resumable; skips windows marked done
python3 multiday.py           # flows per window -> multiday.json
python3 topfill.py            # largest fill, checked against Binance -> topfill.json
cd "$REPO"
python3 -I scripts/data/trading_bot_export.py "$ON"   # -> research/trading-bot-contract/data.json
python3 -I research/trading-bot-contract/build.py     # -> index.html (fails if the words no longer match the data)
