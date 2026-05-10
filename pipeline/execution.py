from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .risk import RiskResult
from .signal import SignalResult


@dataclass
class TradeResult:
    status: str
    side: str
    quantity: int
    entry_price: float
    stop_loss: float
    take_profit: float
    timestamp: datetime
    message: str


def execute_trade(signal: SignalResult, risk: RiskResult, last_price: float) -> TradeResult:
    if not risk.allowed:
        return TradeResult(
            status="skipped",
            side=signal.signal,
            quantity=0,
            entry_price=last_price,
            stop_loss=0.0,
            take_profit=0.0,
            timestamp=datetime.utcnow(),
            message=risk.reason,
        )

    return TradeResult(
        status="filled",
        side=signal.signal,
        quantity=risk.quantity,
        entry_price=last_price,
        stop_loss=risk.stop_loss,
        take_profit=risk.take_profit,
        timestamp=datetime.utcnow(),
        message="Paper trade executed.",
    )
