# Multi-Stock MPC Backtest

Generated on 2026-06-05.

## Setup

- Initial cash: `1,000,000`
- Date range: `2022-01-03` to `2025-12-30`
- Data source: Yahoo Finance via `yfinance`
- Strategy: default long-only MPC controller

## Comparison

| Rank | Symbol | Final equity | Total return | Max drawdown | Last weight |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `2330` | `3,535,460.64` | `253.55%` | `-12.15%` | `93.66%` |
| 2 | `2317` | `3,250,181.55` | `225.02%` | `-9.43%` | `17.87%` |
| 3 | `2454` | `2,818,408.41` | `181.84%` | `-12.75%` | `58.51%` |
| 4 | `2603` | `2,158,087.77` | `115.81%` | `-22.20%` | `91.03%` |
| 5 | `2882` | `1,703,888.72` | `70.39%` | `-9.17%` | `100.00%` |
| 6 | `2303` | `1,447,956.33` | `44.80%` | `-10.69%` | `97.61%` |
| 7 | `2412` | `1,148,998.48` | `14.90%` | `-7.08%` | `13.73%` |

Publication-style figures are available in [figures.md](figures.md).

## Quick Read

- `2330`, `2317`, and `2454` are the strongest results in this run.
- `2317` has a strong return with the smallest drawdown among the top three.
- `2603` produced good return, but the drawdown is much larger, so it is less stable.
- `2412` is defensive in this setup: low drawdown, but also low return.

## Local Outputs

- `reports/comparison_summary.csv`
- `reports/2317_backtest.csv`
- `reports/2454_backtest.csv`
- `reports/2303_backtest.csv`
- `reports/2412_backtest.csv`
- `reports/2882_backtest.csv`
- `reports/2603_backtest.csv`

These CSV outputs are intentionally ignored by Git so large generated data does
not crowd the repository.
