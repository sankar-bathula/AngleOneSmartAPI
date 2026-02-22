# Markowitz Portfolio with Angle One Smart API

This module builds **mean-variance (Markowitz) portfolios** using historical data from the Angle One Smart API.

## Theory

- **Expected returns**: Annualized mean of daily returns.
- **Covariance**: Annualized covariance matrix of daily returns.
- **Minimum variance portfolio**: Weights that minimize portfolio volatility (no short selling).
- **Maximum Sharpe portfolio**: Weights that maximize (return − risk-free rate) / volatility.
- **Efficient frontier**: Set of portfolios that maximize return for each level of risk.

## Files

- `markowitz_optimizer.py` – Core math: expected returns, covariance, min variance, max Sharpe, efficient frontier.
- `markowitz_portfolio_angleone.py` – Fetches daily data from Angle One, runs optimizer, returns weights and metrics.

## Usage

### 1. From code

```python
from SmartApi.markowitz_portfolio_angleone import (
    build_markowitz_portfolio,
    get_optimal_weights_df,
    print_portfolio_summary,
)

# NSE symbols (use -EQ for equity)
symbols = ["SBIN-EQ", "RELIANCE-EQ", "TCS-EQ", "INFY-EQ", "HDFCBANK-EQ"]

result = build_markowitz_portfolio(
    symbols,
    exchange="NSE",
    years_back=2.0,
    risk_free_rate=0.07,   # 7% for Sharpe
    max_sharpe_only=False,
)

print_portfolio_summary(result)

# Weights as DataFrame (e.g. for rebalancing)
weights_df = get_optimal_weights_df(result, strategy="max_sharpe")
print(weights_df)
```

### 2. Run as script

From project root or `SmartApi` folder:

```bash
cd AngleOneSmartAPI
python -m SmartApi.markowitz_portfolio_angleone
# or
cd SmartApi && python markowitz_portfolio_angleone.py
```

Edit the `SYMBOLS` list at the bottom of `markowitz_portfolio_angleone.py` before running.

### 3. Use optimizer with your own returns

If you have a returns DataFrame (dates × assets):

```python
from SmartApi.markowitz_optimizer import (
    expected_returns_and_covariance,
    min_variance_portfolio,
    max_sharpe_portfolio,
    optimal_weights_df,
)
import pandas as pd

returns = pd.read_csv("daily_returns.csv", index_col=0, parse_dates=True)
mu, cov = expected_returns_and_covariance(returns)
w_minvar, r, v = min_variance_portfolio(mu, cov)
w_sharpe, r, v, s = max_sharpe_portfolio(mu, cov, risk_free=0.07)
```

## Requirements

- `creds.py` in `SmartApi` with: `api_key`, `client_code`, `client_pin`, `totp_code`.
- Packages: `pandas`, `numpy`, `scipy`, `pyotp`, SmartApi.

## Notes

- Historical data is fetched via `getCandleData` with `ONE_DAY` interval; symbol tokens are resolved with `searchScrip`.
- Weights are constrained to long-only (no short selling) by default.
- Risk-free rate is used only for the Sharpe ratio; change `risk_free_rate` to match your assumption (e.g. 7% = 0.07).
