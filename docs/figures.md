# Backtest Figures

Generated on 2026-06-05 from local backtest CSV outputs.

## Figure 1: Equity Curves

![MPC backtest equity curves](../figures/fig_equity_curves.png)

This figure compares normalized equity curves across the tested stocks. `2330`
is highlighted as the original reference case.

## Figure 2: Return-Drawdown Trade-off

![Return-drawdown trade-off](../figures/fig_return_drawdown_tradeoff.png)

The upper-left region is preferable: higher total return with lower drawdown
magnitude. In this run, `2317` is notable because it has high return and a
smaller drawdown than the other top performers.

## Figure 3: Metric Leaderboard

![Metric leaderboard](../figures/fig_metric_leaderboard.png)

The left panel ranks total return, while the right panel shows maximum drawdown
magnitude. This makes it easier to compare performance and risk side by side.

## Reproduce

```powershell
$env:PYTHONPATH='src'
$env:MPLCONFIGDIR='figures/.mplconfig'
python -B figures/gen_fig_backtest_publication.py
```

