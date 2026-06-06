import sys
import types

import pandas as pd

from twstock_kline_mpc_control.data import fetch_latest_quote, normalize_tw_ticker


def test_normalize_tw_ticker_defaults_to_listed_market():
    assert normalize_tw_ticker("2330") == "2330.TW"
    assert normalize_tw_ticker("6488.TWO") == "6488.TWO"


def test_fetch_latest_quote_uses_fast_info_and_latest_bar(monkeypatch):
    class FakeTicker:
        fast_info = {
            "last_price": 100.5,
            "previous_close": 99.0,
            "open": 100.0,
            "day_high": 101.0,
            "day_low": 98.5,
            "last_volume": 12345,
        }

        def __init__(self, ticker):
            self.ticker = ticker

        def history(self, period, interval, auto_adjust):
            return pd.DataFrame(
                {"Close": [100.5]},
                index=pd.to_datetime(["2026-06-05 13:30:00"]),
            )

    fake_yf = types.SimpleNamespace(Ticker=FakeTicker)
    monkeypatch.setitem(sys.modules, "yfinance", fake_yf)

    quote = fetch_latest_quote("2330")

    assert quote["ticker"] == "2330.TW"
    assert quote["last_price"] == 100.5
    assert quote["previous_close"] == 99.0
    assert quote["latest_bar_time"] == "2026-06-05 13:30:00"
