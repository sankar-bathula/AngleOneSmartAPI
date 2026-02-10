import pyotp
import creds
from SmartApi import SmartConnect
import pandas as pd

def Generate_TOTP():
	totp = pyotp.TOTP(creds.totp_code)
	return totp.now()


def Generate_Session():
	smartApi = SmartConnect(creds.api_key)
	data = smartApi.generateSession(creds.client_code, creds.client_pin, Generate_TOTP())
	authToken = data['data']['jwtToken']
	refreshToken = data['data']['refreshToken']
	return(smartApi, refreshToken)


smartApi, refreshToken = Generate_Session()

# Get Profile

profile = smartApi.getProfile(refreshToken)
print(profile['data']['exchanges'])

#Get order book
orderbook = smartApi.orderBook()
holdings = smartApi.holding()
tradebook = smartApi.tradeBook()
allholdings = smartApi.allholding()
print(allholdings)