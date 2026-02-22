"""
Markowitz Portfolio using Angle One Smart API.

Fetches historical daily data from Angle One, computes returns,
and runs mean-variance optimization (min variance & max Sharpe).
"""

from datetime import datetime, timedelta
from typing import List

import pandas as pd
import json 

# Use existing session helpers
try:
    import creds
except ImportError:
    creds = None

from SmartApi import SmartConnect
import pyotp

try:
    from .markowitz_optimizer import (
        expected_returns_and_covariance,
        min_variance_portfolio,
        max_sharpe_portfolio,
        efficient_frontier,
        optimal_weights_df,
    )
except ImportError:
    from markowitz_optimizer import (
        expected_returns_and_covariance,
        min_variance_portfolio,
        max_sharpe_portfolio,
        efficient_frontier,
        optimal_weights_df,
    )


def get_session():
    """Create Smart API session using creds (or raise if creds not available)."""
    if creds is None:
        raise ImportError("creds.py is required (api_key, client_code, client_pin, totp_code)")
    smart_api = SmartConnect(creds.api_key)
    totp = pyotp.TOTP(creds.totp_code).now()
    data = smart_api.generateSession(creds.client_code, creds.client_pin, totp)
    if not data.get("status") or "data" not in data:
        raise RuntimeError(f"Session failed: {data}")
    return smart_api, data["data"]["refreshToken"]


def get_symbol_token(smart_api, exchange: str, symbol: str) -> str:
    """Resolve trading symbol to symboltoken via searchScrip."""
    result = smart_api.searchScrip(exchange, symbol)
    if not result.get("data") or not result["data"]:
        raise ValueError(f"No scrip found for exchange={exchange}, symbol={symbol}")
    return str(result["data"][0]["symboltoken"])


def fetch_candle_data(
    smart_api,
    exchange: str,
    tradingsymbol: str,
    symboltoken: str,
    from_date: str,
    to_date: str,
    interval: str = "ONE_DAY",
) -> pd.DataFrame:
    """
    Fetch OHLCV candle data and return DataFrame with datetime index and 'close' column.
    """
    param = {
        "exchange": exchange,
        "tradingsymbol": tradingsymbol,
        "symboltoken": symboltoken,
        "interval": interval,
        "fromdate": from_date,
        "todate": to_date,
    }
    resp = smart_api.getCandleData(param)
    if not resp.get("data"):
        return pd.DataFrame()
    data = pd.DataFrame(resp["data"])
    data = data.rename(columns={0: "timestamp", 1: "open", 2: "high", 3: "low", 4: "close", 5: "volume"})
    # Angle One may return timestamp in ms, seconds, or ISO string
    try:
        data["datetime"] = pd.to_datetime(data["timestamp"], unit="ms")
    except (ValueError, TypeError):
        data["datetime"] = pd.to_datetime(data["timestamp"])
    data = data.set_index("datetime").sort_index()
    return data[["close"]]


def fetch_historical_returns(
    smart_api,
    symbols: List[str],
    exchange: str = "NSE",
    years_back: float = 2.0,
    interval: str = "ONE_DAY",
) -> pd.DataFrame:
    """
    Fetch daily close data for each symbol and build a DataFrame of daily returns.
    Symbols should be trading symbols e.g. ["SBIN-EQ", "RELIANCE-EQ", "TCS-EQ"].

    Returns:
        DataFrame: index = date, columns = symbol, values = daily log returns (or simple returns).
    """
    to_dt = datetime.now()
    from_dt = to_dt - timedelta(days=max(1, int(365 * years_back)))
    from_str = from_dt.strftime("%Y-%m-%d 09:15")
    to_str = to_dt.strftime("%Y-%m-%d 15:30")

    closes = {}
    for sym in symbols:
        try:
            token = get_symbol_token(smart_api, exchange, sym)
            df = fetch_candle_data(smart_api, exchange, sym, token, from_str, to_str, interval)
            if df.empty or len(df) < 2:
                continue
            closes[sym] = df["close"]
        except Exception as e:
            print(f"Skip {sym}: {e}")
            continue

    if not closes:
        raise ValueError("No historical data fetched for any symbol.")

    price_df = pd.DataFrame(closes).sort_index().ffill().bfill()
    # Daily simple returns (percentage change)
    returns_df = price_df.pct_change().dropna()
    return returns_df


def build_markowitz_portfolio(
    symbols: List[str],
    exchange: str = "NSE",
    years_back: float = 2.0,
    risk_free_rate: float = 0.07,
    max_sharpe_only: bool = False,
) -> dict:
    """
    Build Markowitz-optimal portfolio using Angle One historical data.

    Args:
        symbols: List of trading symbols (e.g. ["SBIN-EQ", "RELIANCE-EQ", "TCS-EQ"]).
        exchange: Exchange code (default NSE).
        years_back: Years of history for returns/covariance.
        risk_free_rate: Annual risk-free rate for Sharpe ratio (e.g. 0.07 = 7%).
        max_sharpe_only: If True, only compute max-Sharpe weights; else also min-variance.

    Returns:
        dict with:
          - returns_df: daily returns DataFrame
          - symbols_used: list of symbols that had data
          - min_variance: { weights, expected_return, volatility } or None
          - max_sharpe: { weights, expected_return, volatility, sharpe_ratio }
          - efficient_frontier: { volatilities, returns } (optional)
    """
    smart_api, _ = get_session()
    returns_df = fetch_historical_returns(smart_api, symbols, exchange=exchange, years_back=years_back)
    symbols_used = list(returns_df.columns)
    if len(symbols_used) < 2:
        raise ValueError("Need at least 2 symbols with historical data for Markowitz optimization.")

    mu, cov = expected_returns_and_covariance(returns_df)

    out = {
        "returns_df": returns_df,
        "symbols_used": symbols_used,
        "min_variance": None,
        "max_sharpe": None,
        "efficient_frontier": None,
    }

    # Min variance portfolio (no short selling)
    try:
        w_mv, ret_mv, vol_mv = min_variance_portfolio(mu, cov)
        out["min_variance"] = {
            "weights": w_mv,
            "expected_return": ret_mv,
            "volatility": vol_mv,
        }
    except Exception as e:
        print(f"Min variance optimization failed: {e}")

    # Max Sharpe portfolio
    try:
        w_ms, ret_ms, vol_ms, sharpe_ms = max_sharpe_portfolio(
            mu, cov, risk_free=risk_free_rate, allow_short=False
        )
        out["max_sharpe"] = {
            "weights": w_ms,
            "expected_return": ret_ms,
            "volatility": vol_ms,
            "sharpe_ratio": sharpe_ms,
        }
    except Exception as e:
        print(f"Max Sharpe optimization failed: {e}")

    if not max_sharpe_only:
        try:
            vols, rets = efficient_frontier(mu, cov, n_points=30, allow_short=False)
            out["efficient_frontier"] = {"volatilities": vols, "returns": rets}
        except Exception as e:
            print(f"Efficient frontier failed: {e}")

    return out


def get_optimal_weights_df(result: dict, strategy: str = "max_sharpe") -> pd.DataFrame:
    """
    From build_markowitz_portfolio result, get a DataFrame of symbol -> weight.

    strategy: "max_sharpe" or "min_variance"
    """
    if strategy == "max_sharpe" and result.get("max_sharpe"):
        w = result["max_sharpe"]["weights"]
    elif strategy == "min_variance" and result.get("min_variance"):
        w = result["min_variance"]["weights"]
    else:
        raise ValueError(f"Strategy {strategy} not available in result.")
    return optimal_weights_df(result["symbols_used"], w)


def print_portfolio_summary(result: dict):
    """Print a short summary of the Markowitz result."""
    print("Symbols used:", result["symbols_used"])
    if result.get("min_variance"):
        mv = result["min_variance"]
        print("\n--- Min Variance Portfolio ---")
        print(f"  Expected return (ann.): {mv['expected_return']*100:.2f}%")
        print(f"  Volatility (ann.):     {mv['volatility']*100:.2f}%")
        df_mv = optimal_weights_df(result["symbols_used"], mv["weights"])
        print(df_mv.to_string(index=False))
    if result.get("max_sharpe"):
        ms = result["max_sharpe"]
        print("\n--- Max Sharpe Portfolio ---")
        print(f"  Expected return (ann.): {ms['expected_return']*100:.2f}%")
        print(f"  Volatility (ann.):     {ms['volatility']*100:.2f}%")
        print(f"  Sharpe ratio:          {ms['sharpe_ratio']:.3f}")
        df_ms = optimal_weights_df(result["symbols_used"], ms["weights"])
        print(df_ms.to_string(index=False))


# Example usage when run as script
if __name__ == "__main__":
    # Example symbols (NSE equity)
    SYMBOLS = ["BAJAJHFL","ITC","RPOWER","SUZLON","TATAPOWER","TMCV","TMPV","TRIDENT","UJJIVANSFB"]
    #SYMBOLS = ["NIFTY", "NIFTYBANK", "SENSEX", "NIFTYIT", "NIFTYMIDCAP50", "NIFTYMIDCAP100"]
    result = build_markowitz_portfolio(SYMBOLS, years_back=2.0, risk_free_rate=0.07)
    print_portfolio_summary(result)

