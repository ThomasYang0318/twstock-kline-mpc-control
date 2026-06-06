# Experimental Protocol: Train/Holdout Separation

Generated on 2026-06-06.

## Motivation

Backtests should not reuse the same period for both tuning and evaluation. If a
strategy is calibrated on the exact years used for the final performance table,
the result can overstate out-of-sample performance.

This repository now supports a non-overlapping train/holdout protocol:

- Use the earlier years for parameter calibration.
- Reserve the final `3` to `5` years for the final backtest.
- Report train and holdout results separately.
- Never select parameters based on the holdout result.

## Current Meaning of "Training"

The current strategy is not a neural network and does not fit model weights.
Here, "training" means tuning MPC hyperparameters, such as:

- Planning horizon
- Risk aversion
- Turnover penalty

If a forecasting model is added later, it should use the same protocol: fit on
the training period only, then evaluate once on the holdout period.

## Command

```powershell
$env:PYTHONPATH='src'
python -B -m twstock_kline_mpc_control calibrate data/2330.csv `
  --holdout-years 4 `
  --grid-out reports/2330_train_grid.csv `
  --holdout-out reports/2330_holdout_backtest.csv
```

Use `--holdout-years 3` or `--holdout-years 5` for the paper's sensitivity
checks.

An example result for long-history `2330.TW` data is available in
[holdout_2330.md](holdout_2330.md).

## Paper Wording

> We split each stock's time series chronologically. MPC hyperparameters were
> selected using only the training period, while the final 3-5 years were
> reserved as a non-overlapping holdout backtest. Holdout performance was not
> used for model selection.
