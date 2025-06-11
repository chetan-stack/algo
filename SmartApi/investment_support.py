from SmartApi import SmartConnect #or from SmartApi.smartConnect import SmartConnect
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
import math
import requests
from tvDatafeed import TvDatafeed, Interval
import document


current_date_time = datetime.datetime.now()
form_date = current_date_time - timedelta(days = 365)
traded_list_exit = []
print("current tym",current_date_time)
placeOREDR = True

tradtestocks = {
    "ACC-EQ": "22",
    "AMBUJACEM-EQ": "1270",
    "ADANIPORTS-EQ": "15083",
    "ADANIENT-EQ": "25",
    "AWL-EQ" : "8110",
    'RALLIS-EQ' : "2816",
    'CESC':'628'
}
script_list = {"MARUTI-EQ": "10999", "LALPATHLAB-EQ": "11654", "IDFCFIRSTB-EQ": "11184", "CONCOR-EQ": "4749",
          "PEL-EQ": "2412", "MUTHOOTFIN-EQ": "23650", "ESCORTS-EQ": "958", "PIDILITIND-EQ": "2664",
          "JSWSTEEL-EQ": "11723", "ACC-EQ": "22", "SAIL-EQ": "2963", "ICICIPRULI-EQ": "18652", "GRASIM-EQ": "1232",
          "ASTRAL-EQ": "14418", "BHARATFORG-EQ": "422", "ATUL-EQ": "263", "IPCALAB-EQ": "1633", "BEL-EQ": "383",
          "PNB-EQ": "10666", "HDFCLIFE-EQ": "467", "NATIONALUM-EQ": "6364", "DELTACORP-EQ": "15044", "UPL-EQ": "11287",
          "APOLLOHOSP-EQ": "157", "CIPLA-EQ": "694", "WHIRLPOOL-EQ": "18011", "DALBHARAT-EQ": "8075", "INFY-EQ": "1594",
          "FEDERALBNK-EQ": "1023", "ALKEM-EQ": "11703", "AMBUJACEM-EQ": "1270", "TITAN-EQ": "3506",
          "OBEROIRLTY-EQ": "20242", "CUMMINSIND-EQ": "1901", "NMDC-EQ": "15332", "SUNPHARMA-EQ": "3351",
          "ADANIENT-EQ": "25", "LTTS-EQ": "18564", "PIIND-EQ": "24184", "CHOLAFIN-EQ": "685", "BHEL-EQ": "438",
          "MFSL-EQ": "2142", "M&MFIN-EQ": "13285", "LUPIN-EQ": "10440", "GUJGASLTD-EQ": "10599", "SUNTV-EQ": "13404",
          "ICICIGI-EQ": "21770", "STAR-EQ": "7374", "PVR-EQ": "13147", "GRANULES-EQ": "11872", "MCX-EQ": "31181",
          "INDHOTEL-EQ": "1512", "SBICARD-EQ": "17971", "PFIZER-EQ": "2643", "INDUSTOWER-EQ": "29135",
          "VEDL-EQ": "3063", "BALKRISIND-EQ": "335", "SIEMENS-EQ": "3150", "HAVELLS-EQ": "9819", "DRREDDY-EQ": "881",
          "BERGEPAINT-EQ": "404", "IOC-EQ": "1624", "LT-EQ": "11483", "BANKBARODA-EQ": "4668", "DABUR-EQ": "772",
          "LAURUSLABS-EQ": "19234", "FSL-EQ": "14304", "TORNTPOWER-EQ": "13786", "GMRINFRA-EQ": "13528",
          "MARICO-EQ": "4067", "INDIACEM-EQ": "1515", "EICHERMOT-EQ": "910", "BANDHANBNK-EQ": "2263",
          "GODREJPROP-EQ": "17875", "BHARTIARTL-EQ": "10604", "BPCL-EQ": "526", "NAUKRI-EQ": "13751",
          "HINDALCO-EQ": "1363", "ITC-EQ": "1660", "POLYCAB-EQ": "9590", "CADILAHC-EQ": "7929", "SBILIFE-EQ": "21808",
          "DIXON-EQ": "21690", "HEROMOTOCO-EQ": "1348", "TATAPOWER-EQ": "3426", "ICICIBANK-EQ": "4963",
          "SBIN-EQ": "3045", "HINDPETRO-EQ": "1406", "POWERGRID-EQ": "14977", "ABFRL-EQ": "30108",
          "LICHSGFIN-EQ": "1997", "TRENT-EQ": "1964", "TVSMOTOR-EQ": "8479", "DIVISLAB-EQ": "10940",
          "GODREJCP-EQ": "10099", "GAIL-EQ": "4717", "MINDTREE-EQ": "14356", "BAJAJFINSV-EQ": "16675",
          "VOLTAS-EQ": "3718", "APLLTD-EQ": "25328", "DEEPAKNTR-EQ": "19943", "TATACONSUM-EQ": "3432",
          "HINDUNILVR-EQ": "1394", "ULTRACEMCO-EQ": "11532", "ASIANPAINT-EQ": "236", "CANBK-EQ": "10794",
          "EXIDEIND-EQ": "676", "IEX-EQ": "220", "JUBLFOOD-EQ": "18096", "CHAMBLFERT-EQ": "637", "HDFC-EQ": "1330",
          "WIPRO-EQ": "3787", "L&TFH-EQ": "24948", "MOTHERSUMI-EQ": "4204", "INDUSINDBK-EQ": "5258",
          "COLPAL-EQ": "15141", "CANFINHOME-EQ": "583", "HDFCAMC-EQ": "4244", "NTPC-EQ": "11630", "HAL-EQ": "2303",
          "UBL-EQ": "16713", "SRF-EQ": "3273", "BRITANNIA-EQ": "547", "NESTLEIND-EQ": "17963", "TATAMOTORS-EQ": "3456",
          "BAJFINANCE-EQ": "317", "OFSS-EQ": "10738", "JKCEMENT-EQ": "13270", "TORNTPHARM-EQ": "3518",
          "INDIGO-EQ": "11195", "PFC-EQ": "14299", "PAGEIND-EQ": "14413", "CUB-EQ": "5701", "MANAPPURAM-EQ": "19061",
          "LTI-EQ": "17818", "AUBANK-EQ": "21238", "MRF-EQ": "2277", "COFORGE-EQ": "11543", "METROPOLIS-EQ": "9581",
          "TATACHEM-EQ": "3405", "BOSCHLTD-EQ": "2181", "IBULHSGFIN-EQ": "30125", "RAMCOCEM-EQ": "2043",
          "ZEEL-EQ": "3812", "SYNGENE-EQ": "10243", "RECLTD-EQ": "15355", "TATASTEEL-EQ": "3499",
          "COROMANDEL-EQ": "739", "CROMPTON-EQ": "17094", "AUROPHARMA-EQ": "275", "AXISBANK-EQ": "5900",
          "RBLBANK-EQ": "18391", "PETRONET-EQ": "11351", "JINDALSTEL-EQ": "6733", "GLENMARK-EQ": "7406",
          "KOTAKBANK-EQ": "1922", "GSPL-EQ": "13197", "ADANIPORTS-EQ": "15083", "COALINDIA-EQ": "20374",
          "AMARAJABAT-EQ": "100", "TCS-EQ": "11536", "ONGC-EQ": "2475", "APOLLOTYRE-EQ": "163", "BIOCON-EQ": "11373",
          "PERSISTENT-EQ": "18365", "DLF-EQ": "14732", "SRTRANSFIN-EQ": "4306", "MPHASIS-EQ": "4503",
          "NAVINFLUOR-EQ": "14672", "INDIAMART-EQ": "10726", "MGL-EQ": "17534", "IRCTC-EQ": "13611", "IGL-EQ": "11262",
          "BSOFT-EQ": "6994", "BATAINDIA-EQ": "371", "HCLTECH-EQ": "7229", "SHREECEM-EQ": "3103", "RELIANCE-EQ": "2885",
          "HDFCBANK-EQ": "1333", "TECHM-EQ": "13538", "ASHOKLEY-EQ": "212"};
buy_traded_stock = []
sell_traded_stock = []

exchange = "NSE"
per_trade_fund = 10000
ma_short = 13
ma_long = 22
runcount = 0
# Function to check if a stock meets the specified conditions
def meets_strategy(stock_data):
    # print('checkstetergy',stock_data.values['close'][-1],stock_data['SMA_150'])
    # Check conditions
    condition_1 = stock_data['close'].values[-1] > stock_data['SMA_150'].values[-1]
    condition_2 = stock_data.values['SMA_150'][-1] > stock_data.values['SMA_200'][-1]
   # condition_3 = stock_data['SMA_200'].diff(1).rolling(window=20).sum().iloc[-1] > 0
    condition_4 = stock_data['SMA_50'].values[-1] > stock_data['SMA_150'].values[-1] and stock_data['SMA_50'].values[-1] > stock_data['SMA_200'].values[-1]
    condition_5 = stock_data['close'].values[-1] > stock_data['SMA_50'].values[-1]
    condition_6 = stock_data['close'].values[-1] >= 1.3 * stock_data['52_week_low'].values[-1]
    condition_7 = stock_data['close'].values[-1] <= 1.25 * stock_data['52_week_high'].values[-1]
    all_condition = condition_1 & condition_2 & condition_4 & condition_5 & condition_6 & condition_7
    return condition_1


def fetchdataandreturn_pivot(symbol):
    username = 'YourTradingViewUsername'
    password = 'YourTradingViewPassword'

    tv = TvDatafeed(username, password)
    # index

    symbolhistory = tv.get_hist(symbol=symbol, exchange='NSE', interval=Interval.in_weekly, n_bars=3)
    data = symbolhistory
    if data is not None:
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
            'p': round(pi,2),
            's1': round(S1,2),
            'r1': round(R1,2),
            's2': round(S2,2),
            'r2': round(R2,2),
            'r3': round(R3,2),
            's3': round(S3,2)
        }
        global pivot_fibo_level
        pivot_fibo_level = fibonacci_levels

def defineresistancelevel(fibo_level,close):
  data = fibo_level
  filter_value = close

  matching_keys = [key for key, value in data.items() if value >= filter_value]
  max_key = min(matching_keys, key=lambda k: data[k], default='p')
  return max_key

def definesupportlevel(fibo_level,close):
  data = fibo_level
  filter_value = close

  matching_keys = [key for key, value in data.items() if value <= filter_value]
  max_key = max(matching_keys, key=lambda k: data[k], default='p')
  return max_key

# Example usage
def main():

    print('check stetergy')
    global obj

    current_date_time = datetime.datetime.now()
    form_date = current_date_time - timedelta(days=10)

    api_key = document.api_key
    user_id = document.user_id
    password = document.password
    totp = pyotp.TOTP(document.totp).now()
    # print(feedToken)

    try:
        obj = SmartConnect(api_key=api_key)
        token = obj.generateToken(obj.generateSession(user_id, password, totp)["data"]["refreshToken"])
        jwtToken = token['data']["jwtToken"]
        refreshToken = token['data']['refreshToken']
        feedToken = token['data']['feedToken']
        print(token)
        for script, token in script_list.items():
            historicParam = {
                "exchange": exchange,
                "symboltoken": token,
                "interval": "FIVE_MINUTE",
                "fromdate": form_date.strftime("%Y-%m-%d 09:15"),
                "todate": current_date_time.strftime("%Y-%m-%d %H:%M")
            }
            hist_data = obj.getCandleData(historicParam)["data"]
            LTP = obj.ltpData(exchange, script, token)
            # print(LTP)
            #print("__________hist",hist_data)
            if hist_data != None:
                df = pd.DataFrame(
                    hist_data,
                    columns=['date', 'open', 'high', 'low', 'close', 'volume'])


                # print(df.tail(40))
                if not df.empty:
                        # Load stock data (replace 'your_stock_data.csv' with your actual data)
                        stock_data = df


                        resistancelevel = []
                        supportlevel = []
                        itemclose = df.close.values[-1]
                        itemclosepre = df.close.values[-2]
                        itemclose
                        supports = df[df.low == df.low.rolling(10, center=True).min()].low
                        resistances = df[df.high == df.high.rolling(10, center=True).min()].high
                        supports
                        level = pd.concat([supports,resistances])
                        level = level[abs(level.diff()) > 10]

                        support_item = ''
                        if level is not None:
                            for a in level:
                              if a > itemclose and a < itemclosepre or a < itemclose and a > itemclosepre:
                                buy_traded_stock.append(script)

                        #level
                        # sorted_resistance = sorted(supportlevel, reverse=True)
                        # filtered_resistance = [sorted_resistance[0]] + [b for a, b in zip(sorted_resistance, sorted_resistance[1:]) if a - b >= 100]
                        #print(level)
                        print(script,buy_traded_stock)
                        #print(sorted(supportlevel ,reverse=True),'support')

            time.sleep(2)
        print(buy_traded_stock)

    except Exception as e:
        print("Historic Api failed: {}".format(e),format(datetime.datetime.now()))
        bot_message = f"Historic Api failed {e}"




if __name__ == "__main__":
    main()

