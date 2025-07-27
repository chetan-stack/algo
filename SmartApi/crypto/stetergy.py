import json
import re
import time

import requests
from datetime import datetime, timedelta
import pandas as pd
import pandas_ta as ta
import schedule
import mplfinance as mpf

import crete_update_table
from datetime import datetime
import pytz
from tvDatafeed import TvDatafeed, Interval
import storecandlestickdata
import logging
from tvDatafeed import TvDatafeed, Interval
import checktrending
import placeOrder
# Your TradingView credentials
username = 'YourTradingViewUsername'
password = 'YourTradingViewPassword'

# Connect to TradingView
tv = TvDatafeed(username, password)

crpto = {
    "BTCUSD":"BTCUSD",
}

timeframe_map = {
    '1m': Interval.in_1_minute,
    '5m': Interval.in_5_minute,
    '15m': Interval.in_15_minute,

}

investment_in_inr = 10000
exchange_rate = 80  # Replace with the current exchange rate

logging.basicConfig(
    filename='crptooption.log',  # Name of the log file
    level=logging.INFO,  # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format
    datefmt='%Y-%m-%d %H:%M:%S'  # Date format in logs
)

def fetch_and_process_data(data,rolling_window, level_diff_threshold):
    try:
        df = data
        # df = pd.DataFrame(
        #         data,
        #         columns=['date', 'open', 'high', 'low', 'close', 'volume'])
        # print(df.close.values[-1])
        if df is not None:

            resistancelevel = []
            supportlevel = []
            itemclose = df.close.values[-1]
            # print(itemclose)
            supports = df[df.low == df.low.rolling(rolling_window, center=True).min()].close
            resistances = df[df.high == df.high.rolling(rolling_window, center=True).max()].close
            level = pd.concat([supports, resistances])
            level = level[abs(level.diff()) > level_diff_threshold]
            # print('levels',level)
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
            # print(level)
            return True, level
            # return df, level, registance_item, support_item,itemclose
        else:
            return False, 'no'
    except Exception as e:
        print('error', e)

def get_delta_histo_data(symbol):
    current_date_time = datetime.now()
    start_date_time = current_date_time.replace(hour=0, minute=0, second=0, microsecond=0)
    headers = {
      'Accept': 'application/json'
    }

    r = requests.get('https://api.india.delta.exchange/v2/history/candles', params={
      'resolution': '1m',  'symbol': symbol,
         'start': int(start_date_time.timestamp()),  # Today's midnight timestamp
    'end': int(current_date_time.timestamp())  # Current timestamp

    }, headers = headers)
    histdata = r.json()['result']
    df = pd.DataFrame(
                histdata,
                columns=['date', 'open', 'high', 'low', 'close','time','volume'])
    # Convert 'date' column from timestamp to datetime format
    df['date'] = pd.to_datetime(df['time'], unit='s')

    # Set date as the index
    df.set_index('date', inplace=True)
    df = df.sort_index(ascending=True)  # FIFO (oldest first)
    df['Supertrend'] = ta.supertrend(df['high'], df['low'], df['close'], length=10,
                          multiplier=2)['SUPERT_10_2.0']
    # Check if the last three Supertrend values are the same
    if df['Supertrend'].values[-3] == df['Supertrend'].values[-2] == \
            df['Supertrend'].values[-1]:
        trend_status = '0'  # All values are the same
    else:
        trend_status = '1'  # Values are different
    df['ema_9'] = df['close'].ewm(span=9).mean()
    df['ema_20'] = df['close'].ewm(span=20).mean()
    # df['sell_signal'] = (df['close'] < df['ema_9']) & (df['close'].shift(1) >= df['ema_9'].shift(1))
    df['sell_signal'] = df['close'] < df['ema_9']
    print(df.close.values[-1],df.ema_9.values[-1],df.ema_20.values[-1])
    return df


def get_historical_data(symbol,time):
    # current_date_time = datetime.now()
    # start_date_time = current_date_time.replace(hour=0, minute=0, second=0, microsecond=0)
    # params = {
    #     'resolution': time,
    #     'symbol': symbol,
    #     'start': int(start_date_time.timestamp()),
    #     'end': int(current_date_time.timestamp()),
    #     'count': 100
    # }
    # print('time',start_date_time.timestamp(),current_date_time.timestamp())
    # response = requests.get("https://cdn.india.deltaex.org/v2/history/candles", params=params)
    # historical_data = response.json()
    # # print(len(historical_data['result']))
    # last_candles = historical_data['result'][-100:]
    last_candles = tv.get_hist(symbol=symbol, exchange='CRYPTO',interval=time, n_bars=100)
    df = pd.DataFrame(
                last_candles,
                columns=['date', 'open', 'high', 'low', 'close','volume'])
    df['Supertrend'] = ta.supertrend(df['high'], df['low'], df['close'], length=10,
                          multiplier=2)['SUPERT_10_2.0']

    # Check if the last three Supertrend values are the same
    if df['Supertrend'].values[-3] == df['Supertrend'].values[-2] == \
            df['Supertrend'].values[-1]:
        trend_status = '0'  # All values are the same
    else:
        trend_status = '1'  # Values are different
    df['ema_9'] = df['close'].ewm(span=9).mean()
    df['ema_20'] = df['close'].ewm(span=20).mean()
    # Add the result as a new column (optional)
    df.loc[df.index[-1], 'Trend_Status'] = trend_status
    return df

def fetch_and_process_data2(symbol, interval, n_bars, rolling_window, level_diff_threshold):
    username = 'YourTradingViewUsername'
    password = 'YourTradingViewPassword'

    tv = TvDatafeed(username, password)
    try:
        df = tv.get_hist(symbol=symbol, exchange='CRYPTO', interval=interval, n_bars=100)
        df['Supertrend'] = ta.supertrend(df['high'], df['low'], df['close'], length=10,
                          multiplier=2)['SUPERT_10_2.0']
        df["ema9"] = ta.ema(df["close"], length=9)
        df["ema20"] = ta.ema(df["close"], length=20)
        df["ema50"] = ta.ema(df["close"], length=50)
        # Check if the last three Supertrend values are the same
        if df['Supertrend'].values[-3] == df['Supertrend'].values[-2] == \
                df['Supertrend'].values[-1]:
            trend_status = '0'  # All values are the same
        else:
            trend_status = '1'  # Values are different

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


def generate_sequence_and_find_closest(start, diff, count, compare_value):
    sequence = [start + i * diff for i in range(count)]
    minvalue = min(sequence, key=lambda x: abs(x - compare_value))
    return minvalue



def get_custom_date(timezone_str='Asia/Kolkata'):
    # Set the timezone
    local_tz = pytz.timezone(timezone_str)

    # Get the current time with the correct timezone
    now = datetime.now(local_tz)
    # print(now)
    # Ensure we compare with the correct time (5:30 PM in the local timezone)
    cutoff_time = now.replace(hour=17, minute=30, second=0, microsecond=0)

    # Check if the current time is after 5:30 PM
    if now > cutoff_time:
        # Add one day if the time is after 5:30 PM
        date = now + timedelta(days=1)
    else:
        # Otherwise, use today's date
        date = now

    # Return the date in 'YYMMDD' format
    return date.strftime('%d%m%y')

def getproduct(close,type):
    # Fetch ticker information for a specific symbol
    RTM = int(round(close / 100) * 100)  # to get check acurate price
    # print(close, RTM)
    getatm = generate_sequence_and_find_closest(RTM,2000,20,close)
    datetym = get_custom_date()
    symbol = f"{type}-BTC-{getatm}-{datetym}"  # Example symbol
    print('symbol',symbol)
    response = requests.get("https://cdn.india.deltaex.org/v2/tickers" + f"/{symbol}")
    ticker_info = response.json()
    # print(ticker_info['result'])
    return ticker_info['result']

def process_advanced_signals(data, trend_duration=3):
    """
    Analyze EMA crossover, retest, and other signals with advanced logic.

    Args:
        data (pd.DataFrame): Historical price data with 'close' column.
        trend_duration (int): Minimum duration (in candles) for a valid trend.

    Returns:
        pd.DataFrame: Updated DataFrame with advanced signal logic applied.
    """
    # Calculate EMA 9 and EMA 20
    data['ema_9'] = data['close'].ewm(span=9).mean()
    data['ema_20'] = data['close'].ewm(span=20).mean()
    data['ema_50'] = data['close'].ewm(span=50).mean()
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

    return data

# def exitstetergy():
#     date = datetime.now()
#     fetch = crete_update_table.fetchtcryptoorderbook()
#     # print(fetch)
#     if len(fetch) > 0:
#         for item in fetch:
#             if item['lotsize'] > 0:
#                 symbol = item['script']
#                 response = requests.get("https://cdn.india.deltaex.org/v2/tickers" + f"/{symbol}")
#                 ticker_info = response.json()
#                 print('ticker_info',ticker_info,'ticker_info')
#                 ltp = float(ticker_info['result']['mark_price'])
#                 print(ltp)
#                 target = item['ltp'] * 1.10
#                 stoploss = item['ltp'] * 0.97
#                 # target =item['ltp'] + 10
#                 # stoploss = item['ltp'] - 5
#                 if ltp > target:
#                     profit = (ltp - item['ltp']) * item['lotsize']
#                     crete_update_table.updatecrypto(item['id'],0,profit)
#                     bot_message = f"crypto target hit symbol: {item['script']} - exit: {profit} - ltp: {item['ltp']} - date: {date}"
#                     sendAlert(bot_message)
#                 elif ltp < stoploss:
#                     profit = (ltp - item['ltp']) * item['lotsize']
#                     crete_update_table.updatecrypto(item['id'],0,profit)
#                     bot_message = f"crypto target hit symbol: {item['script']} - exit: {profit} - ltp: {item['ltp']} - date: {date}"
#                     sendAlert(bot_message)
#                 else:
#                     profit = (ltp - item['ltp']) * item['lotsize']
#                     print(f'you are in trade and the profit is {profit} ltp is {ltp} target is {target} stoploss is {stoploss}')
#     else:
#         print('No order place')


import requests
from datetime import datetime

# Dictionary to track max profit and max LTP
crypto_stats = {}

from datetime import datetime
import requests

crypto_stats = {}

def exitstetergynext_ema(df,item):
    print('eenterexit 2')
    date = datetime.now()
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
            place = placeOrder.place_order(item['id'],item['lotsize'],'sell')
            if place['success'] == True:
                    profit_order = (
                                f"Exit by EMA"
                                f"Time: {date} | Symbol: {symbol} | Exit Price: {ltp} | Buy Price: {buyprice} | "
                                f"Profit/Loss: {profit_or_loss}"
                            )

                    crete_update_table.updatecrypto(item['id'], 0, profit_or_loss)
                    sendAlert(profit_order)
            else:
                sendAlert(f"{place}")



# def exitstetergynext_ema(df,item):
#     print('eenterexit 2')
#     date = datetime.now()
#     itemclose = df.close.values[-1]
#     symbol = item['script']
#     buyprice = item['ltp']
#     lotsize = item['lotsize']
#     ltp = df.close.values[-1]
#     ema = df['ema_9'].values[-1]
#     profit_or_loss = (ltp - buyprice) * lotsize
#     print("profit",profit_or_loss)
#     if "CE" in item['script']:
#         if itemclose < ema:
#             place = placeOrder.place_order(item['id'],item['qty'],'sell')
#             if place['success'] == True:
#                     profit_order = (
#                                 f"Exit by EMA"
#                                 f"Time: {date} | Symbol: {symbol} | Exit Price: {ltp} | Buy Price: {buyprice} | "
#                                 f"Profit/Loss: {profit_or_loss}"
#                             )
#
#                     crete_update_table.updateorderplace(id, 0, profit_order)
#                     sendAlert(profit_order)
#             else:
#                 sendAlert(f"{place}")
#     elif "PE" in item['script']:
#         if itemclose < ema:
#             place = placeOrder.place_order(item['id'],item['qty'],'sell')
#             if place['success'] == True:
#                 profit_order = (
#                             f"Exit by EMA"
#                             f"Time: {date} | Symbol: {symbol} | Exit Price: {ltp} | Buy Price: {buyprice} | "
#                             f"Profit/Loss: {profit_or_loss}"
#                         )
#
#                 crete_update_table.updateorderplace(id, 0, profit_order)
#                 sendAlert(profit_order)
#             else:
#                 sendAlert(f"{place}")

def exitstetergywithema():
    print('enter in exit 2')
    getbook = crete_update_table.fetchtcryptoorderbook()
    for item in getbook:
        if item is not None:
            if item['lotsize'] > 0:
                fetchdata = get_delta_histo_data(item['script'])
                exitstetergynext_ema(fetchdata,item)




def exitstetergy():
    fetchtarget = load_data()
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    fetch = crete_update_table.fetchtcryptoorderbook()
    print('Enter in Exit')
    if not fetch:
        print('No order placed')
        return

    for item in fetch:
        if item['lotsize'] > 0:
            symbol = item['script']
            url = f"https://cdn.india.deltaex.org/v2/tickers/{symbol}"
            response = requests.get(url)
            # print(response)
            ticker_info = response.json()
            print(ticker_info)

            if 'result' not in ticker_info or 'mark_price' not in ticker_info['result']:
                print(f"Error: Invalid API response for {symbol}")
                continue

            ltp = float(ticker_info['result']['mark_price'])
            product_id = ticker_info['result']['product_id']

            buy_price = item['ltp']  # Entry price


            # Initialize tracking values if not present
            if symbol not in crypto_stats:
                crypto_stats[symbol] = {
                    'max_profit': float('-inf'),
                    'max_ltp': float('-inf'),
                    #  'target': item['ltp'] * 1.10,  # Initial target
                    # 'stoploss': item['ltp'] * 0.97  # Initial stoploss
                    'target': item['ltp'] + 300,  # Initial target
                    'stoploss': item['ltp'] - 150  # Initial stoploss
                }

            # Update max LTP and profit
            crypto_stats[symbol]['max_ltp'] = max(crypto_stats[symbol]['max_ltp'], ltp)
            profit = (ltp - buy_price) * item['lotsize']
            crypto_stats[symbol]['max_profit'] = max(crypto_stats[symbol]['max_profit'], profit)

            target = crypto_stats[symbol]['target']
            stoploss = crypto_stats[symbol]['stoploss']
            max_ltp = crypto_stats[symbol]['max_ltp']
            print('id',item['id'])
            print(f"LTP: {ltp} | buyprice: {buy_price} | Target: {target} | Stoploss: {stoploss} | Max LTP: {max_ltp} | Profit: {profit} | Max Profit: {crypto_stats[symbol]['max_profit']}")

            if ltp >= target:
                # Increase target by 10 points
                crypto_stats[symbol]['target'] = ltp + 10
                # Adjust trailing stop-loss to 5 points below LTP
                crypto_stats[symbol]['stoploss'] = ltp - 5

                print(f"Target hit! New Target: {crypto_stats[symbol]['target']} | New Stoploss: {crypto_stats[symbol]['stoploss']}")
            # or (ltp <= max_ltp - 5 and max_ltp - buy_price >= 10)
            # ltp < stoploss or (ltp <= max_ltp - 15 and max_ltp - buy_price >= 100):
            elif ltp < stoploss or (ltp <= max_ltp - 15 and max_ltp - buy_price >= 100)::
                print(product_id)
                # Exit trade if:
                # - LTP is 5 points below max LTP AND
                # - max LTP is at least 10 points above the buy price
                place = placeOrder.place_order(product_id,item['lotsize'],'sell')
                if place['success'] == True:
                    crete_update_table.updatecrypto(item['id'], 0, profit)
                    bot_message = (
                        f"Crypto exit triggered!\n"
                        f"Symbol: {symbol}\n"
                        f"Exit Profit: {profit}\n"
                        f"LTP: {ltp}\n"
                        f"Target: {target}\n"
                        f"Stoploss: {stoploss}\n"
                        f"Buy Price: {buy_price}/n"
                        f"Points: {ltp-buy_price}/n"
                        f"Max LTP: {max_ltp}\n"
                        f"Max Profit: {crypto_stats[symbol]['max_profit']}\n"
                        f"Date: {date}"
                    )

                    sendAlert(bot_message)
                    if (ltp <= max_ltp - 15 and max_ltp - buy_price >= 100):
                        sendAlert(f"Exit triggered: LTP dropped below max LTP ---- exit-ltp:{ltp} buyprice:{buy_price} maxltp:{max_ltp} diff.:{max_ltp - buy_price}")
                    print(f"Exit triggered: LTP dropped below max LTP - 5 and max LTP - Buy Price ≥ 10 OR Stoploss hit")
                    del crypto_stats[symbol]
                else:
                    sendAlert(f"{place}")

            else:
                print(f"You are in trade: Profit: {profit} | LTP: {ltp} | Target: {target} | Stoploss: {stoploss}")
        if item['lotsize'] < 0:
            symbol = item['script']
            url = f"https://cdn.india.deltaex.org/v2/tickers/{symbol}"
            response = requests.get(url)
            # print(response)
            ticker_info = response.json()
            print(ticker_info)
            if 'result' not in ticker_info or 'mark_price' not in ticker_info['result']:
                print(f"Error: Invalid API response for {symbol}")
                continue

            ltp = float(ticker_info['result']['mark_price'])
            buy_price = item['ltp']  # Entry price
            target_points = float(fetchtarget['target_points'])
            loss_points = float(fetchtarget['loss_points'])

            # Initialize tracking values if not present
            if symbol not in crypto_stats:
                crypto_stats[symbol] = {
                    'max_profit': float('-inf'),
                    'max_ltp': float('-inf'),
                    #  'target': item['ltp'] * 1.10,  # Initial target
                    # 'stoploss': item['ltp'] * 0.97  # Initial stoploss
                    'target': max(item['ltp'] - target_points,100),  # Initial target
                    'stoploss': item['ltp'] + loss_points  # Initial stoploss
                }

            # Update max LTP and profit
            crypto_stats[symbol]['max_ltp'] = max(crypto_stats[symbol]['max_ltp'], ltp)
            profit = (ltp - buy_price) * item['lotsize']
            crypto_stats[symbol]['max_profit'] = max(crypto_stats[symbol]['max_profit'], profit)

            target = crypto_stats[symbol]['target']
            stoploss = crypto_stats[symbol]['stoploss']
            max_ltp = crypto_stats[symbol]['max_ltp']

            print(f"LTP: {ltp} | buyprice: {buy_price} | Target: {target} | Stoploss: {stoploss} | Max LTP: {max_ltp} | Profit: {profit} | Max Profit: {crypto_stats[symbol]['max_profit']}")
            ordertype = False
            if ltp <= target:
                ordertype = True
                print(f"Target hit! New Target: {crypto_stats[symbol]['target']} | New Stoploss: {crypto_stats[symbol]['stoploss']}")
            # or (ltp <= max_ltp - 5 and max_ltp - buy_price >= 10)
            elif ltp > stoploss:
                ordertype = True
                # Exit trade if:
                # - LTP is 5 points below max LTP AND
                # - max LTP is at least 10 points above the buy price
            if ordertype == True:
                place = placeOrder.place_order(item['id'],item['lotsize'],'sell')
                if place['success'] == True:
                    crete_update_table.updatecrypto(item['id'], 0, profit)
                    bot_message = (
                        f"Crypto exit triggered!\n"
                        f"Symbol: {symbol}\n"
                        f"Exit Profit: {profit}\n"
                        f"LTP: {ltp}\n"
                        f"Target: {target}\n"
                        f"Stoploss: {stoploss}\n"
                        f"Buy Price: {buy_price}/n"
                        f"Points: {ltp-buy_price}/n"
                        f"Max LTP: {max_ltp}\n"
                        f"Max Profit: {crypto_stats[symbol]['max_profit']}\n"
                        f"Date: {date}"
                    )

                    sendAlert(bot_message)
                    if (ltp <= max_ltp - 15 and max_ltp - buy_price >= 100):
                        sendAlert(f"Exit triggered: LTP dropped below max LTP ---- exit-ltp:{ltp} buyprice:{buy_price} maxltp:{max_ltp} diff.:{max_ltp - buy_price}")
                    print(f"Exit triggered: LTP dropped below max LTP - 5 and max LTP - Buy Price ≥ 10 OR Stoploss hit")
                    del crypto_stats[symbol]
                else:
                    sendAlert(f"{place}")

            else:
                print(f"You are in trade: Profit: {profit} | LTP: {ltp} | Target: {target} | Stoploss: {stoploss}")



# with traling target


# def exitstetergy():
#     date = datetime.now()
#     fetch = crete_update_table.fetchtcryptoorderbook()
#     # print(fetch)
#
#     if len(fetch) > 0:
#         for item in fetch:
#             if item['lotsize'] > 0:
#                 symbol = item['script']
#                 response = requests.get(f"https://cdn.india.deltaex.org/v2/tickers/{symbol}")
#                 ticker_info = response.json()
#                 print('ticker_info:', ticker_info)
#
#                 ltp = ticker_info['result']['close']
#                 stoploss = item['ltp'] * 0.97
#
#                 # Initialize or update the highest LTP reached
#                 if 'highest_ltp' not in item:
#                     item['highest_ltp'] = item['ltp']
#                 item['highest_ltp'] = max(item['highest_ltp'], ltp)
#
#                 # Calculate the dynamic trailing stop loss
#                 trailing_stoploss = item['highest_ltp'] * 0.98
#
#                 # Check exit conditions
#                 if ltp >= item['highest_ltp']:  # Update trailing target dynamically
#                     item['highest_ltp'] = ltp  # Update the highest LTP
#                     profit = (ltp - item['ltp']) * item['lotsize']
#
#                     print(
#                         f"Current Profit: {profit}\n"
#                         f"Trailing target updated: Highest LTP: {item['highest_ltp']}, "
#                         f"Trailing Stop Loss: {trailing_stoploss}"
#                     )
#
#                 elif ltp <= (trailing_stoploss-5):  # Exit if LTP drops below trailing stop loss
#                     profit = (ltp - item['ltp']) * item['lotsize']
#                     crete_update_table.updatecrypto(item['id'], 0, profit)
#                     bot_message = (
#                         f"Crypto trailing stop loss hit\n"
#                         f"Symbol: {item['script']}\n"
#                         f"Exit Profit/Loss: {profit}\n"
#                         f"LTP: {ltp}\n"
#                         f"Date: {date}"
#                     )
#                     sendAlert(bot_message)
#                     print(bot_message)
#
#                 elif ltp <= stoploss:  # Exit if stoploss is hit
#                     profit = (ltp - item['ltp']) * item['lotsize']
#                     crete_update_table.updatecrypto(item['id'], 0, profit)
#                     bot_message = (
#                         f"Crypto stoploss hit\n"
#                         f"Symbol: {item['script']}\n"
#                         f"Exit Loss: {profit}\n"
#                         f"LTP: {ltp}\n"
#                         f"Date: {date}"
#                     )
#                     sendAlert(bot_message)
#                     print(bot_message)
#
#                 else:  # Trade still active
#                     profit = (ltp - item['ltp']) * item['lotsize']
#                     print(
#                         f"Active Trade:\n"
#                         f"Current Profit: {profit}\n"
#                         f"Trailing Stop Loss: {trailing_stoploss}\n"
#                         f"Stoploss: {stoploss}\n"
#                         f"Highest LTP: {item['highest_ltp']}"
#                     )
#     else:
#         print('No order placed')


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

def sendimgdata(df,level,symbol):
    add_plots = [
    mpf.make_addplot(df['ema_9'], color='blue', label='9 EMA'),
    mpf.make_addplot(df['ema_20'], color='orange', label='20 EMA'),
    mpf.make_addplot(df['ema_50'], color='green', label='50 EMA')

]
    mpf.plot(df, type='candle', hlines=level.to_list(), addplot=add_plots,style='charles',title=symbol, savefig='static/chart3.png')
    sendImgAlert("Here is an image:", "static/chart3.png")


def calculate_quantity(investment_in_inr, close_price_usd, exchange_rate):
    quantity = investment_in_inr / (close_price_usd * exchange_rate)
    return quantity

def compare_dates_excluding_seconds(last_date_str):
    """
    Compare the current date and time with the last date (ignoring seconds).

    :param last_date_str: String representing the last date in the format '%Y-%m-%d %H:%M:%S.%f'
    :return: True if the dates match (up to the minute), otherwise False
    """
    # Parse the input string to a datetime object
    last_date = datetime.strptime(last_date_str, '%Y-%m-%d %H:%M:%S.%f')

    # Get the current date and time
    current_date = datetime.now()

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

def determine_target_method_1min(df,symbol, swing_lookback=8, atr_threshold=0.9):
    """
    Decide between Fibonacci and ATR-based target + stoploss for 1-min option premium data.
    """
    print('--------------enter define target')
    df = calculate_atr(df)
    recent = df.iloc[-swing_lookback:]
    swing_high = recent['high'].max()
    swing_low = recent['low'].min()
    entry_price = recent.iloc[-1]['close']
    atr = recent.iloc[-1]['ATR']
    swing_range = swing_high - swing_low
    atr_strength_ratio = swing_range / (atr * swing_lookback)
    print(recent,swing_lookback,entry_price)
    result = {
        'entry_price': round(entry_price, 2),
        'atr': round(atr, 2),
    }

    if atr_strength_ratio > atr_threshold:
        # Trending → Use Fibonacci
        diff = swing_high - swing_low
        fib_target = swing_high + (diff * 0.618)
        result.update({
            'symbol':symbol,
            'method': 'fibonacci',
            'target_price': round(fib_target, 2),
            'stoploss_price': round(swing_low, 2),  # Below support
            'reason': f"Trending (range/ATR={atr_strength_ratio:.2f}) — using Fibonacci"
        })
    else:
        # Choppy → Use ATR-based
        atr_target = entry_price + (atr * 1.0)
        atr_stoploss = entry_price - (atr * 1.0)
        result.update({
            'symbol':symbol,
            'method': 'atr',
            'target_price': round(atr_target, 2),
            'stoploss_price': round(atr_stoploss, 2),
            'reason': f"Choppy (range/ATR={atr_strength_ratio:.2f}) — using ATR"
        })

    return result

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


def get_trade_signal(df,symbol):
    # Indicators
    # print("---------",df)
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
    # print("%%%%%%%%%%%%%%%%check-----------",latest)
    # print(df)
    # Fibonacci Levels Calculation
    # Assuming 'df' has a 'datetime' column with datetime objects
    symbol_tokens = {
    "NIFTY": "99926000",
    "BANKNIFTY": "99926009",
    "SENSEX": "99926001"
}
    # exchange = nsechange[symbol]
    # tradingsymbol = symbol
    # symboltoken = symbol_tokens[symbol]  # Token for NIFTY 50 index

    # Fetch LTP data
    # ltp_data = obj.ltpData(exchange=exchange, tradingsymbol=tradingsymbol, symboltoken=symboltoken)
    # print(df)
    ltp_data = df.iloc[-1]
    print("$$$$$%%%%%%%%%%%%%%%___________",ltp_data)
    if True:
        # Extract LTP value
        # ltp = ltp_data['data']
        # print(f"NIFTY 50 LTP: {ltp}")
        highest_price = ltp_data['high']
        lowest_price = ltp_data['low']
        print('&&&&&$$$$$$---------check data',highest_price,lowest_price)
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

    print({
        "buy_signals": buy_signal_summary,
        "sell_signals": sell_signal_summary,
        "final_signal": signal,
        "sideways_info": breakout_levels,
        "support": round(latest['support'], 2),
        "resistance": round(latest['resistance'], 2),
        "fibonacci_levels": fib_levels,
        "current_price": round(latest['close'], 2),
        'trend_message':trend_message
    })
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


def buycall(df,extractsymbol,level,condition):
    product = getproduct(df.close.values[-1], 'C')
    itemclose = df.close.values[-1]
    ema50 = df.ema_50.values[-1]
    # qty = calculate_quantity(investment_in_inr, product['close'], exchange_rate)
    qty = 5
    less_than, greater_than = checkclosenear_price(level,itemclose)
    checkleveldiff = (greater_than - itemclose) > 300
    print('product name', product)
    logging.info(f"product : {product['symbol']},extractsymbol: {extractsymbol}")
    fetchdata = crete_update_table.fetchtcryptoorderbook()
    # print('fetch',fetchdata)
    filteristoken = [
        item for item in fetchdata
        if extractsymbol in item['script'] and int(item['lotsize']) > 0
    ]
    targetset = determine_target_method_1min(df,extractsymbol)
    print('filteristoken', filteristoken, 'len', len(filteristoken))
    logging.info(f"filteristoken value : {filteristoken}")
    lastitemdate = fetchdata[-1]['createddate']
    datematch = compare_dates_excluding_seconds(lastitemdate)
    check_candle_color = df.close.values[-1] > df.open.values[-1]
    trend = checktrending.checktrend(df)
    print(check_candle_color,'date',datematch,'trend',trend)
    if len(filteristoken) == 0 and datematch and check_candle_color and itemclose > ema50 and trend == 'Trending':
        if checkleveldiff:
            place = placeOrder.place_order(product['product_id'],qty,'buy')
            if place['success'] == True:
                crete_update_table.insertcryptoorder(product['symbol'], 'crpto', product['product_id'], qty, product['close'],
                                                     '0')
                bot_message = f"🟢order placed for crypto {condition} symbol {product['symbol']}, buy price {product['close']} quantity {qty} settarget: {targetset}"
                sendAlert(bot_message)
                sendimgdata(df, level, product['symbol'])
                logging.info(f"{bot_message}")
            else:
                sendAlert(f"{extractsymbol} : {place}")
        else:
            sendAlert(f" {extractsymbol} trend is {trend} or ce diff is not greater than 20 points differnce : {greater_than - itemclose} closest registance: {greater_than} itemclose {itemclose} settarget: {targetset}")

def sellcall(df,extractsymbol,level,condition):
    product = getproduct(df.close.values[-1], 'C')
    itemclose = df.close.values[-1]
    ema50 = df.ema_50.values[-1]
    # qty = calculate_quantity(investment_in_inr, product['close'], exchange_rate)
    qty = -5
    less_than, greater_than = checkclosenear_price(level,itemclose)
    checkleveldiff = (greater_than - itemclose) > 300
    print('product name', product)
    logging.info(f"product : {product['symbol']},extractsymbol: {extractsymbol}")
    fetchdata = crete_update_table.fetchtcryptoorderbook()
    # print('fetch',fetchdata)
    filteristoken = [
        item for item in fetchdata
        if extractsymbol in item['script'] and int(item['lotsize']) < 0
    ]
    targetset = determine_target_method_1min(df,extractsymbol)
    print('filteristoken', filteristoken, 'len', len(filteristoken))
    logging.info(f"filteristoken value : {filteristoken}")
    lastitemdate = fetchdata[-1]['createddate']
    datematch = compare_dates_excluding_seconds(lastitemdate)
    check_candle_color = df.close.values[-1] > df.open.values[-1]
    trend = checktrending.checktrend(df)
    print(check_candle_color,'date',datematch,'trend',trend)
    # and check_candle_color and itemclose > ema50
    if len(filteristoken) == 0 and datematch and trend == 'Trending':
        if checkleveldiff:
            place = placeOrder.place_order(product['product_id'],qty,'sell')
            if place['success'] == True:
                crete_update_table.insertcryptoorder(product['symbol'], 'crpto', product['product_id'], qty, product['close'],
                                                     '0')
                bot_message = f"🟢order placed for crypto {condition} symbol {product['symbol']}, sell price {product['close']} quantity {qty} settarget: {targetset}"
                sendAlert(bot_message)
                sendimgdata(df, level, product['symbol'])
                logging.info(f"{bot_message}")
            else:
                sendAlert(f"{extractsymbol} : {place}")
        else:
            sendAlert(f" {extractsymbol} trend is {trend} or ce diff is not greater than 20 points differnce : {greater_than - itemclose} closest registance: {greater_than} itemclose {itemclose} settarget: {targetset}")

def buyput(df,extractsymbol,level,condition):
    product = getproduct(df.close.values[-1], 'P')
    # qty = calculate_quantity(investment_in_inr, product['close'], exchange_rate)
    print('product name', product)
    qty = 5
    itemclose = df.close.values[-1]
    ema50 = df.ema_50.values[-1]
    fetchdata = crete_update_table.fetchtcryptoorderbook()
    less_than, greater_than = checkclosenear_price(level,itemclose)
    logging.info(f"product : {product['symbol']},extractsymbol: {extractsymbol}")

    checkleveldiff = (itemclose - less_than) > 300
    filteristoken = [
        item for item in fetchdata
        if extractsymbol in item['script'] and int(item['lotsize']) > 0
    ]
    lastitemdate = fetchdata[-1]['createddate']
    datematch = compare_dates_excluding_seconds(lastitemdate)
    logging.info(f"filteristoken value : {filteristoken}")
    check_candle_color = df.close.values[-1] < df.open.values[-1]
    trend = checktrending.checktrend(df)
    targetset = determine_target_method_1min(df,extractsymbol)

    print('tend detect',trend)
    if len(filteristoken) == 0 and datematch and check_candle_color and itemclose < ema50 and trend == 'Trending':
        if checkleveldiff:
            place = placeOrder.place_order(product['product_id'],qty,'buy')
            if place['success'] == True:
                crete_update_table.insertcryptoorder(product['symbol'], 'crpto', product['product_id'], qty, product['close'],
                                                     '0')
                bot_message = f"🟢order placed for crypto {condition} symbol {product['symbol']}, buy price {product['close']} quantity {qty} target {targetset}"
                sendAlert(bot_message)
                sendimgdata(df, level, product['symbol'])
                logging.info(f"{bot_message}")
            else:
                sendAlert(f"{extractsymbol} : {place}")
        else:
            sendAlert(f"{extractsymbol} trend is {trend} or pe : diff is not greater than 20 points diffrence : {(itemclose - less_than)} closest support: {less_than} itemclose {itemclose} target {targetset}")

def sellput(df,extractsymbol,level,condition):
    product = getproduct(df.close.values[-1], 'P')
    # qty = calculate_quantity(investment_in_inr, product['close'], exchange_rate)
    print('product name', product)
    qty = -5
    itemclose = df.close.values[-1]
    ema50 = df.ema_50.values[-1]
    fetchdata = crete_update_table.fetchtcryptoorderbook()
    less_than, greater_than = checkclosenear_price(level,itemclose)
    logging.info(f"product : {product['symbol']},extractsymbol: {extractsymbol}")

    checkleveldiff = (itemclose - less_than) > 300
    filteristoken = [
        item for item in fetchdata
        if extractsymbol in item['script'] and int(item['lotsize']) < 0
    ]
    lastitemdate = fetchdata[-1]['createddate']
    datematch = compare_dates_excluding_seconds(lastitemdate)
    logging.info(f"filteristoken value : {filteristoken}")
    check_candle_color = df.close.values[-1] < df.open.values[-1]
    trend = checktrending.checktrend(df)
    targetset = determine_target_method_1min(df,extractsymbol)

    print('tend detect',trend)
    # check_candle_color and itemclose < ema50 and
    if len(filteristoken) == 0 and datematch and trend == 'Trending':
        if checkleveldiff:
            place = placeOrder.place_order(product['product_id'],qty,'sell')
            if place['success'] == True:
                crete_update_table.insertcryptoorder(product['symbol'], 'crpto', product['product_id'], qty, product['close'],
                                                     '0')
                bot_message = f"🟢order placed for crypto {condition} symbol {product['symbol']}, sell price {product['close']} quantity {qty} target {targetset}"
                sendAlert(bot_message)
                sendimgdata(df, level, product['symbol'])
                logging.info(f"{bot_message}")
            else:
                sendAlert(f"{extractsymbol} : {place}")
        else:
            sendAlert(f"{extractsymbol} trend is {trend} or pe : diff is not greater than 20 points diffrence : {(itemclose - less_than)} closest support: {less_than} itemclose {itemclose} target {targetset}")


DATA_FILE = "auto_trade_crypto.json"  # File to store form data

def load_data():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)  # Read existing data
    except (FileNotFoundError, json.JSONDecodeError):
        return {}  # Return empty if file not found or corrupted

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

def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

def stetergytosendalert(symbol, interwal, data, level, closehigh, closelow):
    df = data
    extractsymbol = ''.join(symbol[i] for i in [0,1, 2])
    print(extractsymbol,'extractsymbol')
    qty = 5
    # sup = df['Trend_Status'].values[-1]
    sup = 1
    # print('sup',sup)
    # print('df',df)
    # print('level',level)
    # logging.info(f"levels for intervale: {interwal}, level: {level}")

    # print('close',df.close)
    # print('check data',getproduct(df.close.values[-1],'C'),getproduct(df.close.values[-1],'P'))
    try:
        if len(df) > 0:
            auto_trade = load_data()
            data = storecandlestickdata.createchart(symbol,interwal,df,level)
            print('check all data')
            trend_duration = 2
            checkdata = process_advanced_signals(df, trend_duration)
            signal_data = get_trade_signal(checkdata,symbol)
            check_trend = signal_data["final_signal"]
            storetrend(symbol,signal_data["final_signal"],signal_data["buy_signals"],signal_data["sell_signals"],signal_data['trend_message'],signal_data)
            check_trend_Buy_condition = (check_trend == 'buy')
            check_trend_sell_condition = (check_trend == 'sell')
            latest_data = checkdata.iloc[-1]
            # print('gfh',checktrending.checktrend(df))
            # print(latest_data)
            if latest_data['buy_signal'] and check_trend_Buy_condition:
                bot_message = f"BUY Signal Detected: {symbol} at {latest_data['close']}"
                # sendAlert(bot_message)
                # print(f"BUY Signal Detected: {symbol} at {latest_data['close']}")
                if auto_trade['buy_or_sell'] == 'BUY':
                    buycall(df,extractsymbol,level,'buy_signal')
                elif auto_trade['buy_or_sell'] == 'SELL':
                    sellput(df,extractsymbol,level,'sell_signal')

            elif latest_data['sell_signal'] and check_trend_sell_condition:
                bot_message = f"sell Signal Detected: {symbol} at {latest_data['close']}"
                # sendAlert(bot_message)
                # print(f"SELL Signal Detected: {symbol} at {latest_data['close']}")
                if auto_trade['buy_or_sell'] == 'BUY':
                    buyput(df,extractsymbol,level,'buy_signal')
                elif auto_trade['buy_or_sell'] == 'SELL':
                    sellcall(df,extractsymbol,level,'sell_signal')

            elif latest_data['support_on_9ema'] and check_trend_Buy_condition:
                # bot_message = f"\n🟢 Support Detected on 9 EMA: {symbol} at {latest_data['close']}"
                # sendAlert(bot_message)
                print(f"\n🟢 Support Detected on 9 EMA: {symbol} at {latest_data['close']}")
                print('support_on_9ema')
                logging.info(f"\n🟢 Support Detected on 9 EMA: {symbol} at {latest_data['close']}")
                if auto_trade['buy_or_sell'] == 'BUY':
                     buycall(df,extractsymbol,level,'support_on_9ema')
                elif auto_trade['buy_or_sell'] == 'SELL':
                    sellput(df,extractsymbol,level,'support_on_9ema')

            elif latest_data['support_on_20ema'] and check_trend_Buy_condition:
                # bot_message = f"\n🟢 Support Detected on 20 EMA: {symbol} at {latest_data['close']}"
                # sendAlert(bot_message)
                print('support_on_20ema')
                logging.info(f"\n🟢 Support Detected on 20 EMA: {symbol} at {latest_data['close']}")
                print(f"\n🟢 Support Detected on 20 EMA: {symbol} at {latest_data['close']}")
                if auto_trade['buy_or_sell'] == 'BUY':
                     buycall(df,extractsymbol,level,'Support Detected on 20 EMA')
                elif auto_trade['buy_or_sell'] == 'SELL':
                    sellput(df,extractsymbol,level,'Support Detected on 20 EMA')

            elif latest_data['resistance_on_9ema'] and check_trend_sell_condition:
                print('resistance_on_9ema')
                logging.info(f"\n🟢 Support Detected on resistance_on_9ema: {symbol} at {latest_data['close']}")
                print(f"\n🟢 Support Detected on resistance_on_9ema: {symbol} at {latest_data['close']}")
                if auto_trade['buy_or_sell'] == 'BUY':
                    buyput(df,extractsymbol,level,'resistance_on_9ema')
                elif auto_trade['buy_or_sell'] == 'SELL':
                    sellcall(df,extractsymbol,level,'resistance_on_9ema')

            elif latest_data['resistance_on_20ema'] and check_trend_sell_condition:
                print('resistance_on_20ema')
                logging.info(f"\n🟢 Support Detected on resistance_on_20ema: {symbol} at {latest_data['close']}")
                if auto_trade['buy_or_sell'] == 'BUY':
                    buyput(df, extractsymbol, level,'resistance_on_20ema')
                elif auto_trade['buy_or_sell'] == 'SELL':
                    sellcall(df,extractsymbol,level,'resistance_on_20ema')

            else:
                print('no ema levels')
            for a in level:
                if a > df.low.values[-2] and a < df.close.values[-1] and sup == '1':
                        print('enter1')
                        logging.info(f"a > df.low.values[-2] and a < df.close.values[-1] and sup == '1'")
                        product = getproduct(df.close.values[-1],'C')
                        logging.info(f"product : {product['symbol']},extractsymbol: {extractsymbol}")
                        fetchdata = crete_update_table.fetchtokennbook()
                        filteristoken = [
                            item for item in fetchdata
                            if extractsymbol in item['script'] and int(item['lotsize']) > 0
                        ]
                        print('filteristoken',filteristoken,'len',len(filteristoken))
                        logging.info(f"filteristoken value : {filteristoken}")
                        if len(filteristoken) == 0:
                            crete_update_table.insertcryptoorder(product['symbol'],'crpto',product['product_id'],qty,product['close'],'0')
                            bot_message = f"order placed for crypto interval {interwal} symbol {product['sybol']}, buy price {product['close']} quantity {qty}"
                            sendAlert(bot_message)
                            logging.info(f"{bot_message}")

                elif a < df.high.values[-2] and a > df.close.values[-1] and sup == '1':
                    print('enter2')
                    logging.info(f"a < df.high.values[-2] and a > df.close.values[-1] and sup == '1'")
                    product = getproduct(df.close.values[-1],'P')
                    logging.info(f"product : {product['symbol']},extractsymbol: {extractsymbol}")
                    fetchdata = crete_update_table.fetchtokennbook()
                    filteristoken = [
                        item for item in fetchdata
                        if extractsymbol in item['script'] and int(item['lotsize']) > 0
                    ]
                    print(filteristoken)
                    logging.info(f"filteristoken value : {filteristoken}")
                    if len(filteristoken) == 0:
                        crete_update_table.insertcryptoorder(product['symbol'],'crpto',product['product_id'],qty,product['close'],'0')
                        bot_message = f"order placed for crypto interval {interwal} symbol {product['sybol']}, buy price {product['close']} quantity {qty}"
                        sendAlert(bot_message)
                        logging.info(f"{bot_message}")

            print(f'Their is no support and resistance for interval {interwal}')
        else:
            print('no data')
    except Exception as e:
            print("error: {}".format(e))

# def aggregate_data(df, time_frame):
#     # Convert list of dictionaries to DataFrame
#     df = pd.DataFrame(df)
#
#     # Convert 'time' column to datetime
#     df['time'] = pd.to_datetime(df['time'], unit='s')
#
#     # Set 'time' column as index
#     df.set_index('time', inplace=True)
#
#     # Resample and aggregate
#     resampled_df = df.resample(time_frame).agg({
#         'open': 'first',
#         'high': 'max',
#         'low': 'min',
#         'close': 'last'
#     })
#
#     return resampled_df
def aggregate_data(df, time_frame):
    resampled_df = df.resample(time_frame).agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last'
    })
    return resampled_df
def stetergy():
    fetch = load_data()
    limitorder = fetch['stop_loss']
    linitedprofit = 2000
    placeorder = fetch['auto_place_order']
    try:
      orderdata = crete_update_table.todayorderdata()

      print(orderdata)
      # or orderdata['totalProfit'] <= linitedprofit:

      if placeorder and int(orderdata['stoplossOrder']) < int(limitorder):
          for item in crpto:
            data1m = get_historical_data(item,Interval.in_1_minute)
            # print(checktrending.checktrend(data1m))
            for interval,key in timeframe_map.items():
              data = get_historical_data(item,key)
              # level, data = fetch_and_process_data2(item, Interval.in_5_minute, '100', 20, 20)
              result, level = fetch_and_process_data(data,20, 20)
              df_5min = aggregate_data(data1m, '5T').tail(10)
              closehigh = df_5min.high.values[-2]
              closelow = df_5min.low.values[-2]
              stetergytosendalert(item, interval, data1m, level, closehigh, closelow)
      else:
          print(f"total order: {orderdata['totalOrder']} stoploss order:  {orderdata['stoplossOrder']} profit {orderdata['totalProfit']}")
          # sendAlert(f"total order: {orderdata['totalOrder']} stoploss order:  {orderdata['stoplossOrder']} profit {orderdata['totalProfit']}")
    except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(2)
            stetergy()

# exitstetergy()
# exitstetergywithema()
stetergy()
exitstetergy()
exitstetergywithema()
schedule.every(30).seconds.do(stetergy)
# exitstetergy()
schedule.every(5).seconds.do(exitstetergy)
schedule.every(10).seconds.do(exitstetergywithema)


# schedule.every(5).seconds.do(stetergy)




while True:
    # print("start tym , CURRENT TIME:{}".format(datetime.datetime.now()))
    try:
        schedule.run_pending()
        time.sleep(2)
    except Exception as e:
        raise e
