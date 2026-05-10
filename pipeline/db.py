from __future__ import annotations

import sqlite3
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

from .execution import TradeResult


def init_db(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                status TEXT NOT NULL,
                side TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                entry_price REAL NOT NULL,
                stop_loss REAL NOT NULL,
                take_profit REAL NOT NULL,
                timestamp TEXT NOT NULL,
                message TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_timestamp TEXT NOT NULL,
                latest_close REAL NOT NULL,
                trend TEXT NOT NULL,
                signal TEXT NOT NULL,
                risk_allowed INTEGER NOT NULL,
                risk_reason TEXT NOT NULL
            )
            """
        )


def store_trade(path: Path, trade: TradeResult) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            INSERT INTO trades (
                status, side, quantity, entry_price, stop_loss, take_profit, timestamp, message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                trade.status,
                trade.side,
                trade.quantity,
                trade.entry_price,
                trade.stop_loss,
                trade.take_profit,
                trade.timestamp.isoformat(),
                trade.message,
            ),
        )


def store_run(
    path: Path,
    run_timestamp: str,
    latest_close: float,
    trend: str,
    signal: str,
    risk_allowed: bool,
    risk_reason: str,
) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            INSERT INTO runs (
                run_timestamp, latest_close, trend, signal, risk_allowed, risk_reason
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                run_timestamp,
                latest_close,
                trend,
                signal,
                1 if risk_allowed else 0,
                risk_reason,
            ),
        )


def count_trades_today(path: Path, date_prefix: str) -> int:
    with sqlite3.connect(path) as conn:
        cur = conn.execute(
            "SELECT COUNT(*) FROM trades WHERE timestamp LIKE ?",
            (f"{date_prefix}%",),
        )
        row = cur.fetchone()
    return int(row[0]) if row else 0
