import pandas as pd
import numpy as np
import pyotp
from SmartApi import SmartConnect #or from SmartApi.smartConnect import SmartConnect
# from smartapi import WebSocket
# from smartapi import exceptions
from datetime import datetime, timedelta
import time

import document

# Set your SmartAPI credentials
client_id = document.user_id
access_token = "YOUR_ACCESS_TOKEN"
refresh_token = "YOUR_REFRESH_TOKEN"
api_key = document.api_key
user_id = document.user_id
password = document.password
totp = pyotp.TOTP(document.totp).now()

# Initialize SmartAPI
obj = SmartConnect(api_key=api_key)
# token = obj.generateToken(obj.generateSession(user_id, password, totp)["data"]["refreshToken"])

data = obj.generateSession(user_id, password, totp)
refreshToken = data['data']['refreshToken']
feedToken = obj.getfeedToken()
print(feedToken)
# Set the index you want to trade
index = 'NIFTY 50'

# Set the supertrend parameters
n = 10
m = 2

while True:
    # Get intraday data for the index
    intraday_data = {}
    try:
        intraday_data[index] = obj.getIntraDayCandleData(index, '5minute', datetime.now().strftime('%Y-%m-%d'), datetime.now().strftime('%Y-%m-%d'))
    except Exception as e:
        print("Token is Invalid/Expired. Please generate new token")
        print(str(e))
        exit()

    # Calculate the supertrend for the index
    df = pd.DataFrame(intraday_data[index])
    df['date'] = pd.to_datetime(df['time'], unit='ms')
    df.set_index('date', inplace=True)
    df = df[['open', 'high', 'low', 'close', 'volume']]
    df['ATR'] = pd.DataFrame(pd.concat([df['high'] - df['low'], abs(df['high'] - df['close'].shift()), abs(df['low'] - df['close'].shift())], axis=1).max(axis=1), columns=['ATR'])
    df['upper_band'] = df['high'] - (m * df['ATR'])
    df['lower_band'] = df['low'] + (m * df['ATR'])
    df['in_uptrend'] = True
    for i in range(n, len(df)):
        if df['close'][i] > df['upper_band'][i-1]:
            df['in_uptrend'][i] = True
        elif df['close'][i] < df['lower_band'][i-1]:
            df['in_uptrend'][i] = False
        else:
            df['in_uptrend'][i] = df['in_uptrend'][i-1]
            if (df['in_uptrend'][i-1]) & (df['lower_band'][i] < df['lower_band'][i-1]):
                df['lower_band'][i] = df['lower_band'][i-1]
            if (~df['in_uptrend'][i-1]) & (df['upper_band'][i] > df['upper_band'][i-1]):
                df['upper_band'][i] = df['upper_band'][i-1]
    df['supertrend'] = np.nan
    for i in range(n, len(df)):
        if df['in_uptrend'][i]:
            df['supertrend'][i] = df['lower_band'][i]
        else:
            df['supertrend'][i] = df['upper_band'][i]

    # Place orders for the index
    try:
        ltp = obj.ltpData(index)['data'][0]['lastPrice']
        if df['supertrend'][-1] > ltp:
            order_type = 'SELL'
            order_price = ltp - 0.05*ltp
        else:
            order_type = 'BUY'
            order_price = ltp + 0.05*ltp
        order_quantity = 1
        order_params = {
            "variety": "NORMAL",
            "tradingsymbol": index,
            "symboltoken": obj.getSymbolToken(index),
            "transactiontype": order_type,
            "exchange": "NSE",
            "ordertype": "LIMIT",
            "producttype": "INTRADAY",
            "duration": "DAY",
            "price": order_price,
            "quantity": order_quantity
        }
        # print(obj.placeOrder(orderReceived message. Yes,)
    except Exception as e:
        print("error: {}".format(e))
        bot_message = f"error when exit {e}"
