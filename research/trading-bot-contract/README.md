# Trading-bot page: data and build

- `data.json`: every figure in the sweep sections. Written by `scripts/data/trading_bot_export.py` from the read-only on-chain scripts (`mev-bot-0x51c728-explained/onchain/`). `meta` holds generated_at, rows, first, last, source and method, the same shape as `research/data/meta.json`.
- `page.src.html`: the page. `{{path|fmt}}` pulls a value from data.json. `<!--need: expr-->` pins a claim in the words to the data.
- `build.py`: renders `index.html`. Fails on a missing value or a broken pin. Prints how many numbers are still typed in the source.
- Refresh: `scripts/data/refresh_trading_bot.sh`. Never edit `index.html` by hand.

## Shared data layer
The export also writes research/data/trading_bot_daily.csv and a `trading_bot` section in research/data/meta.json (generated_at, method, rows, source), the same shape as the `commits` section.
