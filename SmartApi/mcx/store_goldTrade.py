import json
import re
import time

import numpy as np
import requests
import schedule

from SmartApi import SmartConnect  # or from SmartApi.smartConnect import SmartConnect
import datetime
import pandas as pd
import document
import pyotp
import pandas_ta as ta
import logging
import mplfinance as mpf
import mcxdb
from datetime import timedelta

logging.basicConfig(
    filename='mcx.log',  # Name of the log file
    level=logging.INFO,  # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format
    datefmt='%Y-%m-%d %H:%M:%S'  # Date format in logs
)

# Initialize API connection
api_key = document.api_key
user_id = document.user_id
password = document.password
totp = pyotp.TOTP(document.totp).now()
obj = SmartConnect(api_key=api_key)
token = obj.generateToken(obj.generateSession(user_id, password, totp)["data"]["refreshToken"])
# print(token)



# Exchange and Token Info for GOLD (example: GOLDM24APRFUT for April 2024 Gold Mini Futures)
exchange = "MCX"
symbol_token = 428777 # GOLDM24APRFUT token, use symbol lookup to verify
interval = "FIVE_MINUTE"  # Options: ONE_MINUTE, FIVE_MINUTE, TEN_MINUTE, etc.

# Time Range
to_date = datetime.datetime.now()
from_date = to_date - datetime.timedelta(days=5)
current_date_time = datetime.datetime.now()
from_date = current_date_time - datetime.timedelta(days=5)
DATA_FILE = "auto_trade.json"  # File to store form data


tokenstore = []


def get_current_gold_token():
    try:
        url = "https://margincalculator.angelone.in/OpenAPI_File/files/OpenAPIScripMaster.json"
        response = requests.get(url)
        df = pd.DataFrame(response.json())

        gold_df = df[
            (df['name'].str.contains('GOLD', case=False)) &
            (df['exch_seg'] == 'MCX') &
            (df['symbol'].str.contains('FUT', case=False))
        ].copy()  # <- this avoids the SettingWithCopyWarning
        # print(gold_df)
        gold_df.loc[:, 'expiry'] = pd.to_datetime(gold_df['expiry'], format='%Y-%m-%d', errors='coerce')
        gold_df = gold_df.sort_values('expiry')

        current = gold_df.iloc[0]
        # print(current)
        result = {
            "token": current['token'],
            "symbol": current['symbol'],
            "expiry": current['expiry']
        }
        tokenstore.append(result)

    except Exception as e:
        print("Error fetching GOLD token:", str(e))
        return None

def gethistoricaldata(token):
    # Get historical candles
    try:
        rolling_window = 20
        level_diff_threshold = 20
        historicParam = {
            "exchange": exchange,
            "symboltoken": 438425,
            "interval": "FIVE_MINUTE",
            "fromdate": from_date.strftime("%Y-%m-%d 09:15"),
            "todate": to_date.strftime("%Y-%m-%d %H:%M")
        }
        hist_data = obj.getCandleData(historicParam)
        # print(hist_data)
        # Convert to DataFrame
        df = pd.DataFrame(hist_data['data'], columns=["timestamp", "open", "high", "low", "close", "volume"])
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
        trend_duration = 3
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
        supports = df[df.low == df.low.rolling(rolling_window, center=True).min()].close
        resistances = df[df.high == df.high.rolling(rolling_window, center=True).max()].close

        level = pd.concat([supports, resistances])
        level = level[abs(level.diff()) > level_diff_threshold]
        return level,df
    except Exception as e:
        print('error', e)
        time.sleep(5)
        main()

def checktrend(df):

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

def get_trade_signal(df):
    # Calculate indicators using pandas-ta
    df['ema_9'] = ta.ema(df['close'], length=9)
    df['ema_20'] = ta.ema(df['close'], length=20)
    df['ema_slope'] = df['ema_20'].diff()

    df['adx'] = ta.adx(df['high'], df['low'], df['close'], length=14)['ADX_14']
    df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=14)
    df['atr_avg'] = df['atr'].rolling(window=14).mean()

    df['vol_avg'] = df['volume'].rolling(window=14).mean()
    df['range'] = df['high'].rolling(window=20).max() - df['low'].rolling(window=20).min()

    latest = df.iloc[-1]

    # Buy logic
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

    # Sell logic
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
    # print("------------------*****************-----------------",latest)

    # Signal
    if all(core_buy) and sum(supporting_buy) >= 2:
        return "buy"
    elif all(core_sell) and sum(supporting_sell) >= 2:
        return "sell"
    else:
        return "no_trade"

token_df = None

def get_delta_histo_data(symbol_token,exchange):
    params = {
            "symboltoken": symbol_token,
            "exchange": exchange,
            "interval": 'FIFTEEN_MINUTE',
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
        df['sell_signal'] = df['close'] < df['ema_9']
        return df

def exitstetergywithema():
    print('enter in exit 2')
    getbook = mcxdb.fetch_all_tokens()
    print('check',getbook)
    if getbook is not None:
        for item in getbook:
            if item is not None:
                if item['lotsize'] > 0:
                    fetchdata = get_delta_histo_data(item['token'],item['exchange'])
                    exitstetergynext_ema(fetchdata,item)

def place_order(product_id, size, side):
     return {'success': True}

def exitstetergynext_ema(df,item):
    print('eenterexit 2')
    date = datetime.datetime.now()
    itemclose = df.close.values[-1]
    symbol = item['script']
    buyprice = item['ltp']
    lotsize = item['lotsize']
    # getting ltp
    symbol = item['script']
    url = f"https://cdn.india.deltaex.org/v2/tickers/{symbol}"
    response = requests.get(url)
    ticker_info = response.json()
    latest_data = df.iloc[-1]

    ltp = float(ticker_info['result']['mark_price'])

    #getting ltp down

    ema = df['ema_9'].values[-1]
    profit_or_loss = (ltp - buyprice) * lotsize
    print("profit",profit_or_loss)
    if latest_data['sell_signal']:
            place = place_order(item['id'],item['lotsize'],'sell')
            if place['success'] == True:
                    profit_order = (
                                f"Exit by EMA"
                                f"Time: {date} | Symbol: {symbol} | Exit Price: {ltp} | Buy Price: {buyprice} | "
                                f"Profit/Loss: {profit_or_loss}"
                            )

                    mcxdb.updateorderplace(item['id'], 0, profit_or_loss)
                    sendAlert(profit_order)
            else:
                sendAlert(f"{place}")


def initialisedTokenMap():
    global token_df

    # Check if token_df is already initialized
    if token_df is None:
        url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
        d = requests.get(url).json()
        token_df = pd.DataFrame.from_dict(d)
        token_df['expiry'] = pd.to_datetime(token_df['expiry'])
        token_df = token_df.astype({'strike': float})
        # print(token_df[token_df.name == 'SILVERMIC'])
    return token_df

# Calling the function
token_df = initialisedTokenMap()


def getTokenInfo(exch_seg, instrumenttype, symbol, strike_price, pe_ce, expiry_day=None):
    df = token_df
    strike_price = strike_price * 100
    # print(strike_price)
    exch_seg = 'MCX'
    instrumenttype = 'OPTCOM'
    if exch_seg == 'MCX':

            return df[
                (df['exch_seg'] == 'MCX') &
                (df['name'] == 'GOLD') &
                (df['instrumenttype'] == 'OPTFUT') &
                (df['expiry'] >= str(datetime.date.today()))
                ].sort_values(by=['expiry'])

    return None  # fallback if no condition matches

def placeorderdetails(exchnage,type,symbol,ltp):
    # tokeninfo = getTokenInfo('NSE', 'OPTIDX', symbol, '', '').iloc[0]['token']
    # print(tokeninfo, "---token")
    global LTP
    LTP = ltp
    RTM = int(round(LTP / 100) * 100)  # to get check acurate price
    ce_symbol_data = getTokenInfo(exchnage, type, symbol, RTM, 'CE').iloc[0]
    pe_symbol_data = getTokenInfo(exchnage, type, symbol, RTM, 'PE').iloc[0]
    return ce_symbol_data,pe_symbol_data

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

def get_pre_historical_data(symbol_token, exchange, interval, from_date, to_date):
    try:
        to_date = datetime.datetime.now()
        from_date = current_date_time - timedelta(days = 1)
        print(symbol_token,exchange, from_date.strftime("%Y-%m-%d 09:15"), to_date.strftime("%Y-%m-%d %H:%M"), interval)
        params = {
            "symboltoken": symbol_token,
            "exchange": 'MCX',
            "interval": 'ONE_MINUTE',
            "fromdate": from_date.strftime("%Y-%m-%d 09:15"),
            "todate": to_date.strftime("%Y-%m-%d %H:%M")
        }
        historical_data = obj.getCandleData(params)['data']
        print('historicaldat',historical_data)
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

            return df
        else:
            print("No historical data found.")
            return None

    except Exception as e:
        print(f"An error occurred: {e}")

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

# Function to load stored data
def load_data():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)  # Read existing data
    except (FileNotFoundError, json.JSONDecodeError):
        return {}  # Return empty if file not found or corrupted

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

def placeemabuyorder(symbol,stickprice,exc,token,lotsize,ltp,interval,itemclose,condition,df):
    fetchdata = load_data()
    lotsize = int(fetchdata['lotsize']) * int(lotsize)
    lastprice = df['close'].iloc[-2]  # Safe way to access the second last close price
    sendsymbol = f"{stickprice}-{lastprice}"  # Ensure stickprice is defined
    mcxdb.inserttokenns(sendsymbol, exc, token, lotsize, ltp, '0')
    bot_message = f'{condition}- {symbol} timeframe status:BUY for {stickprice} Strickprice {stickprice}, Lotzise {lotsize},token {token}  and the time is {datetime.datetime.now()} ordered price {itemclose} and stick price {ltp}'
    sendAlert(bot_message)
    logging.info(f"buy order place successfully for symbol {stickprice}")

def ce_format(cetoken,symbol,interwal,level,itemclose,df,condition):
    stickprice = cetoken['symbol']
    lotsize = cetoken['lotsize']
    token = cetoken['token']
    less_than, greater_than = checkclosenear_price(level,itemclose)
    checkleveldiff = (greater_than - itemclose) > 20
    print('token details :',cetoken['symbol'],stickprice,lotsize)
    ltp = obj.ltpData(cetoken['exch_seg'], stickprice, token)['data']['ltp']
    fetchdata = mcxdb.fetch_all_tokens()
    filteristoken = [item for item in fetchdata if
                     re.match(r'^[A-Za-z]+', item['script']).group() == symbol and item['lotsize'] > 0]
    # lastitemdate = fetchdata[-1]['createddate']
    # datematch = compare_dates_excluding_seconds(lastitemdate)
    datematch = True
    check_candle_color = df.close.values[-1] > df.open.values[-1]
    trend = checktrend(df)
    # premium_data = get_pre_historical_data(token,'MCX',interwal,from_date, current_date_time)
    premium_data = []
    # print(premium_data)
    # premium_check = premium_data['buy_signal'].values[-1]
    if len(filteristoken) == 0 and check_candle_color and trend == 'Trending':
        if checkleveldiff or greater_than == 0:
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
            sendAlert(f" {symbol} ce: premium ema diff is not greater than 20 points differnce : {greater_than - itemclose} closest registance: {greater_than} itemclose {itemclose}")
            # mpf.plot(df, type='candle', hlines=level.to_list(), addplot=add_plots, style='charles', title=title, savefig='static/chart.png')
            # sendImgAlert("Here is an image:", "static/chart.png")


def pe_format(petoken,symbol,interwal,level,itemclose,df,condition):
    stickprice = petoken['symbol']
    lotsize = petoken['lotsize']
    token = petoken['token']
    less_than, greater_than = checkclosenear_price(level,itemclose)
    checkleveldiff = (itemclose - less_than) > 20
    ltp = obj.ltpData(petoken['exch_seg'], stickprice, token)['data']['ltp']
    fetchdata = mcxdb.fetch_all_tokens()
    filteristoken = [item for item in fetchdata if
                     re.match(r'^[A-Za-z]+', item['script']).group() == symbol and item['lotsize'] > 0]
    lastitemdate = fetchdata[-1]['createddate']
    datematch = compare_dates_excluding_seconds(lastitemdate)
    check_candle_color = df.close.values[-1] < df.open.values[-1]
    trend = checktrend(df)
    # premium_data = get_pre_historical_data(token,'MCX',interwal,from_date, current_date_time)
    # premium_check = premium_data['buy_signal'].values[-1]
    premium_data = []
    premium_check = True

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


def main():
    for item in tokenstore:
        print(item)
        level,df = gethistoricaldata(item['token'])
        check_trend = get_trade_signal(df)
        check_trend_Buy_condition = (check_trend == 'buy')
        check_trend_sell_condition = (check_trend == 'sell')
        latest_data = df.iloc[-1]
        cetoken, petoken = placeorderdetails('MCX', 'OPTCOM', item['symbol'], df.close.values[-1])
        print(cetoken,petoken)
        itemclose = df.close.values[-1]
        interwal = '15m'
        symbol = item['symbol']
        if latest_data['buy_signal'] and check_trend_Buy_condition:
            ce_format(cetoken, symbol, interwal, level, itemclose, df, 'buy_signal')
        if latest_data['sell_signal'] and check_trend_sell_condition:
            pe_format(petoken, symbol, interwal, level, itemclose, df, 'sell_signal')

        if latest_data['support_on_9ema'] and check_trend_Buy_condition:
            ce_format(cetoken, symbol, interwal, level, itemclose, df, 'support_on_9ema')
        if latest_data['support_on_20ema'] and check_trend_Buy_condition:
            ce_format(cetoken, symbol, interwal, level, itemclose, df, 'support_on_20ema')
            # if latest_data['support_on_50ema']:
            #     ce_format(cetoken,symbol,interwal,level,itemclose,df,'support_on_50ema')
            # if latest_data['support_on_100ema']:
            #     ce_format(cetoken,symbol,interwal,level,itemclose,df,'support_on_100ema')

        if latest_data['resistance_on_9ema'] and check_trend_sell_condition:
            pe_format(petoken, symbol, interwal, level, itemclose, df, 'resistance_on_9ema')
        if latest_data['resistance_on_20ema'] and check_trend_sell_condition:
            pe_format(petoken, symbol, interwal, level, itemclose, df, 'resistance_on_20ema')
            # if latest_data['resistance_on_50ema']:
            #    pe_format(petoken,symbol,interwal,level,itemclose,df,'resistance_on_50ema')
            # if latest_data['resistance_on_100ema']:
            #    pe_format(petoken,symbol,interwal,level,itemclose,df,'resistance_on_1000ema')

        else:
            print('no ema levels')



# print(get_current_gold_token())
get_current_gold_token()
main()
exitstetergywithema()
# getPremiumData('NFO','43900','nifty')
schedule.every(1).minutes.do(main)
schedule.every(1).minutes.do(exitstetergywithema)


while True:
    try:
        schedule.run_pending()
        time.sleep(2)
    except Exception as e:
        raise e
