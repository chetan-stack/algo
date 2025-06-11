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
form_date = current_date_time - timedelta(days = 10)
traded_list_exit = []
print("current tym",current_date_time)
placeOREDR = True
script_list = {
    "BAJAJFINSV-EQ": "16675",
    'HDFCBANK-EQ': '1333',
    'TITAN-EQ': '3506',
    'HDFCLIFE-EQ': '467',
    'ICICIBANK-EQ': '4963',
    'JSWSTEEL-EQ': '11723',
    'TATASTEEL-EQ': '3499',
    'INFY-EQ': '1594',
    "ITC-EQ": "1660",
    "WIPRO-EQ": "3787",
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

def checkorderlimit():
    try:
        getposition = obj.position()
        if getposition['data'].len >= 3:
           placeOREDR = False


    except Exception as e:
        print("error in check number in Position: {}".format(e))
        sendAlert("error in check number in Position: {}".format(e))



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


        bot_message = f'order status:{order} for {script} with price {ltp:.1f} and the time is {datetime.datetime.now()}'
        sendAlert(bot_message)



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
        bot_message = f"error when exit {e}"
        sendAlert(bot_message)

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
        LTP = obj.ltpData('NSE', 'NIFTY', '26000')
        print(LTP)
        for script, token in script_list.items():
            historicParam = {
                "exchange": exchange,
                "symboltoken": token,
                "interval": "FIVE_MINUTE",
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
                # df["sup"] = ta.supertrend(df['high'], df['low'], df['close'], length=10, multiplier=3)['SUPERT_10_3.0']
                df["ema"] = ta.ema(df["close"], length=200)

                df['stx'] = np.where((df['sup'] > 0.00), np.where((df['close'] > df['sup']), 'up', 'down'), np.NaN)

                # df['stx'] = 'down' if df['sup'].values > df['close'].values else 'up'

                df.dropna(inplace=True)
                # print(df.tail(40))
                print('#------------------------------' ,script,df.close.values[-5],df.close.values[-4],df.close.values[-3],df.close.values[-2],"----",df.sup.values[-1],'-----------------------#',format(datetime.datetime.now()))

                sup_cl = df.stx.values[-1]
                sup_pre = df.stx.values[-2]


                if not df.empty:

                    sup_cl = df.sup.values[-1]
                    close_cl = df.close.values[-1]
                    # pre close
                    sup_pre = df.sup.values[-2]
                    close_pre = df.close.values[-2]

                    # 3 close
                    sup_pre3 = df.sup.values[-3]
                    close_pre3 = df.close.values[-3]
                    emaClose = df['ema'].values[-1]
                    closebar = df['close'].values[-1]
                    supertrend = df['stx'].values[-1]
                    if not df.empty:
                       # print(df)
                       if emaClose <= closebar and supertrend == 'up' and (script not in buy_traded_stock):
                            buy_traded_stock.append(script)
                            GettingLtpData(script, token, "BUY")

                       if emaClose >= closebar and supertrend == 'up' and (script not in sell_traded_stock):
                           sell_traded_stock.append(script)
                           GettingLtpData(script, token, "SEll")

            time.sleep(1)

    except Exception as e:
        print("Historic Api failed: {}".format(e),format(datetime.datetime.now()))
        bot_message = f"Historic Api failed {e}"
        sendAlert(bot_message)
        # strategy()

    try:
        logout = obj.terminateSession(user_id)
        print("Logout Successfull")
    except Exception as e:
        print("Logout failed: {}".format(e))
        bot_message = f"Logout failed {e}"
        sendAlert(bot_message)


strategy()
schedule.every(1).minutes.do(strategy)
# schedule.every(5).minutes.do(checkorderlimit)
schedule.every().day.at("15:05").do(exitQuert)
schedule.every().day.at("15:00").do(PlaceOredrExit)




while True:
        # print("start tym , CURRENT TIME:{}".format(datetime.datetime.now()))
        try:
            schedule.run_pending()
            time.sleep(2)
        except Exception as e:
            raise e