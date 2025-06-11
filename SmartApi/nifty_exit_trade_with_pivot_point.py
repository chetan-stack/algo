from SmartApi import SmartConnect  # or from SmartApi.smartConnect import SmartConnect
import time
import talib as talib
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
import get_strick_price_historicaldata
from tabulate import tabulate



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
    print(tokeninfo, "---token")
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
    print(ce_symbol_data,pe_symbol_data)

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

global target
global tralloss

target = 0
tralloss = 0

def exitontarget(data):
    global target, tralloss

    totalvalue = int(float(data['totalbuyvalue']))
    stoploss = float((totalvalue / 100) * 5)

    # Initialize target if it's the first time
    target = (totalvalue / 100) * 15 if target == 0 else target

    pnltype = 'profit' if int(float(data['unrealised'])) > 0 else 'loss'
    print(target,stoploss,data['pnl'],pnltype,abs(int(float(data['unrealised']))))
    if pnltype == 'profit' and abs(int(float(data['unrealised']))) > target:
        tralloss = (abs(int(float(data['unrealised']))) - float((totalvalue / 100) * 2))
        target = (abs(int(float(data['unrealised']))) + float((totalvalue / 100) * 5))
        print('target', target, 'tral', tralloss, 'pnl', data['pnl'], 'change', (totalvalue / 100) * 5)
    elif pnltype == 'profit' and tralloss != 0 and abs(int(float(data['unrealised']))) < tralloss:
        if data['optiontype'] == 'PE':
            place_order(pe_symbol['token'], pe_symbol['symbol'], pe_symbol['lotsize'], 'NFO', 'SELL',
                        'MARKET', 0, 0)
        elif data['optiontype'] == 'CE':
            place_order(ce_symbol['token'], ce_symbol['symbol'], ce_symbol['lotsize'], 'NFO', 'SELL',
                        'MARKET', 0, 0)
    elif pnltype == 'loss' and abs(int(float(data['unrealised']))) > stoploss:
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
        filtered_data = [item for item in tradebook['data'] if item['symbolname'] == 'NIFTY' and item['netqty'] != '0']
        if filtered_data:
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
        "quantity": 1,
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

def checkcandlestickpattern(df):
    #print('last item of data',df)
    pattern_columns = {
        'CDL_HAMMER': 'Bullish',
        'CDL_BULLISH_ENGULFING': 'Bullish',
        'CDL_PIERCING': 'Bullish',
        'CDL_MORNING_STAR': 'Bullish',
        'CDL_THREE_WHITE_SOLDIERS': 'Bullish',
        'CDL_HANGING_MAN': 'Bearish',
        'CDL_SHOOTING_STAR': 'Bearish',
        'CDL_BEARISH_ENGULFING': 'Bearish',
        'CDL_EVENING_STAR': 'Bearish',
        'CDL_THREE_BLACK_CROWS': 'Bearish',
        'CDL_DARK_CLOUD_COVER': 'Bearish',
        'CDL_DOJI': 'Neutral',
        'CDL_SPINNING_TOP': 'Neutral'
    }
    pattern_columns_list = list(pattern_columns.keys())
    signals = []
    for col in pattern_columns_list:
        if df[col] == 100 or df[col] == -100:
            result = {'signal':pattern_columns[col],'pattern_name':col}
            signals.append(result)

    bot_message = f'5 min signals for Nifty {signals} and the time is {datetime.datetime.now()}'
    if len(signals) > 0:
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

    try:
        # obj = SmartConnect(api_key=api_key)
        # token = obj.generateToken(obj.generateSession(user_id, password, totp)["data"]["refreshToken"])
        # jwtToken = token['data']["jwtToken"]
        # refreshToken = token['data']['refreshToken']
        # feedToken = token['data']['feedToken']
        # print(obj)

        tv = TvDatafeed()
        hist_data = tv.get_hist(symbol='NIFTY', exchange='NSE', interval=Interval.in_5_minute, n_bars=100)
        # print(hist_data)
        if not hist_data.empty:
            df = pd.DataFrame(
                hist_data,
                columns=['date', 'open', 'high', 'low', 'close', 'volume'])

            df["sup"] = ta.supertrend(df['high'], df['low'], df['close'], length=10, multiplier=2)['SUPERT_10_2.0']
            df["ema"] = ta.ema(df["close"], length=9)
            df['stx'] = np.where((df['sup'] > 0.00), np.where((df['close'] > df['sup']), 'up', 'down'), np.NaN)
            df['Candle_Color'] = 1  # Initialize with a value indicating green candles
            df.loc[df['close'] < df['open'], 'Candle_Color'] = 0

            # Calculate candlestick patterns using pandas_ta
            df['CDL_HAMMER'] = talib.CDLHAMMER(df['open'], df['high'], df['low'], df['close'])
            df['CDL_BULLISH_ENGULFING'] = talib.CDLENGULFING(df['open'], df['high'], df['low'], df['close'])
            df['CDL_PIERCING'] = talib.CDLPIERCING(df['open'], df['high'], df['low'], df['close'])
            df['CDL_MORNING_STAR'] = talib.CDLMORNINGSTAR(df['open'], df['high'], df['low'], df['close'])
            df['CDL_THREE_WHITE_SOLDIERS'] = talib.CDL3WHITESOLDIERS(df['open'], df['high'], df['low'], df['close'])

            df['CDL_HANGING_MAN'] = talib.CDLHANGINGMAN(df['open'], df['high'], df['low'], df['close'])
            df['CDL_SHOOTING_STAR'] = talib.CDLSHOOTINGSTAR(df['open'], df['high'], df['low'], df['close'])
            df['CDL_BEARISH_ENGULFING'] = talib.CDLENGULFING(df['open'], df['high'], df['low'], df['close'])
            df['CDL_EVENING_STAR'] = talib.CDLEVENINGSTAR(df['open'], df['high'], df['low'], df['close'])
            df['CDL_THREE_BLACK_CROWS'] = talib.CDL3BLACKCROWS(df['open'], df['high'], df['low'], df['close'])
            df['CDL_DARK_CLOUD_COVER'] = talib.CDLDARKCLOUDCOVER(df['open'], df['high'], df['low'], df['close'])

            df['CDL_DOJI'] = talib.CDLDOJI(df['open'], df['high'], df['low'], df['close'])
            df['CDL_SPINNING_TOP'] = talib.CDLSPINNINGTOP(df['open'], df['high'], df['low'], df['close'])
            # df['CDL_FALLING_THREE_METHODS'] = talib.CDLFALLING3METHODS(df['open'], df['high'], df['low'], df['close'])
            # df['CDL_RISING_THREE_METHODS'] = talib.CDLRISING3METHODS(df['open'], df['high'], df['low'], df['close'])
            pattern_columns = [
            'CDL_HAMMER', 'CDL_BULLISH_ENGULFING', 'CDL_PIERCING', 'CDL_MORNING_STAR', 'CDL_THREE_WHITE_SOLDIERS',
            'CDL_HANGING_MAN', 'CDL_SHOOTING_STAR', 'CDL_BEARISH_ENGULFING', 'CDL_EVENING_STAR', 'CDL_THREE_BLACK_CROWS',
            'CDL_DARK_CLOUD_COVER', 'CDL_DOJI', 'CDL_SPINNING_TOP'
            ]
            filtered_df = df[df[pattern_columns].isin([100, -100]).any(axis=1)]

            # Select only date and pattern columns
            filtered_df = filtered_df[['date','CDL_HAMMER', 'CDL_BULLISH_ENGULFING', 'CDL_PIERCING', 'CDL_MORNING_STAR', 'CDL_THREE_WHITE_SOLDIERS',
                'CDL_HANGING_MAN', 'CDL_SHOOTING_STAR', 'CDL_BEARISH_ENGULFING', 'CDL_EVENING_STAR', 'CDL_THREE_BLACK_CROWS',
                'CDL_DARK_CLOUD_COVER', 'CDL_DOJI', 'CDL_SPINNING_TOP']]
            filtered_df.reset_index(inplace=True)

            # Display the filtered dataframe in a table format with only date and pattern columns
            #print(tabulate(filtered_df, headers='keys', tablefmt='psql'))

            # print(tabulate(df, headers='keys', tablefmt='psql'))

            # print(df.tail())
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
                print(df)
                #print('last item of object',df.iloc[-1])
                print("registance : ", r_level, "support : ", s_level)
                print('option chain : ',getoptionchain.getparams('NIFTY',df.close.values[-1],'ce' if close_cl > sup_cl else 'pe'))
                print('strick price ce',ce_symbol['symbol'],ce_symbol['token'],get_strick_price_historicaldata.gethistoricalldata(ce_symbol['symbol'],ce_symbol['token']))
                print('strick price pe',pe_symbol['symbol'],pe_symbol['token'],get_strick_price_historicaldata.gethistoricalldata(pe_symbol['symbol'],pe_symbol['token']))
                #checkcandlestickpattern(df.iloc[-2])
                #stetergytosendalert(df)

                # print(getorderBook(),'check gerate order')
                if not df.empty:
                    if getorderBook():  # (check if Nifty order is not placed)
                        selltradednity.clear()
                        if close_pre > sup_pre and close_cl < sup_cl:
                           if getoptionchain.getparams('NIFTY',df.close.values[-1],'pe'):
                                print('buy 1')
                                # GettingLtpData('nifty', close_cl, "SELL")
                                place_order(pe_symbol['token'], pe_symbol['symbol'], pe_symbol['lotsize'], 'NFO', 'BUY',
                                            'MARKET', 0, df.close.values[-1])
                                buytradednifty.append('pe')

                        elif close_pre < sup_pre and close_cl > sup_cl:
                           if getoptionchain.getparams('NIFTY',df.close.values[-1],'ce'):
                                print('buy 2')
                                # GettingLtpData('nifty', close_cl, "BUY")
                                place_order(ce_symbol['token'], ce_symbol['symbol'], ce_symbol['lotsize'], 'NFO', 'BUY',
                                            'MARKET', 0, df.close.values[-1])
                                buytradednifty.append('ce')

                        elif df.low.values[-2] < pivot_fibo_level[s_level] and df.close.values[-1] > pivot_fibo_level[s_level] and df.close.values[-1] > df.ema.values[-1]:
                           print('option chain at support: ',getoptionchain.getparams('NIFTY',df.close.values[-1],'ce'))
                           print(df.low.values[-2] , df.low.values[-1] , pivot_fibo_level[s_level])
                           if getoptionchain.getparams('NIFTY',df.close.values[-1],'ce'):
                                print('buy 3')
                                place_order(ce_symbol['token'], ce_symbol['symbol'], ce_symbol['lotsize'], 'NFO', 'BUY',
                                        'MARKET', 0, df.close.values[-1])
                                buytradednifty.append('ce')

                        elif df.high.values[-2] > pivot_fibo_level[r_level] and df.close.values[-1] < pivot_fibo_level[r_level] and df.close.values[-1] < df.ema.values[-1]:
                            print('option chain at resistance: ',getoptionchain.getparams('NIFTY',df.close.values[-1],'pe'))
                            print(df.low.values[-2] , df.low.values[-1] , pivot_fibo_level[r_level])

                            if getoptionchain.getparams('NIFTY',df.close.values[-1],'pe'):
                                 print('buy 4')
                                 place_order(pe_symbol['token'], pe_symbol['symbol'], pe_symbol['lotsize'], 'NFO', 'BUY',
                                            'MARKET', 0, df.close.values[-1])
                                 buytradednifty.append('pe')

                        # elif getoptionchain.placeorderwhenconfermation('NIFTY',df.close.values[-1],'') == 'ce':
                        #         print('option chain send ce order')
                        #         place_order(ce_symbol['token'], ce_symbol['symbol'], ce_symbol['lotsize'], 'NFO', 'BUY',
                        #                 'MARKET', 0, df.close.values[-1])
                        #         buytradednifty.append('ce')

                        # elif getoptionchain.placeorderwhenconfermation('NIFTY',df.close.values[-1],'') == 'pe':
                        #         print('option chain sends pe order')
                        #         place_order(pe_symbol['token'], pe_symbol['symbol'], pe_symbol['lotsize'], 'NFO', 'BUY',
                        #                     'MARKET', 0, df.close.values[-1])
                        #         buytradednifty.append('pe')

                        else:
                            print('Buy not match')

                    else:  # (if Nifty order is placed, then run exit script with supertrend)
                        print('sell order here -----', orderedprice)

                        if ('ce' in buytradednifty) and df.high.values[-2] >= pivot_fibo_level[r_level] and df.close.values[-1] < pivot_fibo_level[r_level]:
                            print('exit --- 1')
                            if getoptionchain.getparams('NIFTY',df.close.values[-1],'pe'):
                                place_order(ce_symbol['token'], ce_symbol['symbol'], ce_symbol['lotsize'], 'NFO', 'SELL',
                                            'MARKET', 0, df.close.values[-1])
                                selltradednity.append('nifty')
                                buytradednifty.clear()


                        elif ('pe' in buytradednifty) and df.low.values[-2] <= pivot_fibo_level[s_level] and df.close.values[-1] > pivot_fibo_level[s_level]:
                            print('exit --- 2')
                            if getoptionchain.getparams('NIFTY',df.close.values[-1],'ce'):
                                place_order(pe_symbol['token'], pe_symbol['symbol'], pe_symbol['lotsize'], 'NFO', 'SELL',
                                            'MARKET', 0, df.close.values[-1])
                                selltradednity.append('nifty')
                                buytradednifty.clear()


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

                        elif df.close.values[-1] < df.ema.values[-1] and ('ce' in buytradednifty):
                            print('exit --- 3')

                            place_order(ce_symbol['token'], ce_symbol['symbol'], ce_symbol['lotsize'], 'NFO', 'SELL',
                                        'MARKET', 0, df.close.values[-1])
                            selltradednity.append('nifty')
                            buytradednifty.clear()

                        elif df.close.values[-1] > df.ema.values[-1] and ('pe' in buytradednifty):
                            print('exit --- 4')

                            place_order(pe_symbol['token'], pe_symbol['symbol'], pe_symbol['lotsize'], 'NFO', 'SELL',
                                        'MARKET', 0, df.close.values[-1])
                            selltradednity.append('nifty')
                            buytradednifty.clear()

                        elif ('pe' in buytradednifty) and get_strick_price_historicaldata.checkexitconditio(pe_symbol['symbol'],pe_symbol['token']):
                            print('exit --- 5 with check strick price condition')

                            place_order(pe_symbol['token'], pe_symbol['symbol'], pe_symbol['lotsize'], 'NFO', 'SELL',
                                        'MARKET', 0, df.close.values[-1])
                            selltradednity.append('nifty')
                            buytradednifty.clear()

                        elif ('ce' in buytradednifty) and get_strick_price_historicaldata.checkexitconditio(ce_symbol['symbol'],ce_symbol['token']):
                            print('exit --- 6 with check strick price condition')

                            place_order(ce_symbol['token'], ce_symbol['symbol'], ce_symbol['lotsize'], 'NFO', 'SELL',
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
                            print('Exit not match')
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

def stetergytosendalert(data):
       df_1min = aggregate_data(data, '1T').tail(100)
       df_5min = aggregate_data(data, '5T').tail(100)
       df_15min = aggregate_data(data, '15T').tail(100)
       df_30min = aggregate_data(data, '30T').tail(10)

       itemlow = data.low.values[-1]
       itemhigh = data.high.values[-1]

       preitemlow = data.low.values[-2]
       preitemhigh = data.high.values[-2]

       itemclose = data.close.values[-1]
       symbol = 'NIFTY'
       getdata = crete_update_table.fetchsupport()
       supportprice1min = [a for a in getdata if a['timeframe'] == '1m']
       supportprice5min = [a for a in getdata if a['timeframe'] == '5m']
       supportprice15min = [a for a in getdata if a['timeframe'] == '15m']
       supportprice30min = [a for a in getdata if a['timeframe'] == '30m']
       #print('set data',supportprice1min[0]['supportlist'],supportprice1min,supportprice5min,)
       if len(supportprice1min[0]['supportlist']) > 0:
           #print('check ----',supportprice1min[0]['supportlist'])
           supportlist = [float(a) for a in supportprice1min[0]['supportlist']]
           for a in supportlist:
              #print(a,'print a data',previtemclose)
              if a > df_1min.low.values[-2] and a < df_1min.close.values[-1]:
                              bot_message = f'braekout  in 1min timeframe status:BUY for {symbol} and the time is {datetime.datetime.now()} ordered price {itemclose}'
                              sendAlert(bot_message)
              elif a < df_1min.high.values[-2] and a > df_1min.close.values[-1]:
                              bot_message = f'braekout  in 1min timeframe status:SELL for {symbol} and the time is {datetime.datetime.now()} ordered price {itemclose}'
                              sendAlert(bot_message)
           else:
                  print('no 1 min support')
       else:
                    print('no 1min timeframe shows target')

       if len(supportprice5min[0]['supportlist']) > 0:
           supportlist5min = [float(a) for a in supportprice5min[0]['supportlist']]
           for a in supportlist5min:
              #print(a,'print a data',previtemclose)
              if a > df_5min.low.values[-2] and a < df_5min.close.values[-1]:
                  bot_message = f'braekout  in 5 min timeframe status:BUY for {symbol} and the time is {datetime.datetime.now()} ordered price {itemclose}'
                  sendAlert(bot_message)
              elif a < df_5min.high.values[-2] and a > df_5min.close.values[-1]:
                  bot_message = f'braekout  in 5 min timeframe status:SELL for {symbol} and the time is {datetime.datetime.now()} ordered price {itemclose}'
                  sendAlert(bot_message)
           else:
               print('no 5min support hit')
       else:
                    print('no 5min timeframe shows target')

       if len(supportprice15min[0]['supportlist']) > 0:
           supportlist15min = [float(a) for a in supportprice15min[0]['supportlist']]
           for a in supportlist15min:
              #print(a,'print a data',previtemclose)
              if a > df_15min.low.values[-2] and a < df_15min.close.values[-1]:
                  bot_message = f'braekout  in 15 min timeframe status:BUY for {symbol} and the time is {datetime.datetime.now()} ordered price {itemclose}'
                  sendAlert(bot_message)
              elif a < df_15min.high.values[-2] and a > df_15min.close.values[-1]:
                  bot_message = f'braekout  in 15 min timeframe status:SELL for {symbol} and the time is {datetime.datetime.now()} ordered price {itemclose}'
                  sendAlert(bot_message)

           else:
                  print('no 15 min support hit')
       else:
                    print('no 15min timeframe shows target')

       if len(supportprice30min[0]['supportlist']) > 0:
           supportlist30min = [float(a) for a in supportprice30min[0]['supportlist']]
           for a in supportlist30min:
               # print(a,'print a data',previtemclose)
               if a > df_30min.low.values[-2] and a < df_30min.close.values[-1]:
                   bot_message = f'braekout  in 30 min timeframe status:BUY for {symbol} and the time is {datetime.datetime.now()} ordered price {itemclose}'
                   sendAlert(bot_message)
               elif a < df_30min.high.values[-2] and a > df_30min.close.values[-1]:
                   bot_message = f'braekout  in 30 min timeframe status:SELL for {symbol} and the time is {datetime.datetime.now()} ordered price {itemclose}'
                   sendAlert(bot_message)
           else:
                   print("no 30 min support hit")
       else:
                        print('no 30 min support hit')



def stetergycheck1min(symbol):
    try:
        username = 'YourTradingViewUsername'
        password = 'YourTradingViewPassword'

        tv = TvDatafeed(username, password)
        data = tv.get_hist(symbol='NIFTY', exchange='NSE', interval=Interval.in_1_minute, n_bars=2000)
        #print(data)
        if data is not None:
            df = pd.DataFrame(
                data,
                columns=['date', 'open', 'high', 'low', 'close', 'volume'])
            df["timestamp"] = pd.date_range(pd.Timestamp.now(), periods=len(df), freq='T')

            # Aggregate to 5-minute, 15-minute, and 30-minute time frames
            df_1min = aggregate_data(df, '1T').tail(100)
            df_5min = aggregate_data(df, '5T').tail(100)
            df_15min = aggregate_data(df, '15T').tail(300)
            stetergytosendalert(df)

        else:
            print('df is none')
    except Exception as e:
        print('error',e)


# Function to aggregate data to different time frames
def aggregate_data(df, time_frame):
    resampled_df = df.resample(time_frame).agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last'
    })
    return resampled_df

def stetergycheck5min(symbol):
    try:
        username = 'YourTradingViewUsername'
        password = 'YourTradingViewPassword'

        tv = TvDatafeed(username, password)
        df = tv.get_hist(symbol=symbol, exchange='NSE', interval=Interval.in_5_minute, n_bars=100)
        if df is not None:
            resistancelevel = []
            supportlevel = []
            itemclose = df.close.values[-1]
            previtemclose = df.close.values[-2]

            supports = df[df.low == df.low.rolling(10, center=True).min()].low
            resistances = df[df.high == df.high.rolling(10, center=True).max()].high

            level = pd.concat([supports, resistances])
            level = level[abs(level.diff()) > 10]

            #return df, level, registance_item, support_item
            if level is not None:
                for a in level:
                    if a > itemclose and a < previtemclose:
                          bot_message = f'braekout  in 1mi timeframe status:SELL for {symbol} and the time is {datetime.datetime.now()} ordered price {itemclose}'
                          sendAlert(bot_message)
                    elif a < itemclose and a > previtemclose:
                          bot_message = f'braekout  in 1mi timeframe status:BUY for {symbol} and the time is {datetime.datetime.now()} ordered price {itemclose}'
                          sendAlert(bot_message)
            else:
                print('no 5min timeframe shows target')

        else:
            print('5min i df is blank')
    except Exception as e:
        print('error',e)

def stetergycheck15min(symbol):
    try:
        username = 'YourTradingViewUsername'
        password = 'YourTradingViewPassword'

        tv = TvDatafeed(username, password)
        df = tv.get_hist(symbol=symbol, exchange='NSE', interval=Interval.in_15_minute, n_bars=100)

        resistancelevel = []
        supportlevel = []
        itemclose = df.close.values[-1]
        previtemclose = df.close.values[-2]

        supports = df[df.low == df.low.rolling(10, center=True).min()].low
        resistances = df[df.high == df.high.rolling(10, center=True).max()].high

        level = pd.concat([supports, resistances])
        level = level[abs(level.diff()) > 10]

        #return df, level, registance_item, support_item
        if level is not None:
            for a in level:
                if a > itemclose and a < previtemclose:
                      bot_message = f'braekout  in 1mi timeframe status:SELL for {symbol} and the time is {datetime.datetime.now()} ordered price {itemclose}'
                      sendAlert(bot_message)
                elif a < itemclose and a > previtemclose:
                      bot_message = f'braekout  in 1mi timeframe status:BUY for {symbol} and the time is {datetime.datetime.now()} ordered price {itemclose}'
                      sendAlert(bot_message)
        else:
            print('no 15min timeframe shows target')
    except Exception as e:
        print('error',e)

def stetergycheck30min(symbol):
    try:
        username = 'YourTradingViewUsername'
        password = 'YourTradingViewPassword'

        tv = TvDatafeed(username, password)
        df = tv.get_hist(symbol=symbol, exchange='NSE', interval=Interval.in_30_minute, n_bars=100)

        resistancelevel = []
        supportlevel = []
        itemclose = df.close.values[-1]
        previtemclose = df.close.values[-2]

        supports = df[df.low == df.low.rolling(10, center=True).min()].low
        resistances = df[df.high == df.high.rolling(10, center=True).max()].high

        level = pd.concat([supports, resistances])
        level = level[abs(level.diff()) > 10]

        #return df, level, registance_item, support_item
        if level is not None:
            for a in level:
                if a > itemclose and a < previtemclose:
                      bot_message = f'braekout  in 1mi timeframe status:SELL for {symbol} and the time is {datetime.datetime.now()} ordered price {itemclose}'
                      sendAlert(bot_message)
                elif a < itemclose and a > previtemclose:
                      bot_message = f'braekout  in 1mi timeframe status:BUY for {symbol} and the time is {datetime.datetime.now()} ordered price {itemclose}'
                      sendAlert(bot_message)
        else:
            print('no 30min timeframe shows target')
    except Exception as e:
        print('error',e)

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
#getorderBook()
fetchdataandreturn_pivot()
strategy()
schedule.every(20).seconds.do(getorderBook)
#schedule.every(1).minutes.do(stetergycheck1min,'NIFTY') #call every 1min to check support and registance
# schedule.every(40).seconds.do(stetergycheck5min,'NIFTY') #call every 5min to check support and registance
# schedule.every(50).seconds.do(stetergycheck15min,'NIFTY') #call every 15min to check support and registance
# schedule.every(60).seconds.do(stetergycheck30min,'NIFTY') #call every 30min to check support and registance

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

