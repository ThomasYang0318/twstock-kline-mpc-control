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


def fetch_intraday_ohlcv(
    symbol: str,
    period: str = "1d",
    interval: str = "1m",
    auto_adjust: bool = False,
) -> pd.DataFrame:
    """Download recent intraday OHLCV data from Yahoo Finance via yfinance."""
    try:
        import yfinance as yf
    except ImportError as exc:  # pragma: no cover - exercised only without dependency
        raise RuntimeError("Install yfinance first: python -m pip install yfinance") from exc

    ticker = normalize_tw_ticker(symbol)
    frame = yf.download(
        ticker,
        period=period,
        interval=interval,
        auto_adjust=auto_adjust,
        progress=False,
    )
    if frame.empty:
        raise ValueError(f"No intraday data returned for {ticker}.")

    if isinstance(frame.columns, pd.MultiIndex):
        frame.columns = frame.columns.get_level_values(0)

    frame = frame.rename(columns={column: column.lower().replace(" ", "_") for column in frame.columns})
    frame.index.name = "datetime"
    return frame.reset_index()


def fetch_latest_quote(symbol: str) -> dict[str, object]:
    """Fetch the latest available quote snapshot.

    Yahoo Finance data for Taiwan equities is best treated as near-real-time or
    delayed data. For exchange-grade tick data, use a broker or licensed feed.
    """
    try:
        import yfinance as yf
    except ImportError as exc:  # pragma: no cover - exercised only without dependency
        raise RuntimeError("Install yfinance first: python -m pip install yfinance") from exc

    ticker_symbol = normalize_tw_ticker(symbol)
    ticker = yf.Ticker(ticker_symbol)
    fast_info = getattr(ticker, "fast_info", {}) or {}
    history = ticker.history(period="1d", interval="1m", auto_adjust=False)

    latest = history.iloc[-1] if not history.empty else None
    last_price = _first_present(fast_info, "last_price", "lastPrice", "regular_market_price")
    if last_price is None and latest is not None:
        last_price = latest.get("Close")

    return {
        "ticker": ticker_symbol,
        "last_price": _to_float(last_price),
        "previous_close": _to_float(_first_present(fast_info, "previous_close", "previousClose")),
        "open": _to_float(_first_present(fast_info, "open", "regular_market_open")),
        "day_high": _to_float(_first_present(fast_info, "day_high", "dayHigh", "regular_market_day_high")),
        "day_low": _to_float(_first_present(fast_info, "day_low", "dayLow", "regular_market_day_low")),
        "volume": _to_float(_first_present(fast_info, "last_volume", "lastVolume", "regular_market_volume")),
        "latest_bar_time": None if latest is None else str(latest.name),
        "source": "Yahoo Finance via yfinance",
    }


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


def _first_present(mapping: object, *keys: str) -> object:
    for key in keys:
        try:
            value = mapping[key]  # type: ignore[index]
        except (KeyError, TypeError):
            continue
        if value is not None:
            return value
    return None


def _to_float(value: object) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
