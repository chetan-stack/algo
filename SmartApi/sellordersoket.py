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
timecomplete = False
storetarget = []



def insialisetoken():
    print('start')
    global token_list
    global getbook
    getbook = crete_update_table.fetchsupport()
    store = []
    for item in getbook:
        if item is not None:
            if "CE" in item['script'] or "PE" in item['script']:
               if item['lotsize'] > 0 or item['lotsize'] < 0:
                store.append(item['token'])
    result = [{
         "exchangeType": 2,
         "tokens": store
    }]
    # sws.on_open = on_open
    print(result)
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
storebuypriceltp = 0

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


def check_headage_data(data,token):
    print('start',token)
    for item in data:
        # Check if lotsize is not '0'
        if str(item['lotsize']) != '0':
            # Remove .0 from profit if it's a string and compare with token
            profit_str = str(item['profit'])
            if profit_str != '0.0' and profit_str.endswith('.0'):
                profit_str = profit_str.replace('.0', '')
                print(profit_str,token)
            # Check if token matches profit
            if profit_str == token:
                print('token')
                return item
    return None

def creatdatatostore(data,checktoken):
    if checktoken != '0.0':
        print('check 1',checktoken)
        checktoken = str(checktoken).replace('.0', '')
        for item in data:
            if item['lotsize'] < 0:
                if item['profit'] == checktoken:
                    return item
    return None

def formatdata(data):
    # print(data['last_traded_price']/100)
    ltp = data['last_traded_price']/100
    # print('ltp',ltp)
    getbook = crete_update_table.fetchsupport()
    filtertoken = [token for token in getbook if token['token'] == data['token'] and str(token['lotsize']) != '0']
    print(len(filtertoken),filtertoken)
    # print('get book',filtertoken)
    #wb = xw.Book("angel_excel.xlsx")
    #st = wb.sheets('nifty')
    #st.range('A1').value = getbook


    if len(filtertoken) > 0:
        getdata = filtertoken[-1]
        if getdata['lotsize'] < 0:
            headgetoken = check_headage_data(getbook,getdata['token'])
            print('headgetoken',headgetoken)
            # print('check condition',filtertoken[0])
            filterdbuyltp = getdata['ltp']
            buylotsize = getdata['lotsize']
            symbol = getdata['script']
            id = getdata['id']
            max_price_achieved = filterdbuyltp
            getstoredata = [item for item in storetarget if item['symbol'] == symbol]
            if len(getstoredata) == 0:
                data = {
                "symbol": symbol,
                'targetprice' : filterdbuyltp * 0.90,
                'stolossprice' : filterdbuyltp * 1.10
                }
                storetarget.append(data)
            exitontarget(ltp, filterdbuyltp, buylotsize, symbol, id,headgetoken)

        elif getdata['lotsize'] > 0:
            filterdbuyltp = getdata['ltp']
            buylotsize = getdata['lotsize']
            symbol = getdata['script']
            id = getdata['id']
            global storebuypriceltp
            storebuypriceltp = ltp
            print('storedltp',storebuypriceltp)
            checkdata = check_headage_data(getbook,getdata['token'])
            print('checkdata',checkdata)
            # if checkdata != None:
            #
            # else:
            #     getstoredata = [item for item in storetarget if item['symbol'] == symbol]
            #     if len(getstoredata) == 0:
            #         data = {
            #         "symbol": symbol,
            #         'targetprice' : filterdbuyltp * 1.05,
            #         'stolossprice' : filterdbuyltp * 0.97
            #         }
            #         storetarget.append(data)
            #     # exitontargetbuy(ltp, filterdbuyltp, buylotsize, symbol, id)


# Define the exitontarget function
def exitontarget(ltp, buyprice, lotsize, symbol, id,headgebuy):
    # print('ceheck',headgebuy)
    lotsize = abs(lotsize)
    date = datetime.datetime.now()
    getvale = next((item for item in storetarget if item['symbol'] == symbol), None)
    index_to_update = next((index for index, item in enumerate(storetarget) if item['symbol'] == symbol), None)
    if getvale:
        targetprice = getvale['targetprice']
        stolossprice = getvale['stolossprice']
    else:
        print('Error : symbol missing')
    # Print the current target and stoploss prices
    print('buy : ',buyprice,'ltp :',ltp,'Current target price:', targetprice, 'Current stoploss price:', stolossprice)
    print('headbuy : ',headgebuy['ltp'],'ltp :',storebuypriceltp)


    if ltp <= targetprice:
        status = "Trailing Target"
        profit_or_loss = (buyprice - ltp) * lotsize
        storetarget[index_to_update]['targetprice'] = ltp * 0.95
        storetarget[index_to_update]['stolossprice'] = ltp * 1.05

    elif ltp >= stolossprice:
        status = "Trailing Stoploss hit"
        headageprofit = (headgebuy['ltp'] - storebuypriceltp) * headgebuy['lotsize']
        profit_or_loss = ((buyprice - ltp) * lotsize)
        profitorder = f'Time: {date} - Symbol: {symbol} - lot: {lotsize} - Exit Price: {ltp} - Buy Price: {buyprice} - Trailing Stoploss Price: {stolossprice} - Target Price: {targetprice} - Profit/Loss: {profit_or_loss} - storebuypriceltp {storebuypriceltp} hdprofit{headageprofit}'
        crete_update_table.updateorderplace(id, 0, profitorder)
        crete_update_table.updateorderplace(headgebuy['id'], 0, headageprofit)
        sendAlert(profitorder)
        del storetarget[index_to_update]

    else:
        status = "In trade"
        headageprofit = (storebuypriceltp -headgebuy['ltp']) * headgebuy['lotsize']
        profit_or_loss = ((buyprice - ltp) * lotsize)
        print('profit for sell trade',profit_or_loss,headageprofit)
    # Create an alert dictionary to print
    # alert = {
    #     "symbol": symbol,
    #     "status": status,
    #     "ltp": ltp,
    #     "buyprice": buyprice,
    #     "trailing_stoploss_price": stolossprice,
    #     "target_price": targetprice,
    #     "profit_or_loss": profit_or_loss
    # }
    #
    # print(alert)



def exitontargetbuy(ltp, buyprice, lotsize, symbol, id):
    date = datetime.datetime.now()
    getvale = next((item for item in storetarget if item['symbol'] == symbol), None)
    index_to_update = next((index for index, item in enumerate(storetarget) if item['symbol'] == symbol), None)
    if getvale:
        targetprice = getvale['targetprice']
        stolossprice = getvale['stolossprice']
    else:
        print('Error : symbol missing')
    # Print the current target and stoploss prices
    print('symbol:',symbol,'buy:',buyprice,'ltp :',ltp,'Current target price:', targetprice, 'Current stoploss price:', stolossprice)


    if ltp >= targetprice:
        status = "Trailing Target"
        profit_or_loss = (ltp - buyprice) * lotsize
        storetarget[index_to_update]['targetprice'] = ltp * 1.05
        storetarget[index_to_update]['stolossprice'] = ltp * 0.995

    elif ltp <= stolossprice:
        status = "Trailing Stoploss hit"
        profit_or_loss = (ltp - buyprice) * lotsize
        profitorder = f'Time: {date} - Symbol: {symbol} - lot: {lotsize} Exit Price: {ltp} - Buy Price: {buyprice} - Trailing Stoploss Price: {stolossprice} - Target Price: {targetprice} - Profit/Loss: {profit_or_loss}'
        crete_update_table.updateorderplace(id, 0, profitorder)
        sendAlert(profitorder)
        del storetarget[index_to_update]

    else:
        status = "In trade"
        profit_or_loss = (ltp - buyprice) * lotsize
        print('profit for buy trade',profit_or_loss)
    # Create an alert dictionary to print
    # alert = {
    #     "symbol": symbol,
    #     "status": status,
    #     "ltp": ltp,
    #     "buyprice": buyprice,
    #     "trailing_stoploss_price": stolossprice,
    #     "target_price": targetprice,
    #     "profit_or_loss": profit_or_loss
    # }
    #
    # print(alert)


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

def set_timecomplete():
    global timecomplete
    timecomplete = True
    print("Time is complete!")

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
schedule.every().day.at("15:25").do(set_timecomplete)

while True:
    # print("start tym , CURRENT TIME:{}".format(datetime.datetime.now()))
    try:
        schedule.run_pending()
        time.sleep(5)
    except Exception as e:
        raise e


# Optionally, join the thread if you want to wait for it to complete
# thread.join()


