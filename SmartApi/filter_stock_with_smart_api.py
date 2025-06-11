import pandas as pd
import pandas_ta as ta
import pyotp
from smartapi import SmartConnect
from datetime import datetime,timedelta
import ta.volatility as th
import document
import numpy as np

# Enter your API credentials
client_id = "CLIENT_ID"
access_token = "ACCESS_TOKEN"
refresh_token = "REFRESH_TOKEN"
redirect_url = "REDIRECT_URL"

api_key = document.api_key
user_id = document.user_id
password = document.password
totp = pyotp.TOTP(document.totp).now()

# Create SmartConnect object
# smart_api = SmartConnect(client_id=client_id, access_token=access_token, refresh_token=refresh_token)

# Renew access token if it has expired
# smart_api.refreshSession()

# Get current date
today = datetime.now().strftime("%Y-%m-%d")
# form_date = current_date_time - timedelta(days=10)

exchange = "NSE"

# Function to get historical data for a symbol from Angle One Smart API
def get_historical_data(symbol, from_date, to_date):
    print(symbol, from_date)
    try:
        smart_api = SmartConnect(api_key=api_key)
        token = smart_api.generateToken(smart_api.generateSession(user_id, password, totp)["data"]["refreshToken"])
        data = smart_api.getCandleData(symbol=symbol, start_date=from_date, end_date=to_date, interval='ONE_MINUTE')
        df = pd.DataFrame(data['data'])
        print(df)
        df.rename(columns={'o': 'open', 'h': 'high', 'l': 'low', 'c': 'close', 'v': 'volume'}, inplace=True)
        df.set_index('timestamp', inplace=True)
        df.index = pd.to_datetime(df.index, unit='ms')
        df.sort_index(inplace=True)
        return df
    except Exception as e:
        print("Error fetching data for {}: {}".format(symbol, str(e)))
        return None

# Function to calculate historical volatility using Pandas TA
def get_hv(df, period=20):
    # hv = th.historical(df.close, window=period, annualize=False)
    # return hv.iloc[-1]
    print(df)
    daily_returns = df.close.pct_change().dropna()
    volatility = np.sqrt((20 * daily_returns.var()) * 252)
    return volatility

# Function to get highly volatile stocks for intraday trading
def get_intraday_highly_volatile_stocks(stocks, date):
    results = []
    # for token in stocks:
    #     print(token)
    #     df = get_historical_data(token, date, date)
    #     if df is not None and len(df) > 0:
    #         hv = get_hv(df)
    #         if hv >= 5:  # Filter highly volatile stocks with historical volatility >= 5%
    #             results.append((token, hv))
    smart_api = SmartConnect(api_key=api_key)
    token = smart_api.generateToken(smart_api.generateSession(user_id, password, totp)["data"]["refreshToken"])
    # print(smart_api)
    current_date_time = datetime.now()
    form_date = current_date_time - timedelta(days=30)
    for script, token in nse_stocks.items():
        historicParam = {
            "exchange": exchange,
            "symboltoken": token,
            "interval": "FIVE_MINUTE",
             "fromdate": form_date.strftime("%Y-%m-%d 09:15"),
            "todate": current_date_time.strftime("%Y-%m-%d %H:%M")
        }
        hist_data = smart_api.getCandleData(historicParam)['data']
        df = hist_data
        df = pd.DataFrame(
            hist_data,
            columns=['date', 'open', 'high', 'low', 'close', 'volume'])
        # print(hist_data)
        if df is not None and len(df) > 0:
            hv = get_hv(df)
            if hv >= 1:  # Filter highly volatile stocks with historical volatility >= 1%
                results.append((token, hv))
    return results

# Example usage
nse_stocks = {
    'ADANIENT-EQ': '25',
    'APOLLOHOSP-EQ': '157',
    'ASIANPAINT-EQ': '236',
    'AXISBANK-EQ': '5900',
    'BAJFINANCE-EQ': '317',
    'BAJAJFINSV-EQ': '16675',
    'BPCL-EQ': '526',
    'BHARTIARTL-EQ': '10604',
    'BRITANNIA-EQ': '547',
    'CIPLA-EQ': '694',
    'COALINDIA-EQ': '20374',
    'DIVISLAB-EQ': '10940',
    'DRREDDY-EQ': '881',
    'EICHERMOT-EQ': '910',
    'GRASIM-EQ': '1232',
    'HCLTECH-EQ': '7229',
    'HDFCBANK-EQ': '1333',
    'HDFCLIFE-EQ': '467',
    'HEROMOTOCO-EQ': '1348',
    'HINDALCO-EQ': '1363',
    'HINDUNILVR-EQ': '1394',
    'HDFC-EQ': '1330',
    'ICICIBANK-EQ': '4963',
    'ITC-EQ': '1660',
    'INDUSINDBK-EQ': '5258',
    'INFY-EQ': '1594',
    'JSWSTEEL-EQ': '11723',
    'KOTAKBANK-EQ': '1922',
    'M&M-EQ': '2031',
    'MARUTI-EQ': '10999',
    'NTPC-EQ': '11630',
    'NESTLEIND-EQ': '17963',
    'ONGC-EQ': '2475',
    'POWERGRID-EQ': '14977',
    'RELIANCE-EQ': '2885',
    'SBILIFE-EQ': '21808',
    'SBIN-EQ': '3045',
    'SUNPHARMA-EQ': '3351',
    'TCS-EQ': '11536',
    'TATACONSUM-EQ': '3432',
    'TATAMOTORS-EQ': '3456',
    'TATASTEEL-EQ': '3499',
    'TECHM-EQ': '13538',
    'TITAN-EQ': '3506',
    'UPL-EQ': '11287',
    'ULTRACEMCO-EQ': '11532',
    'WIPRO-EQ': '3787',
  }

date = today
results = get_intraday_highly_volatile_stocks(nse_stocks, date)
print("Highly volatile stocks for intraday trading on {}: {}".format(date, results))
