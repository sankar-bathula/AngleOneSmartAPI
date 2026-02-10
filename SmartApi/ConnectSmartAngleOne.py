import pyotp
import creds
from SmartApi import SmartConnect
import pandas as pd

def Generate_TOTP():
	totp = pyotp.TOTP(creds.totp_code)
	print(totp.now())
	return totp.now()


def Generate_Session():
	smartApi = SmartConnect(creds.api_key)
	data = smartApi.generateSession(creds.client_code, creds.client_pin, Generate_TOTP())
	authToken = data['data']['jwtToken']
	refreshToken = data['data']['refreshToken']
	return(smartApi, refreshToken)


smartApi, refreshToken = Generate_Session()
	