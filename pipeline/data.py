from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, List


@dataclass
class Candle:
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


def _parse_row(row: dict) -> Candle:
    return Candle(
        date=datetime.strptime(row["date"], "%Y-%m-%d"),
        open=float(row["open"]),
        high=float(row["high"]),
        low=float(row["low"]),
        close=float(row["close"]),
        volume=int(row["volume"]),
    )


def fetch_nifty50_data(path: Path) -> List[Candle]:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing data file at {path}. Provide a CSV with columns: date, open, high, low, close, volume."
        )

    with path.open("r", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = [_parse_row(row) for row in reader]

    if not rows:
        raise ValueError("Nifty50 data file is empty.")

    return rows
