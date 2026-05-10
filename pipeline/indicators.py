from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .data import Candle


@dataclass
class IndicatorPoint:
    candle: Candle
    sma20: float | None
    sma50: float | None
    ema20: float | None
    rsi14: float | None
    macd: float | None
    macd_signal: float | None


def _sma(values: List[float], period: int) -> List[float | None]:
    out: List[float | None] = []
    window_sum = 0.0
    for idx, value in enumerate(values):
        window_sum += value
        if idx >= period:
            window_sum -= values[idx - period]
        if idx + 1 >= period:
            out.append(window_sum / period)
        else:
            out.append(None)
    return out


def _ema(values: List[float], period: int) -> List[float | None]:
    out: List[float | None] = []
    k = 2 / (period + 1)
    ema = None
    for idx, value in enumerate(values):
        if ema is None:
            ema = value
        else:
            ema = (value - ema) * k + ema
        out.append(ema if idx + 1 >= period else None)
    return out


def _rsi(values: List[float], period: int) -> List[float | None]:
    out: List[float | None] = [None]
    gains = []
    losses = []

    for idx in range(1, len(values)):
        change = values[idx] - values[idx - 1]
        gains.append(max(change, 0))
        losses.append(max(-change, 0))

        if idx < period:
            out.append(None)
            continue

        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        if avg_loss == 0:
            out.append(100.0)
        else:
            rs = avg_gain / avg_loss
            out.append(100 - (100 / (1 + rs)))

    return out


def _macd(values: List[float]) -> tuple[List[float | None], List[float | None]]:
    ema12 = _ema(values, 12)
    ema26 = _ema(values, 26)
    macd_line: List[float | None] = []
    for v12, v26 in zip(ema12, ema26):
        if v12 is None or v26 is None:
            macd_line.append(None)
        else:
            macd_line.append(v12 - v26)

    signal = _ema([v if v is not None else 0.0 for v in macd_line], 9)
    signal = [s if macd_line[idx] is not None else None for idx, s in enumerate(signal)]
    return macd_line, signal


def calculate_indicators(candles: List[Candle]) -> List[IndicatorPoint]:
    closes = [c.close for c in candles]

    sma20 = _sma(closes, 20)
    sma50 = _sma(closes, 50)
    ema20 = _ema(closes, 20)
    rsi14 = _rsi(closes, 14)
    macd_line, macd_signal = _macd(closes)

    return [
        IndicatorPoint(
            candle=candle,
            sma20=sma20[idx],
            sma50=sma50[idx],
            ema20=ema20[idx],
            rsi14=rsi14[idx],
            macd=macd_line[idx],
            macd_signal=macd_signal[idx],
        )
        for idx, candle in enumerate(candles)
    ]
