import pyotp
import time
from smartapi import SmartConnect
from datetime import datetime
import datetime

api_key = "pMZtYR5S"
user_id = "c182721"
password = "Csethi@4321"
totp = pyotp.TOTP("ELAC7LJCYC6ENWQBWNEGRGV66U").now()
obj = SmartConnect(api_key=api_key)
obj2 = obj.generateSession(user_id, password, totp)
# print(obj2)
stoploss = 0
targetprice = 0
stoploss = 0
targetprice = 0
traded_list = []
getposition = obj.position()
# print(getposition['data'])


def place_order(symbol, token, transactiontype, exchange, producttype, qty):
    orderparams = {
        "variety": "NORMAL",
        "tradingsymbol": symbol,
        "symboltoken": token,
        "transactiontype": transactiontype,
        "exchange": exchange,
        "ordertype": "MARKET",
        "producttype": producttype,
        "duration": "DAY",
        "price": "0",
        "squareoff": "0",
        "stoploss": "0",
        "quantity": qty
    }
    place = obj.placeOrder(orderparams)
    print(place)

def ExitOrder():
    while True:
        for a in getposition['data']:
            LTP = obj.ltpData(a["exchange"], a["tradingsymbol"], a["symboltoken"])
            getprice = a["avgnetprice"]
            getltp = LTP["data"]["ltp"]
            getopen = LTP["data"]["open"]
            getClose = LTP["data"]["close"]
            pnl = a['pnl']
            # getaverage = LTP["data"]["averageprice"]
            # print(a)
            #if p and l shows 200 loss than than exit
            if (int(float(pnl)) <= -200) and (a["tradingsymbol"] not in traded_list):
                print('start programe')
                traded_list.append(a["tradingsymbol"])
                transactionType = "SELL" if int(a['netqty']) > 0 else "BUY"
                # place_order(a["tradingsymbol"], a["symboltoken"], transactionType, a["exchange"], a["producttype"],
                #                     abs(int(a["netqty"])))

            if (int(float(pnl)) >= 500) and (a["tradingsymbol"] not in traded_list):
                print('start programe')
                traded_list.append(a["tradingsymbol"])
                transactionType = "SELL" if int(a['netqty']) > 0 else "BUY"
                # place_order(a["tradingsymbol"], a["symboltoken"], transactionType, a["exchange"], a["producttype"],
                #                     abs(int(a["netqty"])))
            time.sleep(2)


orderplacetime = int(9) * 60 + int(20)
timenow = (datetime.datetime.now().hour * 60 + datetime.datetime.now().minute)
print("Waiting for 9.20 AM , CURRENT TIME:{}".format(datetime.datetime.now()))

while timenow < orderplacetime:
    time.sleep(0.2)
    timenow = (datetime.datetime.now().hour * 60 + datetime.datetime.now().minute)
print("Ready for Trading , CURRENT TIME:{}".format(datetime.datetime.now()))

try:
    ExitOrder()
except Exception as e:
    raise e