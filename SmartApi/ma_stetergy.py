from smartapi import SmartConnect
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

current_date_time = datetime.datetime.now()
form_date = current_date_time - timedelta(days = 1)
traded_list_exit = []
print("current tym",current_date_time)
placeOREDR = True
script_list = {
    'TITAN-EQ': '3506',
};

buy_traded_stock = []
sell_traded_stock = []

exchange = "NSE"
per_trade_fund = 10000
ma_short = 13
ma_long = 22
runcount = 0


def PlaceOredrExit():
    placeOREDR = False

def sendAlert(bot_message):
    get_message = format(bot_message)
    print(get_message)

    bot_token = "5707293106:AAEPkxexnIdoUxF5r7hpCRS_6CHINgU4HTw"
    bot_chatid = "2027669179"
    send_message = "https://api.telegram.org/bot" + bot_token + "/sendMessage?chat_id=" + bot_chatid + \
                   "&parse_mode=MarkdownV2&text=" + bot_message

    # response = requests.get(send_message)
    response = requests.post(f'https://api.telegram.org/bot{bot_token}/sendMessage', data={'chat_id': bot_chatid, 'text': bot_message})

    print(response)
    return response.json()

def checkorderlimit():
    try:
        getposition = obj.position()
        if getposition['data'].len >= 3:
           placeOREDR = False


    except Exception as e:
        print("error in check number in Position: {}".format(e))


def GettingLtpData(script, token, order):
    LTP = obj.ltpData(exchange, script, token)
#     print(LTP)
    ltp = LTP["data"]["ltp"]
    # quantity = int(per_trade_fund / ltp)
    quantity = int(per_trade_fund * 10 / ltp)

    orderparams = {
        "variety": "NORMAL",
        "tradingsymbol": script,
        "symboltoken": token,
        "transactiontype": order,
        "exchange": exchange,
        "ordertype": "LIMIT",
        "producttype": "INTRADAY",
        "duration": "DAY",
        "price": ltp,
        "squareoff": "0",
        "stoploss": "0",
        "quantity": quantity
    }

    if placeOREDR:
        # orderId = obj.placeOrder(orderparams)
        # print(
        #     f"{order} order Place for {script} at : {datetime.datetime.now()} with Order id {orderId}"
        # )
        bot_message = f"{order} trend for {script} swing trade with price {ltp}"
        bot_token = "5707293106:AAEPkxexnIdoUxF5r7hpCRS_6CHINgU4HTw"
        bot_chatid = "2027669179"
        send_message = "https://api.telegram.org/bot" + bot_token + "/sendMessage?chat_id=" + bot_chatid + \
                       "&parse_mode=MarkdownV2&text=" + bot_message

        response = requests.get(send_message)
        print(response)
        return response.json()

def exitQuert():
    api_key = document.api_key
    user_id = document.user_id
    password = document.password
    totp = pyotp.TOTP(document.totp).now()

    try:
        obj = SmartConnect(api_key=api_key)
        token = obj.generateToken(obj.generateSession(user_id, password, totp)["data"]["refreshToken"])
        getposition = obj.position()

        for a in getposition['data']:
            LTP = obj.ltpData(a["exchange"], a["tradingsymbol"], a["symboltoken"])
            getltp = LTP["data"]["ltp"]

            if (a["tradingsymbol"] not in traded_list_exit):

                traded_list_exit.append(a["tradingsymbol"])
                transactionType = "SELL" if int(a['netqty']) > 0 else "BUY"

                orderparams3 = {"variety": "NORMAL", "tradingsymbol": a["tradingsymbol"], "symboltoken": a["symboltoken"],
                                "transactiontype": transactionType, "exchange": a["exchange"], "ordertype": "LIMIT",
                                "producttype": a["producttype"], "duration": "DAY", "price": getltp, "squareoff": "0",
                                "stoploss": "0", "quantity": abs(int(a["netqty"]))}
                orderId3=obj.placeOrder(orderparams3)
                print(f"{orderparams3} order Place for {a['symboltoken']} at : {datetime.datetime.now()} with Order id {orderId3} order id quantity :{a['netqty']} ")

                time.sleep(2)

    except Exception as e:
        print("error: {}".format(e))

def strategy():
    print('check stetergy')
    global obj

    current_date_time = datetime.datetime.now()
    form_date = current_date_time - timedelta(days=10)

    api_key = document.api_key
    user_id = document.user_id
    password = document.password
    totp = pyotp.TOTP(document.totp).now()


    # print(feedToken)

    try:
        obj = SmartConnect(api_key=api_key)
        token = obj.generateToken(obj.generateSession(user_id, password, totp)["data"]["refreshToken"])
        jwtToken = token['data']["jwtToken"]
        refreshToken = token['data']['refreshToken']
        feedToken = token['data']['feedToken']
        for script, token in script_list.items():
            historicParam = {
                "exchange": exchange,
                "symboltoken": token,
                "interval": "FIFTEEN_MINUTE",
                "fromdate": form_date.strftime("%Y-%m-%d 09:15"),
                "todate": current_date_time.strftime("%Y-%m-%d %H:%M")
            }
            hist_data = obj.getCandleData(historicParam)["data"]
            LTP = obj.ltpData(exchange, script, token)

            # print(hist_data)
            if hist_data != None:
                df = pd.DataFrame(
                    hist_data,
                    columns=['date', 'open', 'high', 'low', 'close', 'volume'])
                df["sup"] = ta.supertrend(df['high'], df['low'], df['close'], length=10, multiplier=3)['SUPERT_10_3.0']
                df['stx'] = np.where((df['sup'] > 0.00), np.where((df['close'] > df['sup']), 'up', 'down'), np.NaN)

                # df['stx'] = 'down' if df['sup'].values > df['close'].values else 'up'

                df.dropna(inplace=True)
                # print(df.tail(40))
                print('#------------------------------' ,script,df.close.values[-5],df.close.values[-4],df.close.values[-3],df.close.values[-2],"----",df.sup.values[-1],'-----------------------#',format(datetime.datetime.now()))
                sup_cl = df.stx.values[-1]
                sup_pre = df.stx.values[-2]


                if not df.empty:
                    # Calculate the Fibonacci retracement levels based on the data
                    print(LTP['data']['low'])
                    high_price = LTP['data']['high']
                    low_price = LTP['data']['low']
                    ltp = LTP['data']['ltp']
                    price_close = LTP['data']['close']

                    diff_price = high_price - low_price
                    fib_levels = [0, 0.236, 0.382, 0.5, 0.618, 0.786]
                    retracements2 = [price_close + level * diff_price  for level in fib_levels]
                    # level2 = last_close + 0.382 * diff
                    # level3 = last_close + 0.618 * diff
                    # level4 = last_close + diff
                    retracements = [high_price - diff_price * level for level in fib_levels]
                    print(retracements2,retracements,high_price,low_price)
                    print(retracements[1])
                    if price_close < retracements[1]:
                        signal_type = 'buy'
                        print(script,signal_type)
                        bot_message = f'order status:fibonacci alert for {script} with price {ltp:.1f} and the time is {datetime.datetime.now()}'
                        sendAlert(bot_message)

                    elif price_close > retracements[-2]:
                        signal_type = 'sell'
                        print(script,signal_type)
                        bot_message = f'order status:fibonacci alert for {script} with price {ltp:.1f} and the time is {datetime.datetime.now()}'
                        sendAlert(bot_message)



            time.sleep(1)

    except Exception as e:
        print("Historic Api failed: {}".format(e),format(datetime.datetime.now()))
    try:
        logout = obj.terminateSession(user_id)
        print("Logout Successfull")
    except Exception as e:
        print("Logout failed: {}".format(e))


strategy()
schedule.every(5).minutes.do(strategy)
schedule.every(10).minutes.do(checkorderlimit)
schedule.every().day.at("15:05").do(exitQuert)
schedule.every().day.at("15:00").do(PlaceOredrExit)




while True:
        # print("start tym , CURRENT TIME:{}".format(datetime.datetime.now()))
        try:
            schedule.run_pending()
            time.sleep(2)
        except Exception as e:
            raise e