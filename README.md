# twstock-kline-mpc-control

Taiwan stock K-line research starter project. It downloads OHLCV data, builds
simple trend and volatility features, then uses a model predictive control
(MPC) style optimizer to decide the next target position.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e ".[dev]"
```

If your pip version is too old for editable `pyproject.toml` installs, install
the runtime dependencies directly and run with `PYTHONPATH=src`:

```powershell
python -m pip install yfinance typer rich pandas numpy scipy matplotlib pytest
$env:PYTHONPATH='src'
```

## Fetch K-line Data

Taiwan stock codes such as `2330` are converted to Yahoo Finance tickers such as
`2330.TW`.

```powershell
twstock-mpc fetch 2330 --start 2022-01-01 --end 2025-12-31 --out data/2330.csv
```

## Run a Backtest

```powershell
twstock-mpc backtest data/2330.csv --initial-cash 1000000 --out reports/2330_backtest.csv
```

The backtest CSV includes close price, target weight, daily portfolio return,
equity curve, and drawdown.

See [docs/backtest_2330.md](docs/backtest_2330.md) for a generated 2330.TW
example result.

## Calibrate Then Hold Out

For research, avoid tuning and evaluating on the same dates. This command tunes
MPC parameters on the earlier period and reserves the final years for a
non-overlapping holdout backtest:

```powershell
twstock-mpc calibrate data/2330.csv --holdout-years 4 --grid-out reports/2330_train_grid.csv --holdout-out reports/2330_holdout_backtest.csv
```

See [docs/experimental_protocol.md](docs/experimental_protocol.md).
For an example using 2010-2021 as train data and 2021-2025 as a final holdout,
see [docs/holdout_2330.md](docs/holdout_2330.md).

## Fetch Latest Available Quote

```powershell
twstock-mpc quote 2330 --out data/2330_intraday.csv
```

The quote command prints the latest available snapshot and can save recent
intraday bars. Yahoo Finance Taiwan data should be treated as latest available
or delayed data, not exchange-grade real-time tick data. See
[docs/realtime_data.md](docs/realtime_data.md).

## Python API

```python
from twstock_kline_mpc_control import MPCConfig, add_indicators, run_backtest
from twstock_kline_mpc_control.data import load_ohlcv_csv

df = load_ohlcv_csv("data/2330.csv")
features = add_indicators(df)
result = run_backtest(features, mpc_config=MPCConfig())
print(result.summary)
```

## Notes

This is a research scaffold, not investment advice. The default signal is
intentionally simple so you can replace it with your own forecasting model,
risk model, or execution rules.
