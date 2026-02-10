import pyotp
import creds
from SmartApi import SmartConnect
import pandas as pd

#Get OTP
def Generate_TOTP():
	totp = pyotp.TOTP(creds.totp_code)
	return totp.now()

# Connect to the Smart API session 
def Generate_Session():
	smartApi = SmartConnect(creds.api_key)
	data = smartApi.generateSession(creds.client_code, creds.client_pin, Generate_TOTP())
	authToken = data['data']['jwtToken']
	refreshToken = data['data']['refreshToken']
	return(smartApi, refreshToken)

# Generate symbol of taken by providing stock name 
def Generate_tokens(exchange, symbol):
	token = smartApi.searchScrip(exchange, symbol)
	symboltoken = token['data'][0]['symboltoken']
	print(symboltoken)
	return(symboltoken)

smartApi, refreshToken = Generate_Session()

exchange = "NSE"
symbol = "BEL-EQ"
token = Generate_tokens(exchange, symbol)
print(token)

#Get Last Trade Price
ltplist = smartApi.ltpData(exchange, symbol, token)
ltp = ltplist['data']['ltp'] 
print(ltp)

# place order 
oderParameters = {
	"variety":"NORMAL",
	"tradingsymbol":symbol,
	"symboltoken":token,
	"transactiontype":"BUY",
	"exchange":exchange,
	"ordertype":"MARKET",
	"producttype":"DELIVERY",
	"duration":"DAY",
	"price":ltp,
	"squareoff":"0",
	"stoploss":"0",
	"quantity":"1",
	"scripconsent":"yes"
	}

order_place = smartApi.placeOrder(oderParameters)
print(order_place)


