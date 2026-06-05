# 2330.TW MPC Backtest

Generated on 2026-06-05.

## Data

- Symbol: `2330.TW`
- Source: Yahoo Finance via `yfinance`
- Daily K-line rows: `968`
- Date range: `2022-01-03` to `2025-12-30`
- Local data file: `data/2330.csv`

## Command

```powershell
$env:PYTHONPATH='src'
python -B -m twstock_kline_mpc_control fetch 2330 --start 2022-01-01 --end 2025-12-31 --out data/2330.csv
python -B -m twstock_kline_mpc_control backtest data/2330.csv --initial-cash 1000000 --out reports/2330_backtest.csv
```

## Result

| Metric | Value |
| --- | ---: |
| Total return | `253.55%` |
| Annualized return | `38.97%` |
| Annualized volatility | `19.76%` |
| Sharpe | `1.9721` |
| Max drawdown | `-12.15%` |
| Final equity | `3,535,460.64` |

## Notes

The strategy is a research baseline, not investment advice. It uses a simple
trend and momentum signal, then applies a bounded long-only MPC optimizer with
risk and turnover penalties.

