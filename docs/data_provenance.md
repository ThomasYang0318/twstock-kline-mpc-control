# Data Provenance and Authenticity

Generated on 2026-06-05.

## Why This Matters

Backtest figures are only useful if the input data can be traced and reproduced.
For a paper or technical report, do not ask readers to trust the plotted curves
alone. Report the data source, retrieval period, exact script, file checksums,
and an independent verification path.

## Primary Data Used in This Repository

- Provider used by the code: Yahoo Finance, accessed through `yfinance`
- Ticker format: Taiwan listed stocks use Yahoo tickers such as `2330.TW`
- Retrieval command:

```powershell
$env:PYTHONPATH='src'
python -B -m twstock_kline_mpc_control fetch 2330 --start 2022-01-01 --end 2025-12-31 --out data/2330.csv
```

The local CSV files are ignored by Git because they are generated data, but
their hashes are listed below so the exact local files can be verified.

## Official Cross-Check Source

For Taiwan listed stocks, use the Taiwan Stock Exchange historical individual
security daily trading page as the official cross-check source:

https://www.twse.com.tw/en/trading/historical/stock-day.html

The TWSE page provides historical daily trading data for individual securities
and states that data is provided since 2010-01-04. Use it to spot-check dates,
close prices, volumes, and date availability for listed stocks.

## Local Data Fingerprints

| Symbol | Rows | Start | End | SHA256 |
| --- | ---: | --- | --- | --- |
| `2303` | 968 | 2022-01-03 | 2025-12-30 | `5c2f05d1c8422348ede85fff24486e2448073bbc44e9481f4087411c0b98f066` |
| `2317` | 968 | 2022-01-03 | 2025-12-30 | `7809501fe38bbcbecbd65a491106d557a546896566770cf8bcf3215dacbb8b21` |
| `2330` | 968 | 2022-01-03 | 2025-12-30 | `997e1e86ea3005aedb49ad4c6bb5bce1a409cf448444fd8fb05441c76466a9d8` |
| `2412` | 968 | 2022-01-03 | 2025-12-30 | `f329e9760a423823f91c6ece8db9d3dc61bd79d0e40ecb8ea1c1c5a0300109a1` |
| `2454` | 968 | 2022-01-03 | 2025-12-30 | `f147c6cc6d66622a409183321bb7d98c394a1f42931050a78f945dbfcf13cadb` |
| `2603` | 968 | 2022-01-03 | 2025-12-30 | `dd4d450cbb43f59e10c5af863daf1385820ac68fc01dbe3f076011ca625e5f5f` |
| `2882` | 968 | 2022-01-03 | 2025-12-30 | `23a95e6566f24aeee5cfde107d148c8aa9b5c0b1b2c99cc9171d3a14b9bc18b9` |

## Verification Protocol for a Paper

1. Cite the data provider used by the experiment.
2. Record the retrieval date and code version.
3. Store the raw generated CSV files or publish their checksums.
4. Recompute the indicators and backtests from raw OHLCV files only.
5. Spot-check several randomly selected rows against TWSE official daily data.
6. Report whether prices are adjusted or unadjusted. This repository currently
   calls `yfinance.download(..., auto_adjust=False)`.

## Suggested Paper Wording

> Daily OHLCV data for Taiwan equities were retrieved using Yahoo Finance via
> `yfinance` on 2026-06-05. To support reproducibility, we report the data
> retrieval command, date range, row counts, and SHA256 checksums of the local
> CSV files. Selected observations were cross-checked against the Taiwan Stock
> Exchange historical individual security daily trading data page.

## Reproduce the Hash Check

```powershell
python -B scripts/validate_data_provenance.py
```

