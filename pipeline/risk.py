from __future__ import annotations

from dataclasses import dataclass

from .config import Config
from .signal import SignalResult


@dataclass
class RiskResult:
    allowed: bool
    reason: str
    quantity: int
    stop_loss: float
    take_profit: float


def check_risk_rules(config: Config, signal: SignalResult, last_price: float, trades_today: int) -> RiskResult:
    if signal.signal == "hold":
        return RiskResult(False, "No trade signal.", 0, 0.0, 0.0)

    if trades_today >= config.max_daily_trades:
        return RiskResult(False, "Max daily trades reached.", 0, 0.0, 0.0)

    risk_amount = config.equity * config.risk_per_trade
    stop_distance = last_price * config.stop_loss_pct

    if stop_distance <= 0:
        return RiskResult(False, "Invalid stop distance.", 0, 0.0, 0.0)

    quantity = int(risk_amount / stop_distance)
    if quantity <= 0:
        return RiskResult(False, "Position size too small.", 0, 0.0, 0.0)

    if signal.signal == "buy":
        stop_loss = last_price - stop_distance
        take_profit = last_price + (last_price * config.take_profit_pct)
    else:
        stop_loss = last_price + stop_distance
        take_profit = last_price - (last_price * config.take_profit_pct)

    return RiskResult(True, "Risk checks passed.", quantity, stop_loss, take_profit)
