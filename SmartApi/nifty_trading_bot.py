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
import requests
import document

current_date_time = datetime.datetime.now()
form_date = current_date_time - timedelta(days = 10)

nifty_store = []

exchange = "NSE"
per_trade_fund = 10000
ma_short = 13
ma_long = 22
runcount = 0

def filterOrder():
    print('_______________show Store Data____________________')
    try:
        # set nifty data into dataframes
        df = pd.DataFrame(
            nifty_store,
            columns=['exchange', 'open', 'high', 'low', 'close', 'ltp'])
        df["sup"] = ta.supertrend(df['high'], df['low'], df['close'], length=10, multiplier=3)['SUPERT_10_3.0']
        df.dropna(inplace=True)
        print(df)
        if not df.empty:

            sup_cl = df.sup.values[-1]
            close_cl = df.close.values[-1]
            # pre close
            sup_pre = df.sup.values[-2]
            close_pre = df.close.values[-2]

            # 3 close
            sup_pre3 = df.sup.values[-3]
            close_pre3 = df.close.values[-3]

            if not df.empty:
                if close_pre >= sup_pre and close_cl < sup_cl:
                    f = open("nifty_store.txt", "a")
                    f.write(str(df['ltp']) + "----" + str(df['close']) + "---------SELL-----------" + "----" )
                    f.close()


                if close_pre <= sup_pre and close_cl > sup_cl:
                    f = open("nifty_store.txt", "a")
                    f.write(str(df['ltp']) + "----" + str(df['close']) + "---------BUY-----------" + "----")
                    f.close()

    except Exception as e:
        print("Nifty Selection Falied: {}".format(e))

def dataStore():
    print('check')
    global obj

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

        # Get nifty data
        niftyLive = obj.ltpData("NSE", "NIFTY", "26000")
        nifty_store.append(niftyLive['data'])
        print(nifty_store)


    except Exception as e:
        print("Historic Api failed: {}".format(e))
    try:
        logout = obj.terminateSession(user_id)
        print("Logout Successfull")
    except Exception as e:
        print("Logout failed: {}".format(e))



def main():
    orderplacetime = int(9) * 60 + int(20)
    timenow = (datetime.datetime.now().hour * 60 + datetime.datetime.now().minute)
    print("Waiting for 9.20 AM , CURRENT TIME:{}".format(datetime.datetime.now()))
    dataStore()
    # schedule.every().day.at("09:20").do(strategy)
    schedule.every(1).minutes.do(dataStore)
    schedule.every(5).minutes.do(filterOrder)


    # while True:
    #     # print("start tym , CURRENT TIME:{}".format(datetime.datetime.now()))
    #     try:
    #         schedule.run_pending()
    #         time.sleep(2)
    #     except Exception as e:
    #         raise e




# if (__name__ == '__main__'):
# #     print("lets start")
#     main()


def telegrameBot():
    bot_token = "5707293106:AAEPkxexnIdoUxF5r7hpCRS_6CHINgU4HTw"
    bot_chatid = "2027669179"
    script = 'tata steel'
    order = 'buy'
    ltp = 200
    bot_message = f"{order} order Place for {script} with price {ltp}"
    print(bot_message)
    send_message = "https://api.telegram.org/bot" + bot_token + "/sendMessage?chat_id=" + bot_chatid +\
                   "&parse_mode=MarkdownV2&text=" + bot_message

    response = requests.get(send_message)
    print(response)
    return response.json()

telegrameBot()

# trading_bot()