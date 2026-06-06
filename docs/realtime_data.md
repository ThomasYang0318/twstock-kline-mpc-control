# Latest Quote and Intraday Data

Generated on 2026-06-06.

## What This Project Can Fetch

The project now supports latest available quote snapshots and recent intraday
bars through Yahoo Finance via `yfinance`.

```powershell
$env:PYTHONPATH='src'
python -B -m twstock_kline_mpc_control quote 2330 --out data/2330_intraday.csv
```

This produces:

- A console quote snapshot.
- Optional intraday OHLCV bars saved to CSV when `--out` is provided.

## Example Output for `2330.TW`

Because 2026-06-06 is a Saturday in Taiwan, the latest available intraday bar
returned by Yahoo Finance was from the previous trading day.

| Field | Value |
| --- | ---: |
| Last price | `2365.0` |
| Previous close | `2395.0` |
| Open | `2395.0` |
| Day high | `2405.0` |
| Day low | `2350.0` |
| Volume | `32795780.0` |
| Latest bar time | `2026-06-05 13:24:00+08:00` |
| Saved intraday rows | `265` |

## Important Limitation

Treat Yahoo Finance Taiwan quotes as latest available, near-real-time, or
delayed market data. Do not describe this as exchange-grade real-time tick data
in a paper. For true real-time trading systems, use a broker API or a licensed
market data feed.

Suggested wording:

> We retrieved latest available quote snapshots and intraday bars
> programmatically using Yahoo Finance via `yfinance`. Because such feeds may be
> delayed and are not exchange-grade tick data, all real-time trading claims
> should be validated against broker or licensed exchange feeds.

