from datetime import datetime,timedelta
from SmartApi import SmartConnect
import document
import pyotp
import datetime
import pandas_ta as ta
import pandas as pd
import numpy as np
import requests



def initialisedTockenMap():
    url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
    d = requests.get(url).json()
    global token_df
    token_df = pd.DataFrame.from_dict(d)
    token_df['expiry'] = pd.to_datetime(token_df['expiry'])
    token_df = token_df.astype({'strike': float})
    print('check', token_df)


print('checl now')
initialisedTockenMap()

def getTokenInfo(exch_seg,instrumenttype,symbol,strike_price,pe_ce):

    df = token_df
    strike_price = strike_price*100
    if exch_seg == 'NSE':
        eq_df = df[(df['exch_seg'] == 'NSE')]
        return eq_df[(eq_df['symbol'] == symbol)]
    elif exch_seg == 'NFO' and (instrumenttype == 'OPTSTK' or instrumenttype == 'OPTIDX'):
        return df[(df['exch_seg'] == 'NFO') & (df['instrumenttype'] == instrumenttype) & (df['name'] == symbol) & ((df['strike'] == strike_price)) & (df['symbol'].str.endswith(pe_ce)) & (df['expiry'] >= str(datetime.date.today()))].sort_values(by=['expiry'])



tokeninfo = getTokenInfo('NSE','OPTIDX','NIFTY','','').iloc[0]['token']
print(tokeninfo)
api_key = document.api_key
user_id = document.user_id
password = document.password
totp = pyotp.TOTP(document.totp).now()
obj = SmartConnect(api_key=api_key)
token = obj.generateToken(obj.generateSession(user_id, password, totp)["data"]["refreshToken"])

LTP = obj.ltpData('NSE','NIFTY',tokeninfo)['data']['ltp']
print('ltp',LTP)

RTM = int(round(LTP/100)*100) #to get check acurate price
print('rtm',RTM)

## now check price and place order details

ce_symbol = getTokenInfo('NFO','OPTIDX','NIFTY',RTM,'CE').iloc[0]
print(ce_symbol)
pe_symbol = getTokenInfo('NFO','OPTIDX','NIFTY',RTM,'PE').iloc[0]

#plcae order

# place_order(ce_symbol['token'],ce_symbol['symbol'],ce_symbol['lotsize'],'NFO','SELL')
# place_order(pe_symbol['token'],pe_symbol['symbol'],pe_symbol['lotsize'],'NFO','SELL')


print(tokeninfo,token,LTP)
