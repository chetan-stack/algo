import schedule
from SmartApi import SmartConnect  # or from SmartApi.smartConnect import SmartConnect
import time
from datetime import datetime
import datetime
import pyotp
import document
import stock_token_list
import crete_update_table

api_key = document.api_key
user_id = document.user_id
password = document.password
totp = pyotp.TOTP(document.totp).now()
obj = SmartConnect(api_key=api_key)
token = obj.generateToken(obj.generateSession(user_id, password, totp)["data"]["refreshToken"])

def placeorder(token, symbol, qty, exch_seg, buy_sell, ordertype, price, orderprice):
    orderparams = {
        "variety": "NORMAL",
        "tradingsymbol": symbol,
        "symboltoken": token,
        "transactiontype": buy_sell,
        "exchange": exch_seg,
        "ordertype": ordertype,
        "producttype": "INTRADAY",
        "duration": "DAY",
        "squareoff": "0",
        "stoploss": "0",
        "quantity": 1,
        'price': price
    }

    orderId = 1
    #orderId = obj.placeOrder(orderparams)
    # print(orderId)
    return orderId

# place_order(pe_symbol['token'], pe_symbol['symbol'], pe_symbol['lotsize'], 'NFO', 'BUY',
#                                             'MARKET', 0, df.close.values[-1])

def getpenddingorderdata():
    date = datetime.date.today()
    fetchdata = crete_update_table.fetchsupportforweb()
    for item in fetchdata:
        if item['createddate']:
            datetime_obj = item['createddate'].split(" ")
            if item['createddate'] and datetime_obj[0] == str(date):
                placeorder(item['token'], item['symbol'], item['lotsize'], item['exchange'], buy_sell, ordertype, price, orderprice)
                print(item)

# getpenddingorderdata()
