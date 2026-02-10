from datetime import datetime, timedelta
from SmartApi import SmartConnect #or from SmartApi.smartConnect import SmartConnect
import pyotp
from logzero import logger
import pandas as pd

api_key = '6ybPZHNp'
username = 'B352053'
pwd = '9046'
smartApi = SmartConnect(api_key)
try:
    token = "H6D2W7QO7EEG3JOKCVVZVZIQYQ"
    totp = pyotp.TOTP(token).now()
except Exception as e:
    logger.error("Invalid Token: The provided token is not valid.")
    raise e

correlation_id = "abcde"
obj = smartApi.generateSession(username, pwd, totp)
print(obj)

def get_day_trader(symbol,token,interval,fromdate,todate):
    try: 
        historicParam = {
        "exchange": "NSE",
        "tradingsymbol": symbol,
        "symboltoken": token,
        "interval": interval,
        "fromdate": fromdate,
        "todate": todate
        }
        # Use the SmartConnect client to fetch candle data
        data = smartApi.getCandleData(historicParam)['data']
        data = pd.DataFrame(data)
        data = data.rename(columns={0: "timestamp", 1: "open", 2: "high", 3: "low", 4: "close", 5: "volume"})
        # SmartAPI typically returns ISO-format timestamps, so no explicit unit is needed here
        data["datetime"] = pd.to_datetime(data["timestamp"])
        data = data.set_index("datetime")
        print(data)
        return data
    except Exception as e:
        logger.error("Error in getting day trader: %s", e)
        return None

daily_data = get_day_trader("SBIN-EQ","3045","FIVE_MINUTE","29-01-2026 09:15", "30-01-2026 15:30")
df_daily_data = pd.DataFrame(daily_data)
print(df_daily_data)