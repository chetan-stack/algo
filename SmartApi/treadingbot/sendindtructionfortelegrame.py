import ast
import os
from datetime import datetime

import numpy as np
import requests
from flask import Flask, render_template, request
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas_ta as ta

import mplfinance as mpf

from tvDatafeed import TvDatafeed, Interval
# import stocks_select_to_trade

app = Flask(__name__)

# Replace with your TradingView credentials
username = 'YourTradingViewUsername'
password = 'YourTradingViewPassword'

tv = TvDatafeed(username, password)

# List of available symbols and their display names
symbols = {
    "NIFTY": 'NIFTY',
    "BANKNIFTY": 'BANKNIFTY',
    "SENSEX":'SENSEX',
    'BTCUSD': 'BTCUSD',
    'CNXFINANCE':'CNXFINANCE',
    "AARTIIND": "Aarti Industries Limited",
    "ABB": "ABB India Limited",
    "ABBOTINDIA": "Abbott India Limited",
    "ABCAPITAL": "Aditya Birla Capital Limited",
    "ABFRL": "Aditya Birla Fashion and Retail Limited",
    "ACC": "ACC Limited",
    "ADANIENT": "Adani Enterprises Limited",
    "ADANIPORTS": "Adani Ports and Special Economic Zone Limited",
    "ALKEM": "Alkem Laboratories Limited",
    "AMBUJACEM": "Ambuja Cements Limited",
    "APOLLOHOSP": "Apollo Hospitals Enterprise Limited",
    "APOLLOTYRE": "Apollo Tyres Limited",
    "ASHOKLEY": "Ashok Leyland Limited",
    "ASIANPAINT": "Asian Paints Limited",
    "ASTRAL": "Astral Limited",
    "ATUL": "Atul Limited",
    "AUBANK": "AU Small Finance Bank Limited",
    "AUROPHARMA": "Aurobindo Pharma Limited",
    "AXISBANK": "Axis Bank Limited",
    "BAJAJ-AUTO": "Bajaj Auto Limited",
    "BAJAJFINSV": "Bajaj Finserv Limited",
    "BAJFINANCE": "Bajaj Finance Limited",
    "BALKRISIND": "Balkrishna Industries Limited",
    "BALRAMCHIN": "Balrampur Chini Mills Limited",
    "BANDHANBNK": "Bandhan Bank Limited",
    "BANKBARODA": "Bank of Baroda",
    "BATAINDIA": "Bata India Limited",
    "BEL": "Bharat Electronics Limited",
    "BERGEPAINT": "Berger Paints India Limited",
    "BHARATFORG": "Bharat Forge Limited",
    "BHARTIARTL": "Bharti Airtel Limited",
    "BHEL": "Bharat Heavy Electricals Limited",
    "BIOCON": "Biocon Limited",
    "BOSCHLTD": "Bosch Limited",
    "BPCL": "Bharat Petroleum Corporation Limited",
    "BRITANNIA": "Britannia Industries Limited",
    "BSOFT": "Birlasoft Limited",
    "CANBK": "Canara Bank",
    "CANFINHOME": "Can Fin Homes Limited",
    "CHAMBLFERT": "Chambal Fertilizers & Chemicals Limited",
    "CHOLAFIN": "Cholamandalam Investment and Finance Company Limited",
    "CIPLA": "Cipla Limited",
    "COALINDIA": "Coal India Limited",
    "COFORGE": "Coforge Limited",
    "COLPAL": "Colgate-Palmolive (India) Limited",
    "CONCOR": "Container Corporation of India Limited",
    "COROMANDEL": "Coromandel International Limited",
    "CROMPTON": "Crompton Greaves Consumer Electricals Limited",
    "CUB": "City Union Bank Limited",
    "CUMMINSIND": "Cummins India Limited",
    "DABUR": "Dabur India Limited",
    "DALBHARAT": "Dalmia Bharat Limited",
    "DEEPAKNTR": "Deepak Nitrite Limited",
    "DIVISLAB": "Divi's Laboratories Limited",
    "DIXON": "Dixon Technologies (India) Limited",
    "DLF": "DLF Limited",
    "DRREDDY": "Dr. Reddy's Laboratories Limited",
    "EICHERMOT": "Eicher Motors Limited",
    "ESCORTS": "Escorts Limited",
    "EXIDEIND": "Exide Industries Limited",
    "FEDERALBNK": "Federal Bank Limited",
    "GAIL": "GAIL (India) Limited",
    "GLENMARK": "Glenmark Pharmaceuticals Limited",
    "GMRINFRA": "GMR Infrastructure Limited",
    "GNFC": "Gujarat Narmada Valley Fertilizers & Chemicals Limited",
    "GODREJCP": "Godrej Consumer Products Limited",
    "GODREJPROP": "Godrej Properties Limited",
    "GRANULES": "Granules India Limited",
    "GRASIM": "Grasim Industries Limited",
    "GUJGASLTD": "Gujarat Gas Limited",
    "HAL": "Hindustan Aeronautics Limited",
    "HAVELLS": "Havells India Limited",
    "HCLTECH": "HCL Technologies Limited",
    "HDFCAMC": "HDFC Asset Management Company Limited",
    "HDFCBANK": "HDFC Bank Limited",
    "HDFCLIFE": "HDFC Life Insurance Company Limited",
    "HEROMOTOCO": "Hero MotoCorp Limited",
    "HINDALCO": "Hindalco Industries Limited",
    "HINDCOPPER": "Hindustan Copper Limited",
    "HINDPETRO": "Hindustan Petroleum Corporation Limited",
    "HINDUNILVR": "Hindustan Unilever Limited",
    "ICICIBANK": "ICICI Bank Limited",
    "ICICIGI": "ICICI Lombard General Insurance Company Limited",
    "ICICIPRULI": "ICICI Prudential Life Insurance Company Limited",
    "IDEA": "Vodafone Idea Limited",
    "IDFC": "IDFC Limited",
    "IDFCFIRSTB": "IDFC First Bank Limited",
    "IEX": "Indian Energy Exchange Limited",
    "IGL": "Indraprastha Gas Limited",
    "INDHOTEL": "The Indian Hotels Company Limited",
    "INDIACEM": "The India Cements Limited",
    "INDIAMART": "Indiamart Intermesh Limited",
    "INDIGO": "InterGlobe Aviation Limited",
    "INDUSINDBK": "IndusInd Bank Limited",
    "INDUSTOWER": "Indus Towers Limited",
    "INFY": "Infosys Limited",
    "IOC": "Indian Oil Corporation Limited",
    "IPCALAB": "Ipca Laboratories Limited",
    "IRCTC": "Indian Railway Catering and Tourism Corporation Limited",
    "ITC": "ITC Limited",
    "JINDALSTEL": "Jindal Steel & Power Limited",
    "JKCEMENT": "JK Cement Limited",
    "JSWSTEEL": "JSW Steel Limited",
    "JUBLFOOD": "Jubilant Foodworks Limited",
    "KOTAKBANK": "Kotak Mahindra Bank Limited",
    "LALPATHLAB": "Dr. Lal Path Labs Limited",
    "LAURUSLABS": "Laurus Labs Limited",
    "LICHSGFIN": "LIC Housing Finance Limited",
    "LT": "Larsen & Toubro Limited",
    "LTF": "L&T Finance Holdings Limited",
    "LTIM": "L&T Infrastructure Finance Company Limited",
    "LTTS": "L&T Technology Services Limited",
    "LUPIN": "Lupin Limited",
    "M&M": "Mahindra & Mahindra Limited",
    "M&MFIN": "Mahindra & Mahindra Financial Services Limited",
    "MANAPPURAM": "Manappuram Finance Limited",
    "MARICO": "Marico Limited",
    "MARUTI": "Maruti Suzuki India Limited",
    "MCDOWELL-N": "United Spirits Limited",
    "MCX": "Multi Commodity Exchange of India Limited",
    "METROPOLIS": "Metropolis Healthcare Limited",
    "MFSL": "Max Financial Services Limited",
    "MGL": "Mahanagar Gas Limited",
    "MOTHERSON": "Motherson Sumi Systems Limited",
    "MPHASIS": "Mphasis Limited",
    "MRF": "MRF Limited",
    "MUTHOOTFIN": "Muthoot Finance Limited",
    "NATIONALUM": "National Aluminium Company Limited",
    "NAUKRI": "Info Edge (India) Limited",
    "NAVINFLUOR": "Navin Fluorine International Limited",
    "NESTLEIND": "Nestle India Limited",
    "NMDC": "NMDC Limited",
    "NTPC": "NTPC Limited",
    "OBEROIRLTY": "Oberoi Realty Limited",
    "OFSS": "Oracle Financial Services Software Limited",
    "ONGC": "Oil and Natural Gas Corporation Limited",
    "PAGEIND": "Page Industries Limited",
    "PEL": "Piramal Enterprises Limited",
    "PERSISTENT": "Persistent Systems Limited",
    "PETRONET": "Petronet LNG Limited",
    "PFC": "Power Finance Corporation Limited",
    "PIDILITIND": "Pidilite Industries Limited",
    "PIIND": "PI Industries Limited",
    "PNB": "Punjab National Bank",
    "POLYCAB": "Polycab India Limited",
    "POWERGRID": "Power Grid Corporation of India Limited",
    "PVRINOX": "PVR Limited",
    "RAMCOCEM": "The Ramco Cements Limited",
    "RBLBANK": "RBL Bank Limited",
    "RECLTD": "REC Limited",
    "RELIANCE": "Reliance Industries Limited",
    "SAIL": "Steel Authority of India Limited",
    "SBICARD": "SBI Cards and Payment Services Limited",
    "SBILIFE": "SBI Life Insurance Company Limited",
    "SBIN": "State Bank of India",
    "SHREECEM": "Shree Cement Limited",
    "SHRIRAMFIN": "Shriram Transport Finance Company Limited",
    "SIEMENS": "Siemens Limited",
    "SRF": "SRF Limited",
    "SUNPHARMA": "Sun Pharmaceutical Industries Limited",
    "SUNTV": "Sun TV Network Limited",
    "SYNGENE": "Syngene International Limited",
    "TATACHEM": "Tata Chemicals Limited",
    "TATACOMM": "Tata Communications Limited",
    "TATACONSUM": "Tata Consumer Products Limited",
    "TATAMOTORS": "Tata Motors Limited",
    "TATAPOWER": "Tata Power Company Limited",
    "TATASTEEL": "Tata Steel Limited",
    "TCS": "Tata Consultancy Services Limited",
    "TECHM": "Tech Mahindra Limited",
    "TITAN": "Titan Company Limited",
    "TORNTPHARM": "Torrent Pharmaceuticals Limited",
    "TRENT": "Trent Limited",
    "TVSMOTOR": "TVS Motor Company Limited",
    "UBL": "United Breweries Limited",
    "ULTRACEMCO": "UltraTech Cement Limited",
    "UPL": "UPL Limited",
    "VEDL": "Vedanta Limited",
    "VOLTAS": "Voltas Limited",
    "WIPRO": "Wipro Limited",
    "ZEEL": "Zee Entertainment Enterprises Limited",
    "ZYDUSLIFE": "Cadila Healthcare Limited"


    # Add more symbols as needed
}

cryptosymbol = {
    'BITCOINUSD':'BITCOINUSD'
}

# Map string time frames to Interval objects
timeframe_map = {
    '1m': Interval.in_1_minute,
    '3m': Interval.in_3_minute,
    '5m': Interval.in_5_minute,
    '15m': Interval.in_15_minute,
    '30m': Interval.in_30_minute,
    '45m': Interval.in_45_minute,
    '1h': Interval.in_1_hour,
    '2h': Interval.in_2_hour,
    '3h': Interval.in_3_hour,
    '4h': Interval.in_4_hour,
    '1d': Interval.in_daily,
    '1w': Interval.in_weekly,
    '1M': Interval.in_monthly,
}

trendcheck = {
    'Only Support':1,
    'Both':2
}

exchangedropdown = {
    'NSE':'NSE',
    'MCX':'MCX',
    'CRYPTO':'CRYPTO',
    'BSE':'BSE'
}

# List of available time frames and their display names
timeframes = {
    '1m': '1 Minute',
    '3m': '3 Minutes',
    '5m': '5 Minutes',
    '15m': '15 Minutes',
    '30m': '30 Minutes',
    '45m': '45 Minutes',
    '1h': '1 Hour',
    '2h': '2 Hours',
    '3h': '3 Hours',
    '4h': '4 Hours',
    '1d': '1 Day',
    '1w': '1 Week',
    '1M': '1 Month',
}
readeddata = ''
def readfile():
    file_path = "stocklistedwithsupport.txt"
    with open(file_path, "r") as file:
        while True:
            line = file.readline()
            if not line:
                break
            print(line)
            return ast.literal_eval(line)

def  optionchaindetection(symbol,target,type):
    try:
        url = f"https://www.nseindia.com/api/option-chain-equities?symbol={symbol}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en-US,en;q=0.9,bs;q=0.8',
            'Cookie': '_ga=GA1.1.1264432697.1673939756; _ga_PJSKY6CFJH=GS1.1.1695886444.13.0.1695886444.60.0.0; defaultLang=en; _ga_QJZ4447QD3=GS1.1.1717392523.55.0.1717392523.0.0.0; bm_sz=3457BC929D00520E0CD1634BAFF7ED5A~YAAQj28/F8Kry7iPAQAAcTlY3RefI17JVJnvhnruDLduan7p5mTVDsPKwnp2M1RytoH7xdxRGZuJqA3CUFvhtKQ6nxTdJ2FutqI4eZiFl6wkkJTrg12w+0cN9rmwMQp/2gXeEm9UtPu5kGzMytHf15gPx1szYwCaA+XLnz16SaZxFxHa4jzT0peE2yU9ovrHR+pNJR7EytPrttL1dsaMFJX/KaD0ctdjJ4TyL0IiOdhQ/YuzF9uDomEb7Wv/nopqkKldQsHtkO8cQCyOO7eMhTzXdlncRFUBDgjoN7TWzqVh+7StycOccxMnb2vzGyjOg/3nskAkryHbeTphOOs9KYXzxYZvh7nk6b9HUnlocWzn32uvBZDMR6u3nqcvqLqAtakvw3+0w3+o67Avtw==~3683381~4535096; nsit=46PI8ih9kBgnNSmv6ZOvCxaq; nseappid=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhcGkubnNlIiwiYXVkIjoiYXBpLm5zZSIsImlhdCI6MTcxNzQwNzEyNCwiZXhwIjoxNzE3NDE0MzI0fQ.XCbLgzcTMBHSDfPJ0ZCQsUwfV6DaUMgpk-vRASyymWw; AKA_A2=A; bm_mi=47DC94F2287D5CB54E90ACE980A6C2DD~YAAQhm4/F3+fJbuPAQAAUBFx3RfzEPIp4NYm/4E8Wx65vxpHNOoM5JwpkFHzECKPjQFwoVZT0JDBfEkByCc7jwOrGA+saEApxuz5ECG2O4pbxoN6w8ncWTrD37zOl011NvuFN0AY7oKN8ek/ui4cuklbgheEu2334LC+cv5gQ/mNQI7T8Cv5MJPqtZP51Y8Q7pDRncMFF7xoyoVGUOvWPB7axBliDsWv6MMmjCBiV5t6YBS4z5b5Qlba6zuE5sBDHk/Xbdh5KIoX3zcbbRmUukhez3RbDnxiV4XS/yWGLZT4e1CXx8zKYVt6tr8ijnzBWo5b2eSAaougRAmS~1; ak_bmsc=18E371E7E32B525F080C36377657C380~000000000000000000000000000000~YAAQhm4/FwygJbuPAQAAqhpx3RfjqYVSMQPp4HCs5OzP9efbAtIsgebTun0W0CT5FgkI74RWIjt8gOCPloOwCmNiFCGmo8hdhClo/Wz4qgeO/myfOTyfbUydKcRZCQ/Ps8nDx1DzayCnLeGUKaIDmS0JmFsiM182RYOE52Fa3T0UEd1YmaMpsiby2e7f02aIj2ZKfZGqsJeXnMiqTOt6e5FqC0eYGgs9xYuMrm6MS8qoWE12+yN25xeO6AjObUYAcEZuwj7sxC6SvG8IaZ2mxo9A+N7aKrrcv8dR19SjINMviazsCnTwVZ/rMpYGaFhYx8sRWywZ4AwSeuSNSazHEiXJfal+L7bx/SNBtcP0pC+CtyAiJZS5O3BkoDri6txUmS7SAtwBlghyMMOu7/f+GSadfwPwIcCr9l+vja0I1yrKjs5mktJRrDUD7ICzdcT380D0dO0z+0ifLcqhBfbdtdJTzovg0Ud3if1CF+m4w66tg0HvDS31s2XowmM=; _ga_87M7PJ3R97=GS1.1.1717407126.94.1.1717407128.0.0.0; RT="z=1&dm=nseindia.com&si=c18a1119-1f6c-4487-8f1e-fba62a072b48&ss=lwyj5z1t&sl=1&se=8c&tt=2nm&bcn=%2F%2F684d0d4c.akstat.io%2F&ld=8p34s"; _abck=6485F05FA55DEFC3F98E9E0C0673542E~0~YAAQhm4/F4OgJbuPAQAAqCJx3QtQ3GB/r8SZfBax0ovmwAkhLdlf/u4WehUnPfkgrEp89vtlICwV33xlLJpyFaWwl80DJlguOPhVWKwX+oKZn8n6QgB+/3CAnFarfMZKfThL9aL7updbSV7UoF3gsSFruBMif9+5ZWIpxoZUI/i5Bx5zGw+2QMLzWX3QSB8LuZPcsFURsxoFjLIHL/YFpb9zYuRM+/nxMaTHm9/14yOJyy0+sMXE9YZNnadtLkf3A2vkzSB/LhJAbI2eK+t7ksE7hbgV+HtA3HN4zbfRIlOiSJhPA91ayPTClCwWMWI15SG9WDb3gtlFdtzELCLed64w70nqKju/scHEAicqfXaYYDd+iF1G2MaDh8H2J+1c~-1~-1~-1; bm_sv=FE21B3137ACBE75D270F08BCCD1039AF~YAAQhm4/F4SgJbuPAQAAqCJx3RefBeEGkvU2Zkeguk4pQbpt38X+X06XmnLVScm9Jlxh8b/prYIfP9bCWEjornqtlkPeA/7d/wPwRPlc47Kef+VxHgQErVB68PMC6UpMhAj1Qpe0JtbUnR1LhnHN+4Ho62O36g1JUNqg+COEjKpo+AGwOD+WLL+ipHuWwL5pFOlvBaLrsG1AAHZ34FOFlVJme63PsFaA/fsRFMeGrH2aLg3ftYANtyHZzPeMg7azDCuw~1'

        }
        session = requests.session()
        request = session.get(url, headers=headers)
        cookies = dict(request.cookies)
        # print(cookies)
        # print(session.get(url,headers=headers,cookies=cookies))
        response = session.get(url, headers=headers, cookies=cookies).json()['filtered']['data']
        rawdata = pd.DataFrame(response)
        # print(response,'response')
        docdata = []
        for i in response:
            for j, k in i.items():
                if j == 'CE' or j == 'PE':
                    info = k
                    info['instrumenet Type'] = j
                    docdata.append(info)
        df = pd.DataFrame(docdata)
        target = int(target)
        today_date = datetime.today().date().strftime('%d-%b-%Y')  # Get today's date

        max_open_interest_index = df['openInterest'].idxmax()

        closest_strike_price = min(df['strikePrice'], key=lambda x: abs(x - target))
        setdf = df[(df['strikePrice'] == closest_strike_price)]

        data = {
            'pe_oi': setdf[setdf['instrumenet Type'] == 'PE']['openInterest'].values[-1],
            'ce_oi': setdf[setdf['instrumenet Type'] == 'CE']['openInterest'].values[-1],
            'pe_change': setdf[setdf['instrumenet Type'] == 'PE']['changeinOpenInterest'].values[-1],
            'ce_change': setdf[setdf['instrumenet Type'] == 'CE']['changeinOpenInterest'].values[-1],
            'strick': closest_strike_price,
            'max oi': df['openInterest'].max(),
            'max oi type': df.loc[max_open_interest_index, 'instrumenet Type'],
            'max oi strick': df.loc[max_open_interest_index, 'strikePrice']
        }

        returndata = setdf.to_json(orient='records')
        print(returndata)
        return returndata
    except Exception as e:
        print(e)

def fetch_and_process_data(symbol, interval,exchange, n_bars, rolling_window, level_diff_threshold):
    try:
        df = tv.get_hist(symbol=symbol, exchange=exchange, interval=interval, n_bars=n_bars)
        df['ema9'] = ta.ema(df["close"], length=9)
        df['ema14'] = ta.ema(df["close"], length=14)

        if df is not None:
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

            return df, level, registance_item, support_item,itemclose
        else:
            return 'not data found'
    except Exception as e:
        print('error',e)

def analyze_nifty_data(symbol, interval, n_bars, rolling_window, level_diff_threshold):
    # Connect to TradingView
    tv = TvDatafeed('username', 'password')

    # Fetch historical data
    df = tv.get_hist(symbol=symbol, exchange='NSE', interval=interval, n_bars=n_bars)
    itemclose = df.close.values[-1]

    # Calculate support and resistance levels
    supports = df[df.low == df.low.rolling(rolling_window, center=True).min()].close
    resistances = df[df.high == df.high.rolling(rolling_window, center=True).max()].close

    level = pd.concat([supports, resistances])
    level = level[abs(level.diff()) > level_diff_threshold]

    resistancelevel = []
    supportlevel = []
    for a in level:
        if a > itemclose:
            resistancelevel.append(a)
        else:
            supportlevel.append(a)

    if resistancelevel:
        resistance_item = max(resistancelevel, key=lambda x: x if x > itemclose else float('-inf'))
    else:
        resistance_item = None

    if supportlevel:
        support_item = max(supportlevel, key=lambda x: x if x < itemclose else float('-inf'))
    else:
        support_item = None

    print("Resistance Levels:", sorted(resistancelevel, reverse=True))
    print("Support Levels:", sorted(supportlevel, reverse=True))
    print("Nearest Resistance:", resistance_item)
    print("Nearest Support:", support_item)

    # Calculate trend lines
    def calculate_trend_lines(df):
        trend_points_up = df[df.low == df.low.rolling(10, center=True).min()].dropna()
        x_up = (trend_points_up.index - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')
        y_up = trend_points_up.low.values

        trend_points_down = df[df.high == df.high.rolling(10, center=True).max()].dropna()
        x_down = (trend_points_down.index - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')
        y_down = trend_points_down.high.values

        coefficients_up = np.polyfit(x_up, y_up, 1)
        coefficients_down = np.polyfit(x_down, y_down, 1)

        uptrend_line = np.poly1d(coefficients_up)
        downtrend_line = np.poly1d(coefficients_down)

        return uptrend_line, downtrend_line

    uptrend_line, downtrend_line = calculate_trend_lines(df)

    # Create trend line data
    x_vals = np.linspace((df.index[0] - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s'),
                         (df.index[-1] - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s'), 100)
    uptrend_vals = uptrend_line(x_vals)
    downtrend_vals = downtrend_line(x_vals)

    trend_up = pd.Series(uptrend_vals, index=pd.to_datetime(x_vals, unit='s'))
    trend_down = pd.Series(downtrend_vals, index=pd.to_datetime(x_vals, unit='s'))

    # Plot with trend lines
    add_plot = [
        mpf.make_addplot(trend_up, color='green'),
        mpf.make_addplot(trend_down, color='red')
    ]

    return df, level, resistance_item, support_item, itemclose,add_plot

    #mpf.plot(df, type='candle', hlines=level.to_list(), style='charles', addplot=add_plot)

    print("Uptrend Line:", uptrend_line)
    print("Downtrend Line:", downtrend_line)


# @app.route('/', methods=['GET', 'POST'])
def index(symbol,exchangetype,interval_str):

    symbol = symbol  # Default symbol
    crypto = 'BITCOINUSD'
    trend = 1
    selectedstock = ''
    symboltype = ''
    datapass = 'ICICIBANK'
    exchangetype = exchangetype
    interval_str = interval_str  # Default interval
    n_bars = 100  # Default number of bars
    rolling_window = 20  # Default rolling window size
    level_diff_threshold = 20  # Default level difference threshold
    title = f"{symbol} - {interval_str}"

    # if request.method == 'POST':
    #     symbol = request.form.get('symbol')
    #     trend = request.form.get('trend')
    #     exchangetype = request.form.get('exchangedropdown')
    #     symboltype = request.form.get('symboltype')
    #     selectedstock = request.form.get('selectedstock')
    #     interval_str = request.form.get('timeframe')
    #     n_bars = int(request.form.get('n_bars'))
    #     rolling_window = int(request.form.get('rolling_window'))
    #     level_diff_threshold = int(request.form.get('level_diff_threshold'))
    #     datapass = symboltype if symboltype else symbol
    #     print('trend check',trend)
    interval = timeframe_map[interval_str]
    if int(trend) > 1:
        print('enter')
        if symboltype != '':
            if "EQ" in symboltype:
                # Remove "EQ" from symboltype
                cleaned_symboltype = symboltype.replace("-EQ", "")
            else:
                cleaned_symboltype = symboltype
            df, level, registance_item, support_item, itemclose, add_plot = analyze_nifty_data(symbol, interval, n_bars,
                                                                                         rolling_window,
                                                                                         level_diff_threshold)   # if selectedstock != '':

        else:
            df, level, registance_item, support_item, itemclose,add_plot =  analyze_nifty_data(symbol, interval, n_bars,
                                                                                         rolling_window,
                                                                                         level_diff_threshold)   # if selectedstock != '':
    else:
        print('enter in else')
        if symboltype != '':
            if "EQ" in symboltype:
                # Remove "EQ" from symboltype
                cleaned_symboltype = symboltype.replace("-EQ", "")
            else:
                cleaned_symboltype = symboltype
            df, level, registance_item, support_item, itemclose = fetch_and_process_data(cleaned_symboltype, interval,exchangetype,
                                                                                         n_bars,
                                                                                         rolling_window,
                                                                                         level_diff_threshold)
        else:
            df, level, registance_item, support_item, itemclose = fetch_and_process_data(symbol, interval,exchangetype, n_bars,
                                                                                         rolling_window,
                                                                                         level_diff_threshold)  # if selectedstock != '':

    #     df, level, registance_item, support_item = fetch_and_process_data(selectedstock, interval, n_bars, rolling_window,
    #                                                                       level_diff_threshold)
    # option_chain = optionchaindetection(symbol,itemclose,'')
    option_chain = 'abc'
    selectedstocks = readfile()
    # Save the chart as an image
    if not df.empty and not level.empty:
        try:
            image_path = 'static/chart.png'
            if os.path.exists(image_path):
                os.remove(image_path)
            # Plot the data
            if int(trend) > 1:
                mpf.plot(df, type='candle', hlines=level.to_list(), style='charles', addplot=add_plot,title=title,savefig='static/chart.png')
            else:
                add_plot = [
                    mpf.make_addplot(df['ema9'], color='blue', width=1),
                    mpf.make_addplot(df['ema14'], color='orange', width=1),

                    # Blue EMA line, adjust color and width as needed
                ]
                mpf.plot(df, type='candle', hlines=level.to_list(),addplot=add_plot, style='charles',title=title, savefig='static/chart.png')
            print("Plot saved successfully.")
            return registance_item, support_item, level.to_list()

        except Exception as e:
            print(f"An error occurred while plotting: {e}")
    else:
        print("DataFrame or level data is empty.")
    return None
#     return render_template('index.html', symbols=symbols,cryptosymbol=cryptosymbol,trend=trendcheck,symboltype=symboltype,exchangedropdown=exchangedropdown, symbol=symbol,option_chain=option_chain, timeframes=timeframes, timeframe=interval_str,
#                            n_bars=n_bars, rolling_window=rolling_window, level_diff_threshold=level_diff_threshold,
#                            registance_item=registance_item, support_item=support_item,readeddata=selectedstocks,levellist=level.to_list())
#
#
#
# if __name__ == '__main__':
#     app.run(debug=True)
