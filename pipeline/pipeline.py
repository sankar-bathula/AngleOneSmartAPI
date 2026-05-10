from __future__ import annotations

from datetime import datetime

from .config import Config, DEFAULT_CONFIG
from .data import fetch_nifty50_data
from .db import count_trades_today, init_db, store_run, store_trade
from .execution import execute_trade
from .indicators import calculate_indicators
from .risk import check_risk_rules
from .signal import generate_signal
from .trend import detect_trend


def run_pipeline(config: Config = DEFAULT_CONFIG) -> dict:
    init_db(config.db_path)

    candles = fetch_nifty50_data(config.data_path)
    indicators = calculate_indicators(candles)
    latest = indicators[-1]

    trend = detect_trend(latest)
    signal = generate_signal(latest, trend)

    today_prefix = datetime.utcnow().date().isoformat()
    trades_today = count_trades_today(config.db_path, today_prefix)

    risk = check_risk_rules(config, signal, latest.candle.close, trades_today)
    trade = execute_trade(signal, risk, latest.candle.close)

    store_trade(config.db_path, trade)
    store_run(
        config.db_path,
        run_timestamp=datetime.utcnow().isoformat(),
        latest_close=latest.candle.close,
        trend=trend.trend,
        signal=signal.signal,
        risk_allowed=risk.allowed,
        risk_reason=risk.reason,
    )

    return {
        "latest_date": latest.candle.date.strftime("%Y-%m-%d"),
        "latest_close": latest.candle.close,
        "trend": trend.trend,
        "trend_reason": trend.reason,
        "signal": signal.signal,
        "signal_reason": signal.reason,
        "risk_allowed": risk.allowed,
        "risk_reason": risk.reason,
        "trade_status": trade.status,
        "trade_message": trade.message,
    }
