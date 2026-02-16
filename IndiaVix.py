"""
High VIX → Avoid selling naked options

Falling VIX + Rising Nifty → Strong bullish trend

Rising VIX + Falling Nifty → Fear move

Low VIX + Sideways Nifty → Range-bound market

High VIX + Sideways Nifty → Volatile market

Low VIX + Falling Nifty → Bearish trend

Low VIX + Rising Nifty → Bullish trend

VIX < 15 → Calm market

VIX > 20 → Volatile market

VIX > 30 → Fear market

VIX > 40 → Panic market

VIX > 50 → Extreme fear market

"""
import requests

url = "https://www.nseindia.com/api/allIndices"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)
data = response.json()

for index in data['data']:
    if index['index'] == "INDIA VIX":
        print(index)
        
