from SmartApi import SmartConnect  # or from SmartApi.smartConnect import SmartConnect
import time
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


api_key = document.api_key
user_id = document.user_id
password = document.password
totp = pyotp.TOTP(document.totp).now()
obj = SmartConnect(api_key=api_key)
token = obj.generateToken(obj.generateSession(user_id, password, totp)["data"]["refreshToken"])

current_date_time = datetime.datetime.now() - timedelta(days=1)
form_date = current_date_time - timedelta(days=10)
traded_list_exit = []
print("current tym", current_date_time)
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
    'RELIANCE-EQ': '2885',
    'TCS-EQ': '11536',

};
buy_traded_stock = []
sell_traded_stock = []

exchange = "NSE"
per_trade_fund = 10000
ma_short = 13
ma_long = 22
runcount = 0
selltradednity = []
buytradednifty = []
orderedprice = 0
targettobuy = ''
targettosell = ''
targettoexit = ''
ce_symbol = {}
pe_symbol = {}
orderprice = {}


def initialisedTockenMap():
    url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
    d = requests.get(url).json()
    global token_df
    token_df = pd.DataFrame.from_dict(d)
    token_df['expiry'] = pd.to_datetime(token_df['expiry'])
    token_df = token_df.astype({'strike': float})
    # print('check', token_df)
    placeorderdetails()


def fetchdataandreturn_pivot():
    username = 'YourTradingViewUsername'
    password = 'YourTradingViewPassword'

    tv = TvDatafeed(username, password)
    # index
    nifty_index_data = tv.get_hist(symbol='NIFTY', exchange='NSE', interval=Interval.in_daily, n_bars=3)
    data = nifty_index_data
    # print(data['high'].values[-2], data['low'].values[-2], data['close'].values[-2])
    high_price = data['high'].values[-2]
    low_price = data['low'].values[-2]
    close_price = data['close'].values[-2]
    datafile = []
    # print(high_price, low_price, close_price)
    # Calculate Fibonacci Levels
    pi = (high_price + low_price + close_price) / 3
    R1 = pi + (0.382 * (high_price - low_price))
    R2 = pi + (0.6182 * (high_price - low_price))
    R3 = R2 + (R2 - R1)
    S1 = pi - (0.382 * (high_price - low_price))
    S2 = pi - (0.6182 * (high_price - low_price))
    S3 = S2 - (R1 - S1)
    fibonacci_levels = {
        'p': round(pi, 2),
        's1': round(S1, 2),
        'r1': round(R1, 2),
        's2': round(S2, 2),
        'r2': round(R2, 2),
        'r3': round(R3, 2),
        's3': round(S3, 2)
    }
    global pivot_fibo_level
    pivot_fibo_level = fibonacci_levels


def defineresistancelevel(fibo_level, close):
    data = fibo_level
    filter_value = close

    matching_keys = [key for key, value in data.items() if value >= filter_value]
    max_key = min(matching_keys, key=lambda k: data[k], default='p')
    return max_key


def definesupportlevel(fibo_level, close):
    data = fibo_level
    filter_value = close

    matching_keys = [key for key, value in data.items() if value <= filter_value]
    max_key = max(matching_keys, key=lambda k: data[k], default='p')
    return max_key


def orderplacewithpivot(df, param):
    print(pivot_fibo_level)
    Method = 'pe' if param == 'buy' else ('ce' if param == 'sell' else None)
    r_level = defineresistancelevel(pivot_fibo_level, df.close.values[-1])
    s_level = definesupportlevel(pivot_fibo_level, df.close.values[-1])

    # print('resistance', r_level, 'supports', s_level,'close',df.close.values[-1],'second-right-high',df.high.values[-2] )

    if r_level in pivot_fibo_level or s_level in pivot_fibo_level:
        print(param, df.low.values[-2] <= pivot_fibo_level[s_level] and df.close.values[-1] > pivot_fibo_level[s_level])
        if param == 'buy':
            if df.high.values[-2] >= pivot_fibo_level[r_level] and df.close.values[-1] < pivot_fibo_level[r_level]:

                return 'pe'

            elif df.low.values[-2] <= pivot_fibo_level[s_level] and df.close.values[-1] > pivot_fibo_level[s_level]:

                return 'ce'

        elif param == 'sell':
            if df.high.values[-2] >= pivot_fibo_level[r_level] and df.close.values[-1] < pivot_fibo_level[s_level]:
                return 'ce'

            elif df.low.values[-2] <= pivot_fibo_level[s_level] and df.close.values[-1] > pivot_fibo_level[s_level]:

                return 'pe'

    else:
        print("nothing")


# def orderplacewithpivot(df,param):
#     print(pivot_fibo_level)
#     Method_pe = 'ce' if param == 'buy' else 'pe'
#     Methor_ce = 'pe' if param == 'sell' else 'ce'
#     r_level = defineresistancelevel(pivot_fibo_level,df.close.values[-1])
#     s_level = definesupportlevel(pivot_fibo_level,df.close.values[-1])
#
#     print('resistance',r_level,'supports',s_level)
#
#     if r_level in pivot_fibo_level or s_level in pivot_fibo_level:
#
#         if df.high.values[-2] >= pivot_fibo_level[r_level] and df.close.values[-1] < pivot_fibo_level[r_level]:
#                 return Method_pe
#         elif df.low.values[-1] <= pivot_fibo_level[s_level] and df.close.values[-1] > pivot_fibo_level[s_level]:
#                 return Methor_ce
#         else:
#               print ("nothing")
#     else:
#         print ("nothing")


# def orderplacewithpivot(df,param):
#     print(pivot_fibo_level)
#     Method_pe = 'pe' if param == 'buy' else 'ce'
#     Methor_ce = 'ce' if param == 'sell' else 'pe'
#     r_level = defineresistancelevel(pivot_fibo_level,df.close.values[-1])
#     s_level = definesupportlevel(pivot_fibo_level,df.close.values[-1])
#
#     print('resistance',r_level,'supports',s_level)
#
#     if r_level in pivot_fibo_level or s_level in pivot_fibo_level:
#
#         if df.high.values[-2] >= pivot_fibo_level[r_level] and df.close.values[-1] < pivot_fibo_level[r_level]:
#                 return 'ce_sell'
#         elif df.low.values[-2] <= pivot_fibo_level[s_level] and df.close.values[-1] > pivot_fibo_level[s_level]:
#                 return 'ce_buy'
#         if df.high.values[-2] >= pivot_fibo_level[s_level] and df.close.values[-1] < pivot_fibo_level[s_level]:
#                 return 'pe_buy'
#         elif df.low.values[-2] <= pivot_fibo_level[s_level] and df.close.values[-1] > pivot_fibo_level[s_level]:
#                 return 'pe_sell'
#         else:
#               print ("nothing")
#     else:
#         print ("nothing")


def getTokenInfo(exch_seg, instrumenttype, symbol, strike_price, pe_ce, expiry_day=None):
    df = token_df
    strike_price = strike_price * 100
    if exch_seg == 'NSE':
        # print('nse')
        eq_df = df[(df['exch_seg'] == 'NSE')]
        # print(eq_df[(eq_df['name'] == 'NIFTY')],'---####---')
        return eq_df[(eq_df['name'] == 'NIFTY')]
    elif exch_seg == 'NFO' and (instrumenttype == 'OPTSTK' or instrumenttype == 'OPTIDX'):
        print('nfo')
        return df[(df['exch_seg'] == 'NFO') & (df['instrumenttype'] == instrumenttype) & (df['name'] == symbol) & (
        (df['strike'] == strike_price)) & (df['symbol'].str.endswith(pe_ce)) & (
                              df['expiry'] >= str(datetime.date.today()))].sort_values(by=['expiry'])


def placeorderdetails():
    tokeninfo = getTokenInfo('NSE', 'OPTIDX', 'NIFTY', '', '').iloc[0]['token']
    print(tokeninfo, "---fghjk")
    global LTP
    LTP = obj.ltpData('NSE', 'NIFTY', tokeninfo)['data']['ltp']
    RTM = int(round(LTP / 100) * 100)  # to get check acurate price
    print(LTP, RTM)
    ## now check price and place order details
    # print(getTokenInfo('NFO', 'OPTIDX', 'NIFTY', RTM, 'CE').iloc[0])

    ce_symbol_data = getTokenInfo('NFO', 'OPTIDX', 'NIFTY', RTM, 'CE').iloc[0]
    pe_symbol_data = getTokenInfo('NFO', 'OPTIDX', 'NIFTY', RTM, 'PE').iloc[0]

    ce_symbol['token'] = ce_symbol_data['token']
    ce_symbol['symbol'] = ce_symbol_data['symbol']
    ce_symbol['lotsize'] = ce_symbol_data['lotsize']

    pe_symbol['token'] = pe_symbol_data['token']
    pe_symbol['symbol'] = pe_symbol_data['symbol']
    pe_symbol['lotsize'] = pe_symbol_data['lotsize']


def PlaceOredrExit():
    placeOREDR = False


# def getorderBook():
#     tradebook = obj.position()
#     # print(tradebook)
#     #if len(selltradednity) > 0 or len(buytradednifty) > 0:
#     if tradebook['data'] is not None:
#         for a in tradebook['data']:
#             if a['symbolname'] == 'NIFTY' and a['netqty'] != '0':
#                 return False
#             else:
#                 return True
#     else:
#         return True

def exitontarget(data):
    totalvalue = int(float(data['totalbuyvalue']))
    stoploss = float((totalvalue / 100) * 10)
    target = float((totalvalue / 100) * 20)
    pnltype = 'profit' if int(float(data['pnl'])) > 0 else 'loss'
    if pnltype == 'loss' and abs(int(float(data['pnl']))) > stoploss or pnltype == 'profit' and int(float(data['pnl'])) > target:
        if data['optiontype'] == 'PE':
            place_order(pe_symbol['token'], pe_symbol['symbol'], pe_symbol['lotsize'], 'NFO', 'SELL',
                                        'MARKET', 0, 0)
        elif data['optiontype'] == 'CE':
            place_order(ce_symbol['token'], ce_symbol['symbol'], ce_symbol['lotsize'], 'NFO', 'SELL',
                                        'MARKET', 0, 0)
        else:
            print('No stoploss or target hit')
    else:
        print('No Exit Targrt target hit for 1/3','pnl:',int(float(data['pnl'])),'type:',pnltype,'totalorder:',totalvalue,'stoploss:',stoploss,'target:',target)

def getorderBook():
    tradebook = obj.position()

    # if len(selltradednity) > 0 or len(buytradedBANKNIFTY) > 0:
    if tradebook['data'] is not None:
        filtered_data = [item for item in tradebook['data'] if item['symbolname'] == 'NIFTY']
        # print(filtered_data[-1]['tradingsymbol'])
        last_item = filtered_data[-1]  # Accessing the last item in the filtered list
        print(last_item)

        if last_item and last_item['symbolname'] == 'NIFTY' and last_item['netqty'] != '0':
            exitontarget(last_item)
            buytradednifty.append(last_item['optiontype'])
            orderprice['data'] = last_item['avgnetprice']
            if (last_item['optiontype'] == 'CE'):
                ce_symbol['token'] = last_item['symboltoken']
                ce_symbol['symbol'] = last_item['tradingsymbol']
                ce_symbol['lotsize'] = last_item['lotsize']
                ce_symbol['orderprice'] = last_item['avgnetprice']
                ce_symbol['optiontype'] = last_item['optiontype']
            elif (last_item['optiontype'] == 'PE'):
                pe_symbol['token'] = last_item['symboltoken']
                pe_symbol['symbol'] = last_item['tradingsymbol']
                pe_symbol['lotsize'] = last_item['lotsize']
                pe_symbol['orderprice'] = last_item['avgnetprice']
                pe_symbol['optiontype'] = last_item['optiontype']

            else:
                print('no order found')
            return False
        else:
            return True
    else:
        return True


def getdatabase():
    table = crete_update_table.fetchdata()
    print(table, 'table')
    if len(table) > 0:
        key, json_string = table[-1]
        json_data = json.loads(json_string)
        if (json_data['tradingsymbol'] == ce_symbol['symbol']) or (json_data['tradingsymbol'] == pe_symbol['symbol']):
            return False
        else:
            return True
    else:
        return True


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
    response = requests.post(f'https://api.telegram.org/bot{bot_token}/sendMessage',
                             data={'chat_id': bot_chatid, 'text': bot_message})

    print(response)
    return response.json()


def GettingLtpData(script, token, order):
    # orderparams = {
    #     "variety": "NORMAL",
    #     "tradingsymbol": script,
    #     "symboltoken": token,
    #     "transactiontype": order,
    #     "exchange": exchange,
    #     "ordertype": "LIMIT",
    #     "producttype": "INTRADAY",,
    #     "duration": "DAY",
    #     "price": ltp,
    #     "squareoff": "0",
    #     "stoploss": "0",
    #     "quantity": quantity
    # }

    # if placeOREDR:
    # orderId = obj.placeOrder(orderparams)
    # print(
    #         f"{order} order Place for {script} at : {datetime.datetime.now()} with Order id {orderId}"
    #     )

    bot_message = f'order status:{order} for {script} with price {token} and the time is {datetime.datetime.now()}'
    sendAlert(bot_message)


def place_order(token, symbol, qty, exch_seg, buy_sell, ordertype, price, orderprice):
    orderparams = {
        "variety": "NORMAL",
        "tradingsymbol": symbol,
        "symboltoken": token,
        "transactiontype": buy_sell,
        "exchange": exch_seg,
        "ordertype": ordertype,
        "producttype": "INTRADAY",
        "duration": "DAY",
        "squareoff": "0",
        "stoploss": "0",
        "quantity": qty,
        'price': price
    }

    orderId = 1
    #orderId = obj.placeOrder(orderparams)
    # print(orderId)

    if placeOREDR:
        # orderId = obj.placeOrder(orderparams)
        print(
            f"{buy_sell} order Place for {symbol} at : {datetime.datetime.now()} with Order id {orderId} price {price} ordered price {orderedprice}"
        )

    bot_message = f'order status:{buy_sell} for {symbol} with price {token} and the time is {datetime.datetime.now()} ordered price {orderedprice}'
    dumptext = json.dumps(orderparams)
    crete_update_table.insertdata(dumptext)
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

                orderparams3 = {"variety": "NORMAL", "tradingsymbol": a["tradingsymbol"],
                                "symboltoken": a["symboltoken"],
                                "transactiontype": transactionType, "exchange": a["exchange"], "ordertype": "LIMIT",
                                "producttype": a["producttype"], "duration": "DAY", "price": getltp, "squareoff": "0",
                                "stoploss": "0", "quantity": abs(int(a["netqty"]))}
                orderId3 = obj.placeOrder(orderparams3)
                print(
                    f"{orderparams3} order Place for {a['symboltoken']} at : {datetime.datetime.now()} with Order id {orderId3} order id quantity :{a['netqty']} ")

                time.sleep(2)

    except Exception as e:
        print("error: {}".format(e))
        bot_message = f"error when exit {e}"
        sendAlert(bot_message)

# def getoption():


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
        # obj = SmartConnect(api_key=api_key)
        # token = obj.generateToken(obj.generateSession(user_id, password, totp)["data"]["refreshToken"])
        # jwtToken = token['data']["jwtToken"]
        # refreshToken = token['data']['refreshToken']
        # feedToken = token['data']['feedToken']
        # print(obj)

        tv = TvDatafeed()
        hist_data = tv.get_hist(symbol='NIFTY', exchange='NSE', interval=Interval.in_1_minute, n_bars=50)
        # print(hist_data)
        if not hist_data.empty:
            df = pd.DataFrame(
                hist_data,
                columns=['date', 'open', 'high', 'low', 'close', 'volume'])

            df["sup"] = ta.supertrend(df['high'], df['low'], df['close'], length=10, multiplier=3)['SUPERT_10_3.0']
            df["ema"] = ta.ema(df["close"], length=10)
            df['stx'] = np.where((df['sup'] > 0.00), np.where((df['close'] > df['sup']), 'up', 'down'), np.NaN)
            df['Candle_Color'] = 1  # Initialize with a value indicating green candles
            df.loc[df['close'] < df['open'], 'Candle_Color'] = 0

            if not df.empty:
                print('#------------------------------', df.close.values[-5], df.close.values[-4], df.close.values[-3],
                      df.close.values[-2], "----", df.sup.values[-1], '-----------------------#',
                      format(datetime.datetime.now()))

                sup_cl = df.sup.values[-1]
                close_cl = df.close.values[-1]
                # pre close
                sup_pre = df.sup.values[-2]
                close_pre = df.close.values[-2]

                # 3 close
                sup_pre3 = df.sup.values[-3]
                close_pre3 = df.close.values[-3]

                # 4 close
                sup_pre4 = df.sup.values[-4]
                close_pre4 = df.close.values[-4]

                r_level = defineresistancelevel(pivot_fibo_level, df.close.values[-1])
                s_level = definesupportlevel(pivot_fibo_level, df.close.values[-1])
                print("registance : ", r_level, "support : ", s_level)
                print(getoptionchain.getparams('NIFTY',df.close.values[-1],'ce'))
                # print(getorderBook(),'check gerate order')
                if not df.empty:
                    if getorderBook():  # (check if Nifty order is not placed)
                        if close_pre >= sup_pre and close_cl < sup_cl:
                            # GettingLtpData('nifty', close_cl, "SELL")
                            place_order(pe_symbol['token'], pe_symbol['symbol'], pe_symbol['lotsize'], 'NFO', 'BUY',
                                        'MARKET', 0, df.close.values[-1])
                            buytradednifty.append('pe')

                        elif close_pre <= sup_pre and close_cl > sup_cl:
                            # GettingLtpData('nifty', close_cl, "BUY")
                            place_order(ce_symbol['token'], ce_symbol['symbol'], ce_symbol['lotsize'], 'NFO', 'BUY',
                                        'MARKET', 0, df.close.values[-1])
                            buytradednifty.append('ce')

                        elif close_cl > sup_cl and df.low.values[-2] <= pivot_fibo_level[s_level] and df.close.values[-1] > pivot_fibo_level[s_level] and df.close.values[-1] > df.ema.values[-1]:
                           if getoptionchain.getparams('NIFTY',df.close.values[-1],'ce'):
                                place_order(ce_symbol['token'], ce_symbol['symbol'], ce_symbol['lotsize'], 'NFO', 'BUY',
                                        'MARKET', 0, df.close.values[-1])
                                buytradednifty.append('ce')

                        elif close_cl < sup_cl and df.high.values[-2] >= pivot_fibo_level[r_level] and df.close.values[-1] < pivot_fibo_level[r_level] and df.close.values[-1] < df.ema.values[-1]:
                            if getoptionchain.getparams('NIFTY',df.close.values[-1],'pe'):
                                 place_order(pe_symbol['token'], pe_symbol['symbol'], pe_symbol['lotsize'], 'NFO', 'BUY',
                                            'MARKET', 0, df.close.values[-1])
                                 buytradednifty.append('pe')

                        else:
                            print('not match')

                    else:  # (if Nifty order is placed, then run exit script with supertrend)
                        print('sell order here -----', orderedprice)

                        if close_cl > sup_cl and df.high.values[-2] >= pivot_fibo_level[r_level] and df.close.values[-1] < pivot_fibo_level[r_level]:
                            print('exit --- 1')
                            place_order(ce_symbol['token'], ce_symbol['symbol'], ce_symbol['lotsize'], 'NFO', 'SELL',
                                        'MARKET', 0, df.close.values[-1])
                            selltradednity.append('nifty')

                        elif close_cl < sup_cl and df.low.values[-2] <= pivot_fibo_level[s_level] and df.close.values[-1] > pivot_fibo_level[s_level]:
                            print('exit --- 2')

                            place_order(pe_symbol['token'], pe_symbol['symbol'], pe_symbol['lotsize'], 'NFO', 'SELL',
                                        'MARKET', 0, df.close.values[-1])
                            selltradednity.append('nifty')

                        elif close_cl > sup_cl and ('pe' in buytradednifty):
                            print('exit --- 1.1')
                            place_order(pe_symbol['token'], pe_symbol['symbol'], pe_symbol['lotsize'], 'NFO', 'SELL',
                                        'MARKET', 0, df.close.values[-1])
                            selltradednity.append('nifty')
                            buytradednifty.clear()

                        elif close_cl < sup_cl and ('ce' in buytradednifty):
                            print('exit --- 2.1')
                            place_order(ce_symbol['token'], ce_symbol['symbol'], ce_symbol['lotsize'], 'NFO', 'SELL',
                                        'MARKET', 0, df.close.values[-1])
                            selltradednity.append('nifty')
                            buytradednifty.clear()

                        elif df.close.values[-1] < df.ema.values[-1] and ('CE' in buytradednifty):
                            print('exit --- 3')

                            place_order(ce_symbol['token'], ce_symbol['symbol'], ce_symbol['lotsize'], 'NFO', 'SELL',
                                        'MARKET', 0, df.close.values[-1])
                            selltradednity.append('nifty')
                            buytradednifty.clear()

                        elif df.close.values[-1] > df.ema.values[-1] and ('PE' in buytradednifty):
                            print('exit --- 4')

                            place_order(pe_symbol['token'], pe_symbol['symbol'], pe_symbol['lotsize'], 'NFO', 'SELL',
                                        'MARKET', 0, df.close.values[-1])
                            selltradednity.append('nifty')
                            buytradednifty.clear()

                        # elif df.close.values[-1] <= (int(orderprice['data']) - 10) and ('CE' in buytradednifty):
                        #     print('exit --- 5')
                        #
                        #     place_order(ce_symbol['token'], ce_symbol['symbol'], ce_symbol['lotsize'], 'NFO', 'SELL',
                        #                 'MARKET', 0, df.close.values[-1])
                        #     selltradednity.append('nifty')
                        #     buytradednifty.clear()
                        #
                        # elif df.close.values[-1] >= (int(orderprice['data']) + 20) and df.close.value[-2] > \
                        #         df.close.value[-1] and ('CE' in buytradednifty):
                        #     print('exit --- 5.1')
                        #
                        #     place_order(ce_symbol['token'], ce_symbol['symbol'], ce_symbol['lotsize'], 'NFO', 'SELL',
                        #                 'MARKET', 0, df.close.values[-1])
                        #     selltradednity.append('nifty')
                        #     buytradednifty.clear()
                        #
                        #
                        # elif df.close.values[-1] >= (int(orderprice['data']) - 10) and ('PE' in buytradednifty):
                        #     print('exit --- 6')
                        #
                        #     place_order(pe_symbol['token'], pe_symbol['symbol'], pe_symbol['lotsize'], 'NFO', 'SELL',
                        #                 'MARKET', 0, df.close.values[-1])
                        #     selltradednity.append('nifty')
                        #     buytradednifty.clear()



                        else:
                            print('not match')
                else:
                    print('df empty')
            time.sleep(1)
        else:
            print('not working')



    except Exception as e:
        print("Script Not Working: {}".format(e), format(datetime.datetime.now()))
        bot_message = f"Historic Api failed {e}"
        # sendAlert(bot_message)
        strategy()

    # try:
    #     logout = obj.terminateSession(user_id)
    #     print("Logout Successfull")
    # except Exception as e:
    #     print("Logout failed: {}".format(e))
    #     bot_message = f"Logout failed {e}"
    #     # sendAlert(bot_message)


# try:
#     api_key = document.api_key
#     user_id = document.user_id
#     password = document.password
#     totp = pyotp.TOTP(document.totp).now()
#
#     obj = SmartConnect(api_key=api_key)
#     token = obj.generateSession(user_id, password, totp)
#     print("--------",obj,token)
#     if obj:
#         strategy()
#
#
# except Exception as e:
#     print("Build Connection Error: {}".format(e), format(datetime.datetime.now()))
initialisedTockenMap()
# getorderBook()
fetchdataandreturn_pivot()
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

# important notes:
# obj.tradeBook()
# obj.orderBook()
# obj.position()
# obj.holding()
