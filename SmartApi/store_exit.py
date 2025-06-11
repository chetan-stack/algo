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


api_key = document.api_key
user_id = document.user_id
password = document.password
totp = pyotp.TOTP(document.totp).now()
obj = SmartConnect(api_key=api_key)
token = obj.generateToken(obj.generateSession(user_id, password, totp)["data"]["refreshToken"])

current_date_time = datetime.datetime.now()
from_date = current_date_time - timedelta(days = 1)
interval = "ONE_MINUTE"


nsechange = {
    'NIFTY':'NFO',
    'BANKNIFTY':'NFO',
    'SENSEX':'BFO'

}

def get_historical_data(symbol_token, exchange, interval, from_date, to_date):
    try:
        rolling_window = 10
        level_diff_threshold = 10
        print(symbol_token, from_date.strftime("%Y-%m-%d 09:15"), to_date.strftime("%Y-%m-%d %H:%M"), interval)
        params = {
            "symboltoken": symbol_token,
            # "exchange": 'NFO',
            "exchange": exchange,
            "interval": 'ONE_MINUTE',
            "fromdate": from_date.strftime("%Y-%m-%d 09:15"),
            "todate": to_date.strftime("%Y-%m-%d %H:%M")
        }

        historical_data = obj.getCandleData(params)['data']

        if historical_data is not None:
            df = pd.DataFrame(historical_data).tail(100)
            print("DataFrame Shape:", df.shape)

            df.columns = ["datetime", "open", "high", "low", "close", "volume"]
            df["datetime"] = pd.to_datetime(df["datetime"])
            df.set_index("datetime", inplace=True)

            df["sup"] = ta.supertrend(df['high'], df['low'], df['close'], length=10, multiplier=3)['SUPERT_10_3.0']
            df["ema9"] = ta.ema(df["close"], length=9)
            df["ema20"] = ta.ema(df["close"], length=20)
            df['sell_signal'] = (df['close'] < df['ema9']) & (df['close'].shift(1) >= df['ema9'].shift(1))
            df['buy_signal'] = (df['close'] > df['ema9']) & (df['close'].shift(1) <= df['ema9'].shift(1))

            supports = df[df.low == df.low.rolling(rolling_window, center=True).min()].close
            resistances = df[df.high == df.high.rolling(rolling_window, center=True).max()].close

            level = pd.concat([supports, resistances])
            level = level[abs(level.diff()) > level_diff_threshold]
            return level,df
        else:
            print("No historical data found.")
            return None

    except Exception as e:
        print(f"An error occurred: {e}")
        getstoreetoken()



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

storewaitlimit = []
DATA_FILE = "auto_trade.json"  # File to store form data
# Function to load stored data
def load_data():
      # File to store form data
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)  # Read existing data
    except (FileNotFoundError, json.JSONDecodeError):
        return {}  # Return empty if file not found or corrupted
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

def exitstetergy(df,level,item):
    date = datetime.datetime.now()
    # itemclose = df.close.values[-1]
    symbol = item['script']
    buyprice = item['ltp']
    lotsize = item['lotsize']
    id = item['id']
    match = re.match(r"^[A-Za-z]+", item['script'])
    first_string = match.group() if match else None
    ltp = obj.ltpData(nsechange[first_string], symbol, item['token'])['data']['ltp']
    # ema = df.ema9.values[-1]
    latest_data = df.iloc[-1]
    less_than, greater_than = checkclosenear_price(level,df.close.values[-1])
    profit_or_loss = (ltp - buyprice) * lotsize
    print('profit',profit_or_loss,'sell signal:',latest_data['sell_signal'],latest_data['buy_signal'])
    print("close","ema",df.close.values[-1],df.ema9.values[-1])
    print('target = ',greater_than,"stoploss = ",less_than,"buyprice = ",buyprice,"ltp =  ",df.close.values[-1])
    print(symbol,lotsize,buyprice)
    lastitemdate = item['createddate']
    datematch = compare_dates_excluding_seconds(lastitemdate)
    orderplaced = False
    loaddata = load_data()['store']

    # print("--------",loaddata)
    # print("-------chytcj======",first_string,loaddata[0])
    filterloaddata = [item for item in loaddata if item['symbol'] == first_string]
    # print("-----",filterloaddata)
    if df.close.values[-1] < df.ema9.values[-1] and datematch:
        store = {
                'symbol': symbol,
                'count':1
            }
        maxcount = 2
        if len(storewaitlimit) > 0:
            for item in storewaitlimit:
                if symbol == item['symbol']:
                    item['count'] += 1
                    if item['count'] > maxcount:
                         orderplaced = True
                else:
                    storewaitlimit.append(store)
        else:
             storewaitlimit.append(store)


    elif df.close.values[-1] < less_than and datematch:
        orderplaced = True
    elif df.close.values[-1] > greater_than and datematch:
        orderplaced = True

    elif filterloaddata == 'no_trade':
        orderplaced = True

    if orderplaced:
       if True:
                  # if filterloaddata == 'no_trade':

            match = re.match(r"^[A-Za-z]+", item['script'])
            first_string = match.group() if match else None
            orderId,checkorderplace = place_order(token,symbol,lotsize,nsechange[first_string],'SELL','MARKET',ltp)
            if checkorderplace:
                profit_order = (
                            f"Exit by EMA"
                            f"Time: {date} | Symbol: {symbol} | Exit Price: {ltp} | Buy Price: {buyprice} | "
                            f"Profit/Loss: {profit_or_loss}"
                        )

                crete_update_table.updateorderplace(id, 0, profit_order)
                sendAlert(profit_order)
            else:
                sendAlert(f"{orderId}")

       else:
           profit_order = f"Ema exit matches but still in trade : {filterloaddata}"
           print(profit_order)
           # sendAlert(profit_order)


def calculate_sell_trade_levels_with_fibo_pivot(df, swing_lookback=5, rr_ratio=2):
    """
    Enhanced sell trade level calculator with Fibonacci and Pivot levels.
    """

    if len(df) < swing_lookback + 1:
        raise ValueError("Not enough data to compute swing levels.")

    # Last candle
    entry_price = df['close'].iloc[-1]

    # Define swing high/low range
    swing_high = df['high'].iloc[-swing_lookback:-1].max()
    swing_low = df['low'].iloc[-swing_lookback:-1].min()

    # Fibonacci levels (assuming down move: retracement from high to low)
    fib_levels = {
        'fibo_0': swing_low,
        'fibo_38.2': swing_high - 0.382 * (swing_high - swing_low),
        'fibo_50': swing_high - 0.5 * (swing_high - swing_low),
        'fibo_61.8': swing_high - 0.618 * (swing_high - swing_low),
        'fibo_100': swing_high,
        'fibo_ext_161.8': swing_low - 0.618 * (swing_high - swing_low)
    }

    # Pivot Points (Classic formula)
    last_high = df['high'].iloc[-2]
    last_low = df['low'].iloc[-2]
    last_close = df['close'].iloc[-2]
    pivot = (last_high + last_low + last_close) / 3
    s1 = 2 * pivot - last_high
    s2 = pivot - (last_high - last_low)
    r1 = 2 * pivot - last_low
    r2 = pivot + (last_high - last_low)

    pivot_levels = {
        'pivot': round(pivot, 2),
        's1': round(s1, 2),
        's2': round(s2, 2),
        'r1': round(r1, 2),
        'r2': round(r2, 2)
    }

    # Stop-loss: above swing high or R1
    stop_loss = max(swing_high, r1)

    # Risk per unit
    risk = stop_loss - entry_price
    if risk <= 0:
        raise ValueError("Invalid setup: stop-loss is below entry.")

    # Target Option 1: Fixed RR
    target_rr = entry_price - rr_ratio * risk

    # Target Option 2: Pivot level (S1/S2)
    target_pivot = s1 if entry_price > s1 else s2

    # Target Option 3: Fibonacci extension
    target_fibo = fib_levels['fibo_ext_161.8']

    return {
        'entry_price': round(entry_price, 2),
        'stop_loss': round(stop_loss, 2),
        'risk_per_unit': round(risk, 2),
        'target_rr': round(target_rr, 2),
        'target_pivot': round(target_pivot, 2),
        'target_fibo_ext_161.8': round(target_fibo, 2),
        'fibonacci_levels': {k: round(v, 2) for k, v in fib_levels.items()},
        'pivot_levels': pivot_levels,
        'risk_reward_ratio': rr_ratio
    }


def exitstetergysell(df,level,item,headge):
    print('-----------------',headge)
    date = datetime.datetime.now()
    # headge = headge[0]
    print(headge)
    fetchtarget = load_data()
    detecttarget = calculate_sell_trade_levels_with_fibo_pivot(df)
    # itemclose = df.close.values[-1]
    symbol = item['script']
    buyprice = item['ltp']
    lotsize = abs(item['lotsize'])
    id = item['id']
    match = re.match(r"^[A-Za-z]+", item['script'])
    first_string = match.group() if match else None
    ltp = obj.ltpData(nsechange[first_string], symbol, item['token'])['data']['ltp']
    # print("----------------------", headge['script'], headge['token'])
    headgeltp = obj.ltpData(nsechange[first_string], headge['script'], headge['token'])['data']['ltp']
    # print('-----',headgeltp)
    # ema = df.ema9.values[-1]
    latest_data = df.iloc[-1]
    less_than, greater_than = checkclosenear_price(level,df.close.values[-1])
    profit_or_loss = (buyprice - ltp) * lotsize
    headgeprofit = (headgeltp - headge['ltp']) * headge['lotsize']
    print(headgeltp , headge['ltp'])
    print('profit',profit_or_loss,'headge profit',headgeprofit,'sell signal:',latest_data['sell_signal'],latest_data['buy_signal'])
    print("close","ema",df.close.values[-1],df.ema9.values[-1])
    print('target = ',greater_than,"stoploss = ",less_than,"buyprice = ",buyprice,"ltp =  ",df.close.values[-1])
    print(symbol,lotsize,buyprice)
    lastitemdate = item['createddate']
    datematch = compare_dates_excluding_seconds(lastitemdate)
    orderplaced = False
    loaddata = load_data()['store']
    reason = ''
    # print(detecttarget)
    print(df.close.values[-1],ltp,fetchtarget['target_points'],fetchtarget['loss_points'])
    target_points = float(fetchtarget['target_points'])
    loss_points = float(fetchtarget['loss_points'])
    if ltp <= (buyprice - target_points) or ltp >= (buyprice + loss_points):
        orderplaced = True
        reason = "target or stoploss hit"

    # elif ltp <= float(detecttarget['target_rr']):
    #     orderplaced = True
    #     reason = "target_rr"
    # elif ltp <= float(detecttarget['target_fibo_ext_161.8']):
    #     orderplaced = True
    #     reason = "fibo_161.8_hit"
    # elif ltp <= float(detecttarget['target_pivot']):
    #     orderplaced = True
    #     reason = "pivot_s2_hit"
    elif df.close.values[-1] < less_than and datematch:
        orderplaced = True
    elif df.close.values[-1] > greater_than and datematch:
        orderplaced = True

    if orderplaced:
       if True:
                  # if filterloaddata == 'no_trade':

            match = re.match(r"^[A-Za-z]+", item['script'])
            first_string = match.group() if match else None
            orderId,checkorderplace = place_order(token,symbol,lotsize,nsechange[first_string],'SELL','MARKET',ltp)
            if checkorderplace:
                profit_order = (
                            f"Exit by EMA Reason:{reason}"
                            f"Time: {date} | Symbol: {symbol} | Exit Price: {ltp} | Buy Price: {buyprice} | "
                            f"Profit/Loss: {profit_or_loss}"
                        )
                crete_update_table.updateorderplace(headge['id'],0,headgeprofit)
                crete_update_table.updateorderplace(id, 0, profit_order)
                sendAlert(profit_order)
            else:
                sendAlert(f"{orderId}")

       else:
           profit_order = f"Ema exit matches but still in trade : {filterloaddata}"
           print(profit_order)
           # sendAlert(profit_order)


def getstoreetoken():
    print('enter exit')
    getbook = crete_update_table.fetchsupport()
    store = []
    for item in getbook:
        if item is not None:
            if "CE" in item['script'] or "PE" in item['script']:
               if item['lotsize'] > 0 and item['profit'] == 0:
                   try:
                        match = re.match(r"^[A-Za-z]+", item['script'])
                        first_string = match.group() if match else None
                        current_date_time = datetime.datetime.now()
                        from_date = current_date_time - timedelta(days = 1)
                        leveel,fetchdata = get_historical_data(item['token'], nsechange[first_string], interval, from_date, current_date_time)
                        if len(fetchdata) > 0:
                            exitstetergy(fetchdata,leveel, item)
                   except Exception as e:
                        print(f"Error fetching or processing data for {item['token']}: {e}")
                        time.sleep(4)
                        getstoreetoken()
               elif item['lotsize'] < 0:
                    try:
                        match = re.match(r"^[A-Za-z]+", item['script'])
                        first_string = match.group() if match else None
                        current_date_time = datetime.datetime.now()
                        from_date = current_date_time - timedelta(days = 1)
                        leveel,fetchdata = get_historical_data(item['token'], nsechange[first_string], interval, from_date, current_date_time)
                        if len(fetchdata) > 0:
                            matcheshedge = [a for a in getbook if first_string == re.match(r"^[A-Za-z]+", a['script']).group() and a['lotsize'] > 0][0]
                            # print(matcheshedge)
                            exitstetergysell(fetchdata,leveel, item,matcheshedge)
                    except Exception as e:
                        print(f"Error fetching or processing data for {item['token']}: {e}")
                        time.sleep(4)
                        getstoreetoken()

    time.sleep(2)



getstoreetoken()
schedule.every(10).seconds.do(getstoreetoken)
# fetchdata = get_historical_data(863943, nsechange['SENSEX'], interval, from_date, current_date_time)

# # placeoptionsellorder('BANKNIFTY','BANKNIFTY04SEP2451400CE',49076,'25',223,'1m',51410)
# ltp = obj.ltpData('NFO', 'BANKNIFTY27MAR2548000PE', '61085')['data']['ltp']
# print(ltp)


while True:
    try:
        schedule.run_pending()
        time.sleep(2)
    except Exception as e:
        raise e

