from nsetools import Nse
import pandas as pd

nse = Nse()

# Get top gainers
gainers = nse.get_top_gainers()
df_gainers = pd.DataFrame(gainers)
print("Top Gainers:")
print(df_gainers)

# Get top losers
losers = nse.get_top_losers()
df_losers = pd.DataFrame(losers)
print("Top Losers:")
print(df_losers)
