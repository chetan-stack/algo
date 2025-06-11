from SmartApi import SmartConnect  # or from SmartApi.smartConnect import SmartConnect
from datetime import datetime, timedelta
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
import time
from tvDatafeed import TvDatafeed, Interval
import crete_update_table
import json
import getoptionchain


# api_key = document.api_key
# user_id = document.user_id
# password = document.password
# totp = pyotp.TOTP(document.totp).now()
# obj = SmartConnect(api_key=api_key)
# token = obj.generateToken(obj.generateSession(user_id, password, totp)["data"]["refreshToken"])
#
# current_date_time = datetime.datetime.now() - timedelta(days=1)
# form_date = current_date_time - timedelta(days=10)

def gethistoricalldata(symbol,token):
    current_date_time = datetime.datetime.now()
    form_date = current_date_time - timedelta(days=10)

    api_key = document.api_key
    user_id = document.user_id
    password = document.password
    totp = pyotp.TOTP(document.totp).now()

    try:
        obj = SmartConnect(api_key=api_key)
        token = obj.generateToken(obj.generateSession(user_id, password, totp)["data"]["refreshToken"])
        jwtToken = token['data']["jwtToken"]
        refreshToken = token['data']['refreshToken']
        feedToken = token['data']['feedToken']
        historicParam = {
            "exchange": 'NFO',
            "symboltoken": '65467',
            "interval": "FIVE_MINUTE",
            "fromdate": form_date.strftime("%Y-%m-%d 09:15"),
            "todate": current_date_time.strftime("%Y-%m-%d %H:%M")
        }
        hist_data = obj.getCandleData(historicParam)["data"]
        print(hist_data)

        if hist_data:
            df = pd.DataFrame(
                hist_data,
                columns=['date', 'open', 'high', 'low', 'close', 'volume'])
            df["sup"] = ta.supertrend(df['high'], df['low'], df['close'], length=10, multiplier=2)['SUPERT_10_2.0']
            df["ema"] = ta.ema(df["close"], length=9)
            df['stx'] = np.where((df['sup'] > 0.00), np.where((df['close'] > df['sup']), 'up', 'down'), np.NaN)
            df['Candle_Color'] = 1  # Initialize with a value indicating green candles
            df.loc[df['close'] < df['open'], 'Candle_Color'] = 0
            if df.close.values[-1] > df.ema.values[-1] and df.close.values[-1] > df.open.values[-1]:
                return True
            else:
                 return False
        else:
            return False

    except Exception as e:
        print('error',e)

def checkexitconditio(symbol,token):
    current_date_time = datetime.datetime.now()
    form_date = current_date_time - timedelta(days=10)

    api_key = document.api_key
    user_id = document.user_id
    password = document.password
    totp = pyotp.TOTP(document.totp).now()

    try:
        obj = SmartConnect(api_key=api_key)
        token = obj.generateToken(obj.generateSession(user_id, password, totp)["data"]["refreshToken"])
        jwtToken = token['data']["jwtToken"]
        refreshToken = token['data']['refreshToken']
        feedToken = token['data']['feedToken']
        historicParam = {
            "exchange": 'NFO',
            "symboltoken": token,
            "interval": "FIVE_MINUTE",
            "fromdate": form_date.strftime("%Y-%m-%d 09:15"),
            "todate": current_date_time.strftime("%Y-%m-%d %H:%M")
        }
        hist_data = obj.getCandleData(historicParam)["data"]
        print(hist_data)

        if hist_data:
            df = pd.DataFrame(
                hist_data,
                columns=['date', 'open', 'high', 'low', 'close', 'volume'])
            df["sup"] = ta.supertrend(df['high'], df['low'], df['close'], length=10, multiplier=1)['SUPERT_10_1.0']
            df["ema"] = ta.ema(df["close"], length=9)
            df['stx'] = np.where((df['sup'] > 0.00), np.where((df['close'] > df['sup']), 'up', 'down'), np.NaN)
            df['Candle_Color'] = 1  # Initialize with a value indicating green candles
            df.loc[df['close'] < df['open'], 'Candle_Color'] = 0
            if df.close.values[-2] > df.ema.values[-2] or df.close.values[-1] < df.ea.values[-1]:
                return True
            else:
                 return False

    except Exception as e:
        print('error',e)


#print(gethistoricalldata('main','mainn'))
