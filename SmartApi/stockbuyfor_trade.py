import technically_filtered_stock
import datetime
from datetime import timedelta
# from datetime import datetime, timedelta
# from datetime import datetime
import storetoken
import re
import threading
import time
import numpy as np
import yfinance as yf
import pandas_ta as ta

import requests
from tabulate import tabulate

from SmartApi import SmartConnect  # or from SmartApi.smartConnect import SmartConnect
import schedule
from tvDatafeed import TvDatafeed, Interval
import pandas as pd
import crete_update_table
import logging
import mplfinance as mpf
import document
import pyotp

logging.basicConfig(
    filename='optionsorderlog2.log',  # Name of the log file
    level=logging.INFO,  # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format
    datefmt='%Y-%m-%d %H:%M:%S'  # Date format in logs
)

global storestocklis
lotsize = 10

username = 'YourTradingViewUsername'
password = 'YourTradingViewPassword'

tv = TvDatafeed(username, password)
#
api_key = document.api_key
user_id = document.user_id
password = document.password
totp = pyotp.TOTP(document.totp).now()
obj = SmartConnect(api_key=api_key)
token = obj.generateToken(obj.generateSession(user_id, password, totp)["data"]["refreshToken"])

timeframe_map = {
    '1m': Interval.in_1_minute,
    '5m': Interval.in_5_minute,
    '15m': Interval.in_15_minute,
    '30m': Interval.in_30_minute,
}

def fetch_and_process_data(symbol, interval, n_bars, rolling_window, level_diff_threshold):
    try:
        df = tv.get_hist(symbol=symbol, exchange='NSE', interval=interval, n_bars=1000)
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
        # Support Detection
        data['support_on_9ema'] = (data['close'] >= data['ema_9']) & (
                    abs(data['close'] - data['ema_9']) <= 0.01 * data['ema_9'])
        data['support_on_20ema'] = (data['close'] >= data['ema_20']) & (
                    abs(data['close'] - data['ema_20']) <= 0.01 * data['ema_20'])

        data['resistance_on_9ema'] = (data['close'] <= data['ema_9']) & (abs(data['close'] - data['ema_9']) <= 0.01 * data['ema_9'])
        data['resistance_on_20ema'] = (data['close'] <= data['ema_20']) & (abs(data['close'] - data['ema_20']) <= 0.01 * data['ema_20'])

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


def checktrend(df):
    # ✅ Step 3: Ensure data is not empty
    if df is None or df.empty:
        print("No data fetched. Check symbol or login status.")
        exit()

    # ✅ Step 4: Calculate Wick and Body Sizes
    df["Body"] = abs(df["close"] - df["open"])
    df["Upper Wick"] = df["high"] - df[["open", "close"]].max(axis=1)
    df["Lower Wick"] = df[["open", "close"]].min(axis=1) - df["low"]
    df["Total Wick"] = df["Upper Wick"] + df["Lower Wick"]
    df["Noise Ratio"] = df["Total Wick"] / df["Body"].replace(0, np.nan)  # Avoid divide by zero

    # ✅ Step 5: Define Market Noise vs Trend
    noise_threshold = 1.5  # If wick is 1.5x or more of body, it's noisy
    df["Market Noise"] = df["Noise Ratio"] > noise_threshold
    df["Trending"] = df["Noise Ratio"] < 1.0  # If wick is small relative to body, it's trending

    # ✅ Step 6: Identify Range-bound Market (Sideways)
    df["Prev High"] = df["high"].rolling(5).max().shift(1)
    df["Prev Low"] = df["low"].rolling(5).min().shift(1)
    df["Body Avg"] = df["Body"].rolling(5).mean().shift(1)
    df["Sideways"] = (df["Body"] < df["Body Avg"] * 0.7) & (df["high"] < df["Prev High"]) & (df["low"] > df["Prev Low"])

    # ✅ Step 7: Analyze last 5 candles for confirmation
    df["Noise Count"] = df["Market Noise"].rolling(5).sum()
    df["Trend Count"] = df["Trending"].rolling(5).sum()
    df["Sideways Count"] = df["Sideways"].rolling(5).sum()

    # ✅ Step 8: Define Market Condition (Noise, Trending, Sideways, Mixed)
    df["Market Condition"] = np.where(df["Noise Count"] >= 3, "Noise",
                             np.where(df["Trend Count"] >= 3, "Trending",
                             np.where(df["Sideways Count"] >= 3, "Sideways", "Mixed")))
    # ✅ Step 9: Print last 10 rows with Market Condition
    # print(df[["open", "close", "high", "low", "Noise Ratio", "Market Condition"]].tail(30))
    return df["Market Condition"].values[-1]

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

def placeemabuyorder(symbol, stickprice, exchange, token, lotsize, ltp, interwal, itemclose, condition, df):
    print(symbol)

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


def check_target(df,price):
    # Set the target price level
    price_level = price  # Adjust as needed
    target_price = round(price_level, -1)

    # Check if price touches the target
    df['Touched'] = (df['low'] <= target_price) & (df['high'] >= target_price)
    print(df['Touched'])
    # Analyze movement after price touch
    results = []
    lookahead_bars = 100  # Number of bars to check after touch

    for idx in df[df['Touched']].index:
        row_position = df.index.get_loc(idx)  # Get integer index position

        if row_position + lookahead_bars < len(df):
            future = df.iloc[row_position:row_position + lookahead_bars]
            max_gain = max(future['high']) - target_price
            max_loss = target_price - min(future['low'])
            results.append({'Timestamp': idx, 'Gain': max_gain, 'Loss': max_loss})

    # Convert results to DataFrame
    results_df = pd.DataFrame(results)

    if not results_df.empty:
        avg_gain = results_df['Gain'].mean()
        avg_loss = results_df['Loss'].mean()

        # Use Risk-Reward Ratio 1:2
        stop_loss = avg_loss
        target = avg_gain  # Adjust for different RR ratios

        print(f"After touching {target_price}:")
        print(f"✅ Recommended Stop-Loss: {stop_loss:.2f} points")
        print(f"✅ Recommended Target: {target:.2f} points")

    # Function to classify trend
    def classify_trend(df):
        if df.empty:
            return "No data available"

        mean_gain = df['Gain'].mean()
        mean_loss = df['Loss'].mean()

        # Define thresholds (adjust based on market conditions)
        trend_threshold = 10  # Points to define strong movement

        if mean_gain > trend_threshold and mean_loss < trend_threshold / 2:
            return "Uptrend 📈"
        elif mean_loss > trend_threshold and mean_gain < trend_threshold / 2:
            return "Downtrend 📉"
        elif mean_gain < trend_threshold and mean_loss < trend_threshold:
            return "Sideways ↔️"
        else:
            return "Mixed movement"

    # Determine the trend
    market_trend = classify_trend(results_df)
    return market_trend,target,stop_loss



def buy(token,lotsize,symbol,interwal,level,itemclose,df,condition):
    stickprice = symbol
    lotsize = lotsize
    # lotsize = cetoken['lotsize']

    less_than, greater_than = checkclosenear_price(level,itemclose)
    checkleveldiff = (greater_than - itemclose) > 20
    # print('token details :',cetoken['symbol'],symbol,lotsize)
    ltp = obj.ltpData('NSE', symbol, token)['data']['ltp']
    fetchdata = crete_update_table.fetchtokennbook()
    filteristoken = [item for item in fetchdata if
                     re.match(r'^[A-Za-z]+', item['script']).group() == symbol and item['lotsize'] > 0]
    lastitemdate = fetchdata[-1]['createddate']
    datematch = compare_dates_excluding_seconds(lastitemdate)
    check_candle_color = df.close.values[-1] > df.open.values[-1]
    trend = checktrend(df)
    if len(filteristoken) == 0 and datematch and check_candle_color and trend:
        if checkleveldiff or greater_than == 0:
            logging.info(f"place order : True")
            placeemabuyorder(symbol, stickprice, token, token, lotsize, ltp, interwal, itemclose, condition, df)

            title = f"{symbol} - {interwal}"
            add_plots = [
                mpf.make_addplot(df['ema_9'], color='blue', label='9 EMA'),
                mpf.make_addplot(df['ema_20'], color='orange', label='20 EMA')
            ]

            mpf.plot(df, type='candle', hlines=level.to_list(), addplot=add_plots, style='charles', title=title, savefig='static/chart.png')
            sendImgAlert("Here is an image:", "static/chart.png")

        else:
            title = f"{symbol} - {interwal}"
            add_plots = [
                mpf.make_addplot(df['ema_9'], color='blue', label='9 EMA'),
                mpf.make_addplot(df['ema_20'], color='orange', label='20 EMA')
            ]
            sendAlert(f" {symbol} ce diff is not greater than 20 points differnce : {greater_than - itemclose} closest registance: {greater_than} itemclose {itemclose}")
            # mpf.plot(df, type='candle', hlines=level.to_list(), addplot=add_plots, style='charles', title=title, savefig='static/chart.png')
            # sendImgAlert("Here is an image:", "static/chart.png")


def sell(token,lotsize,symbol,interwal,level,itemclose,df,condition):
    stickprice = symbol
    lotsize = lotsize
    less_than, greater_than = checkclosenear_price(level,itemclose)
    checkleveldiff = (itemclose - less_than) > 20
    ltp = obj.ltpData('NSE', symbol, token)['data']['ltp']
    fetchdata = crete_update_table.fetchtokennbook()
    filteristoken = [item for item in fetchdata if
                     re.match(r'^[A-Za-z]+', item['script']).group() == symbol and item['lotsize'] > 0]
    lastitemdate = fetchdata[-1]['createddate']
    datematch = compare_dates_excluding_seconds(lastitemdate)
    check_candle_color = df.close.values[-1] < df.open.values[-1]
    trend = checktrend(df)
    if len(filteristoken) == 0 and datematch and check_candle_color and trend:
        if checkleveldiff:
            logging.info(f"level 2 : place order : True ")
            placeemabuyorder(symbol,stickprice, token, token, lotsize, ltp,interwal,itemclose,condition,df)
            title = f"{symbol} - {interwal}"
            add_plots = [
                mpf.make_addplot(df['ema_9'], color='blue', label='9 EMA'),
                mpf.make_addplot(df['ema_20'], color='orange', label='20 EMA')
            ]
            mpf.plot(df, type='candle',hlines=level.to_list(),addplot=add_plots, style='charles',title=title, savefig='static/chart.png')
            sendImgAlert("Here is an image:", "static/chart.png")
        else:
            title = f"{symbol} - {interwal}"
            add_plots = [
                mpf.make_addplot(df['ema_9'], color='blue', label='9 EMA'),
                mpf.make_addplot(df['ema_20'], color='orange', label='20 EMA')
            ]
            sendAlert(f"{symbol} pe : diff is not greater than 20 points diffrence : {(itemclose - less_than)} closest support: {less_than} itemclose {itemclose}")
            # mpf.plot(df, type='candle', hlines=level.to_list(), addplot=add_plots, style='charles', title=title, savefig='static/chart.png')
            # sendImgAlert("Here is an image:", "static/chart.png")



def checkema_levels(data,symbol,interwal,level,token):
    df = data
    itemclose = df.close.values[-1]
    # print('item close',itemclose)
    latest_data = data.iloc[-1]
    print(latest_data)
    lotsize = 10

    if latest_data['buy_signal']:
        buy(token,lotsize,symbol,interwal,level,itemclose,df,'buy_signal')
    if latest_data['sell_signal']:
        sell(token,lotsize,symbol,interwal,level,itemclose,df,'sell_signal')
    # if latest_data['support_on_9ema']:
    #     buy(tokendata,symbol,interwal,level,itemclose,df,'support_on_9ema')
    if latest_data['support_on_20ema']:
        buy(token,symbol,lotsize,interwal,level,itemclose,df,'support_on_20ema')
    # if latest_data['resistance_on_9ema']:
    #    sell(tokendata,symbol,interwal,level,itemclose,df,'resistance_on_9ema')
    if latest_data['resistance_on_20ema']:
       sell(token,symbol,lotsize,interwal,level,itemclose,df,'resistance_on_20ema')
    else:
                print('no ema levels')


checkwithdata=  [{'symbol': 'PRAENG', 'token': '13944'}, {'symbol': 'AFIL', 'token': '24162'}, {'symbol': 'RAMANEWS', 'token': '13565'}, {'symbol': 'ORIENTHOT', 'token': '12650'}, {'symbol': 'XTGLOBAL', 'token': '25235'}, {'symbol': 'THOMASCOOK', 'token': '12831'}, {'symbol': 'HILTON', 'token': '14629'}, {'symbol': 'RATEGAIN', 'token': '7183'}, {'symbol': 'MGEL', 'token': '1593'}]
def storestocklist():
    for item in checkwithdata:
        interval = timeframe_map['1m']
        bars = 100
        rollingwindow = 20
        level_diff_threshold = 20
        result,level,df = fetch_and_process_data(item['symbol'],interval,bars,rollingwindow,level_diff_threshold)
        time.sleep(2)
        checkema_levels(df,item['symbol'],interval,level,item['token'])
        # print(item.nsecode)
    # print(storestocklis)

# storestocklist()

def main():
    set = technically_filtered_stock.condition
    # print(set)
    getlist = technically_filtered_stock.get_data(set['top-gainers-and-losers'])
    storedata = []
    global storestocklis
    for item in getlist[:10]:
        token = storetoken.getstockTokenInfo(item['nsecode'])

        if not token:
            continue  # Skip this item and move to the next one

        print(token)
        storedata.append({'symbol': item['nsecode'], 'token': token['token']})

    print('store',storedata)
    storestocklis = storedata

# main()
storestocklist()
schedule.every(1).minutes.do(storestocklist)
# placeoptionsellorder('BANKNIFTY','BANKNIFTY04SEP2451400CE',49076,'25',223,'1m',51410)


while True:
    try:
        schedule.run_pending()
        time.sleep(2)
    except Exception as e:
        raise e

