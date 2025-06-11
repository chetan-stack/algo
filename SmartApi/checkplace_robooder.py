
from SmartApi import SmartConnect #or from SmartApi.smartConnect import SmartConnect
import time
from datetime import datetime,timedelta
import datetime
import pandas_ta as ta
import pandas as pd
import numpy as np
import os
import sys
import pyotp
import schedule
import math
import requests

import document


api_key = document.api_key
user_id = document.user_id
password = document.password
totp = pyotp.TOTP(document.totp).now()
obj = SmartConnect(api_key=api_key)
token = obj.generateToken(obj.generateSession(user_id, password, totp)["data"]["refreshToken"])



def getorderBook():
    tradebook = obj.position()
    #if len(selltradednity) > 0 or len(buytradedBANKNIFTY) > 0:
    if tradebook['data'] is not None:
        filtered_data = [item for item in tradebook['data'] if item['symbolname'] == 'BANKNIFTY']
        # print(filtered_data[-1]['tradingsymbol'])
        last_item = filtered_data[-1]  # Accessing the last item in the filtered list
        if last_item and last_item['symbolname'] == 'BANKNIFTY' and last_item['netqty'] != '0':
            return False
        else:
            return True
    else:
        return True





def GettingLtpData(script, token, order):
    exchange = "NSE"
    current_date_time = datetime.datetime.now()
    form_date = current_date_time - timedelta(days=10)

    api_key = document.api_key
    user_id = document.user_id
    password = document.password
    totp = pyotp.TOTP(document.totp).now()


    # print(feedToken)

    obj = SmartConnect(api_key=api_key)
    tokens = obj.generateToken(obj.generateSession(user_id, password, totp)["data"]["refreshToken"])
    jwtToken = tokens['data']["jwtToken"]
    refreshToken = tokens['data']['refreshToken']
    feedToken = tokens['data']['feedToken']
    print(token)

    LTP = obj.ltpData(exchange, script, token)
#     print(LTP)
    ltp = LTP["data"]["ltp"]
    # quantity = int(per_trade_fund / ltp)
    # quantity = int(per_trade_fund * 10 / ltp)
    quantity = 1


    orderparams = {
        "variety": "ROBO",
        "tradingsymbol": script,
        "symboltoken": token,
        "transactiontype": order,
        "exchange": exchange,
        "ordertype": "LIMIT",
        "producttype": "INTRADAY",
        "duration": "DAY",
        "price": ltp,
        "squareoff": "2",
        "stoploss": "2",
        "quantity": quantity
    }

    if True:
        orderId = obj.placeOrder(orderparams)
        print(
                f"{order} order Place for {script} at : {datetime.datetime.now()} with Order id {orderId}"
            )

print(getorderBook())

