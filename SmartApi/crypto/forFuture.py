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
    df['buy_signal'] = df['close'] > df['ema_9']

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
    url = "https://cdn.india.deltaex.org/v2/tickers"
    try:
        response = requests.get(url)
        response.raise_for_status()
        tickers = response.json().get("result", [])

        btcusd_futures = {
            item['symbol']: item
            for item in tickers
            if item['symbol'].startswith("BTCUSD") and ("FUT" in item['symbol'] or "PERP" in item['symbol'])
        }
        print(btcusd_futures)
        return btcusd_futures

    except requests.RequestException as e:
        print(f"Error fetching BTCUSD futures data: {e}")
        return {}

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

def exitstetergynext_ema_sell(df, item):
    print('Enter Exit EMA - SELL')
    date = datetime.now()
    itemclose = df.close.values[-1]
    symbol = item['script']
    sell_price = item['ltp']  # Entry price for sell
    lotsize = item['lotsize']

    if lotsize >= 0:
        print("Not a short position. Skipping...")
        return

    # Get LTP
    url = f"https://cdn.india.deltaex.org/v2/tickers/{symbol}"
    response = requests.get(url)
    ticker_info = response.json()
    latest_data = df.iloc[-1]

    ltp = float(ticker_info['result']['mark_price'])

    # EMA logic
    ema = df['ema_9'].values[-1]
    profit_or_loss = (sell_price - ltp) * abs(lotsize)
    print("Profit (SELL side):", profit_or_loss)

    if latest_data['buy_signal']:  # Exit on BUY signal (for short position)
        place = placeOrder.place_order(item['id'], abs(lotsize), 'buy')  # Buy to close short
        if place['success'] == True:
            profit_order = (
                f"Exit by EMA (SELL side)\n"
                f"Time: {date} | Symbol: {symbol} | Exit Price: {ltp} | Sell Price: {sell_price} | "
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
            elif item['lotsize'] < 0:
                fetchdata = get_delta_histo_data(item['script'])
                exitstetergynext_ema_sell(fetchdata,item)




def exitstetergy():
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    fetch = crete_update_table.fetchtcryptoorderbook()
    print('Enter in Exit')
    if not fetch:
        print('No order placed')
        return

    for item in fetch:
        if item['lotsize'] > 0:
            print(item['script'])
            symbol = item['script']
            url = f"https://cdn.india.deltaex.org/v2/tickers/{symbol}"
            response = requests.get(url)
            ticker_info = response.json()

            if 'result' not in ticker_info or 'mark_price' not in ticker_info['result']:
                print(f"Error: Invalid API response for {symbol}")
                continue

            ltp = float(ticker_info['result']['mark_price'])
            buy_price = item['ltp']  # Entry price


            # Initialize tracking values if not present
            if symbol not in crypto_stats:
                if item['lotsize'] > 0:
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

            print(f"LTP: {ltp} | buyprice: {buy_price} | Target: {target} | Stoploss: {stoploss} | Max LTP: {max_ltp} | Profit: {profit} | Max Profit: {crypto_stats[symbol]['max_profit']}")

            if ltp >= target:
                # Increase target by 10 points
                crypto_stats[symbol]['target'] = ltp + 10
                # Adjust trailing stop-loss to 5 points below LTP
                crypto_stats[symbol]['stoploss'] = ltp - 5

                print(f"Target hit! New Target: {crypto_stats[symbol]['target']} | New Stoploss: {crypto_stats[symbol]['stoploss']}")
            # or (ltp <= max_ltp - 5 and max_ltp - buy_price >= 10)
            elif ltp < stoploss or (ltp <= max_ltp - 15 and max_ltp - buy_price >= 100):
                # Exit trade if:
                # - LTP is 5 points below max LTP AND
                # - max LTP is at least 10 points above the buy price
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
        elif item['lotsize'] < 0:
            print(item['script'])
            symbol = item['script']
            url = f"https://cdn.india.deltaex.org/v2/tickers/{symbol}"
            response = requests.get(url)
            ticker_info = response.json()

            if 'result' not in ticker_info or 'mark_price' not in ticker_info['result']:
                print(f"Error: Invalid API response for {symbol}")
                continue
            ltp = float(ticker_info['result']['mark_price'])
            sell_price = item['ltp']  # Entry price for SELL
            # Initialize tracking values if not present
            if symbol not in crypto_stats:
                if item['lotsize'] < 0:
                    crypto_stats[symbol] = {
                        'max_profit': float('-inf'),
                        'min_ltp': float('inf'),
                        'target': sell_price - 300,   # Target is BELOW sell price
                        'stoploss': sell_price + 150  # Stoploss is ABOVE sell price
                    }

            # Update min LTP and profit
            crypto_stats[symbol]['min_ltp'] = min(crypto_stats[symbol]['min_ltp'], ltp)
            profit = (sell_price - ltp) * abs(item['lotsize'])  # Inverted for sell
            crypto_stats[symbol]['max_profit'] = max(crypto_stats[symbol]['max_profit'], profit)

            target = crypto_stats[symbol]['target']
            stoploss = crypto_stats[symbol]['stoploss']
            min_ltp = crypto_stats[symbol]['min_ltp']

            print(f"LTP: {ltp} | Sell Price: {sell_price} | Target: {target} | Stoploss: {stoploss} | Min LTP: {min_ltp} | Profit: {profit} | Max Profit: {crypto_stats[symbol]['max_profit']}")

            if ltp <= target:
                # Price fell enough -> move target further down
                crypto_stats[symbol]['target'] = ltp - 10
                crypto_stats[symbol]['stoploss'] = ltp + 5

                print(f"Target hit! New Target: {crypto_stats[symbol]['target']} | New Stoploss: {crypto_stats[symbol]['stoploss']}")
            elif ltp > stoploss or (ltp >= min_ltp + 15 and sell_price - min_ltp >= 100):
                # Exit if price bounces up OR profit was good but now pulling back
                place = placeOrder.place_order(item['id'], abs(item['lotsize']), 'buy')  # Buy to close short
                if place['success'] == True:
                    crete_update_table.updatecrypto(item['id'], 0, profit)
                    bot_message = (
                        f"Crypto SELL exit triggered!\n"
                        f"Symbol: {symbol}\n"
                        f"Exit Profit: {profit}\n"
                        f"LTP: {ltp}\n"
                        f"Target: {target}\n"
                        f"Stoploss: {stoploss}\n"
                        f"Sell Price: {sell_price}\n"
                        f"Points: {sell_price - ltp}\n"
                        f"Min LTP: {min_ltp}\n"
                        f"Max Profit: {crypto_stats[symbol]['max_profit']}\n"
                        f"Date: {date}"
                    )

                    sendAlert(bot_message)
                    if (ltp >= min_ltp + 15 and sell_price - min_ltp >= 100):
                        sendAlert(f"Exit triggered: LTP bounced after falling - exit-ltp:{ltp} sellprice:{sell_price} minltp:{min_ltp} diff.:{sell_price - min_ltp}")
                    print("Exit triggered: LTP bounced or Stoploss hit")
                    del crypto_stats[symbol]
                else:
                    sendAlert(f"{place}")
            else:
                print(f"In trade: Profit: {profit} | LTP: {ltp} | Target: {target} | Stoploss: {stoploss}")


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


def buycall(df,extractsymbol,level,condition):
    # product = getproduct(df.close.values[-1], 'C')
    # product = getproduct(df.close.values[-1], 'C')
    product = {
        'symbol':extractsymbol,
        'product_id':'12',
        'close':df.close.values[-1]
    }
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
                bot_message = f"🟢order placed for crypto {condition} symbol {product['symbol']}, buy price {product['close']} quantity {qty}"
                sendAlert(bot_message)
                sendimgdata(df, level, product['symbol'])
                logging.info(f"{bot_message}")
            else:
                sendAlert(f"{extractsymbol} : {place}")
        else:
            sendAlert(f" {extractsymbol} trend is {trend} or ce diff is not greater than 20 points differnce : {greater_than - itemclose} closest registance: {greater_than} itemclose {itemclose}")




def buyput(df,extractsymbol,level,condition):
    # product = getproduct(df.close.values[-1], 'P')
    # product = getproduct(df.close.values[-1], 'C')
    product = {
        'symbol':extractsymbol,
        'product_id':'12',
        'close':df.close.values[-1]
    }
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
    print('tend detect',trend)
    if len(filteristoken) == 0 and datematch and check_candle_color and itemclose < ema50 and trend == 'Trending':
        if checkleveldiff:
            place = placeOrder.place_order(product['product_id'],qty,'buy')
            sellqty = -abs(qty)
            if place['success'] == True:
                crete_update_table.insertcryptoorder(product['symbol'], 'crpto', product['product_id'], sellqty, product['close'],
                                                     '0')
                bot_message = f"🟢order placed for crypto {condition} symbol {product['symbol']}, sell price {product['close']} quantity {qty}"
                sendAlert(bot_message)
                sendimgdata(df, level, product['symbol'])
                logging.info(f"{bot_message}")
            else:
                sendAlert(f"{extractsymbol} : {place}")
        else:
            sendAlert(f"{extractsymbol} trend is {trend} or pe : diff is not greater than 20 points diffrence : {(itemclose - less_than)} closest support: {less_than} itemclose {itemclose}")


def stetergytosendalert(symbol, interwal, data, level, closehigh, closelow):
    df = data
    # extractsymbol = ''.join(symbol[i] for i in [0,1, 2])
    extractsymbol = symbol
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
            data = storecandlestickdata.createchart(symbol,interwal,df,level)
            print('check all data')
            trend_duration = 2
            checkdata = process_advanced_signals(df, trend_duration)
            latest_data = checkdata.iloc[-1]
            # print('gfh',checktrending.checktrend(df))
            # print(latest_data)
            if latest_data['buy_signal']:
                bot_message = f"BUY Signal Detected: {symbol} at {latest_data['close']}"
                # sendAlert(bot_message)
                # print(f"BUY Signal Detected: {symbol} at {latest_data['close']}")
                buycall(df,extractsymbol,level,'buy_signal')

            elif latest_data['sell_signal']:
                bot_message = f"sell Signal Detected: {symbol} at {latest_data['close']}"
                # sendAlert(bot_message)
                # print(f"SELL Signal Detected: {symbol} at {latest_data['close']}")
                buyput(df,extractsymbol,level,'buy_signal')
            elif latest_data['support_on_9ema']:
                # bot_message = f"\n🟢 Support Detected on 9 EMA: {symbol} at {latest_data['close']}"
                # sendAlert(bot_message)
                print(f"\n🟢 Support Detected on 9 EMA: {symbol} at {latest_data['close']}")
                print('support_on_9ema')
                logging.info(f"\n🟢 Support Detected on 9 EMA: {symbol} at {latest_data['close']}")
                buycall(df,extractsymbol,level,'support_on_9ema')
            elif latest_data['support_on_20ema']:
                # bot_message = f"\n🟢 Support Detected on 20 EMA: {symbol} at {latest_data['close']}"
                # sendAlert(bot_message)
                print('support_on_20ema')
                logging.info(f"\n🟢 Support Detected on 20 EMA: {symbol} at {latest_data['close']}")
                print(f"\n🟢 Support Detected on 20 EMA: {symbol} at {latest_data['close']}")
                buycall(df,extractsymbol,level,'support_on_20ema')

            elif latest_data['resistance_on_9ema']:
                print('resistance_on_9ema')
                logging.info(f"\n🟢 Support Detected on resistance_on_9ema: {symbol} at {latest_data['close']}")
                print(f"\n🟢 Support Detected on resistance_on_9ema: {symbol} at {latest_data['close']}")
                buyput(df,extractsymbol,level,'resistance_on_9ema')
            elif latest_data['resistance_on_20ema']:
                print('resistance_on_20ema')
                logging.info(f"\n🟢 Support Detected on resistance_on_20ema: {symbol} at {latest_data['close']}")
                buyput(df, extractsymbol, level,'resistance_on_20ema')

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
    limitorder = 10
    linitedprofit = 2000
    try:
      orderdata = crete_update_table.todayorderdata()

      print(orderdata)
      # or orderdata['totalProfit'] <= linitedprofit:

      if orderdata['stoplossOrder'] < limitorder:
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
# stetergy()
exitstetergy()
# exitstetergywithema()
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
