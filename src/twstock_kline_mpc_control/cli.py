from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from .backtest import run_backtest
from .data import fetch_ohlcv, load_ohlcv_csv, save_ohlcv_csv
from .mpc import MPCConfig


app = typer.Typer(no_args_is_help=True, help="Taiwan stock K-line MPC control CLI.")
console = Console()


@app.command()
def fetch(
    symbol: str = typer.Argument(..., help="Taiwan stock code, e.g. 2330."),
    start: str = typer.Option(..., help="Start date, YYYY-MM-DD."),
    end: Optional[str] = typer.Option(None, help="End date, YYYY-MM-DD."),
    interval: str = typer.Option("1d", help="Yahoo Finance interval."),
    out: Path = typer.Option(Path("data/kline.csv"), help="Output CSV path."),
) -> None:
    """Download OHLCV K-line data."""
    frame = fetch_ohlcv(symbol=symbol, start=start, end=end, interval=interval)
    save_ohlcv_csv(frame, out)
    console.print(f"Saved {len(frame)} rows to [bold]{out}[/bold]")


@app.command()
def backtest(
    csv_path: Path = typer.Argument(..., help="CSV file produced by fetch."),
    initial_cash: float = typer.Option(1_000_000.0, help="Initial account value."),
    horizon: int = typer.Option(5, help="MPC planning horizon in trading days."),
    risk_aversion: float = typer.Option(10.0, help="Risk penalty."),
    turnover_penalty: float = typer.Option(0.5, help="Trading smoothness penalty."),
    transaction_cost: float = typer.Option(0.001, help="One-way transaction cost ratio."),
    out: Optional[Path] = typer.Option(None, help="Optional equity curve CSV path."),
) -> None:
    """Run the default MPC allocation backtest."""
    frame = load_ohlcv_csv(csv_path)
    result = run_backtest(
        frame,
        mpc_config=MPCConfig(
            horizon=horizon,
            risk_aversion=risk_aversion,
            turnover_penalty=turnover_penalty,
            transaction_cost=transaction_cost,
        ),
        initial_cash=initial_cash,
    )

    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        result.equity_curve.to_csv(out, index=False)
        console.print(f"Saved equity curve to [bold]{out}[/bold]")

    table = Table(title="Backtest Summary")
    table.add_column("Metric")
    table.add_column("Value", justify="right")
    for key, value in result.summary.items():
        table.add_row(key, f"{value:,.4f}")
    console.print(table)
