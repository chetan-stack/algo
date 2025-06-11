import datetime
import threading
import time
import requests
import schedule

from SmartApi.smartWebSocketV2 import SmartWebSocketV2
from logzero import logger
import pyotp
import document
from SmartApi import SmartConnect  # or from SmartApi.smartConnect import SmartConnect
import crete_update_table

# Initialize API connection
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


def insialisetoken():
    print('start')
    global token_list
    global getbook
    getbook = crete_update_table.fetchsupport()
    store = []
    for item in getbook:
        if item is not None:
            if item['lotsize'] > 0 and "Stock" in item['script']:
               store.append(item['token'])
    result = [{
         "exchangeType": 1,
         "tokens": store
    }]
    # sws.on_open = on_open

    return result

token_list = insialisetoken()
# print(token_list)

def sendAlert(bot_message):
    get_message = format(bot_message)
    print(get_message)

    bot_token = "5707293106:AAEPkxexnIdoUxF5r7hpCRS_6CHINgU4HTw"
    bot_chatid = "2027669179"
    send_message = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={bot_chatid}&parse_mode=MarkdownV2&text={bot_message}"

    response = requests.post(f'https://api.telegram.org/bot{bot_token}/sendMessage',
                             data={'chat_id': bot_chatid, 'text': bot_message})

    print(response)
    return response.json()

storedata = []
storedata.append("58438")
# token_list = [{"exchangeType": 2, "tokens": storedata}]
token_list1 = [{'exchangeType': 2, 'tokens': ['58447']}]


sws = SmartWebSocketV2(AUTH_TOKEN, API_KEY, CLIENT_CODE, FEED_TOKEN)

def on_data(wsapp, message):
    # logger.info("Ticks: {}".format(message))
    print(message)
    formatdata(message)


def on_open(wsapp):
    logger.info("on open")
    token_list = insialisetoken()
    print('token list',token_list)
    sws.subscribe(correlation_id, mode, token_list)

def on_error(wsapp, error):
    logger.error(error)

def on_close(wsapp):
    logger.info("Close")

def close_connection():
    sws.close_connection()

def onunsubscribe():
    print('____________________________unscribe________________')
    token_list = insialisetoken()
    # sws.unsubscribe(correlation_id, mode, token_list)
    # time.sleep(2)
    print("__________unsubscribe_______________")
    # token_list1 = [{"exchangeType": 5, "tokens": ["437994","429116","426308"]}]

    sws.subscribe(correlation_id, mode, token_list)

def formatdata(data):
    # print(data['last_traded_price']/100)
    ltp = data['last_traded_price']/100
    # print('ltp',ltp)
    getbook = crete_update_table.fetchsupport()
    filtertoken = [token for token in getbook if token['token'] == data['token'] and token['lotsize'] > 0 and 'Stock'in token['script']]
    print(len(filtertoken),filtertoken)
    #wb = xw.Book("angel_excel.xlsx")
    #st = wb.sheets('nifty')
    #st.range('A1').value = getbook


    if len(filtertoken) > 0:
        # print('check condition',filtertoken[0])
        getdata = filtertoken[0]
        filterdbuyltp = getdata['ltp']
        buylotsize = getdata['lotsize']
        max_price_achieved = filterdbuyltp
        # max_price_achieved = exitontarget(ltp, filterdbuyltp, buylotsize,getdata['script'],getdata['id'], max_price_achieved)

        # exitontarget(ltp,filterdbuyltp,buylotsize,getdata['script'],getdata['id'],max_price_achieved)

        targetprice = filterdbuyltp * 1.01
        stolossprice = filterdbuyltp * 0.995
        targetprice,stolossprice = exitontarget(ltp, filterdbuyltp, buylotsize,getdata['script'],getdata['id'],targetprice, stolossprice)


def exitontarget(ltp, buyprice, lotsize, symbol, id, targetprice,stolossprice):
    date = datetime.datetime.now()
      # Update the max price achieved if the current LTP is higher
    print('data')

    # Determine the status based on trailing stoploss and target
    if ltp >= targetprice:
        targetprice = ltp * 1.01
        stolossprice = ltp * 0.995

    elif ltp <= stolossprice:
        status = "Trailing Stoploss hit"
        profit_or_loss = (ltp - buyprice) * lotsize
        profitorder = f'Time : {date} - Symbol : {symbol} Exit Price : {ltp} - Buy price : {buyprice} - "trailing_stoploss_price": {stolossprice},target_price : {targetprice} - max_price_achieved : {targetprice} - profit : {profit_or_loss}'
        crete_update_table.updateorderplace(id, 0, profitorder)
        sendAlert(profitorder)

    else:
        status = "In trade"
        profit_or_loss = (ltp - buyprice) * lotsize




    alert = {
        "symbol": symbol,
        "status": status,
        "ltp": ltp,
        "buyprice": buyprice,
        "trailing_stoploss_price": stolossprice,
        "target_price": targetprice,
        "profit_or_loss": profit_or_loss,
    }

    print(alert)

    # Return the updated max price achieved for future reference
    return targetprice,stolossprice

# Trailing stop loss code:
# def exitontarget(ltp, buyprice, lotsize, symbol, id, max_price_achieved):
#     date = datetime.datetime.now()
#     # Update the max price achieved if the current LTP is higher
#     max_price_achieved = max(max_price_achieved, ltp)
#     # Trailing stop: 5% below the highest price achieved
#     trailing_stoploss_price = max_price_achieved * 0.95
#
#     # Fixed target price: 20% above the buyprice
#     target_price = buyprice * 1.3
#
#
#     # Determine the status based on trailing stoploss and target
#     if ltp <= trailing_stoploss_price:
#         status = "Trailing Stoploss hit"
#         profit_or_loss = (ltp - buyprice) * lotsize
#         profitorder = f'Time : {date} - Symbol : {symbol} Exit Price : {ltp} - Buy price : {buyprice} - "trailing_stoploss_price": {trailing_stoploss_price},target_price : {target_price} - max_price_achieved : {max_price_achieved} - profit : {profit_or_loss}'
#         crete_update_table.updateorderplace(id, 0, profitorder)
#         sendAlert(profitorder)
#
#     elif ltp >= target_price:
#         status = "Target hit"
#         profit_or_loss = (ltp - buyprice) * lotsize
#         profitorder = f'Time : {date} - Symbol : {symbol} Exit Price : {ltp} - Buy price : {buyprice} - "trailing_stoploss_price": {trailing_stoploss_price},target_price : {target_price} - max_price_achieved : {max_price_achieved} - profit : {profit_or_loss}'
#         crete_update_table.updateorderplace(id, 0, profitorder)
#         sendAlert(profitorder)
#
#     else:
#         status = "In trade"
#         profit_or_loss = (ltp - buyprice) * lotsize
#
#
#
#
#     alert = {
#         "symbol": symbol,
#         "status": status,
#         "ltp": ltp,
#         "buyprice": buyprice,
#         "trailing_stoploss_price": trailing_stoploss_price,
#         "target_price": target_price,
#         "profit_or_loss": profit_or_loss,
#         "max_price_achieved": max_price_achieved
#     }
#
#     print(alert)
#
#     # Return the updated max price achieved for future reference
#     return max_price_achieved

def websocket_thread():
    sws.connect()

# Assign the callbacks
sws.on_open = on_open
sws.on_data = on_data
sws.on_error = on_error
sws.on_close = on_close

# sws.connect()
# Start WebSocket connection in a separate thread

thread = threading.Thread(target=websocket_thread)
thread.start()

print('2____________________subscribe___________________')
# time.sleep(10)
# print('3____________________subscribe___________________')
# sws.unsubscribe(correlation_id, mode, token_list)
# storedata.append("36740")
# sws.subscribe(correlation_id, mode, token_list)
#
#
# token_list2 = [{"exchangeType": 2, "tokens": ["36740"]}]
# sws.subscribe(correlation_id, mode, token_list2)
#
# time.sleep(5)
# sws.unsubscribe(correlation_id, mode, token_list)
# time.sleep(10)
# print('4____________________subscribe___________________')
# sws.subscribe(correlation_id, mode, token_list1)
schedule.every(5).seconds.do(onunsubscribe)
# schedule.every().day.at("15:15").do(on_close)

while True:
    # print("start tym , CURRENT TIME:{}".format(datetime.datetime.now()))
    try:
        schedule.run_pending()
        time.sleep(5)
    except Exception as e:
        raise e


# Optionally, join the thread if you want to wait for it to complete
# thread.join()


