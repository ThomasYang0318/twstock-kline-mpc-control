"""Validate local generated OHLCV CSV fingerprints."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

EXPECTED = {
    "2303": ("2022-01-03", "2025-12-30", 968, "5c2f05d1c8422348ede85fff24486e2448073bbc44e9481f4087411c0b98f066"),
    "2317": ("2022-01-03", "2025-12-30", 968, "7809501fe38bbcbecbd65a491106d557a546896566770cf8bcf3215dacbb8b21"),
    "2330": ("2022-01-03", "2025-12-30", 968, "997e1e86ea3005aedb49ad4c6bb5bce1a409cf448444fd8fb05441c76466a9d8"),
    "2412": ("2022-01-03", "2025-12-30", 968, "f329e9760a423823f91c6ece8db9d3dc61bd79d0e40ecb8ea1c1c5a0300109a1"),
    "2454": ("2022-01-03", "2025-12-30", 968, "f147c6cc6d66622a409183321bb7d98c394a1f42931050a78f945DBFCF13CADB".lower()),
    "2603": ("2022-01-03", "2025-12-30", 968, "dd4d450cbb43f59e10c5af863daf1385820ac68fc01dbe3f076011ca625e5f5f"),
    "2882": ("2022-01-03", "2025-12-30", 968, "23a95e6566f24aeee5cfde107d148c8aa9b5c0b1b2c99cc9171d3a14b9bc18b9"),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    failures = []
    for symbol, (expected_start, expected_end, expected_rows, expected_hash) in EXPECTED.items():
        path = DATA_DIR / f"{symbol}.csv"
        if not path.exists():
            failures.append(f"{symbol}: missing {path}")
            continue

        frame = pd.read_csv(path)
        actual = {
            "rows": len(frame),
            "start": str(frame["date"].iloc[0]),
            "end": str(frame["date"].iloc[-1]),
            "sha256": sha256(path),
        }
        expected = {
            "rows": expected_rows,
            "start": expected_start,
            "end": expected_end,
            "sha256": expected_hash,
        }
        if actual != expected:
            failures.append(f"{symbol}: expected {expected}, got {actual}")
        else:
            print(f"{symbol}: ok")

    if failures:
        print("\nValidation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("\nAll local data fingerprints match docs/data_provenance.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

