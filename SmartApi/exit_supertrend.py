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

import document

current_date_time = datetime.datetime.now() - timedelta(days = 1)
form_date = current_date_time - timedelta(days = 10)

print("current tym",current_date_time)

script_list = {
    "ADANIPORTS-EQ": "15083",
    'ADANIENT-EQ': '25',
    'APOLLOHOSP-EQ': '157',
    "BANKBARODA-EQ": "4668",
    'TITAN-EQ': '3506',
    "BAJAJFINSV-EQ": "16675",
    "DIVISLAB-EQ": "10940",
    'HINDALCO-EQ': '1363',

};

buy_traded_stock = []
sell_traded_stock = []

exchange = "NSE"
per_trade_fund = 10000
ma_short = 13
ma_long = 22
runcount = 0

def GettingLtpData(script, token, order):
    LTP = obj.ltpData(exchange, script, token)
#     print(LTP)
    ltp = LTP["data"]["ltp"]
    # quantity = int(per_trade_fund / ltp)
    quantity = 1

    orderparams = {
        "variety": "NORMAL",
        "tradingsymbol": script,
        "symboltoken": token,
        "transactiontype": order,
        "exchange": exchange,
        "ordertype": "MARKET",
        "producttype": "DELIVERY",
        "duration": "DAY",
        "price": ltp,
        "squareoff": "0",
        "stoploss": "0",
        "quantity": quantity
    }
    orderId = obj.placeOrder(orderparams)
    print(
        f"{order} order Place for {script} at : {datetime.datetime.now()} with Order id {orderId}"
    )

def strategy():
    print('check stetergy')
    global obj

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
        getposition = obj.holding()
        print(getposition, "__________Positions")
        for a in getposition['data']:
            historicParam = {
                "exchange": exchange,
                "symboltoken": a["symboltoken"],
                "interval": "FIVE_MINUTE",
                "fromdate": form_date.strftime("%Y-%m-%d 09:15"),
                "todate": current_date_time.strftime("%Y-%m-%d %H:%M")
            }
            hist_data = obj.getCandleData(historicParam)["data"]
            LTP = obj.ltpData(exchange, a["tradingsymbol"], token)
            ltp = LTP["data"]["ltp"]

            # print(hist_data)
            if hist_data != None:
                df = pd.DataFrame(
                    hist_data,
                    columns=['date', 'open', 'high', 'low', 'close', 'volume'])
                df["sup"] = ta.supertrend(df['high'], df['low'], df['close'], length=10, multiplier=3)['SUPERT_10_3.0']

                df.dropna(inplace=True)
                sup_cl = df.stx.values[-1]
                sup_pre = df.stx.values[-2]
                print("super close = ",sup_cl,"+++++++ pre close = ",sup_pre,"_____________ltp",ltp)


                if not df.empty:
                    if sup_cl or sup_pre == ltp and (a["tradingsymbol"] not in buy_traded_stock):
                        transactionType = "SELL" if int(a['netqty']) > 0 else "BUY"
                        buy_traded_stock.append(a["tradingsymbol"])
                        GettingLtpData(a["tradingsymbol"], token, transactionType)

            time.sleep(1)

    except Exception as e:
        print("Historic Api failed: {}".format(e),format(datetime.datetime.now()))
    try:
        logout = obj.terminateSession(user_id)
        print("Logout Successfull")
    except Exception as e:
        print("Logout failed: {}".format(e))


strategy()
schedule.every(1).minutes.do(strategy)


while True:
        # print("start tym , CURRENT TIME:{}".format(datetime.datetime.now()))
        try:
            schedule.run_pending()
            time.sleep(2)
        except Exception as e:
            raise e
