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
