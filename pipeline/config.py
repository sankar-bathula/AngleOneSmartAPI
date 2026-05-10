from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    data_path: Path = Path("data/nifty50.csv")
    db_path: Path = Path("data/trades.db")
    equity: float = 1_000_000.0
    max_daily_trades: int = 3
    risk_per_trade: float = 0.01
    stop_loss_pct: float = 0.015
    take_profit_pct: float = 0.03


DEFAULT_CONFIG = Config()
