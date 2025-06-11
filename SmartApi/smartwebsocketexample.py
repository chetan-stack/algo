# -*- coding: utf-8 -*-
"""
Created on Wed May 26 18:50:44 2021

@author: Sandip.Khairnar
"""

from smartApiWebsocket import SmartWebSocket
import pyotp
import document
from SmartApi import SmartConnect #or from SmartApi.smartConnect import SmartConnect

api_key = document.api_key
user_id = document.user_id
password = document.password
totp = pyotp.TOTP(document.totp).now()
obj = SmartConnect(api_key=api_key)
token = obj.generateToken(obj.generateSession(user_id, password, totp)["data"]["refreshToken"])

AUTH_TOKEN = token["data"]["jwtToken"]
API_KEY = api_key
CLIENT_CODE = user_id
FEED_TOKEN = token["data"]["refreshToken"]

# feed_token=092017047

# token="mcx_fo|224395"
token="nse_cm|2885&nse_cm|1594&nse_cm|11536&nse_cm|3045"
# token="mcx_fo|226745&mcx_fo|220822&mcx_fo|227182&mcx_fo|221599"
task="mw"
ss = SmartWebSocket(FEED_TOKEN, CLIENT_CODE)
print(ss)
def on_message(ws, message):
    print("Ticks: {}".format(message))
    
def on_open(ws):
    print("on open")
    ss.subscribe(task,token)
    
def on_error(ws, error):
    print(error)
    
def on_close(ws):
    print("Close")

# Assign the callbacks.
ss._on_open = on_open
ss._on_message = on_message
ss._on_error = on_error
ss._on_close = on_close

ss.connect()
