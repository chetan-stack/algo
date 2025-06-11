import datetime
import json
from datetime import timedelta
# from datetime import datetime, timedelta
# from datetime import datetime
import re
import threading
import time

import yfinance as yf
import pandas_ta as ta

import requests
from tabulate import tabulate

from SmartApi import SmartConnect  # or from SmartApi.smartConnect import SmartConnect
import schedule
from tvDatafeed import TvDatafeed, Interval
import pandas as pd
import crete_update_table
import getoptionchain
import storetoken
import document
import pyotp
import storecandlestickdata
import logging
import mplfinance as mpf

logging.basicConfig(
    filename='optionsorderlog2.log',  # Name of the log file
    level=logging.INFO,  # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format
    datefmt='%Y-%m-%d %H:%M:%S'  # Date format in logs
)


api_key = document.api_key
user_id = document.user_id
password = document.password
totp = pyotp.TOTP(document.totp).now()
obj = SmartConnect(api_key=api_key)
token = obj.generateToken(obj.generateSession(user_id, password, totp)["data"]["refreshToken"])

username = 'YourTradingViewUsername'
password = 'YourTradingViewPassword'

tv = TvDatafeed(username, password)

timeframe_map = {
    '1m': Interval.in_1_minute,
    # '5m': Interval.in_5_minute,
    # '15m': Interval.in_15_minute,
    # '30m': Interval.in_30_minute,
}

nsechange = {
    'NIFTY':'NSE',
    'BANKNIFTY':'NSE',
    'SENSEX':'BSE'

}

fochange = {
    'NIFTY':'NFO',
    'BANKNIFTY':'NFO',
    'SENSEX':'BFO'
}

symbols = {
    "NIFTY": 'NIFTY',
    "BANKNIFTY": 'BANKNIFTY',
    'SENSEX':'SENSEX'
}

current_date_time = datetime.datetime.now()
from_date = current_date_time - timedelta(days = 1)
DATA_FILE = "auto_trade.json"  # File to store form data


# Function to load stored data
def load_data():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)  # Read existing data
    except (FileNotFoundError, json.JSONDecodeError):
        return {}  # Return empty if file not found or corrupted


limitorder = 2
linitedprofit = 2000


# def fetchdataandreturn_pivot():
#     username = 'YourTradingViewUsername'
#     password = 'YourTradingViewPassword'
#
#     tv = TvDatafeed(username, password)
#     # index
#     nifty_index_data = tv.get_hist(symbol='NIFTY', exchange='NSE', interval=Interval.in_daily, n_bars=3)
#     data = nifty_index_data
#     # print(data['high'].values[-2], data['low'].values[-2], data['close'].values[-2])
#     high_price = data['high'].values[-2]
#     low_price = data['low'].values[-2]
#     close_price = data['close'].values[-2]
#     datafile = []
#     # print(high_price, low_price, close_price)
#     # Calculate Fibonacci Levels
#     pi = (high_price + low_price + close_price) / 3
#     R1 = pi + (0.382 * (high_price - low_price))
#     R2 = pi + (0.6182 * (high_price - low_price))
#     R3 = R2 + (R2 - R1)
#     S1 = pi - (0.382 * (high_price - low_price))
#     S2 = pi - (0.6182 * (high_price - low_price))
#     S3 = S2 - (R1 - S1)
#     fibonacci_levels = {
#         'p': round(pi, 2),
#         's1': round(S1, 2),
#         'r1': round(R1, 2),
#         's2': round(S2, 2),
#         'r2': round(R2, 2),
#         'r3': round(R3, 2),
#         's3': round(S3, 2)
#     }
#
#     global pivot_fibo_level
#     pivot_fibo_level = fibonacci_levels
#     print(pivot_fibo_level)


def fetchdataandreturn_pivot():
    username = 'YourTradingViewUsername'
    password = 'YourTradingViewPassword'

    tv = TvDatafeed(username, password)

    # Initialize an array to store the levels for each symbol
    pivot_fibo_levels_array = []
    # Loop through each symbol in the symbols dictionary
    for symbol_name, symbol_code in symbols.items():
        # print(symbol_code,nsechange[symbol_code])
        index_data = tv.get_hist(symbol=symbol_code, exchange=nsechange[symbol_code], interval=Interval.in_daily, n_bars=3)
        data = index_data
        # print(data)
        high_price = data['high'].values[-2]
        low_price = data['low'].values[-2]
        close_price = data['close'].values[-2]

        # Calculate Fibonacci Levels
        pi = (high_price + low_price + close_price) / 3
        R1 = pi + (0.382 * (high_price - low_price))
        R2 = pi + (0.6182 * (high_price - low_price))
        R3 = high_price + 2 * (pi - low_price)
        S1 = pi - (0.382 * (high_price - low_price))
        S2 = pi - (0.6182 * (high_price - low_price))
        S3 = S2 - (R1 - S1)

        fibonacci_levels = {
            'symbol': symbol_name,
            'p': round(pi, 2),
            's1': round(S1, 2),
            'r1': round(R1, 2),
            's2': round(S2, 2),
            'r2': round(R2, 2),
            'r3': round(R3, 2),
            's3': round(S3, 2)
        }

        # Append the levels to the array
        pivot_fibo_levels_array.append(fibonacci_levels)

    # Print or return the array with the Fibonacci levels for each symbol

    global pivot_fibo_level
    pivot_fibo_level = pivot_fibo_levels_array
    print(pivot_fibo_level)
    # return pivot_fibo_levels_array



def fetch_and_process_data(symbol, interval, n_bars, rolling_window, level_diff_threshold):
    try:
        df = tv.get_hist(symbol=symbol, exchange=nsechange[symbol], interval=interval, n_bars=100)
        df['Supertrend'] = ta.supertrend(df['high'], df['low'], df['close'], length=10,
                          multiplier=2)['SUPERT_10_2.0']

        # Check if the last three Supertrend values are the same
        if df['Supertrend'].values[-3] == df['Supertrend'].values[-2] == \
                df['Supertrend'].values[-1]:
            trend_status = '0'  # All values are the same
        else:
            trend_status = '1'  # Values are different
         # Calculate EMA 9 and EMA 20
        data = df
        trend_duration=3
        data['ema_9'] = data['close'].ewm(span=9).mean()
        data['ema_20'] = data['close'].ewm(span=20).mean()
        data['ema_50'] = data['close'].ewm(span=50).mean()
        data['ema_100'] = data['close'].ewm(span=100).mean()

        # Support Detection
        data['support_on_9ema'] = (data['close'] >= data['ema_9']) & (
            abs(data['close'] - data['ema_9']) <= 0.01 * data['ema_9'])

        data['support_on_20ema'] = (data['close'] >= data['ema_20']) & (
            abs(data['close'] - data['ema_20']) <= 0.01 * data['ema_20'])

        data['support_on_50ema'] = (data['close'] >= data['ema_50']) & (
            abs(data['close'] - data['ema_50']) <= 0.01 * data['ema_50'])

        data['support_on_100ema'] = (data['close'] >= data['ema_100']) & (
            abs(data['close'] - data['ema_100']) <= 0.01 * data['ema_100'])




        data['resistance_on_9ema'] = (data['close'] <= data['ema_9']) & (
            abs(data['close'] - data['ema_9']) <= 0.01 * data['ema_9'])

        data['resistance_on_20ema'] = (data['close'] <= data['ema_20']) & (
            abs(data['close'] - data['ema_20']) <= 0.01 * data['ema_20'])

        data['resistance_on_50ema'] = (data['close'] <= data['ema_50']) & (
            abs(data['close'] - data['ema_50']) <= 0.01 * data['ema_50'])

        data['resistance_on_100ema'] = (data['close'] <= data['ema_100']) & (
            abs(data['close'] - data['ema_100']) <= 0.01 * data['ema_100'])



        # Shifted values for crossover detection
        data['prev_ema_9'] = data['ema_9'].shift(1)
        data['prev_ema_20'] = data['ema_20'].shift(1)

        # Detect Bullish and Bearish Crossovers
        data['bullish_crossover'] = (data['prev_ema_9'] < data['prev_ema_20']) & (data['ema_9'] > data['ema_20'])
        data['bearish_crossover'] = (data['prev_ema_9'] > data['prev_ema_20']) & (data['ema_9'] < data['ema_20'])

        # Detect Retests
        data['retest'] = abs(data['close'] - data['ema_9']) <= 0.01 * data['ema_9']  # Retest within 1% of EMA 9

        # EMA Trend Detection
        data['ema_9_slope'] = data['ema_9'] - data['ema_9'].shift(1)
        data['ema_20_slope'] = data['ema_20'] - data['ema_20'].shift(1)

        # Trend Confirmation
        data['bullish_trend'] = (data['ema_9'] > data['ema_20']) & (data['ema_9_slope'] > 0)
        data['bearish_trend'] = (data['ema_9'] < data['ema_20']) & (data['ema_9_slope'] < 0)

        # Prolonged Trend Detection
        data['bullish_trend_duration'] = data['bullish_trend'].rolling(trend_duration).sum() >= trend_duration
        data['bearish_trend_duration'] = data['bearish_trend'].rolling(trend_duration).sum() >= trend_duration
        # print(data['bearish_trend_duration'])
        # Buy/Sell Signals
        data['buy_signal'] = data['bullish_crossover'] & data['retest'] & data['bullish_trend_duration']
        data['sell_signal'] = data['bearish_crossover'] & data['retest'] & data['bearish_trend_duration']
        # Add the result as a new column (optional)
        df.loc[df.index[-1], 'Trend_Status'] = trend_status
        # print(df)
        if df is not None:
            # df.ema = ta.ema(df.close, length=9)
            # print('ema', df.ema.values[-1])
            resistancelevel = []
            supportlevel = []
            itemclose = df.close.values[-1]

            supports = df[df.low == df.low.rolling(rolling_window, center=True).min()].close
            resistances = df[df.high == df.high.rolling(rolling_window, center=True).max()].close

            level = pd.concat([supports, resistances])
            level = level[abs(level.diff()) > level_diff_threshold]

            for a in level:
                if a > itemclose:
                    resistancelevel.append(a)
                else:
                    supportlevel.append(a)

            # Handle empty lists
            if resistancelevel:
                registance_item = max(resistancelevel, key=lambda x: x if x > itemclose else float('-inf'))
            else:
                registance_item = None

            if supportlevel:
                support_item = max(supportlevel, key=lambda x: x if x < itemclose else float('-inf'))
            else:
                support_item = None
            return True, level, df
            # return df, level, registance_item, support_item,itemclose
        else:
            return False, 'no', df
    except Exception as e:
        print('error', e)


# def storesupportlevel():
#     for script,token in symbols.items():
#         for interval,key in timeframe_map.items():
#
#             fetch_and_process_data(script, key, '100', '20', '20')
storedata = []


# def checktable(timeframe,symbol):
#     fetchdta = crete_update_table.fetchsupport()
#     for person in fetchdta:
#         if person["timeframe"] == timeframe and person["symbol"] == symbol:
#             return person["id"]
#     return None


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


def defineresistancelevel(fibo_level, close):
    # Filter out any string values from the fibo_level dictionary
    filtered_data = {key: value for key, value in fibo_level.items() if isinstance(value, (int, float))}

    # Find keys where the value is greater than or equal to the close value
    matching_keys = [key for key, value in filtered_data.items() if value >= close]

    # Get the key corresponding to the smallest value among the matching keys
    max_key = min(matching_keys, key=lambda k: filtered_data[k], default='p')

    return max_key

def definesupportlevel(fibo_level, close):
    # Filter out any string values from the fibo_level dictionary
    filtered_data = {key: value for key, value in fibo_level.items() if isinstance(value, (int, float))}

    # Find keys where the value is less than or equal to the close value
    matching_keys = [key for key, value in filtered_data.items() if value <= close]

    # Get the key corresponding to the largest value among the matching keys
    max_key = max(matching_keys, key=lambda k: filtered_data[k], default='p')

    return max_key

def find_pe_or_ce(text):
    results = ''
    if 'PE' in text:
        results = 'pe'
    if 'CE' in text:
        results = 'ce'
    return results

# def placeoptionsellorder(symbol,stickprice,exc,token,lotsize,ltp,interval,itemclose,condition,):
#     lotsize = int(lotsize)
#     print(lotsize)
#     logging.info(f"enter in sell {symbol},{stickprice},{token},{lotsize},{ltp},{interval},{itemclose} ")
#     checktype = find_pe_or_ce(stickprice)
#     logging.info(f"order type {checktype} ")
#     strickprice = itemclose + 1000 if checktype == 'ce' else itemclose - 1000 if checktype == 'pe' else 0
#     logging.info(f"strick ptice type {strickprice}")
#     cetoken, petoken = storetoken.placeorderdetails('NFO', 'OPTIDX', symbol, strickprice)
#     fetchdata = crete_update_table.fetchtokennbook()
#     filteristoken = [item for item in fetchdata if re.match(r'^[A-Za-z]+', item['script']).group() == symbol and item['lotsize'] < 0]
#     logging.info(f"alredy order place or not {filteristoken}")
#     if len(filteristoken) == 0:
#                 logging.info(f"enter bracket order")
#                 forltp = cetoken if checktype == 'ce' else petoken if checktype == 'pe' else 0
#                 ltpbuy = obj.ltpData(forltp['exch_seg'], forltp['symbol'], forltp['token'])['data']['ltp']
#                 logging.info(f"lpt for headage buy order: {ltpbuy}")
#                 lotsize -= (int(lotsize) + int(lotsize))
#                 print(lotsize)
#                 # lotsize = -25
#                 logging.info(f"sell place order lotsize : {lotsize}")
#                 # crete_update_table.inserttokenns(petoken['symbo23l'], petoken['exch_seg'], petoken['token'], petoken['lotsize'], ltpbuy, token) if checktype == 'pe' else crete_update_table.inserttokenns(cetoken['symbol'], cetoken['exch_seg'], cetoken['token'], cetoken['lotsize'], ltpbuy, token) if checktype == 'ce' else 'no order'
#                 # logging.info(f"place buy order {checktype}")
#                 #
#                 crete_update_table.inserttokenns(stickprice, petoken['exch_seg'], token, lotsize, ltp, '0')
#                 logging.info(f"place sell order {stickprice}")
#
#                 bot_message = f'braekout  in {interval} timeframe status:sell for {stickprice} Strickprice {stickprice}, Lotzise {lotsize},token {token}  and the time is {datetime.datetime.now()} ordered price {itemclose} and stick price {ltp}'
#                 sendAlert(bot_message)

# placeoptionsellorder([],[],'nifty',)
def placeoptionsellorder(df,level,symbol,stickprice,exc,token,lotsize,ltp,interval,itemclose,condition,):
    lotsize = int(lotsize)
    ltp = obj.ltpData(exc, stickprice, token)['data']['ltp']
    print(lotsize,stickprice)
    logging.info(f"enter in sell {symbol},{stickprice},{token},{lotsize},{ltp},{interval},{itemclose} ")
    checktype = find_pe_or_ce(stickprice)
    logging.info(f"order type {checktype} ")
    strickprice = itemclose + 1000 if checktype == 'ce' else itemclose - 1000 if checktype == 'pe' else 0
    logging.info(f"strick ptice type {strickprice}")
    print("----",strickprice,checktype,symbol,fochange[symbol])
    cetoken, petoken = storetoken.placeorderdetails(fochange[symbol], 'OPTIDX', symbol, strickprice)
    # print("----check",cetoken,petoken)
    fetchdata = crete_update_table.fetchtokennbook()
    filteristoken = [item for item in fetchdata if re.match(r'^[A-Za-z]+', item['script']).group() == symbol and item['lotsize'] < 0]
    logging.info(f"alredy order place or not {filteristoken}")
    if len(filteristoken) == 0:
                logging.info(f"enter bracket order")
                forltp = cetoken if checktype == 'ce' else petoken if checktype == 'pe' else 0
                ltpbuy = obj.ltpData(forltp['exch_seg'], forltp['symbol'], forltp['token'])['data']['ltp']
                # logging.info(f"lpt for headage buy order: {ltpbuy}")
                lotsize -= (int(lotsize) + int(lotsize))
                print(lotsize)
                # lotsize = -25
                logging.info(f"sell place order lotsize : {lotsize}")
                if checktype == 'pe':
                    crete_update_table.inserttokenns(petoken['symbol'], petoken['exch_seg'], petoken['token'], petoken['lotsize'], ltpbuy, token)
                elif checktype == 'ce':
                    crete_update_table.inserttokenns(cetoken['symbol'], cetoken['exch_seg'], cetoken['token'], cetoken['lotsize'], ltpbuy, token)
                else:
                    print('No order')
                # logging.info(f"place buy order {checktype}")
                #
                crete_update_table.inserttokenns(stickprice, exc, token, lotsize, ltp, '0')
                title = f"{symbol} - {interval}"
                add_plots = [
                    mpf.make_addplot(df['ema_9'], color='blue', label='9 EMA'),
                    mpf.make_addplot(df['ema_20'], color='orange', label='20 EMA')
                ]

                mpf.plot(df, type='candle', hlines=level.to_list(), addplot=add_plots, style='charles', title=title, savefig='static/chart.png')
                sendImgAlert("Here is an image:", "static/chart.png")
                logging.info(f"place sell order {stickprice}")
                bot_message = f'braekout  in {interval} timeframe status:sell for {stickprice} Strickprice {stickprice}, Lotzise {lotsize},token {token}  and the time is {datetime.datetime.now()} ordered price {itemclose} and stick price {ltp}'
                sendAlert(bot_message)



def stoplossarea(df,ltp,ordertype):
    target = ltp * 1.10
    stoploss = df.low.values[-2] if storedata == 1 else df.high.close[-2]
    change = df.high.values[-2] - df.low.values[-2]

# def getPremiumData(exchange, maintoken,stickprice):
#     logging.info(f"enter in premium data stuctutre{maintoken} exchange {exchange}")
#     current_date_time = datetime.datetime.now()
#     form_date = current_date_time - timedelta(days=3)
#     api_key = document.api_key
#     user_id = document.user_id
#     password = document.password
#     totp = pyotp.TOTP(document.totp).now()
#
#     obj = SmartConnect(api_key=api_key)
#     token = obj.generateToken(obj.generateSession(user_id, password, totp)["data"]["refreshToken"])
#     jwtToken = token['data']["jwtToken"]
#     refreshToken = token['data']['refreshToken']
#     feedToken = token['data']['feedToken']
#     print(feedToken)
#     try:
#
#         historicParam = {
#             "exchange": exchange,
#             "symboltoken": maintoken,
#             "interval": "ONE_MINUTE",
#             "fromdate": form_date.strftime("%Y-%m-%d 09:15"),
#             "todate": current_date_time.strftime("%Y-%m-%d %H:%M")
#         }
#         hist_data = obj.getCandleData(historicParam)["data"]
#         df = pd.DataFrame(hist_data,columns=['date', 'open', 'high', 'low', 'close', 'volume'])
#         logging.info(f'get premuim data succesfully')
#         df["sup"] = ta.supertrend(df['high'], df['low'], df['close'], length=10, multiplier=3)['SUPERT_10_3.0']
#         df["ema"] = ta.ema(df["close"], length=9)
#         df.dropna(inplace=True)
#         resistancelevel = []
#         supportlevel = []
#         itemclose = df.close.values[-1]
#         logging.info(f"premium data created")
#         supports = df[df.low == df.low.rolling(10, center=True).min()].close
#         resistances = df[df.high == df.high.rolling(10, center=True).max()].close
#
#         level = pd.concat([supports, resistances])
#         level = level[abs(level.diff()) > 10]
#         title = f"{stickprice} + 1m"
#         logging.info('all level created with timeframe 1m')
#         mpf.plot(df, type='candle', hlines=level.to_list(), style='charles',title=title, savefig='static/chart2.png')
#         sendImgAlert("Here is an image:", "static/chart2.png")
#         logging.info(f"create chart successfully for premium.")
#         return level,df
#     except Exception as e:
#         bot_message = f"Historic API failed: {e}"
#         sendAlert(bot_message)

def getPremiumData(exchange, maintoken,stickprice):
    current_date_time = datetime.datetime.now()
    form_date = current_date_time - timedelta(days=3)
    print(current_date_time,form_date)
    api_key = document.api_key
    user_id = document.user_id
    password = document.password
    totp = pyotp.TOTP(document.totp).now()

    obj = SmartConnect(api_key=api_key)
    token = obj.generateToken(obj.generateSession(user_id, password, totp)["data"]["refreshToken"])
    jwtToken = token['data']["jwtToken"]
    refreshToken = token['data']['refreshToken']
    feedToken = token['data']['feedToken']
    print(feedToken)
    try:

        historicParam = {
            "exchange": exchange,
            "symboltoken": maintoken,
            "interval": "ONE_MINUTE",
            "fromdate": form_date.strftime("%Y-%m-%d 09:15"),
            "todate": current_date_time.strftime("%Y-%m-%d %H:%M")
        }
        hist_data = obj.getCandleData(historicParam)["data"]
        storedata = hist_data[:100]
        df = pd.DataFrame(storedata,columns=['date', 'open', 'high', 'low', 'close', 'volume'])
        df["sup"] = ta.supertrend(df['high'], df['low'], df['close'], length=10, multiplier=3)['SUPERT_10_3.0']
        df["ema"] = ta.ema(df["close"], length=9)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        resistancelevel = []
        supportlevel = []
        itemclose = df.close.values[-1]
        supports = df[df.low == df.low.rolling(10, center=True).min()].close
        resistances = df[df.high == df.high.rolling(10, center=True).max()].close

        level = pd.concat([supports, resistances])
        level = level[abs(level.diff()) > 10]

        title = f"{stickprice} - 1m"
        logging.info('all level created with timeframe 1m')
        try:
            # ltp= 200.00
            # resistance = min([x for x in level if x > ltp], key=lambda x: abs(x - ltp), default=None)
            # support = min([x for x in level if x < ltp], key=lambda x: abs(x - ltp), default=None)
            # target = resistance if (resistance is not None and resistance < (ltp * 1.10)) else (ltp * 1.10)
            # stoploss = support if (support is not None and support > (ltp * 0.95)) else (ltp * 0.95)
            # # condition = df.close.values[-1] > df.ema.values[-1]
            # print(target,stoploss,support,resistance)
            mpf.plot(df, type='candle', hlines=level.to_list(), style='charles',title=title, savefig='static/chart.png')
            sendImgAlert("Here is an image:", "static/chart.png")
        except Exception as e:
            print(e)
            sendAlert(f"{e}")
        print('done')
        logging.info(f"create chart successfully for premium.")

        return level,df

    except Exception as e:
        bot_message = f"Historic API failed: {e}"
        # sendAlert(bot_message)


# def placebuyorder(symbol,stickprice,exc,token,lotsize,ltp,interval,itemclose,mainlevel,df):
#     bot_message = f'enter in place order {stickprice} {exc} {token}'
#     sendAlert(bot_message)
#     logging.info(f"enter in place buy order order : {stickprice},{exc},{token},{lotsize},{ltp},{interval},{itemclose} ")
#     checkprice = 10 if symbol == 'NIFTY' else 20 if symbol == 'BANKNIFTY' else 20
#     targetchange = (ltp * 1.10) - ltp
#     delta = 0
#     #ordertype = 1 if 'CE' in stickprice else 0
#     level,premiumdf = getPremiumData(exc,token,stickprice)
#     try:
#         resistance = min([x for x in level if x > ltp], key=lambda x: abs(x - ltp), default=None)
#         support = min([x for x in level if x < ltp], key=lambda x: abs(x - ltp), default=None)
#         target = resistance if (resistance is not None and resistance < (ltp * 1.10)) else (ltp * 1.10)
#         stoploss = support if (support is not None and support > (ltp * 0.95)) else (ltp * 0.95)
#
#         condition = premiumdf.close.values[-1] > premiumdf.ema.values[-1]
#         if condition:
#         # if True:
#             stickprice = f"{stickprice} - {target} - {stoploss}"
#             # crete_update_table.insert_place_order(symbol,exc,token,delta,itemclose,ltp,target,stoploss,lotsize,'0')
#             crete_update_table.inserttokenns(stickprice, exc, token, lotsize, ltp, '0')
#             bot_message = f'braekout  in {interval} level: {mainlevel} - {symbol} timeframe status:BUY for {stickprice} Strickprice {stickprice}, Lotzise {lotsize},token {token}  and the time is {datetime.datetime.now()} ordered price {itemclose} and stick price {ltp}'
#             sendAlert(bot_message)
#             logging.info(f"buy order place successfully for symbol {stickprice}" )
#
#         else:
#             data = {
#                 'targetchange': targetchange,
#                 'totaltarget': targetchange * lotsize,
#                 'buyprice': ltp,
#                 'symbol': symbol,
#                 'stickprice': stickprice
#             }
#             logging.info(f"not placing order for symbol {data}" )
#             bot_message = f'This order in not fit for good profit target is {data} '
#             sendAlert(bot_message)
#     except Exception as e:
#         bot_message = f"Historic API failed: {e}"
#         sendAlert(bot_message)

def placebuyorder(symbol,stickprice,exc,token,lotsize,ltp,interval,itemclose,mainlevel,df):
    crete_update_table.inserttokenns(stickprice, exc, token, lotsize, ltp, '0')
    bot_message = f'braekout  in {interval} level: {mainlevel} - {symbol} timeframe status:BUY for {stickprice} Strickprice {stickprice}, Lotzise {lotsize},token {token}  and the time is {datetime.datetime.now()} ordered price {itemclose} and stick price {ltp}'
    sendAlert(bot_message)
    logging.info(f"buy order place successfully for symbol {stickprice}" )

def sendImgAlert(bot_message, image_path=None):
    bot_token = "5707293106:AAEPkxexnIdoUxF5r7hpCRS_6CHINgU4HTw"
    bot_chatid = "2027669179"

    if image_path:
        # Send image
        url = f'https://api.telegram.org/bot{bot_token}/sendPhoto'
        with open(image_path, 'rb') as photo:
            response = requests.post(url, data={'chat_id': bot_chatid}, files={'photo': photo})
    else:
        # Send text message
        url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
        response = requests.post(url, data={'chat_id': bot_chatid, 'text': bot_message, 'parse_mode': 'MarkdownV2'})

    print(response)
    return response.json()

def stetergytosendalert(script, interwal, data, level, closehigh, closelow,tdf):
    df = data
    sup = df['Trend_Status'].values[-1]

    itemclose = data.close.values[-1]
    symbol = script
    # getdata = crete_update_table.fetchsupport()
    cetoken, petoken = storetoken.placeorderdetails(fochange[script], 'OPTIDX', symbol, df.close.values[-1])
    df['Candle_Color'] = 1  # Initialize with a value indicating green candles
    df.loc[df['close'] < df['open'], 'Candle_Color'] = 0
    print(cetoken['symbol'], petoken['symbol'])
    logging.info(f"sup is 0 then side ways market - sup value: {sup}")
    # if len(data) > 0 and sup == '1':
    if len(data) > 0:

        print('enter')
        # Start a new thread for plotting
        data = storecandlestickdata.createchart(script,interwal,df,level)


        print(data)

        cetrue = (closehigh < df.close.values[-1]) if closehigh != '' else True
        petrue = (closelow > df.close.values[-1]) if closelow != '' else True
        logging.info(f"symbol {script} - interval {interwal} - pe {petrue} - ce {cetrue} - timeframe {tdf}")
        for a in level:
            # print(a,'print a data',previtemclose)
            if a > df.low.values[-2] and a < df.close.values[-1] and df.Candle_Color.values[-1] == 1 and cetrue:
                logging.info(f"first level check for call : a > df.low.values[-2] and a < df.close.values[-1] and df.Candle_Color.values[ -1] == 1 and cetrue{cetrue} ")
                cetoken,petoken = storetoken.placeorderdetails('NSE', 'OPTIDX', symbol, df.close.values[-1])
                ce_format(cetoken,symbol,interwal,level,itemclose,df,'buy check on support and registance')
                # if getoptionchain.getparams(symbol, df.close.values[-1], 'ce'):
                #     logging.info(f"option chain : True ")
                #     # cetoken,petoken = storetoken.placeorderdetails('NSE', 'OPTIDX', symbol, df.close.values[-1])
                #     stickprice = cetoken['symbol']
                #     lotsize = cetoken['lotsize']
                #     token = cetoken['token']
                #     # print('token details :',cetoken['symbol'],stickprice,lotsize)
                #     ltp = obj.ltpData(cetoken['exch_seg'], stickprice, token)['data']['ltp']
                #     fetchdata = crete_update_table.fetchtokennbook()
                #     filteristoken = [item for item in fetchdata if
                #                      re.match(r'^[A-Za-z]+', item['script']).group() == symbol and item['lotsize'] > 0]
                #     if len(filteristoken) == 0:
                #         logging.info(f"place order : True ")
                #         placebuyorder(symbol,stickprice, cetoken['exch_seg'], token, lotsize, ltp,interwal,itemclose,a,df)
                #         title = f"{symbol} - {interwal}"
                #         mpf.plot(df, type='candle', hlines=level.to_list(), style='charles',title=title, savefig='static/chart.png')
                #         sendImgAlert("Here is an image:", "static/chart.png")
                #     placeoptionsellorder(symbol,stickprice,token,lotsize,ltp,interwal,itemclose)

            elif a < df.high.values[-2] and a > df.close.values[-1] and df.Candle_Color.values[-1] == 0 and petrue:
                logging.info(f"second level check for put : a < df.high.values[-2] and a > df.close.values[-1] and df.Candle_Color.values[-1] == 0 and petrue{petrue}")
                cetoken,petoken = storetoken.placeorderdetails('NSE', 'OPTIDX', symbol, df.close.values[-1])
                pe_format(petoken,symbol,interwal,level,itemclose,df,'sell side order place')
                # if getoptionchain.getparams(symbol, df.close.values[-1], 'pe'):
                #     logging.info(f"level 2 : option chain : True ")
                #     # cetoken,petoken = storetoken.placeorderdetails('NSE', 'OPTIDX', symbol, df.close.values[-1])
                #     stickprice = petoken['symbol']
                #     lotsize = petoken['lotsize']
                #     token = petoken['token']
                #     ltp = obj.ltpData(petoken['exch_seg'], stickprice, token)['data']['ltp']
                #     fetchdata = crete_update_table.fetchtokennbook()
                #     filteristoken = [item for item in fetchdata if
                #                      re.match(r'^[A-Za-z]+', item['script']).group() == symbol and item['lotsize'] > 0]
                #     if len(filteristoken) == 0:
                #         logging.info(f"level 2 : place order : True ")
                #         placebuyorder(symbol,stickprice, petoken['exch_seg'], token, lotsize, ltp,interwal,itemclose,a,df)
                #         title = f"{symbol} - {interwal}"
                #         mpf.plot(df, type='candle', hlines=level.to_list(), style='charles',title=title, savefig='static/chart.png')
                #         sendImgAlert("Here is an image:", "static/chart.png")
                #     placeoptionsellorder(symbol,stickprice,token,lotsize,ltp,interwal,itemclose)


        else:
            print('no support zone')
            logging.info(f"no biying level for {script} for interval {interwal}")
    else:
        print(f'data length : {len(data)} or may be side ways market sup value : {sup}')


def pivotpointstatergy(script, interwal, data, level, closehigh, closelow,tdf):
    logging.info(f"interval {interwal} enter in pivot level")
    df = data
    deflevel = [item for item in pivot_fibo_level if item['symbol'] == script]
    sup = df['Trend_Status'].values[-1]
    print('pivot levels',deflevel[0])
    pivotlevel = deflevel[0]
    r_level = defineresistancelevel(pivotlevel, df.close.values[-1])
    s_level = definesupportlevel(pivotlevel, df.close.values[-1])
    print(r_level,s_level,pivotlevel[r_level],pivotlevel[s_level])
    itemlow = data.low.values[-1]
    itemhigh = data.high.values[-1]

    preitemlow = data.low.values[-2]
    preitemhigh = data.high.values[-2]

    itemclose = data.close.values[-1]
    symbol = script
    # getdata = crete_update_table.fetchsupport()
    cetoken, petoken = storetoken.placeorderdetails(fochange[script], 'OPTIDX', symbol, df.close.values[-1])
    df['Candle_Color'] = 1  # Initialize with a value indicating green candles
    df.loc[df['close'] < df['open'], 'Candle_Color'] = 0
    print(cetoken['symbol'], petoken['symbol'])
    logging.info(f"sup is 0 then side ways market - sup value: {sup}")
    if len(data) > 0:

    # if len(data) > 0 and sup == '1':
        cetrue = (closehigh < df.close.values[-1]) if closehigh != '' else True
        petrue = (closelow > df.close.values[-1]) if closelow != '' else True
        logging.info(f"symbol {script} - interval {interwal} - pe {petrue} - ce {cetrue} - timeframe {tdf}")

        if df.low.values[-2] < pivotlevel[s_level] and df.close.values[-1] > pivotlevel[s_level] and df.Candle_Color.values[-1] == 1 and cetrue:
            logging.info(f"third level for pivot point : df.low.values[-2] < pivotlevel[s_level] and df.close.values[-1] > pivotlevel[s_level] and cetrue{cetrue}")
            cetoken,petoken = storetoken.placeorderdetails('NSE', 'OPTIDX', symbol, df.close.values[-1])
            ce_format(cetoken,symbol,interwal,level,itemclose,df,'buy check on support and registance')
            # if getoptionchain.getparams(symbol, df.close.values[-1], 'ce'):
            #     logging.info(f"level 3 : option chain : True ")
            #     # cetoken,petoken = storetoken.placeorderdetails('NSE', 'OPTIDX', symbol, df.close.values[-1])
            #     stickprice = cetoken['symbol']
            #     lotsize = cetoken['lotsize']
            #     token = cetoken['token']
            #     # print('token details :',cetoken['symbol'],stickprice,lotsize)
            #     ltp = obj.ltpData(cetoken['exch_seg'], stickprice, token)['data']['ltp']
            #     fetchdata = crete_update_table.fetchtokennbook()
            #     filteristoken = [item for item in fetchdata if
            #                      re.match(r'^[A-Za-z]+', item['script']).group() == symbol and item['lotsize'] > 0]
            #     if len(filteristoken) == 0:
            #         logging.info(f"level 3 : place order : True ")
            #         placebuyorder(symbol,stickprice, cetoken['exch_seg'], token, lotsize, ltp,interwal,itemclose,s_level,df)
            #
            #     # placeoptionsellorder(symbol,stickprice,token,lotsize,ltp,interwal,itemclose)

        elif df.high.values[-2] > pivotlevel[r_level] and df.close.values[-1] < pivotlevel[r_level] and df.Candle_Color.values[-1] == 0 and petrue:
            logging.info(f"fourth level for pivot point : df.high.values[-2] > pivotlevel[r_level] and df.close.values[-1] < pivotlevel[r_level] and petrue {petrue}")
            cetoken,petoken = storetoken.placeorderdetails('NSE', 'OPTIDX', symbol, df.close.values[-1])
            pe_format(petoken,symbol,interwal,level,itemclose,df,'sell side order place')
            # if getoptionchain.getparams(symbol, df.close.values[-1], 'pe'):
            #     logging.info(f"level 4 : option chain : True ")
            #     # cetoken,petoken = storetoken.placeorderdetails('NSE', 'OPTIDX', symbol, df.close.values[-1])
            #     stickprice = petoken['symbol']
            #     lotsize = petoken['lotsize']
            #     token = petoken['token']
            #     ltp = obj.ltpData(petoken['exch_seg'], stickprice, token)['data']['ltp']
            #     fetchdata = crete_update_table.fetchtokennbook()
            #     filteristoken = [item for item in fetchdata if
            #                      re.match(r'^[A-Za-z]+', item['script']).group() == symbol and item['lotsize'] > 0]
            #     if len(filteristoken) == 0:
            #         logging.info(f"level 4 : place order : True ")
            #         placebuyorder(symbol,stickprice, petoken['exch_seg'], token, lotsize, ltp,interwal,itemclose,s_level,df)
            #
            #     # placeoptionsellorder(symbol,stickprice,token,lotsize,ltp,interwal,itemclose)


    else:
        print('no support zone')
        logging.info(f"no biying level for {script} for interval {interwal}")



def aggregate_data(df, time_frame):
    resampled_df = df.resample(time_frame).agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last'
    })
    return resampled_df

# def storesupportlevel():
#     print('start stetergy')
#     closehigh = ''
#     closelow = ''
#     for script, token in symbols.items():
#         result1, level1, data = fetch_and_process_data(script, Interval.in_1_minute, '100', 20, 20)
#         print('success',result1)
#         # time.sleep(2)
#         for interval, key in timeframe_map.items():
#             result, level, df = fetch_and_process_data(script, key, '100', 20, 20)
#
#             if result1:
#                 print('level', level)
#
#                 df_5min = aggregate_data(data, '5T').tail(10)
#                 closehigh = df_5min.high.values[-2]
#                 closelow = df_5min.low.values[-2]
#                 change = closehigh - closelow
#                 if change > 20 and script == 'NIFTY' or change > 40 and script == 'BANKNIFTY':
#                     # merged_array = level + pivot_fibo_level  # Merging the two arrays
#                     stetergytosendalert(script, interval, data, level, closehigh, closelow)
#                 else:
#                     df_15min = aggregate_data(data, '15T').tail(10)
#                     closehigh = df_15min.high.values[-2]
#                     closelow = df_15min.low.values[-2]
#                     change = closehigh - closelow
#                     if change > 20 and script == 'NIFTY' or change > 40 and script == 'BANKNIFTY':
#                             stetergytosendalert(script, interval, data, level, closehigh, closelow)
#
#                     else:
#                         print('Side Ways Market')
#
#                 # fetchdta = crete_update_table.fetchsupport()
#                 # string_result = ' '.join(map(str, level.to_list()))
#                 # print(len(fetchdta))
#                 # if len(fetchdta) > 0:
#                 #     stetergytosendalert(script,interval,df,level)
#                 #     getid = checktable(interval,script)
#                 #     if getid is not None:
#                 #             crete_update_table.updatesupport(getid,string_result)
#                 #     else:
#                 #             crete_update_table.createupport(interval,string_result,script)
#                 #
#                 # else:
#                 #     crete_update_table.createupport(interval,string_result,script)
#
#                 # print('store data',fetchdta)

def place_order(token, symbol, qty, exch_seg, buy_sell, ordertype, price):
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
        # orderId = obj.placeOrder(orderparams)
        orderId = 1
        # print(orderId)

        if orderId:
            # orderId = obj.placeOrder(orderparams)
            print(
                    f"{buy_sell} order Place for {symbol} at : {datetime.datetime.now()} with Order id {orderId}"
                )
            bot_message = f'order status:{buy_sell} for {symbol} with price {token} and the time is {datetime.datetime.now()}'
            sendAlert(bot_message)
            return orderId,True
        else:
            return orderId,False



def calculate_atr(df, period=5):
    """
    Calculate ATR for 1-minute data (shorter period).
    """
    df['H-L'] = df['high'] - df['low']
    df['H-PC'] = abs(df['high'] - df['close'].shift(1))
    df['L-PC'] = abs(df['low'] - df['close'].shift(1))
    df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
    df['ATR'] = df['TR'].rolling(window=period).mean()
    return df

def determine_target_method_1min(df, symbol, swing_lookback=8, atr_threshold=None, use_dynamic_threshold=True):
    """
    Decide between Fibonacci and ATR-based target/stoploss for 1-min option premium data.

    Parameters:
    - df: DataFrame with 'high', 'low', 'close'
    - symbol: Option symbol
    - swing_lookback: Number of candles to check swing range
    - atr_threshold: Optional fixed threshold for swing_range / (ATR * lookback)
    - use_dynamic_threshold: If True, sets atr_threshold using past data

    Returns:
    - dict with entry, target, stoploss, method, reason
    """
    print('--------------ENTER: define target logic')

    # === Validate data
    if df.shape[0] < swing_lookback + 1:
        return {"error": f"Not enough data to compute target for {symbol}"}

    df = calculate_atr(df)
    recent = df.iloc[-swing_lookback:]
    swing_high = recent['high'].max()
    swing_low = recent['low'].min()
    entry_price = recent.iloc[-1]['close']
    atr = recent.iloc[-1]['ATR']

    swing_range = swing_high - swing_low
    atr_strength_ratio = swing_range / (atr * swing_lookback)

    # === Dynamic Threshold Option ===
    if use_dynamic_threshold and atr_threshold is None:
        # Calculate a median ratio over last 20 windows as baseline
        rolling_ratios = []
        for i in range(20, len(df) - swing_lookback):
            temp = df.iloc[i:i + swing_lookback]
            temp_range = temp['high'].max() - temp['low'].min()
            temp_atr = temp.iloc[-1]['ATR']
            ratio = temp_range / (temp_atr * swing_lookback)
            rolling_ratios.append(ratio)
        atr_threshold = round(np.median(rolling_ratios), 2) if rolling_ratios else 0.9

    print(f"Symbol: {symbol}, Entry: {entry_price:.2f}, ATR: {atr:.2f}, Range/ATR: {atr_strength_ratio:.2f}, Threshold: {atr_threshold}")

    result = {
        'symbol': symbol,
        'entry_price': round(entry_price, 2),
        'atr': round(atr, 2)
    }

    # === Decision: Trend or Choppy
    if atr_strength_ratio > atr_threshold:
        # Trending → Use Fibonacci
        fib_target = swing_high + (swing_range * 0.618)
        result.update({
            'method': 'fibonacci',
            'target_price': round(fib_target, 2),
            'stoploss_price': round(swing_low, 2),
            'reason': f"Trending (range/ATR={atr_strength_ratio:.2f}) > threshold={atr_threshold} → Fibonacci"
        })
    else:
        # Choppy → Use ATR-based
        fib_target = swing_high + (swing_range * 0.618)
        atr_target = entry_price + (atr * 1.0)
        atr_stoploss = entry_price - (atr * 1.0)
        result.update({
            'method': 'atr',
            'target_price': round(atr_target, 2),
            'stoploss_price': round(atr_stoploss, 2),
            'fibotarget_price': round(fib_target, 2),
            'fibostoploss_price': round(swing_low, 2),
            'reason': f"Choppy (range/ATR={atr_strength_ratio:.2f}) ≤ threshold={atr_threshold} → ATR"
        })

    return result

def storetarget(targetresult,symbol):
    load = load_data()
    print("------------", load)

    if 'storetarget' not in load or not isinstance(load['storetarget'], list):
        load['storetarget'] = []

    updated = False
    for item in load['storetarget']:
        if item['symbol'] == symbol:
            item['entry_price'] = targetresult['entry_price']
            item['method'] = targetresult['method']
            item['target_price'] = targetresult['target_price']
            item['stoploss_price'] = targetresult['stoploss_price']
            item['reason'] = targetresult['reason']

            updated = True
            break

    if not updated:

        load['storetarget'].append(targetresult)

    save_data(load)

def placeemabuyorder(symbol,stickprice,exc,token,lotsize,ltp,interval,itemclose,condition,df):
    fetchdata = load_data()
    lotsize = int(fetchdata['lotsize']) * int(lotsize)
    lastprice = df['close'].iloc[-2]  # Safe way to access the second last close price
    sendsymbol = f"{stickprice}-{lastprice}"  # Ensure stickprice is defined
    buy_or_sell = fetchdata['buy_or_sell']
    orderId,checkorderplace = place_order(token,symbol,lotsize,exc,'BUY','MARKET',ltp)
    if checkorderplace == True:
            crete_update_table.inserttokenns(sendsymbol, exc, token, lotsize, ltp, '0')
            print("-----target result-----------------")
            targetresult = determine_target_method_1min(df,symbol)
            print("-----target result-----------------",targetresult)
            storetarget(targetresult,symbol)
            bot_message = f'Order Id: {orderId} {condition}- {symbol} timeframe status:BUY for {stickprice} Strickprice {stickprice}, Lotzise {lotsize},token {token}  and the time is {datetime.datetime.now()} ordered price {itemclose} and stick price {ltp} targetjson:{str(targetresult)}'
            sendAlert(bot_message)
            logging.info(f"buy order place successfully for symbol {stickprice}" )
    else:
        sendAlert(f"{orderId}")

def compare_dates_excluding_seconds(last_date_str):
    print(last_date_str)
    """
    Compare the current date and time with the last date (ignoring seconds).

    :param last_date_str: String representing the last date in the format '%Y-%m-%d %H:%M:%S.%f'
    :return: True if the dates match (up to the minute), otherwise False
    """
    # Parse the input string to a datetime object
    last_date = datetime.datetime.strptime(last_date_str, '%Y-%m-%d %H:%M:%S.%f')

    # Get the current date and time
    current_date = datetime.datetime.now()

    # Remove seconds and microseconds for comparison
    last_date_trimmed = last_date.replace(second=0, microsecond=0)
    current_date_trimmed = current_date.replace(second=0, microsecond=0)

    # Compare the trimmed dates
    return last_date_trimmed != current_date_trimmed

def checkclosenear_price(level,close):
    less_than = None
    greater_than = None

    for price in level:
        price = int(price)  # Ensure price is an integer

        if price < close:
            if less_than is None or (close - price) < (close - less_than):
                less_than = price
        elif price > close:
            if greater_than is None or (price - close) < (greater_than - close):
                greater_than = price

    # Ensure a valid return type
    less_than = less_than if less_than is not None else 0  # Default to 0 if no lower value found
    greater_than = greater_than if greater_than is not None else 0  # Default to 0 if no higher value found

    return less_than, greater_than

import numpy as np

def checktrend(df):
    # ✅ Step 3: Ensure data is not empty
    # if df is None or df.empty:
    #     print("No data fetched. Check symbol or login status.")
    #     exit()
    #
    # # ✅ Step 4: Calculate Wick and Body Sizes
    # df["Body"] = abs(df["close"] - df["open"])
    # df["Upper Wick"] = df["high"] - df[["open", "close"]].max(axis=1)
    # df["Lower Wick"] = df[["open", "close"]].min(axis=1) - df["low"]
    # df["Total Wick"] = df["Upper Wick"] + df["Lower Wick"]
    # df["Noise Ratio"] = df["Total Wick"] / df["Body"].replace(0, np.nan)  # Avoid divide by zero
    #
    # # ✅ Step 5: Define Market Noise vs Trend
    # noise_threshold = 1.5  # If wick is 1.5x or more of body, it's noisy
    # df["Market Noise"] = df["Noise Ratio"] > noise_threshold
    # df["Trending"] = df["Noise Ratio"] < 1.0  # If wick is small relative to body, it's trending
    #
    # # ✅ Step 6: Identify Range-bound Market (Sideways)
    # df["Prev High"] = df["high"].rolling(5).max().shift(1)
    # df["Prev Low"] = df["low"].rolling(5).min().shift(1)
    # df["Body Avg"] = df["Body"].rolling(5).mean().shift(1)
    # df["Sideways"] = (df["Body"] < df["Body Avg"] * 0.7) & (df["high"] < df["Prev High"]) & (df["low"] > df["Prev Low"])
    #
    # # ✅ Step 7: Analyze last 5 candles for confirmation
    # df["Noise Count"] = df["Market Noise"].rolling(5).sum()
    # df["Trend Count"] = df["Trending"].rolling(5).sum()
    # df["Sideways Count"] = df["Sideways"].rolling(5).sum()
    #
    # # ✅ Step 8: Define Market Condition (Noise, Trending, Sideways, Mixed)
    # df["Market Condition"] = np.where(df["Noise Count"] >= 3, "Noise",
    #                          np.where(df["Trend Count"] >= 3, "Trending",
    #                          np.where(df["Sideways Count"] >= 3, "Sideways", "Mixed")))
    # # ✅ Step 9: Print last 10 rows with Market Condition
    # # print(df[["open", "close", "high", "low", "Noise Ratio", "Market Condition"]].tail(30))
    # return df["Market Condition"].values[-1]
        if df is None or df.empty:
            df["Market Condition"] = 'no data'


        df["Body"] = abs(df["close"] - df["open"])
        df["High-Low"] = df["high"] - df["low"]
        window_size = 10
        df["Max High"] = df["high"].rolling(window_size).max()
        df["Min Low"] = df["low"].rolling(window_size).min()
        df["Range"] = df["Max High"] - df["Min Low"]
        df["Sideways"] = (df["Range"] < df["Range"].rolling(window_size).mean()) & \
                         (df["Body"].rolling(window_size).mean() < df["Body"].rolling(window_size).mean().shift(1))
        df["Trending"] = (df["Range"] > df["Range"].rolling(window_size).mean() * 1) & \
                         (df["Body"].rolling(window_size).mean() > df["Body"].rolling(window_size).mean().shift(
                             1) * 1)
        df["Market Condition"] = np.where(df["Sideways"], "Sideways",
                                          np.where(df["Trending"], "Trending", "Mixed"))
        df["Market Condition"] = df["Market Condition"].iloc[-1]
        # print(df)
        return df["Market Condition"].values[-1]


def get_pre_historical_data(symbol_token, exchange, interval, from_date, to_date):
    try:
        to_date = datetime.datetime.now()
        from_date = current_date_time - timedelta(days = 1)
        print(symbol_token, from_date.strftime("%Y-%m-%d 09:15"), to_date.strftime("%Y-%m-%d %H:%M"), interval)
        params = {
            "symboltoken": symbol_token,
            "exchange": exchange,
            "interval": 'ONE_MINUTE',
            "fromdate": from_date.strftime("%Y-%m-%d 09:15"),
            "todate": to_date.strftime("%Y-%m-%d %H:%M")
        }

        historical_data = obj.getCandleData(params)['data']

        if historical_data is not None:
            df = pd.DataFrame(historical_data).tail(10)
            print("DataFrame Shape:", df.shape)

            df.columns = ["datetime", "open", "high", "low", "close", "volume"]
            df["datetime"] = pd.to_datetime(df["datetime"])
            df.set_index("datetime", inplace=True)

            df["sup"] = ta.supertrend(df['high'], df['low'], df['close'], length=10, multiplier=3)['SUPERT_10_3.0']
            df["ema9"] = ta.ema(df["close"], length=9)
            df["ema20"] = ta.ema(df["close"], length=20)
            # df['buy_signal'] = (df['close'] > df['ema9']) & (df['close'].shift(1) <= df['ema9'].shift(1))
            df['buy_signal'] = df['close'] > df['ema9']
            # print(df)
            return df
        else:
            print("No historical data found.")
            return None

    except Exception as e:
        print(f"An error occurred: {e}")



def ce_format(cetoken,symbol,interwal,level,itemclose,df,condition):
    stickprice = cetoken['symbol']
    lotsize = cetoken['lotsize']
    token = cetoken['token']
    less_than, greater_than = checkclosenear_price(level,itemclose)
    checkleveldiff = (greater_than - itemclose) > 20
    print('token details :',cetoken['symbol'],stickprice,lotsize)
    ltp = obj.ltpData(cetoken['exch_seg'], stickprice, token)['data']['ltp']
    fetchdata = crete_update_table.fetchtokennbook()
    filteristoken = [item for item in fetchdata if
                     re.match(r'^[A-Za-z]+', item['script']).group() == symbol and item['lotsize'] > 0]
    lastitemdate = fetchdata[-1]['createddate']
    datematch = compare_dates_excluding_seconds(lastitemdate)
    check_candle_color = df.close.values[-1] > df.open.values[-1]
    trend = checktrend(df)
    premium_data = get_pre_historical_data(token,fochange[symbol],interwal,from_date, current_date_time)
    premium_check = premium_data['buy_signal'].values[-1]
    targetresult = determine_target_method_1min(premium_data,symbol)
    storetarget(targetresult,symbol)
    if len(filteristoken) == 0 and datematch and check_candle_color and trend == 'Trending':
        if checkleveldiff or greater_than == 0 and premium_check:
            logging.info(f"place order : True")
            # symbol = symbol + premium_data.close.values[-1]
            placeemabuyorder(symbol, stickprice, cetoken['exch_seg'], token, lotsize, ltp, interwal, itemclose, condition, premium_data)

            title = f"{symbol} - {interwal}"
            add_plots = [
                mpf.make_addplot(df['ema_9'], color='blue', label='9 EMA'),
                mpf.make_addplot(df['ema_20'], color='orange', label='20 EMA')
            ]

            mpf.plot(df, type='candle', hlines=level.to_list(), addplot=add_plots, style='charles', title=title, savefig='static/chart.png')
            sendImgAlert("Here is an image:", "static/chart.png")

            # placeoptionsellorder(symbol, stickprice, token, lotsize, ltp, interwal, itemclose)

        else:
            title = f"{symbol} - {interwal}"
            add_plots = [
                mpf.make_addplot(df['ema_9'], color='blue', label='9 EMA'),
                mpf.make_addplot(df['ema_20'], color='orange', label='20 EMA')
            ]
            sendAlert(f" {symbol} ce: premium ema check {premium_check} and diff is not greater than 20 points differnce : {greater_than - itemclose} closest registance: {greater_than} itemclose {itemclose}")
            # mpf.plot(df, type='candle', hlines=level.to_list(), addplot=add_plots, style='charles', title=title, savefig='static/chart.png')
            # sendImgAlert("Here is an image:", "static/chart.png")

def pe_format(petoken,symbol,interwal,level,itemclose,df,condition):
    stickprice = petoken['symbol']
    lotsize = petoken['lotsize']
    token = petoken['token']
    less_than, greater_than = checkclosenear_price(level,itemclose)
    checkleveldiff = (itemclose - less_than) > 20
    ltp = obj.ltpData(petoken['exch_seg'], stickprice, token)['data']['ltp']
    fetchdata = crete_update_table.fetchtokennbook()
    filteristoken = [item for item in fetchdata if
                     re.match(r'^[A-Za-z]+', item['script']).group() == symbol and item['lotsize'] > 0]
    lastitemdate = fetchdata[-1]['createddate']
    datematch = compare_dates_excluding_seconds(lastitemdate)
    check_candle_color = df.close.values[-1] < df.open.values[-1]
    trend = checktrend(df)
    premium_data = get_pre_historical_data(token,fochange[symbol],interwal,from_date, current_date_time)
    premium_check = premium_data['buy_signal'].values[-1]
    targetresult = determine_target_method_1min(premium_data,symbol)
    storetarget(targetresult,symbol)
    if len(filteristoken) == 0 and datematch and check_candle_color and trend == 'Trending':
        if checkleveldiff and premium_check:
            logging.info(f"level 2 : place order : True ")
            placeemabuyorder(symbol,stickprice, petoken['exch_seg'], token, lotsize, ltp,interwal,itemclose,condition,premium_data)
            title = f"{symbol} - {interwal}"
            add_plots = [
                mpf.make_addplot(df['ema_9'], color='blue', label='9 EMA'),
                mpf.make_addplot(df['ema_20'], color='orange', label='20 EMA')
            ]
            mpf.plot(df, type='candle',hlines=level.to_list(),addplot=add_plots, style='charles',title=title, savefig='static/chart.png')
            sendImgAlert("Here is an image:", "static/chart.png")
            # placeoptionsellorder(symbol,stickprice,token,lotsize,ltp,interwal,itemclose)
        else:
            title = f"{symbol} - {interwal}"
            add_plots = [
                mpf.make_addplot(df['ema_9'], color='blue', label='9 EMA'),
                mpf.make_addplot(df['ema_20'], color='orange', label='20 EMA')
            ]
            sendAlert(f"{symbol} pe : premium ema check {premium_check} and  diff is not greater than 20 points diffrence : {(itemclose - less_than)} closest support: {less_than} itemclose {itemclose}")
            # mpf.plot(df, type='candle', hlines=level.to_list(), addplot=add_plots, style='charles', title=title, savefig='static/chart.png')
            # sendImgAlert("Here is an image:", "static/chart.png")

def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)


import pandas_ta as ta
import numpy as np

def get_trade_signal(df,symbol):
    # Indicators
    # print(df)
    df['ema_9'] = ta.ema(df['close'], length=9)
    df['ema_20'] = ta.ema(df['close'], length=20)
    df['ema_slope'] = df['ema_9'].diff()

    adx_len = 10
    atr_len = 10
    rolling_len = 10
    range_len = 10

    df['adx'] = ta.adx(df['high'], df['low'], df['close'], length=adx_len)[f'ADX_{adx_len}']
    df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=atr_len)
    df['atr_avg'] = df['atr'].rolling(window=rolling_len).mean()
    df['vol_avg'] = df['volume'].rolling(window=rolling_len).mean()
    df['range'] = df['high'].rolling(window=range_len).max() - df['low'].rolling(window=range_len).min()

    # Support and Resistance Levels
    lookback = 20
    df['support'] = df['low'].rolling(window=lookback).min()
    df['resistance'] = df['high'].rolling(window=lookback).max()

    latest = df.iloc[-1]
    # print(df)
    # Fibonacci Levels Calculation
    # Assuming 'df' has a 'datetime' column with datetime objects
    symbol_tokens = {
    "NIFTY": "99926000",
    "BANKNIFTY": "99926009",
    "SENSEX": "99926001"
}
    exchange = nsechange[symbol]
    tradingsymbol = symbol
    symboltoken = symbol_tokens[symbol]  # Token for NIFTY 50 index

    # Fetch LTP data
    ltp_data = obj.ltpData(exchange=exchange, tradingsymbol=tradingsymbol, symboltoken=symboltoken)
    print(ltp_data)
    if ltp_data['status'] == True:
        # Extract LTP value
        ltp = ltp_data['data']
        # print(f"NIFTY 50 LTP: {ltp}")
        highest_price = ltp['high']
        lowest_price = ltp['low']
        print('check data',highest_price,lowest_price)
        diff = highest_price - lowest_price
        # usecase =  ltp['open'] > ltp['high']
        fib_levels = {
            'highest_price':highest_price,
            'lowest_price':lowest_price,
            '0.786': round(lowest_price + 0.786 * diff),
            '0.618': round(lowest_price + 0.618 * diff),
            '0.5': round(lowest_price + 0.5 * diff),
            '0.382': round(lowest_price + 0.382 * diff),
            '0.236': round(lowest_price + 0.236 * diff),
            '0': lowest_price
        }
    else:
        fib_levels = {}
    # Core Buy Conditions
    core_buy = [
        latest['ema_9'] > latest['ema_20'],
        latest['close'] > latest['ema_9'],
        latest['adx'] > 20
    ]
    supporting_buy = [
        latest['ema_slope'] > 0.1,
        latest['atr'] > latest['atr_avg'],
        latest['volume'] > latest['vol_avg'],
        latest['range'] > df['range'].mean()
    ]

    # Core Sell Conditions
    core_sell = [
        latest['ema_9'] < latest['ema_20'],
        latest['close'] < latest['ema_9'],
        latest['adx'] > 20
    ]
    supporting_sell = [
        latest['ema_slope'] < -0.1,
        latest['atr'] > latest['atr_avg'],
        latest['volume'] > latest['vol_avg'],
        latest['range'] > df['range'].mean()
    ]

    returncorebuy = {
        'ema > ema20': latest['ema_9'] > latest['ema_20'],
        'close > ema9': latest['close'] > latest['ema_9'],
        'adx > 20': latest['adx'] > 20,
        'ema_slope > 0.1': latest['ema_slope'] > 0.1,
        'atr > atr_avg': latest['atr'] > latest['atr_avg'],
        'volume > avg': latest['volume'] > latest['vol_avg'],
        'range > avg': latest['range'] > df['range'].mean()
    }

    returncoresell = {
        'ema < ema20': latest['ema_9'] < latest['ema_20'],
        'close < ema9': latest['close'] < latest['ema_9'],
        'adx > 20': latest['adx'] > 20,
        'ema_slope < -0.1': latest['ema_slope'] < -0.1,
        'atr > atr_avg': latest['atr'] > latest['atr_avg'],
        'volume > avg': latest['volume'] > latest['vol_avg'],
        'range > avg': latest['range'] > df['range'].mean()
    }

    # Sideways Market Detection
    recent_range = latest['range']
    low_volatility = latest['atr'] < latest['atr_avg']
    low_adx = latest['adx'] < 20
    sideways = low_volatility and low_adx

    # Potential Breakout Levels
    breakout_levels = ""
    if sideways:
        breakout_levels = f"⚠️ Sideways market detected.\nWatch for breakout above 🔼 {latest['resistance']:.2f} or breakdown below 🔽 {latest['support']:.2f}."

    # Utility to display condition results
    def split_condition_flags(cond_dict):
        true_keys = [k for k, v in cond_dict.items() if v]
        false_keys = [k for k, v in cond_dict.items() if not v]
        return f"✅ {', '.join(true_keys)} | ❌ {', '.join(false_keys)}"

    buy_signal_summary = split_condition_flags(returncorebuy)
    sell_signal_summary = split_condition_flags(returncoresell)
    # Check if price broke resistance or support with trend alignment
    broke_resistance = latest['close'] > latest['resistance'] and latest['ema_9'] > latest['ema_20']
    broke_support = latest['close'] < latest['support'] and latest['ema_9'] < latest['ema_20']

    broke_above_fib = any(latest['close'] > price for level, price in fib_levels.items() if level in ['61.8%', '78.6%']) and latest['ema_9'] > latest['ema_20']
    broke_below_fib = any(latest['close'] < price for level, price in fib_levels.items() if level in ['61.8%', '78.6%']) and latest['ema_9'] < latest['ema_20']

    near_support = abs(latest['close'] - latest['support']) <= latest['atr']
    near_resistance = abs(latest['close'] - latest['resistance']) <= latest['atr']
    near_fib = any(abs(latest['close'] - lvl) <= latest['atr'] for lvl in fib_levels.values())

    # Final decision
    if all(core_buy) and sum(supporting_buy) >= 2:
        signal = "buy"
        trend_message = "✅ Buy signal confirmed. Trending setup."
    elif all(core_sell) and sum(supporting_sell) >= 2:
        signal = "sell"
        trend_message = "✅ Sell signal confirmed. Trending setup."
    elif broke_resistance or broke_above_fib:
        signal = "buy"
        trend_message = "📈 Breakout above resistance or key Fibonacci level detected. Buy momentum building."
    elif broke_support or broke_below_fib:
        signal = "sell"
        trend_message = "📉 Breakdown below support or Fibonacci level detected. Sell pressure increasing."
    elif near_support or near_resistance or near_fib:
        signal = "wait"
        trend_message = (
            f"⚠️ Price near key {'support' if near_support else 'resistance' if near_resistance else 'Fibonacci'} level.\n"
            f"💡 Wait for breakout or confirmation before entering a trade."
        )
    elif sideways:
        signal = "sideways"
        trend_message = "📉 Sideways market detected. Watch breakout above/below key levels."
    else:
        signal = "no_trade"
        trend_message = "⏳ No strong trend or breakout setup yet. Wait for better confirmation."


    return {
        "buy_signals": buy_signal_summary,
        "sell_signals": sell_signal_summary,
        "final_signal": signal,
        "sideways_info": breakout_levels,
        "support": round(latest['support'], 2),
        "resistance": round(latest['resistance'], 2),
        "fibonacci_levels": fib_levels,
        "current_price": round(latest['close'], 2),
        'trend_message':trend_message
    }


# def get_trade_signal(df):
#     # Calculate indicators using pandas-ta
#     # df = aggregate_data(df, '5T')
#     df['ema_9'] = ta.ema(df['close'], length=9)
#     df['ema_20'] = ta.ema(df['close'], length=20)
#     df['ema_slope'] = df['ema_9'].diff()
#     # print()
#     adx_len = 10
#     atr_len = 10
#     rolling_len = 10
#     range_len = 10  # Slightly faster than 20 for quicker consolidation detection
#
#     # ADX (trend strength)
#     df['adx'] = ta.adx(df['high'], df['low'], df['close'], length=adx_len)[f'ADX_{adx_len}']
#
#     # ATR (volatility)
#     df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=atr_len)
#     df['atr_avg'] = df['atr'].rolling(window=rolling_len).mean()
#
#     # Volume average
#     df['vol_avg'] = df['volume'].rolling(window=rolling_len).mean()
#
#     # Price range over last `range_len` candles
#     df['range'] = df['high'].rolling(window=range_len).max() - df['low'].rolling(window=range_len).min()
#
#     latest = df.iloc[-1]
#
#     # Buy logic
#     core_buy = [
#         latest['ema_9'] > latest['ema_20'],
#         latest['close'] > latest['ema_9'],
#         latest['adx'] > 20
#     ]
#     supporting_buy = [
#         latest['ema_slope'] > 0.1,
#         latest['atr'] > latest['atr_avg'],
#         latest['volume'] > latest['vol_avg'],
#         latest['range'] > df['range'].mean()
#     ]
#
#     # Sell logic
#     core_sell = [
#         latest['ema_9'] < latest['ema_20'],
#         latest['close'] < latest['ema_9'],
#         latest['adx'] > 20
#     ]
#     supporting_sell = [
#         latest['ema_slope'] < -0.1,
#         latest['atr'] > latest['atr_avg'],
#         latest['volume'] > latest['vol_avg'],
#         latest['range'] > df['range'].mean()
#     ]
#     # print("------------------*****************-----------------",latest)
#     returncorebuy = {
#         'ema > ema20':latest['ema_9'] > latest['ema_20'],
#        'close > ema9': latest['close'] > latest['ema_9'],
#        'adx': latest['adx'] > 20,
#        'ema_slope': latest['ema_slope'] > 0.1,
#        'atr': latest['atr'] > latest['atr_avg'],
#       'volume':  latest['volume'] > latest['vol_avg'],
#        'range': latest['range'] > df['range'].mean()
#     }
#     returncoresell = {
#        'ema': latest['ema_9'] < latest['ema_20'],
#        'close': latest['close'] < latest['ema_9'],
#         'adx':latest['adx'] > 20,
#         'ema_slop': latest['ema_slope'] < -0.1,
#         'atr': latest['atr'] > latest['atr_avg'],
#        'volume': latest['volume'] > latest['vol_avg'],
#        'range': latest['range'] > df['range'].mean()
#     }
#
#     # Function to split into true/false keys
#     def split_condition_flags(cond_dict):
#         true_keys = [k for k, v in cond_dict.items() if v]
#         false_keys = [k for k, v in cond_dict.items() if not v]
#         return f"✅ {', '.join(true_keys)} | ❌ {', '.join(false_keys)}"
#
#     # Result strings
#     buy_signal_summary = split_condition_flags(returncorebuy)
#     sell_signal_summary = split_condition_flags(returncoresell)
#     print("check gow",df)
#     # Signal
#     if all(core_buy) and sum(supporting_buy) >= 2:
#         return buy_signal_summary,sell_signal_summary,"buy"
#     elif all(core_sell) and sum(supporting_sell) >= 2:
#         return buy_signal_summary,sell_signal_summary,"sell"
#     else:
#         return buy_signal_summary,sell_signal_summary,"no_trade"

# def storetrend(symbol,trend):
#     load = load_data()
#     print("------------",load)
#
#     if len(load['store']) > 0:
#         for item in load['store']:
#             if item['symbol'] == symbol:
#                 item['trend'] = trend
#             else:
#                 const = {
#                     'symbol':symbol,
#                     'trend':trend
#                 }
#                 load['store'].append(const)
#
#     else:
#         load['store'] = []
#         const = [{
#                     'symbol':symbol,
#                     'trend':trend
#                 }]
#         load['store'] = const
#
#     save_data(load)

def storetrend(symbol, trend,returncorebuy,returncoresell,trend_message,signal_data):
    load = load_data()
    print("------------", load)

    if 'store' not in load or not isinstance(load['store'], list):
        load['store'] = []

    updated = False
    for item in load['store']:
        if item['symbol'] == symbol:
            item['trend'] = trend
            item['returncorebuy'] = str(returncorebuy)
            item['returncoresell'] = str(returncoresell)
            item['trend_message'] = trend_message
            item['fibonacci_levels'] = str(signal_data['fibonacci_levels'])
            item['resistance'] = str(signal_data['resistance'])
            item['support'] = str(signal_data['support'])
            item['sideways_info'] = str(signal_data['sideways_info'])
            item['current_price'] = str(signal_data['current_price'])

            updated = True
            break

    if not updated:
        const = {
            'symbol': symbol,
            'trend': trend,
            'returncorebuy': str(returncorebuy),
            'returncoresell': str(returncoresell),
            'trend_message': trend_message,
            'fibonacci_levels' : str(signal_data['fibonacci_levels']),
            'resistance' : str(signal_data['resistance']),
            'support' : str(signal_data['support']),
            'sideways_info' : str(signal_data['sideways_info']),
            'current_price': str(signal_data['current_price'])
        }
        load['store'].append(const)

    save_data(load)


def checkema_levels(data,symbol,interwal,level):
    df = data
    auto_trade = load_data()
    itemclose = df.close.values[-1]
    # returncorebuy,returncoresell,check_trend = get_trade_signal(df)
    signal_data = get_trade_signal(df,symbol)
    check_trend = signal_data["final_signal"]
    storetrend(symbol,signal_data["final_signal"],signal_data["buy_signals"],signal_data["sell_signals"],signal_data['trend_message'],signal_data)
    print(f"-----------------************trend detection for symbol {symbol} : {check_trend} ************-------------------")
    # print('item close',itemclose)
    latest_data = data.iloc[-1]
    print('last data',latest_data)
    cetoken, petoken = storetoken.placeorderdetails(fochange[symbol], 'OPTIDX', symbol, df.close.values[-1])
    print('sdfghjk',cetoken,petoken)
    check_trend_Buy_condition = (check_trend == 'buy')
    check_trend_sell_condition = (check_trend == 'sell')
    # check_trend_Buy_condition = True
    # check_trend_sell_condition = True
    # df['Candle_Color'] = 1  # Initialize with a value indicating green candles
    # df.loc[df['close'] < df['open'], 'Candle_Color'] = 0
    # print('symbol',symbol)
    # print('ce symbol',cetoken['symbol'], petoken['symbol'])

    # cetrue = (closehigh < df.close.values[-1]) if closehigh != '' else True
    # petrue = (closelow > df.close.values[-1]) if closelow != '' else True
    if latest_data['buy_signal'] and check_trend_Buy_condition:
        if auto_trade['buy_or_sell'] == 'BUY':
            ce_format(cetoken,symbol,interwal,level,itemclose,df,'buy_signal')
        elif auto_trade['buy_or_sell'] == 'SELL':
            placeoptionsellorder(df,level,symbol,petoken['symbol'],petoken['exch_seg'],petoken['token'],petoken['lotsize'],'ltp',interwal,itemclose,'buy_signal')
    if latest_data['sell_signal'] and check_trend_sell_condition:
        if auto_trade['buy_or_sell'] == 'BUY':
            pe_format(df,level,petoken,symbol,interwal,level,itemclose,df,'sell_signal')
        elif auto_trade['buy_or_sell'] == 'SELL':
            placeoptionsellorder(df,level,symbol,cetoken['symbol'],cetoken['exch_seg'],cetoken['token'],cetoken['lotsize'],'ltp',interwal,itemclose,'buy_signal')


    if latest_data['support_on_9ema'] and check_trend_Buy_condition:
        if auto_trade['buy_or_sell'] == 'BUY':
            ce_format(cetoken,symbol,interwal,level,itemclose,df,'support_on_9ema')
        elif auto_trade['buy_or_sell'] == 'SELL':
            placeoptionsellorder(df,level,symbol,petoken['symbol'],petoken['exch_seg'],petoken['token'],petoken['lotsize'],'ltp',interwal,itemclose,'buy_signal')


    if latest_data['support_on_20ema'] and check_trend_Buy_condition:
        if auto_trade['buy_or_sell'] == 'BUY':
            ce_format(cetoken,symbol,interwal,level,itemclose,df,'support_on_20ema')
        elif auto_trade['buy_or_sell'] == 'SELL':
            placeoptionsellorder(df,level,symbol,petoken['symbol'],petoken['exch_seg'],petoken['token'],petoken['lotsize'],'ltp',interwal,itemclose,'buy_signal')

    # if latest_data['support_on_50ema']:
    #     ce_format(cetoken,symbol,interwal,level,itemclose,df,'support_on_50ema')
    # if latest_data['support_on_100ema']:
    #     ce_format(cetoken,symbol,interwal,level,itemclose,df,'support_on_100ema')


    if latest_data['resistance_on_9ema'] and check_trend_sell_condition:
        if auto_trade['buy_or_sell'] == 'BUY':
            pe_format(petoken,symbol,interwal,level,itemclose,df,'resistance_on_9ema')
        elif auto_trade['buy_or_sell'] == 'SELL':
            placeoptionsellorder(df,level,symbol,cetoken['symbol'],cetoken['exch_seg'],cetoken['token'],cetoken['lotsize'],'ltp',interwal,itemclose,'buy_signal')

    if latest_data['resistance_on_20ema'] and check_trend_sell_condition:
       if auto_trade['buy_or_sell'] == 'BUY':
            pe_format(petoken,symbol,interwal,level,itemclose,df,'resistance_on_20ema')
       elif auto_trade['buy_or_sell'] == 'SELL':
            placeoptionsellorder(df,level,symbol,cetoken['symbol'],cetoken['exch_seg'],cetoken['token'],cetoken['lotsize'],'ltp',interwal,itemclose,'buy_signal')

    # if latest_data['resistance_on_50ema']:
    #    pe_format(petoken,symbol,interwal,level,itemclose,df,'resistance_on_50ema')
    # if latest_data['resistance_on_100ema']:
    #    pe_format(petoken,symbol,interwal,level,itemclose,df,'resistance_on_1000ema')

    else:
                print('no ema levels')
def storesupportlevel():
    try:
        auto_trade = load_data()
        # print('start strategy',auto_trade)
        closehigh = ''
        closelow = ''
        orderdata = crete_update_table.todayorderdata()
        print(orderdata)
        # print('---------------------***',('auto placed order', auto_trade['auto_place_order'], orderdata['stoplossOrder']) <= int(auto_trade['stop_loss']),----int(orderdata['totalProfit']) <= linitedprofit)
        print(f"-------'auto placed order' : {auto_trade['auto_place_order']} , stoploss order linit : {auto_trade['stop_loss']} , stoploss order : {orderdata['stoplossOrder']} -----------------------------------")
        # int(orderdata['totalProfit']) <= linitedprofit
        if auto_trade['auto_place_order'] and int(orderdata['stoplossOrder']) < int(auto_trade['stop_loss']):
            for script, token in symbols.items():
                if auto_trade[token]:
                    try:
                        result1, level1, data = fetch_and_process_data(script, Interval.in_1_minute, '100', 20, 20)
                        checkema_levels(data,script,'1m',level1)
                        for interval, key in timeframe_map.items():
                            try:
                                result, level, df = fetch_and_process_data(script, key, '100', 20, 20)

                                if result1:
                                    print('level', level)
                                    df_5min = aggregate_data(data, '5T').tail(10)
                                    closehigh = df_5min.high.values[-2]
                                    closelow = df_5min.low.values[-2]
                                    change = closehigh - closelow
                                    if (change >= 20 and script == 'NIFTY') or (change >= 40 and script == 'BANKNIFTY'):
                                        # merged_array = level + pivot_fibo_level  # Merging the two arrays
                                        stetergytosendalert(script, interval, data, level, closehigh, closelow,'df_5min')
                                        if interval == '5m':
                                            pivotpointstatergy(script, interval, data, level, closehigh, closelow,'df_5min')
                                    else:
                                        df_15min = aggregate_data(data, '15T').tail(10)
                                        closehigh = df_15min.high.values[-2]
                                        closelow = df_15min.low.values[-2]
                                        change = closehigh - closelow
                                        if (change > 20 and script == 'NIFTY') or (change > 40 and script == 'BANKNIFTY'):
                                            stetergytosendalert(script, interval, data, level, closehigh, closelow,'df_15min')
                                            if interval == '5m':
                                                pivotpointstatergy(script, interval, data, level, closehigh, closelow,'df_15min')
                                        else:
                                            print('Side Ways Market')

                            except Exception as e:
                                print(f"Error processing data for script {script} and interval {interval}: {e}")
                                storesupportlevel()
                    except Exception as e:
                        print(f"Error fetching data for script {script}: {e}")
                        storesupportlevel()
        else:
            print(f"auto order {auto_trade['auto_place_order']} limite hit for stoploss order {int(orderdata['stoplossOrder'])} and limit is {auto_trade['stop_loss']}")
    except Exception as e:
        print(f"General error in storesupportlevel: {e}")
        storesupportlevel()

# Ensure that all required functions and variables are defined:
# symbols, fetch_and_process_data, Interval, timeframe_map, aggregate_data, stetergytosendalert
# Also ensure that you have proper error handling for other functions if they might raise exceptions.


# fetch_and_process_data('NIFTY', Interval.in_1_minute, '100', '20', '20')

fetchdataandreturn_pivot()
storesupportlevel()
# getPremiumData('NFO','43900','nifty')
schedule.every(1).minutes.do(storesupportlevel)
# placeoptionsellorder('BANKNIFTY','BANKNIFTY04SEP2451400CE',49076,'25',223,'1m',51410)



while True:
    try:
        schedule.run_pending()
        time.sleep(2)
    except Exception as e:
        raise e


