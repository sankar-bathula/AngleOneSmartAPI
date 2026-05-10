from __future__ import annotations

from dataclasses import dataclass

from .indicators import IndicatorPoint
from .trend import TrendResult


@dataclass
class SignalResult:
    signal: str
    reason: str


def generate_signal(point: IndicatorPoint, trend: TrendResult) -> SignalResult:
    if trend.trend == "unknown":
        return SignalResult(signal="hold", reason="Trend unknown.")

    rsi = point.rsi14
    macd = point.macd
    macd_signal = point.macd_signal

    if rsi is None or macd is None or macd_signal is None:
        return SignalResult(signal="hold", reason="Not enough data for signal.")

    if trend.trend == "up" and rsi < 70 and macd > macd_signal:
        return SignalResult(signal="buy", reason="Uptrend with RSI < 70 and MACD above signal.")

    if trend.trend == "down" and rsi > 30 and macd < macd_signal:
        return SignalResult(signal="sell", reason="Downtrend with RSI > 30 and MACD below signal.")

    return SignalResult(signal="hold", reason="Conditions not met for entry.")
