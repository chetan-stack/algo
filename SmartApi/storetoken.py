from datetime import datetime, timedelta
import datetime
import time
import pandas as pd
import requests
import schedule


import requests
import pandas as pd

# Define the variable outside the function to hold the data
token_df = None


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
# print(token_df)


def getTokenInfo(exch_seg, instrumenttype, symbol, strike_price, pe_ce, expiry_day=None):
    df = token_df
    strike_price = strike_price * 100
    if exch_seg == 'NSE':
        # print('nse')
        eq_df = df[(df['exch_seg'] == 'NSE')]
        # print(eq_df[(eq_df['name'] == 'NIFTY')],'---####---')
        return eq_df[(eq_df['name'] == 'NIFTY')]
    elif exch_seg == 'NFO' and (instrumenttype == 'OPTSTK' or instrumenttype == 'OPTIDX'):
        print('nfo')
        return df[(df['exch_seg'] == 'NFO') & (df['instrumenttype'] == instrumenttype) & (df['name'] == symbol) & (
        (df['strike'] == strike_price)) & (df['symbol'].str.endswith(pe_ce)) & (
                              df['expiry'] >= str(datetime.date.today()))].sort_values(by=['expiry'])
    elif exch_seg == 'BFO' and instrumenttype == 'OPTIDX':
        # Fetch BSE options (BFO - Sensex options)
        return df[
            (df['exch_seg'] == 'BFO') &
            (df['instrumenttype'] == 'OPTIDX') &
            (df['name'] == symbol) &
            (df['strike'] == strike_price) &
            (df['symbol'].str.endswith(pe_ce)) &
            (df['expiry'] >= str(datetime.date.today()))
        ].sort_values(by=['expiry'])


def placeorderdetails(exchnage,type,symbol,ltp):
    # tokeninfo = getTokenInfo('NSE', 'OPTIDX', symbol, '', '').iloc[0]['token']
    # print(tokeninfo, "---token")
    global LTP
    LTP = ltp
    RTM = int(round(LTP / 100) * 100)  # to get check acurate price
    # print(LTP, RTM)
    ## now check price and place order details
    # print(getTokenInfo('NFO', 'OPTIDX', 'NIFTY', RTM, 'CE').iloc[0])

    ce_symbol_data = getTokenInfo(exchnage, type, symbol, RTM, 'CE').iloc[0]
    pe_symbol_data = getTokenInfo(exchnage, type, symbol, RTM, 'PE').iloc[0]
    # print(ce_symbol_data,pe_symbol_data)
    return ce_symbol_data,pe_symbol_data
    # ce_symbol['token'] = ce_symbol_data['token']
    # ce_symbol['symbol'] = ce_symbol_data['symbol']
    # ce_symbol['lotsize'] = ce_symbol_data['lotsize']
    #
    # pe_symbol['token'] = pe_symbol_data['token']
    # pe_symbol['symbol'] = pe_symbol_data['symbol']
    # pe_symbol['lotsize'] = pe_symbol_data['lotsize']
# schedule.every(1).minutes.do(initialisedTockenMap)
import json

def getjson():
    # Path to the JSON file
    file_path = "OpenAPIScripMaster.json"

    # Open and load the JSON file
    with open(file_path, 'r') as file:
        json_data = json.load(file)

    # Print the JSON data
    return json_data

def getstockTokenInfo(symbol):
    # global token_df  # Ensure token_df is accessible globally
    data = getjson()
    for item in data:
        if item.get('name') and item['name'].lower() == symbol.lower():
            return item

# Example Usage:
# result = getTokenInfo('NSE', None, 'RELIANCE')  # Fetch stock token
# result = getTokenInfo('NFO', 'OPTSTK', 'RELIANCE', 2800, 'CE')  # Fetch option token

# initialisedTokenMap()


# placeorderdetails('NFO', 'OPTIDX','NIFTY',25500)
