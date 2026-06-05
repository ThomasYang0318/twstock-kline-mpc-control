from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_OHLCV_COLUMNS = {"open", "high", "low", "close", "volume"}


def normalize_tw_ticker(symbol: str) -> str:
    """Return a Yahoo Finance ticker for common Taiwan stock code inputs."""
    clean = symbol.strip().upper()
    if clean.endswith((".TW", ".TWO")):
        return clean
    if clean.isdigit():
        return f"{clean}.TW"
    return clean


def fetch_ohlcv(
    symbol: str,
    start: str,
    end: str | None = None,
    interval: str = "1d",
    auto_adjust: bool = False,
) -> pd.DataFrame:
    """Download OHLCV data from Yahoo Finance via yfinance."""
    try:
        import yfinance as yf
    except ImportError as exc:  # pragma: no cover - exercised only without dependency
        raise RuntimeError("Install yfinance first: python -m pip install yfinance") from exc

    ticker = normalize_tw_ticker(symbol)
    frame = yf.download(
        ticker,
        start=start,
        end=end,
        interval=interval,
        auto_adjust=auto_adjust,
        progress=False,
    )
    if frame.empty:
        raise ValueError(f"No data returned for {ticker}. Check the symbol and date range.")

    if isinstance(frame.columns, pd.MultiIndex):
        frame.columns = frame.columns.get_level_values(0)

    frame = frame.rename(columns={column: column.lower().replace(" ", "_") for column in frame.columns})
    frame.index.name = "date"
    return frame.reset_index()


def load_ohlcv_csv(path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(path, parse_dates=["date"])
    missing = REQUIRED_OHLCV_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing OHLCV columns: {sorted(missing)}")
    return frame.sort_values("date").reset_index(drop=True)


def save_ohlcv_csv(frame: pd.DataFrame, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(target, index=False)

