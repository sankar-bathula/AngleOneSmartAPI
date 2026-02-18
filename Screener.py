import pandas as pd
import yfinance as yf
import requests
import numpy as np
from datetime import datetime

# ----------------------------
# STEP 1: Get NIFTY 100 Stocks
# ----------------------------
def get_nifty100():
    url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20100"
    headers = {"User-Agent": "Mozilla/5.0"}
    session = requests.Session()
    response = session.get(url, headers=headers)
    data = response.json()
    symbols = [stock["symbol"] for stock in data["data"]]
    return [s + ".NS" for s in symbols]

# ----------------------------
# STEP 2: Fetch Stock Data
# ----------------------------
def fetch_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="1y")

        if hist.empty:
            return None

        hist["50DMA"] = hist["Close"].rolling(50).mean()
        hist["200DMA"] = hist["Close"].rolling(200).mean()

        latest = hist.iloc[-1]
        price = latest["Close"]
        dma50 = latest["50DMA"]
        dma200 = latest["200DMA"]

        six_month_return = (
            (hist["Close"].iloc[-1] - hist["Close"].iloc[-126])
            / hist["Close"].iloc[-126]
        ) * 100 if len(hist) > 126 else None

        return {
            "ticker": ticker,
            "sector": info.get("sector", "Unknown"),
            "market_cap": info.get("marketCap", 0),
            "roe": info.get("returnOnEquity", 0),
            "de_ratio": info.get("debtToEquity", 0),
            "free_cash_flow": info.get("freeCashflow", 0),
            "price": price,
            "dma50": dma50,
            "dma200": dma200,
            "six_month_return": six_month_return
        }

    except:
        return None

# ----------------------------
# MAIN SCREENING LOGIC
# ----------------------------
def run_screener():

    print("Fetching Nifty 100 stocks...")
    tickers = get_nifty100()

    print("Downloading stock data...")
    records = []

    for ticker in tickers:
        print("Processing:", ticker)
        data = fetch_stock_data(ticker)
        if data:
            records.append(data)

    df = pd.DataFrame(records)

    # Remove invalid rows
    df = df[df["market_cap"] > 0]

    # ----------------------------
    # STEP 3: Sector Rotation
    # ----------------------------
    sector_returns = (
        df.groupby("sector")["six_month_return"]
        .mean()
        .sort_values(ascending=False)
    )

    top_sectors = sector_returns.head(3).index.tolist()
    print("\nTop Sectors:", top_sectors)

    df = df[df["sector"].isin(top_sectors)]

    # ----------------------------
    # STEP 4: Long-Term Filters
    # ----------------------------
    df = df[
        (df["roe"] > 0.15) &
        (df["de_ratio"] < 100) &  # yfinance gives % format
        (df["free_cash_flow"] > 0)
    ]

    # ----------------------------
    # STEP 5: Momentum Confirmation
    # ----------------------------
    df = df[
        (df["price"] > df["dma200"]) &
        (df["dma50"] > df["dma200"])
    ]

    # ----------------------------
    # STEP 6: Final Ranking
    # ----------------------------
    df["score"] = (
        df["six_month_return"] * 0.5 +
        df["roe"] * 100 * 0.3 +
        (1 / (df["de_ratio"] + 1)) * 0.2
    )

    df = df.sort_values("score", ascending=False)

    return df


# ----------------------------
# RUN
# ----------------------------
if __name__ == "__main__":
    results = run_screener()
    print("\nFinal Selected Stocks:\n")
    print(results[["ticker", "sector", "six_month_return", "roe", "score"]])
