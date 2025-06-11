import datetime
import threading
import time

import schedule
import xlwings as xw

import requests

from SmartApi.smartWebSocketV2 import SmartWebSocketV2
from logzero import logger
import pyotp
import document
from SmartApi import SmartConnect #or from SmartApi.smartConnect import SmartConnect
import crete_update_table


api_key = document.api_key
user_id = document.user_id
password = document.password
totp = pyotp.TOTP(document.totp).now()
obj = SmartConnect(api_key=api_key)
token = obj.generateToken(obj.generateSession(user_id, password, totp)["data"]["refreshToken"])

AUTH_TOKEN = token["data"]["jwtToken"]
API_KEY = api_key
CLIENT_CODE = user_id
FEED_TOKEN = obj.getfeedToken()


correlation_id = "abc123"
action = 1
mode = 1


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


def insialisetoken():
    print('start')
    global token_list
    global getbook
    getbook = crete_update_table.fetchtokennbook()
    store = []
    for item in getbook:
        if item is not None:
            if item['lotsize'] > 0:
               store.append(item['token'])
    result = [{
         "exchangeType": 1,
         "tokens": store
    }]
    # sws.on_open = on_open
    return result
#
# token_list = insialisetoken()
# print(token_list)


# token_list = [
#     {
#         "exchangeType": 2,
#         "tokens": ["39663"]
#     },
#     {
#         "exchangeType": 2,
#         "tokens": ["54955"]
#     },
#
# ]
# token_list1 = [
#     {
#         "exchangeType": 5,
#         "tokens": ["244999"]
#     }
# ]

sws = SmartWebSocketV2(AUTH_TOKEN, API_KEY, CLIENT_CODE, FEED_TOKEN)
print(sws)
def on_data(wsapp, message):
    # logger.info("Ticks: {}".format(message))
    print(message)
    formatdata(message)
    # close_connection()


def onunsubscribe():
    print('____________________________unscribe________________')
    token_list = insialisetoken()
    sws.unsubscribe(correlation_id, mode, token_list)
    # time.sleep(2)
    print('______token list______',token_list)
    sws.subscribe(correlation_id, mode, token_list)

def on_open(wsapp):
    logger.info("on open")
    token_list = insialisetoken()
    print('token list',token_list)
    sws.subscribe(correlation_id, mode, token_list)
    # sws.unsubscribe(correlation_id, mode, token_list1)


def on_error(wsapp, error):
    logger.error(error)


def on_close(wsapp):
    logger.info("Close")



def close_connection():
    sws.close_connection()



def formatdata(data):
    # print(data)
    # print(data['last_traded_price']/100)
    ltp = data['last_traded_price']/100
    getbook = crete_update_table.fetchtokennbook()
    filtertoken = [token for token in getbook if token['token'] == data['token'] and token['lotsize'] > 0]
    # print(len(filtertoken),filtertoken)
    #wb = xw.Book("angel_excel.xlsx")
    #st = wb.sheets('nifty')
    #st.range('A1').value = getbook


    if len(filtertoken) > 0:
        # print('check condition',filtertoken[0])
        getdata = filtertoken[0]
        filterdbuyltp = getdata['ltp']
        buylotsize = getdata['lotsize']
        max_price_achieved = filterdbuyltp
        max_price_achieved = exitontarget(ltp, filterdbuyltp, buylotsize,getdata['script'],getdata['id'], max_price_achieved)

        # exitontarget(ltp,filterdbuyltp,buylotsize,getdata['script'],getdata['id'])






# Trailing stop loss code:
def exitontarget(ltp, buyprice, lotsize, symbol, id, max_price_achieved):
    date = datetime.datetime.now()
    # Update the max price achieved if the current LTP is higher
    max_price_achieved = max(max_price_achieved, ltp)
    # Trailing stop: 5% below the highest price achieved
    trailing_stoploss_price = max_price_achieved * 0.95

    # Fixed target price: 20% above the buyprice
    target_price = buyprice * 1.3


    # Determine the status based on trailing stoploss and target
    if ltp <= trailing_stoploss_price:
        status = "Trailing Stoploss hit"
        profit_or_loss = (ltp - buyprice) * lotsize
        profitorder = f'Time : {date} - Symbol : {symbol} Exit Price : {ltp} - Buy price : {buyprice} - "trailing_stoploss_price": {trailing_stoploss_price},target_price : {target_price} - max_price_achieved : {max_price_achieved} - profit : {profit_or_loss}'
        crete_update_table.updateorderplace(id, 0, profitorder)
        sendAlert(profitorder)

    elif ltp >= target_price:
        status = "Target hit"
        profit_or_loss = (ltp - buyprice) * lotsize
        profitorder = f'Time : {date} - Symbol : {symbol} Exit Price : {ltp} - Buy price : {buyprice} - "trailing_stoploss_price": {trailing_stoploss_price},target_price : {target_price} - max_price_achieved : {max_price_achieved} - profit : {profit_or_loss}'
        # trailing_stoploss_price = target_price * 0.95
        crete_update_table.updateorderplace(id, 0, profitorder)
        sendAlert(profitorder)

    else:
        status = "In trade"
        profit_or_loss = (ltp - buyprice) * lotsize

    # profitorder = f'Time : {date} - Symbol : {symbol} Exit Price : {ltp} - Buy price : {buyprice} - "trailing_stoploss_price": {trailing_stoploss_price},target_price : {target_price} - max_price_achieved : {max_price_achieved} - profit : {profit_or_loss}'
    # crete_update_table.updateorderplace(id, lotsize, profitorder)

    alert = {
        "symbol": symbol,
        "status": status,
        "ltp": ltp,
        "buyprice": buyprice,
        "trailing_stoploss_price": trailing_stoploss_price,
        "target_price": target_price,
        "profit_or_loss": profit_or_loss,
        "max_price_achieved": max_price_achieved
    }
    storedata = crete_update_table.fetchtokennbook()
    # wb = xsw.Book("angel_excel.xlsx")
    # st = wb.sheets('nifty')
    # st.range('A1').value = storedata

    # Print or log the alert
    # print(alert)

    # Return the updated max price achieved for future reference
    return max_price_achieved



# def exitontarget(ltp,buyprice,lotsize,symbol,id):
#     # print('get')
#     date = datetime.datetime.now()
#     stoploss_price = buyprice * 0.9  # 10% below the buyprice
#     target_price = buyprice * 1.2    # 20% above the buyprice
#
#     # Determine the status
#     if ltp <= stoploss_price:
#         status = "Stoploss hit"
#         profit_or_loss = (ltp - buyprice) * lotsize
#         profitorder = f'Ltp {ltp} - Buyprice : {buyprice} profit - {profit_or_loss}'
#         crete_update_table.updateorderplace(id,0,profitorder)
#         profitorder = f'Time : {date} - Symbol : {symbol} Exit Price : {ltp} - Buy price : {buyprice} - profit : {profit_or_loss}'
#         sendAlert(profitorder)
#
#     elif ltp >= target_price:
#         status = "Target hit"
#         profit_or_loss = (ltp - buyprice) * lotsize
#         profitorder = f'Ltp {ltp} - Buyprice : {buyprice} profit - {profit_or_loss}'
#         crete_update_table.updateorderplace(id,0,profitorder)
#         profitorder = f'Time : {date} - Symbol : {symbol} Exit Price : {ltp} - Buy price : {buyprice} - profit : {profit_or_loss}'
#         sendAlert(profitorder)
#     else:
#         status = "In trade"
#         profit_or_loss = (ltp - buyprice) * lotsize
#
#     alert = {
#         "symbol":symbol,
#         "status": status,
#         "ltp": ltp,
#         "buyprice": buyprice,
#         "stoploss_price": stoploss_price,
#         "target_price": target_price,
#         "profit_or_loss": profit_or_loss,
#
#     }
#     print(alert)

def websocket_thread():
    sws.connect()

# Assign the callbacks.
sws.on_open = on_open
sws.on_data = on_data
sws.on_error = on_error
sws.on_close = on_close
# sws.connect()


thread = threading.Thread(websocket_thread())
thread.start()
print("________________sunscibe__________________")
# time.sleep(5)
# sws.unsubscribe(correlation_id, mode, token_list1)
#
# print('____________________subscribe___________________')
# sws.subscribe(correlation_id, mode, token_list)
# time.sleep(10)
# print('____________________unsubscribe___________________')
# sws.unsubscribe(correlation_id, mode, token_list)
# time.sleep(2)
# sws.close_connection()

# schedule.every(5).seconds.do(onunsubscribe)

# while True:
#     # print("start tym , CURRENT TIME:{}".format(datetime.datetime.now()))
#     try:
#         schedule.run_pending()
#         time.sleep(2)
#     except Exception as e:
#         raise e
