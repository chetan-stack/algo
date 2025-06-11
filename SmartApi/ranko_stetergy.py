from smartapi import SmartConnect
import time
from datetime import datetime
import datetime
import pyotp

api_key = "pMZtYR5S"
user_id = "c182721"
password = "Csethi@4321"
totp = pyotp.TOTP("ELAC7LJCYC6ENWQBWNEGRGV66U").now()
print(totp)
obj = SmartConnect(api_key=api_key)
obj2 = obj.generateSession(user_id, password, totp)
print(obj2)

token = obj.generateToken(obj.generateSession(user_id, password, totp)["data"]["refreshToken"])
jwtToken = token['data']["jwtToken"]
refreshToken = token['data']['refreshToken']
feedToken = token['data']['feedToken']
# print(obj2)
# f_only = {"MARUTI-EQ": "10999", "LALPATHLAB-EQ": "11654", "IDFCFIRSTB-EQ": "11184", "CONCOR-EQ": "4749",
#           "PEL-EQ": "2412", "MUTHOOTFIN-EQ": "23650", "ESCORTS-EQ": "958", "PIDILITIND-EQ": "2664",
#           "JSWSTEEL-EQ": "11723", "ACC-EQ": "22", "SAIL-EQ": "2963", "ICICIPRULI-EQ": "18652", "GRASIM-EQ": "1232",
#           "ASTRAL-EQ": "14418", "BHARATFORG-EQ": "422", "ATUL-EQ": "263", "IPCALAB-EQ": "1633", "BEL-EQ": "383",
#           "PNB-EQ": "10666", "HDFCLIFE-EQ": "467", "NATIONALUM-EQ": "6364", "DELTACORP-EQ": "15044", "UPL-EQ": "11287",
#           "APOLLOHOSP-EQ": "157", "CIPLA-EQ": "694", "WHIRLPOOL-EQ": "18011", "DALBHARAT-EQ": "8075", "INFY-EQ": "1594",
#           "FEDERALBNK-EQ": "1023", "ALKEM-EQ": "11703", "AMBUJACEM-EQ": "1270", "TITAN-EQ": "3506",
#           "OBEROIRLTY-EQ": "20242", "CUMMINSIND-EQ": "1901", "NMDC-EQ": "15332", "SUNPHARMA-EQ": "3351",
#           "ADANIENT-EQ": "25", "LTTS-EQ": "18564", "PIIND-EQ": "24184", "CHOLAFIN-EQ": "685", "BHEL-EQ": "438",
#           "MFSL-EQ": "2142", "M&MFIN-EQ": "13285", "LUPIN-EQ": "10440", "GUJGASLTD-EQ": "10599", "SUNTV-EQ": "13404",
#           "ICICIGI-EQ": "21770", "STAR-EQ": "7374", "PVR-EQ": "13147", "GRANULES-EQ": "11872", "MCX-EQ": "31181",
#           "INDHOTEL-EQ": "1512", "SBICARD-EQ": "17971", "M&M-EQ": "2031", "PFIZER-EQ": "2643", "INDUSTOWER-EQ": "29135",
#           "VEDL-EQ": "3063", "BALKRISIND-EQ": "335", "SIEMENS-EQ": "3150", "HAVELLS-EQ": "9819", "DRREDDY-EQ": "881",
#           "BERGEPAINT-EQ": "404", "IOC-EQ": "1624", "LT-EQ": "11483", "BANKBARODA-EQ": "4668", "DABUR-EQ": "772",
#           "LAURUSLABS-EQ": "19234", "FSL-EQ": "14304", "TORNTPOWER-EQ": "13786", "GMRINFRA-EQ": "13528",
#           "MARICO-EQ": "4067", "INDIACEM-EQ": "1515", "EICHERMOT-EQ": "910", "BANDHANBNK-EQ": "2263",
#           "GODREJPROP-EQ": "17875", "BHARTIARTL-EQ": "10604", "BPCL-EQ": "526", "NAUKRI-EQ": "13751",
#           "HINDALCO-EQ": "1363", "ITC-EQ": "1660", "POLYCAB-EQ": "9590", "CADILAHC-EQ": "7929", "SBILIFE-EQ": "21808",
#           "DIXON-EQ": "21690", "HEROMOTOCO-EQ": "1348", "TATAPOWER-EQ": "3426", "ICICIBANK-EQ": "4963",
#           "SBIN-EQ": "3045", "HINDPETRO-EQ": "1406", "POWERGRID-EQ": "14977", "ABFRL-EQ": "30108",
#           "LICHSGFIN-EQ": "1997", "TRENT-EQ": "1964", "TVSMOTOR-EQ": "8479", "DIVISLAB-EQ": "10940",
#           "GODREJCP-EQ": "10099", "GAIL-EQ": "4717", "MINDTREE-EQ": "14356", "BAJAJFINSV-EQ": "16675",
#           "VOLTAS-EQ": "3718", "APLLTD-EQ": "25328", "DEEPAKNTR-EQ": "19943", "TATACONSUM-EQ": "3432",
#           "HINDUNILVR-EQ": "1394", "ULTRACEMCO-EQ": "11532", "ASIANPAINT-EQ": "236", "CANBK-EQ": "10794",
#           "EXIDEIND-EQ": "676", "IEX-EQ": "220", "JUBLFOOD-EQ": "18096", "CHAMBLFERT-EQ": "637", "HDFC-EQ": "1330",
#           "WIPRO-EQ": "3787", "L&TFH-EQ": "24948", "MOTHERSUMI-EQ": "4204", "INDUSINDBK-EQ": "5258",
#           "COLPAL-EQ": "15141", "CANFINHOME-EQ": "583", "HDFCAMC-EQ": "4244", "NTPC-EQ": "11630", "HAL-EQ": "2303",
#           "UBL-EQ": "16713", "SRF-EQ": "3273", "BRITANNIA-EQ": "547", "NESTLEIND-EQ": "17963", "TATAMOTORS-EQ": "3456",
#           "BAJFINANCE-EQ": "317", "OFSS-EQ": "10738", "JKCEMENT-EQ": "13270", "TORNTPHARM-EQ": "3518",
#           "INDIGO-EQ": "11195", "PFC-EQ": "14299", "PAGEIND-EQ": "14413", "CUB-EQ": "5701", "MANAPPURAM-EQ": "19061",
#           "LTI-EQ": "17818", "AUBANK-EQ": "21238", "MRF-EQ": "2277", "COFORGE-EQ": "11543", "METROPOLIS-EQ": "9581",
#           "TATACHEM-EQ": "3405", "BOSCHLTD-EQ": "2181", "IBULHSGFIN-EQ": "30125", "RAMCOCEM-EQ": "2043",
#           "ZEEL-EQ": "3812", "SYNGENE-EQ": "10243", "RECLTD-EQ": "15355", "TATASTEEL-EQ": "3499",
#           "COROMANDEL-EQ": "739", "CROMPTON-EQ": "17094", "AUROPHARMA-EQ": "275", "AXISBANK-EQ": "5900",
#           "RBLBANK-EQ": "18391", "PETRONET-EQ": "11351", "JINDALSTEL-EQ": "6733", "GLENMARK-EQ": "7406",
#           "KOTAKBANK-EQ": "1922", "GSPL-EQ": "13197", "ADANIPORTS-EQ": "15083", "COALINDIA-EQ": "20374",
#           "AMARAJABAT-EQ": "100", "TCS-EQ": "11536", "ONGC-EQ": "2475", "APOLLOTYRE-EQ": "163", "BIOCON-EQ": "11373",
#           "PERSISTENT-EQ": "18365", "DLF-EQ": "14732", "SRTRANSFIN-EQ": "4306", "MPHASIS-EQ": "4503",
#           "NAVINFLUOR-EQ": "14672", "INDIAMART-EQ": "10726", "MGL-EQ": "17534", "IRCTC-EQ": "13611", "IGL-EQ": "11262",
#           "BSOFT-EQ": "6994", "BATAINDIA-EQ": "371", "HCLTECH-EQ": "7229", "SHREECEM-EQ": "3103", "RELIANCE-EQ": "2885",
#           "HDFCBANK-EQ": "1333", "TECHM-EQ": "13538", "ASHOKLEY-EQ": "212"}


# nifty 50 stocks only

f_only = {
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
};

exchange = "NSE"
traded_list = []
invest_per_trade = 3000


def GettingLtpData():
    while True:
        for symbol, token in f_only.items():
            LTP = obj.ltpData(exchange, symbol, token)
            #             print(LTP["data"]["open"],"-----------ltp")
            high = LTP["data"]["high"]
            low = LTP["data"]["low"]
            ltp = LTP["data"]["ltp"]
            openTrade = LTP["data"]["open"]
            quantity = int(invest_per_trade / ltp)
            # print(f"Scirpt:{symbol}, High:{high}, Low:{low}, LTP:{ltp},openTrade:{openTrade}")
            if ltp == openTrade + 5:
                print(openTrade)
                traded_list.append(symbol)
                orderparams1 = {"variety": "NORMAL", "tradingsymbol": symbol, "symboltoken": token,
                                "transactiontype": "BUY", "exchange": exchange, "ordertype": "LIMIT",
                                "producttype": "INTRADAY", "duration": "DAY", "price": ltp, "squareoff": "0",
                                "stoploss": "0", "quantity": quantity}
                #                 orderId1=obj.placeOrder(orderparams1)
                print(f"Buy order Place for {symbol} at : {datetime.datetime.now()} with Order id {orderId1}{ltp}")
            if ltp == openTrade - 5:
                traded_list.append(symbol)  # "HDFCBANK-EQ": "1333""HDFCBANK-EQ": "1333","TCS-EQ": "11536","AXISBANK-EQ": "5900","JSWSTEEL-EQ": "11723","PIDILITIND-EQ": "2664"
                orderparams2 = {"variety": "NORMAL", "tradingsymbol": symbol, "symboltoken": token,
                                "transactiontype": "SELL", "exchange": exchange, "ordertype": "LIMIT",
                                "producttype": "INTRADAY", "duration": "DAY", "price": ltp, "squareoff": "0",
                                "stoploss": "0", "quantity": quantity}
                #                 orderId2=obj.placeOrder(orderparams2)
                print(f"Sell order Place for {symbol} at : {datetime.datetime.now()} with Order id {orderId2}")


orderplacetime = int(9) * 60 + int(20)
timenow = (datetime.datetime.now().hour * 60 + datetime.datetime.now().minute)
print("Waiting for 9.20 AM , CURRENT TIME:{}".format(datetime.datetime.now()))

while timenow < orderplacetime:
    time.sleep(0.5)
    timenow = (datetime.datetime.now().hour * 60 + datetime.datetime.now().minute)
print("Ready for Trading , CURRENT TIME:{}".format(datetime.datetime.now()))

try:
    GettingLtpData()
except Exception as e:
    raise e