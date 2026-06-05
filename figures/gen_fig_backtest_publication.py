"""Generate publication-style figures from MPC backtest CSV outputs."""

from __future__ import annotations

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports"
OUTPUT_DIR = ROOT / "figures"
INITIAL_CASH = 1_000_000.0
SYMBOLS = ["2330", "2317", "2454", "2603", "2882", "2303", "2412"]

PALETTE = {
    "2330": "#D55E00",  # highlighted baseline
    "2317": "#0072B2",
    "2454": "#009E73",
    "2603": "#CC79A7",
    "2882": "#E69F00",
    "2303": "#56B4E9",
    "2412": "#7A7A7A",
}


def apply_publication_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "DejaVu Serif"],
            "font.size": 10,
            "axes.titlesize": 11,
            "axes.titleweight": "bold",
            "axes.labelsize": 10,
            "legend.fontsize": 8.5,
            "legend.frameon": False,
            "figure.dpi": 300,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.18,
            "grid.linestyle": "-",
            "lines.linewidth": 1.8,
            "lines.markersize": 4,
        }
    )


def load_curves() -> dict[str, pd.DataFrame]:
    curves = {}
    for symbol in SYMBOLS:
        path = REPORT_DIR / f"{symbol}_backtest.csv"
        frame = pd.read_csv(path, parse_dates=["date"])
        frame["equity_multiple"] = frame["equity"] / INITIAL_CASH
        curves[symbol] = frame
    return curves


def load_summary() -> pd.DataFrame:
    path = REPORT_DIR / "comparison_summary.csv"
    if path.exists():
        summary = pd.read_csv(path, dtype={"symbol": str})
    else:
        rows = []
        for symbol, curve in load_curves().items():
            rows.append(
                {
                    "symbol": symbol,
                    "final_equity": curve["equity"].iloc[-1],
                    "total_return": curve["equity"].iloc[-1] / INITIAL_CASH - 1.0,
                    "max_drawdown": curve["drawdown"].min(),
                    "last_weight": curve["target_weight"].iloc[-1],
                }
            )
        summary = pd.DataFrame(rows)
    return summary.sort_values("total_return", ascending=False).reset_index(drop=True)


def save_figure(fig: plt.Figure, name: str) -> None:
    fig.savefig(OUTPUT_DIR / f"{name}.pdf")
    fig.savefig(OUTPUT_DIR / f"{name}.png", dpi=300)
    plt.close(fig)


def fig_equity_curves(curves: dict[str, pd.DataFrame]) -> None:
    fig, ax = plt.subplots(figsize=(6.75, 3.2))
    for symbol in SYMBOLS:
        curve = curves[symbol]
        color = PALETTE[symbol]
        linewidth = 2.3 if symbol == "2330" else 1.55
        alpha = 1.0 if symbol in {"2330", "2317", "2454"} else 0.78
        zorder = 5 if symbol == "2330" else 3
        ax.plot(
            curve["date"],
            curve["equity_multiple"],
            label=symbol,
            color=color,
            linewidth=linewidth,
            alpha=alpha,
            zorder=zorder,
        )

    ax.set_title("MPC Backtest Equity Curves")
    ax.set_ylabel("Equity Multiple")
    ax.set_xlabel("Date")
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.legend(ncol=7, loc="upper left", bbox_to_anchor=(0.0, 1.02), columnspacing=0.9)
    ax.set_ylim(bottom=0.75)
    save_figure(fig, "fig_equity_curves")


def fig_return_drawdown_tradeoff(summary: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(4.6, 3.2))
    x = summary["max_drawdown"].abs() * 100
    y = summary["total_return"] * 100
    sizes = 40 + (summary["final_equity"] / summary["final_equity"].max()) * 130

    for idx, row in summary.iterrows():
        symbol = row["symbol"]
        ax.scatter(
            abs(row["max_drawdown"]) * 100,
            row["total_return"] * 100,
            s=sizes.iloc[idx],
            color=PALETTE.get(symbol, "#7A7A7A"),
            edgecolor="white",
            linewidth=0.9,
            zorder=3,
        )
        ax.text(
            abs(row["max_drawdown"]) * 100 + 0.35,
            row["total_return"] * 100 + 1.2,
            symbol,
            fontsize=8.5,
            color="#333333",
        )

    ax.set_title("Return-Drawdown Trade-off")
    ax.set_xlabel("Maximum Drawdown Magnitude (%)")
    ax.set_ylabel("Total Return (%)")
    ax.set_xlim(0, max(x) + 4)
    ax.set_ylim(0, max(y) + 35)
    save_figure(fig, "fig_return_drawdown_tradeoff")


def fig_metric_leaderboard(summary: pd.DataFrame) -> None:
    ordered = summary.sort_values("total_return", ascending=True)
    y = np.arange(len(ordered))
    colors = [PALETTE.get(symbol, "#7A7A7A") for symbol in ordered["symbol"]]

    fig, axes = plt.subplots(1, 2, figsize=(6.75, 3.0), sharey=True)

    axes[0].barh(y, ordered["total_return"] * 100, color=colors, height=0.62)
    axes[0].set_yticks(y)
    axes[0].set_yticklabels(ordered["symbol"])
    axes[0].set_xlabel("Total Return (%)")
    axes[0].set_title("Return")
    for pos, value in zip(y, ordered["total_return"] * 100):
        axes[0].text(value + 3, pos, f"{value:.0f}", va="center", fontsize=8, color="#444444")

    axes[1].barh(y, ordered["max_drawdown"].abs() * 100, color=colors, height=0.62)
    axes[1].set_xlabel("Max Drawdown (%)")
    axes[1].set_title("Risk")
    for pos, value in zip(y, ordered["max_drawdown"].abs() * 100):
        axes[1].text(value + 0.35, pos, f"{value:.1f}", va="center", fontsize=8, color="#444444")

    axes[0].set_xlim(0, max(ordered["total_return"] * 100) * 1.15)
    axes[1].set_xlim(0, max(ordered["max_drawdown"].abs() * 100) * 1.2)
    fig.suptitle("Cross-Stock MPC Backtest Summary", fontsize=11, fontweight="bold", y=1.03)
    fig.tight_layout()
    save_figure(fig, "fig_metric_leaderboard")


def main() -> None:
    apply_publication_style()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    curves = load_curves()
    summary = load_summary()
    fig_equity_curves(curves)
    fig_return_drawdown_tradeoff(summary)
    fig_metric_leaderboard(summary)
    print("Generated publication figures in figures/")


if __name__ == "__main__":
    main()

