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
        df["ema14"] = ta.ema(df["close"], length=14)

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
    # print('symbol',symbol)
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

def exitstetergy():
    date = datetime.now()
    fetch = crete_update_table.fetchtcryptoorderbook()
    print(fetch)
    if len(fetch) > 0:
        for item in fetch:
            if item['lotsize'] > 0:
                symbol = item['script']
                response = requests.get("https://cdn.india.deltaex.org/v2/tickers" + f"/{symbol}")
                ticker_info = response.json()
                print('ticker_info',ticker_info,'ticker_info')
                ltp = ticker_info['result']['close']
                # target = item['ltp'] * 1.10
                # stoploss = item['ltp'] * 0.97
                target =item['ltp'] + 10
                stoploss = item['ltp'] - 5
                if ltp > target:
                    profit = (ltp - item['ltp']) * item['lotsize']
                    crete_update_table.updatecrypto(item['id'],0,profit)
                    bot_message = f"crypto target hit symbol: {item['script']} - exit: {profit} - ltp: {item['ltp']} - date: {date}"
                    sendAlert(bot_message)
                elif ltp < stoploss:
                    profit = (ltp - item['ltp']) * item['lotsize']
                    crete_update_table.updatecrypto(item['id'],0,profit)
                    bot_message = f"crypto target hit symbol: {item['script']} - exit: {profit} - ltp: {item['ltp']} - date: {date}"
                    sendAlert(bot_message)
                else:
                    profit = (ltp - item['ltp']) * item['lotsize']
                    print(f'you are in trade and the profit is {profit} target is {target} stoploss is {stoploss}')
    else:
        print('No order place')


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
    mpf.make_addplot(df['ema_20'], color='orange', label='20 EMA')
]
    mpf.plot(df, type='candle', hlines=level.to_list(), addplot=add_plots,style='charles',title=symbol, savefig='static/chart3.png')
    sendImgAlert("Here is an image:", "static/chart3.png")


def calculate_quantity(investment_in_inr, close_price_usd, exchange_rate):
    quantity = investment_in_inr / (close_price_usd * exchange_rate)
    return quantity

def buycall(df,extractsymbol,level):
    product = getproduct(df.close.values[-1], 'C')
    qty = calculate_quantity(investment_in_inr, product['close'], exchange_rate)
    print('product', product)
    logging.info(f"product : {product['symbol']},extractsymbol: {extractsymbol}")
    fetchdata = crete_update_table.fetchtcryptoorderbook()
    # print('fetch',fetchdata)
    filteristoken = [
        item for item in fetchdata
        if extractsymbol in item['script'] and int(item['lotsize']) > 0
    ]
    print('filteristoken', filteristoken, 'len', len(filteristoken))
    logging.info(f"filteristoken value : {filteristoken}")
    if len(filteristoken) == 0:
        crete_update_table.insertcryptoorder(product['symbol'], 'crpto', product['product_id'], qty, product['close'],
                                             '0')
        bot_message = f"🟢order placed for crypto support_on_9ema symbol {product['symbol']}, buy price {product['close']} quantity {qty}"
        sendAlert(bot_message)
        sendimgdata(df, level, product['symbol'])
        logging.info(f"{bot_message}")



def buyput(df,extractsymbol,level):
    product = getproduct(df.close.values[-1], 'P')
    qty = calculate_quantity(investment_in_inr, product['close'], exchange_rate)
    logging.info(f"product : {product['symbol']},extractsymbol: {extractsymbol}")
    fetchdata = crete_update_table.fetchtcryptoorderbook()
    filteristoken = [
        item for item in fetchdata
        if extractsymbol in item['script'] and int(item['lotsize']) > 0
    ]
    logging.info(f"filteristoken value : {filteristoken}")
    if len(filteristoken) == 0:
        crete_update_table.insertcryptoorder(product['symbol'], 'crpto', product['product_id'], qty, product['close'],
                                             '0')
        bot_message = f"🟢order placed for crypto resistance_on_9ema symbol {product['symbol']}, buy price {product['close']} quantity {qty}"
        sendAlert(bot_message)
        sendimgdata(df, level, product['symbol'])
        logging.info(f"{bot_message}")

def stetergytosendalert(symbol, interwal, data, level, closehigh, closelow):
    df = data
    extractsymbol = ''.join(symbol[i] for i in [0,1, 2])
    print(extractsymbol,'extractsymbol')
    qty = 10
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
            # print(latest_data)
            if latest_data['buy_signal']:
                bot_message = f"BUY Signal Detected: {symbol} at {latest_data['close']}"
                sendAlert(bot_message)
                print(f"BUY Signal Detected: {symbol} at {latest_data['close']}")
            elif latest_data['sell_signal']:
                bot_message = f"sell Signal Detected: {symbol} at {latest_data['close']}"
                sendAlert(bot_message)
                print(f"SELL Signal Detected: {symbol} at {latest_data['close']}")
            elif latest_data['support_on_9ema']:
                # bot_message = f"\n🟢 Support Detected on 9 EMA: {symbol} at {latest_data['close']}"
                # sendAlert(bot_message)
                print(f"\n🟢 Support Detected on 9 EMA: {symbol} at {latest_data['close']}")
                print('support_on_9ema')
                logging.info(f"\n🟢 Support Detected on 9 EMA: {symbol} at {latest_data['close']}")
                buycall(df,extractsymbol,level)
            elif latest_data['support_on_20ema']:
                # bot_message = f"\n🟢 Support Detected on 20 EMA: {symbol} at {latest_data['close']}"
                # sendAlert(bot_message)
                print('support_on_20ema')
                logging.info(f"\n🟢 Support Detected on 20 EMA: {symbol} at {latest_data['close']}")
                print(f"\n🟢 Support Detected on 20 EMA: {symbol} at {latest_data['close']}")
                buycall(df,extractsymbol,level)

            elif latest_data['resistance_on_9ema']:
                print('resistance_on_9ema')
                logging.info(f"\n🟢 Support Detected on resistance_on_9ema: {symbol} at {latest_data['close']}")
                print(f"\n🟢 Support Detected on resistance_on_9ema: {symbol} at {latest_data['close']}")
                buyput(df,extractsymbol,level)
            elif latest_data['resistance_on_20ema']:
                print('resistance_on_20ema')
                logging.info(f"\n🟢 Support Detected on resistance_on_20ema: {symbol} at {latest_data['close']}")
                buyput(df, extractsymbol, level)

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
    try:
      for item in crpto:
        data1m = get_historical_data(item,Interval.in_1_minute)
        for interval,key in timeframe_map.items():
          data = get_historical_data(item,key)
          # level, data = fetch_and_process_data2(item, Interval.in_5_minute, '100', 20, 20)
          result, level = fetch_and_process_data(data,20, 20)
          df_5min = aggregate_data(data1m, '5T').tail(10)
          closehigh = df_5min.high.values[-2]
          closelow = df_5min.low.values[-2]
          stetergytosendalert(item, interval, data1m, level, closehigh, closelow)
    except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(2)
            stetergy()
#
stetergy()
schedule.every(30).seconds.do(stetergy)
# exitstetergy()
schedule.every(5).seconds.do(exitstetergy)



while True:
    # print("start tym , CURRENT TIME:{}".format(datetime.datetime.now()))
    try:
        schedule.run_pending()
        time.sleep(2)
    except Exception as e:
        raise e
