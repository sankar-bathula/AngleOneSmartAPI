import pandas as pd
import yfinance as yf
import requests

# -----------------------------
# STEP 1: Get NIFTY 100 list
# -----------------------------
url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20100"

headers = {
    "User-Agent": "Mozilla/5.0"
}

session = requests.Session()
response = session.get(url, headers=headers)
data = response.json()

symbols = [stock["symbol"] for stock in data["data"]]
tickers = [s + ".NS" for s in symbols]

print(f"Total stocks fetched: {len(tickers)}")


# -----------------------------
# STEP 2: Fetch sector + mcap
# -----------------------------
records = []

for ticker in tickers:
    print("Processing:", ticker)
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        records.append({
            "ticker": ticker,
            "sector": info.get("sector", "Unknown"),
            "market_cap": info.get("marketCap", 0)
        })

    except Exception as e:
        print("Error:", e)

df = pd.DataFrame(records)

# Remove invalid rows
df = df[df["market_cap"] > 0]


# -----------------------------
# STEP 3: Get Top stocks by sector
# -----------------------------
top_per_sector = (
    df.sort_values(["sector", "market_cap"], ascending=[True, False])
      .groupby("sector")
      .head(5)  # Top 5 per sector
)

print(top_per_sector)


# -----------------------------
# STEP 4: If you want top 100 overall but sector balanced
# -----------------------------
sector_counts = 10  # adjust per sector

balanced_top = (
    df.sort_values(["sector", "market_cap"], ascending=[True, False])
      .groupby("sector")
      .head(sector_counts)
)

# Limit to 100 stocks max
balanced_top = balanced_top.head(100)

print("\nFinal Top Stocks:")
print(balanced_top)
with pd.ExcelWriter("Data\\top_stocks.xlsx") as writer:
    top_per_sector.to_excel(writer, sheet_name="Top per Sector")
    balanced_top.to_excel(writer, sheet_name="Balanced Top 100")