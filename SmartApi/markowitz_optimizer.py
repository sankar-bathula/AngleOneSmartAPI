"""
Markowitz Portfolio Theory - Mean-Variance Optimization.

Given historical returns, computes:
- Expected returns (mean) and covariance matrix
- Minimum variance portfolio
- Maximum Sharpe ratio portfolio (tangency portfolio)
- Efficient frontier (risk vs return)
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from typing import Tuple, Optional


def expected_returns_and_covariance(returns: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute annualized expected returns (mean) and covariance matrix from daily returns.

    Args:
        returns: DataFrame with assets as columns, dates as index; values = daily returns.

    Returns:
        mu: Annualized expected returns (vector).
        cov: Annualized covariance matrix (square).
    """
    # 252 trading days per year for annualization
    trading_days = 252
    mu = returns.mean(axis=0).values * trading_days
    cov = returns.cov().values * trading_days
    return mu, cov


def portfolio_return(weights: np.ndarray, mu: np.ndarray) -> float:
    """Portfolio expected return: w' * mu."""
    return np.dot(weights, mu)


def portfolio_volatility(weights: np.ndarray, cov: np.ndarray) -> float:
    """Portfolio volatility (annualized): sqrt(w' * Cov * w)."""
    return np.sqrt(np.dot(weights.T, np.dot(cov, weights)))


def portfolio_sharpe(weights: np.ndarray, mu: np.ndarray, cov: np.ndarray, risk_free: float = 0.07) -> float:
    """Sharpe ratio (annualized). risk_free = annual risk-free rate (e.g. 7% = 0.07)."""
    ret = portfolio_return(weights, mu)
    vol = portfolio_volatility(weights, cov)
    if vol <= 0:
        return 0.0
    return (ret - risk_free) / vol


def _weight_constraint_sum_one(x: np.ndarray) -> float:
    """Constraint: weights sum to 1."""
    return np.sum(x) - 1.0


def min_variance_portfolio(mu: np.ndarray, cov: np.ndarray) -> Tuple[np.ndarray, float, float]:
    """
    Minimum variance portfolio (no short selling).

    Returns:
        weights: Optimal weights (sum = 1, all >= 0).
        expected_return: Portfolio expected return.
        volatility: Portfolio volatility.
    """
    n = len(mu)
    bounds = [(0.0, 1.0)] * n
    constraints = [{"type": "eq", "fun": _weight_constraint_sum_one}]

    def neg_vol(w):
        return portfolio_volatility(w, cov)

    result = minimize(
        neg_vol,
        x0=np.ones(n) / n,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
    )
    if not result.success:
        raise ValueError(f"Min variance optimization failed: {result.message}")
    w = result.x
    return w, portfolio_return(w, mu), portfolio_volatility(w, cov)


def max_sharpe_portfolio(
    mu: np.ndarray,
    cov: np.ndarray,
    risk_free: float = 0.07,
    allow_short: bool = False,
) -> Tuple[np.ndarray, float, float, float]:
    """
    Maximum Sharpe ratio portfolio (tangency portfolio).

    Args:
        mu: Expected returns.
        cov: Covariance matrix.
        risk_free: Annual risk-free rate.
        allow_short: If False, weights are constrained to [0, 1].

    Returns:
        weights: Optimal weights.
        expected_return: Portfolio expected return.
        volatility: Portfolio volatility.
        sharpe: Sharpe ratio.
    """
    n = len(mu)
    if allow_short:
        bounds = [(-1.0, 1.0)] * n
    else:
        bounds = [(0.0, 1.0)] * n
    constraints = [{"type": "eq", "fun": _weight_constraint_sum_one}]

    def neg_sharpe(w):
        return -portfolio_sharpe(w, mu, cov, risk_free)

    result = minimize(
        neg_sharpe,
        x0=np.ones(n) / n,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
    )
    if not result.success:
        raise ValueError(f"Max Sharpe optimization failed: {result.message}")
    w = result.x
    ret = portfolio_return(w, mu)
    vol = portfolio_volatility(w, cov)
    sharpe = portfolio_sharpe(w, mu, cov, risk_free)
    return w, ret, vol, sharpe


def efficient_frontier(
    mu: np.ndarray,
    cov: np.ndarray,
    n_points: int = 50,
    allow_short: bool = False,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute efficient frontier: (volatility, return) for a range of target returns.

    Returns:
        volatilities: Array of length n_points.
        returns_arr: Array of length n_points.
    """
    _, min_ret, _ = min_variance_portfolio(mu, cov)
    max_ret = np.max(mu)
    target_returns = np.linspace(min_ret, max_ret, n_points)

    n = len(mu)
    if allow_short:
        bounds = [(-1.0, 1.0)] * n
    else:
        bounds = [(0.0, 1.0)] * n

    volatilities = []
    returns_list = []

    for target in target_returns:
        constraints = [
            {"type": "eq", "fun": _weight_constraint_sum_one},
            {"type": "eq", "fun": lambda w, t=target: portfolio_return(w, mu) - t},
        ]
        result = minimize(
            lambda w: portfolio_volatility(w, cov),
            x0=np.ones(n) / n,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
        )
        if result.success:
            vol = portfolio_volatility(result.x, cov)
            ret = portfolio_return(result.x, mu)
            volatilities.append(vol)
            returns_list.append(ret)
        else:
            volatilities.append(np.nan)
            returns_list.append(np.nan)

    return np.array(volatilities), np.array(returns_list)


def optimal_weights_df(
    symbols: list,
    weights: np.ndarray,
) -> pd.DataFrame:
    """Build a DataFrame of symbol -> weight for display or rebalancing."""
    return pd.DataFrame({"symbol": symbols, "weight": weights}).sort_values("weight", ascending=False)
