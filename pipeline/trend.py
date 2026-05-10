from __future__ import annotations

from dataclasses import dataclass

from .indicators import IndicatorPoint


@dataclass
class TrendResult:
    trend: str
    reason: str


def detect_trend(point: IndicatorPoint) -> TrendResult:
    if point.sma20 is None or point.sma50 is None:
        return TrendResult(trend="unknown", reason="Not enough data for SMA trend.")

    if point.sma20 > point.sma50 and point.candle.close > point.sma50:
        return TrendResult(trend="up", reason="SMA20 above SMA50 and close above SMA50.")

    if point.sma20 < point.sma50 and point.candle.close < point.sma50:
        return TrendResult(trend="down", reason="SMA20 below SMA50 and close below SMA50.")

    return TrendResult(trend="sideways", reason="SMA20/SMA50 not aligned.")
