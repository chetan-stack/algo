import time

import pyotp
import schedule
import xlwings as xsw
import getstockoptionchain
import yfinance as yf
import pandas as pd
from SmartApi import SmartConnect, document  # or from SmartApi.smartConnect import SmartConnect
import stock_token_list

# Replace 'TCS.NS' with the ticker symbol of the Indian stock you're interested in

# Fetch live stock data
api_key = document.api_key
user_id = document.user_id
password = document.password
totp = pyotp.TOTP(document.totp).now()


stockscanner = [
    "AARTIIND",
    "ABB",
    "ABBOTINDIA",
    "ABCAPITAL",
    "ABFRL",
    "ACC",
    "ADANIENT",
    "ADANIPORTS",
    "ALKEM",
    "AMBUJACEM",
    "APOLLOHOSP",
    "APOLLOTYRE",
    "ASHOKLEY",
    "ASIANPAINT",

]

obj = SmartConnect(api_key=api_key)
token = obj.generateToken(obj.generateSession(user_id, password, totp)["data"]["refreshToken"])


storedata = []

def storegerateddata():
    for i in stockscanner:
        try:
            stock_symbol = i + '-EQ'
            symboltoken = stock_token_list.scripts[stock_symbol]
            print(stock_symbol)
            LTP = obj.ltpData('NSE', stock_symbol, symboltoken)
            print(LTP['data']['close'])
            # stock_data = yf.Ticker(stock_symbol)
            # Get the latest stock price (Last Traded Price or LTP)
            latest_price = LTP['data']['close']
            #print(stock_symbol,latest_price)

            catchdata = getstockoptionchain.getparams(i,latest_price,'ce')

            createformat = {
                'symbol': i,
                'price': latest_price,
                'pe_oi':catchdata['pe_oi'],
                'pe_change':catchdata['pe_change'],
                'ce_oi': catchdata['ce_oi'],
                'ce_change': catchdata['ce_change'],
                'Strick price': catchdata['strick'],
                'max oi': catchdata['max oi'],
                'max oi type': catchdata['max oi type'],
                'max oi strick': catchdata['max oi strick'],
                'signal': 'buy' if catchdata['ce_change'] < catchdata['pe_change'] else 'sell'
            }

            symbol_index = None
            for index, data in enumerate(storedata):
                if data['symbol'] == i:
                    # Update the existing entry in storedata
                    # data.update(createformat)
                    symbol_index = index
                    break
            if symbol_index is None:
                storedata.append(createformat)
            else:
                # Update the entry at the same index
                storedata[symbol_index] = createformat
            # storedata.append(createformat)
            df = pd.DataFrame(storedata)
            print(storedata)
            time.sleep(0.5)
            wb = xsw.Book("angeone.xlsx")
            st = wb.sheets('nifty')
            st.range('A1').value = df
            # storeexceldata()
        except Exception as e:
            print(e)

def storeexceldata():
    wb = xsw.Book("angeone.xlsx")
    st = wb.sheets('nifty')
    st.range('A1').value = storedata



storegerateddata()
schedule.every(1).minutes.do(storegerateddata)

while True:
    # print("start tym , CURRENT TIME:{}".format(datetime.datetime.now()))
    try:
        schedule.run_pending()
        time.sleep(2)
    except Exception as e:
        raise e
