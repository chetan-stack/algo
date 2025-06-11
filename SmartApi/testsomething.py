import datetime
import json
import re
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
maxprofit = []
nsechange = {
    'NIFTY':2,
    'BANKNIFTY':2,
    'SENSEX':4
}
DATA_FILE = "auto_trade.json"  # File to store form data
# Function to load stored data
def load_data():
      # File to store form data
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)  # Read existing data
        # print(json.load(file))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}  # Return empty if file not found or corrupted

def insialisetoken():
    print('start')
    global token_list
    global getbook
    getbook = crete_update_table.fetchsupport()
    store = []

    for item in getbook:
        if item is not None:
            if "CE" in item['script'] or "PE" in item['script']:
               if item['lotsize'] > 0:
                   match = re.match(r"^[A-Za-z]+", item['script'])
                   first_string = match.group() if match else None
                   storedata = { "exchangeType": nsechange[first_string],
                             "tokens": [item['token']]
                                }
                   store.append(storedata)
                   # store.append(item['token'])
    result = [{
         "exchangeType": 2,
         "tokens": [74819]
    }]
    # sws.on_open = on_open
    # print(result)
    return store

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

def check_headage_data(data,token):
    tokenignore = []
    for item in data:
        # Check if lotsize is not '0'
        if str(item['lotsize']) != '0':
            # Remove .0 from profit if it's a string and compare with token
            profit_str = str(item['profit'])
            if profit_str != '0.0' and profit_str.endswith('.0'):
                profit_str = profit_str.replace('.0', '')
                tokenignore.append(item['token'])
            # Check if token matches profit
    return tokenignore


def formatdata(data):
    # print(data['last_traded_price']/100)
    ltp = data['last_traded_price']/100
    # print('ltp',ltp)
    getbook = crete_update_table.fetchsupport()
    ignoretoke = check_headage_data(getbook,data['token'])
    print('ignore token',ignoretoke)
    filtertoken = [token for token in getbook if token['token'] == data['token'] and token['lotsize'] > 0 and token['token'] not in ignoretoke]
    print(len(filtertoken),filtertoken)
    #wb = xw.Book("angel_excel.xlsx")
    #st = wb.sheets('nifty')
    #st.range('A1').value = getbook


    if len(filtertoken) > 0:
        # print('check condition',filtertoken[0])
        getdata = filtertoken[-1]
        filterdbuyltp = getdata['ltp']
        buylotsize = getdata['lotsize']
        symbol = getdata['script']
        id = getdata['id']
        max_price_achieved = filterdbuyltp
        # max_price_achieved = exitontarget(ltp, filterdbuyltp, buylotsize,getdata['script'],getdata['id'], max_price_achieved)

        # exitontarget(ltp,filterdbuyltp,buylotsize,getdata['script'],getdata['id'],max_price_achieved)

        # targetprice = filterdbuyltp * 1.05
        # stolossprice = filterdbuyltp * 0.97
        # targetprice,stolossprice = exitontarget(ltp, filterdbuyltp, buylotsize,getdata['script'],getdata['id'],targetprice, stolossprice)
        # if getdata['token'] == int(float(getdata['token'])):
        #     print('no target for  this token',symbol)
        # else:

        getstoredata = [item for item in storetarget if item['symbol'] == symbol]
        loaddata = load_data()
        loadstore = loaddata['store']
        match = re.match(r"^[A-Za-z]+", symbol)
        first_string = match.group() if match else None
        # print("check---------------",loadstore)
        # print(loaddata)
        filterloaddata = [item for item in loadstore if item['symbol'] == first_string]
        # print("niwchek-----",filterloaddata)
        target_points = int(loaddata['target_points'])
        stoploss_points = int(loaddata['loss_points'])
        min_change = int(loaddata['trade_range_min'])
        max_change = int(loaddata['trade_range_max'])
        gettrend = filterloaddata[0]['trend']


        #atr get and set target
        atrtarget = loaddata['storetarget']
        filteratrdata = [item for item in atrtarget if item['symbol'] == first_string]
        gettargetatr = filteratrdata[0]['target_price']
        getstoplossatr = filteratrdata[0]['stoploss_price']



        # print("------dfgh",gettrend)
        print(target_points,stoploss_points,min_change,max_change)

        # target_points = 20
        # stoploss_points = 10
        # min_change = 5
        # max_change = 15
        # print(getdata)
        if len(getstoredata) == 0:
            # data = {
            # "symbol": symbol,
            # 'targetprice' : filterdbuyltp * 1.10,
            # 'stolossprice' : filterdbuyltp - 5
            # }

            data = {
                "symbol": symbol,
                'targetprice': filterdbuyltp + int(target_points),
                'stolossprice': filterdbuyltp - int(stoploss_points),
                'gettargetatr':gettargetatr,
                'getstoplossatr':getstoplossatr
            }
            maxprofitdata = {
                'symbol':symbol,
                'profit':0,

            }
            maxprofit.append(maxprofitdata)
            storetarget.append(data)
            print(data,maxprofitdata)
        exitontarget(ltp, filterdbuyltp, buylotsize, symbol, id,min_change,max_change,gettrend)

# Define the exitontarget function


# Define the exitontarget function
# def exitontarget(ltp, buyprice, lotsize, symbol, id):
#     date = datetime.datetime.now()
#     getvale = next((item for item in storetarget if item['symbol'] == symbol), None)
#     index_to_update = next((index for index, item in enumerate(storetarget) if item['symbol'] == symbol), None)
#     if getvale:
#         targetprice = getvale['targetprice']
#         stolossprice = getvale['stolossprice']
#     else:
#         print('Error : symbol missing')
#     # Print the current target and stoploss prices
#     print('ltp :',ltp,'Current target price:', targetprice, 'Current stoploss price:', stolossprice)
#
#     # Determine the status based on trailing stoploss and target
#     # if timecomplete == True:
#     #     status = "Trailing Stoploss hit"
#     #     profit_or_loss = (buyprice - ltp) * lotsize
#     #     profitorder = f'Time: {date} - Symbol: {symbol} - Exit Price: {ltp} - Buy Price: {buyprice} - Trailing Stoploss Price: {stolossprice} - Target Price: {targetprice} - Profit/Loss: {profit_or_loss}'
#     #     crete_update_table.updateorderplace(id, 0, profitorder)
#     #     sendAlert(profitorder)
#     #     del storetarget[index_to_update]
#
#     if ltp >= targetprice:
#         status = "Trailing Target"
#         profit_or_loss = (ltp - buyprice) * lotsize
#         storetarget[index_to_update]['targetprice'] = ltp * 1.05
#         storetarget[index_to_update]['stolossprice'] = ltp * 0.995
#
#     elif ltp <= stolossprice:
#         status = "Trailing Stoploss hit"
#         profit_or_loss = (ltp - buyprice) * lotsize
#         profitorder = f'Time: {date} - Symbol: {symbol} - Exit Price: {ltp} - Buy Price: {buyprice} - Trailing Stoploss Price: {stolossprice} - Target Price: {targetprice} - Profit/Loss: {profit_or_loss}'
#         crete_update_table.updateorderplace(id, 0, profitorder)
#         sendAlert(profitorder)
#         del storetarget[index_to_update]
#
#     else:
#         status = "In trade"
#         profit_or_loss = (ltp - buyprice) * lotsize
#         print(profit_or_loss)
#     # Create an alert dictionary to print
#     # alert = {
#     #     "symbol": symbol,
#     #     "status": status,
#     #     "ltp": ltp,
#     #     "buyprice": buyprice,
#     #     "trailing_stoploss_price": stolossprice,
#     #     "target_price": targetprice,
#     #     "profit_or_loss": profit_or_loss
#     # }
#     #
#     # print(alert)

def place_order(token, symbol, qty, exch_seg, buy_sell, ordertype, price):
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
            "quantity": qty,
            'price': price
        }
        # orderId = obj.placeOrder(orderparams)
        orderId = 1
        # print(orderId)

        if orderId:
            # orderId = obj.placeOrder(orderparams)
            print(
                    f"{buy_sell} order Place for {symbol} at : {datetime.datetime.now()} with Order id {orderId}"
                )
            bot_message = f'order status:{buy_sell} for {symbol} with price {token} and the time is {datetime.datetime.now()}'
            sendAlert(bot_message)
            return orderId,True
        else:
            return orderId,False


def enteryexit(profit_order,index_to_update,index_to_profit,ltp, buyprice, lotsize, symbol, id,min_change,max_change,gettrend):
    match = re.match(r"^[A-Za-z]+", symbol)
    first_string = match.group() if match else None
    nsechangedata = {
    'NIFTY':'NFO',
    'BANKNIFTY':'NFO',
    'SENSEX':'BFO'

    }
    orderId,checkorderplace = place_order(token,symbol,lotsize,nsechangedata[first_string],'SELL','MARKET',ltp)
    if checkorderplace:
        crete_update_table.updateorderplace(id, 0, profit_order)
        sendAlert(profit_order)
        del storetarget[index_to_update]  # Remove exited position
        del maxprofit[index_to_profit]
    else:
         sendAlert(f"{orderId}")



def exitontarget(ltp, buyprice, lotsize, symbol, id,min_change,max_change,gettrend):
    print("--------------------")
    date = datetime.datetime.now()
    print(lotsize)


    # Retrieve stored values
    get_value = next((item for item in storetarget if item['symbol'] == symbol), None)
    mar_profit_value = next((item for item in maxprofit if item['symbol'] == symbol), None)
    index_to_update = next((index for index, item in enumerate(storetarget) if item['symbol'] == symbol), None)
    index_to_profit = next((index for index, item in enumerate(maxprofit) if item['symbol'] == symbol), None)

    if not get_value or index_to_update is None:
        print(f"Error: Symbol {symbol} missing in storetarget.")
        return

    # Extract target and stoploss prices
    target_price = get_value['targetprice']
    stoploss_price = get_value['stolossprice']
    #atr target and stoploss
    atrtarget = get_value['gettargetatr']
    atrstoploss = get_value['getstoplossatr']
    print('--------------',atrstoploss,atrtarget)

    print(f'LTP: {ltp} | Current Target Price: {target_price} | Current Stoploss Price: {stoploss_price}')

    # Calculate Profit/Loss
    profit_or_loss = (ltp - buyprice) * lotsize

    # Track max LTP
    if mar_profit_value:
        mar_profit_value['max_ltp'] = max(ltp, mar_profit_value.get('max_ltp', ltp))
        # if (mar_profit_value['max_ltp'] - buyprice) > 4:
        #     if mar_profit_value['stolossprice'] < buyprice:
        #          mar_profit_value['stolossprice'] = buyprice
        #     else:
        #         mar_profit_value['stolossprice'] = mar_profit_value['stolossprice'] + 1
    else:
        maxprofit.append({'symbol': symbol, 'profit': profit_or_loss, 'max_ltp': ltp})
        # max_ltp = mar_profit_value['max_ltp']

    if ltp >= target_price:
        status = "Trailing Target"
        # storetarget[index_to_update]['targetprice'] = ltp * 1.02
        # storetarget[index_to_update]['stolossprice'] = ltp * 0.98
        if gettrend == 'no_trade':
            max_profit_value = mar_profit_value['profit'] if mar_profit_value else 0

            profit_order = (
                f"Time: {date} | Symbol: {symbol} | Exit Price: {ltp} | Buy Price: {buyprice} | "
                f"Trailing Stoploss Price: {stoploss_price} | Target Price: {target_price} | "
                f"Profit/Loss: {profit_or_loss} | Max Profit: {max_profit_value} | Max LTP: {mar_profit_value['max_ltp']}"
            )

            # crete_update_table.updateorderplace(id, 0, profit_order)
            # sendAlert(profit_order)
            # del storetarget[index_to_update]  # Remove exited position
            # del maxprofit[index_to_profit]
            enteryexit(profit_order,index_to_update,index_to_profit,ltp, buyprice, lotsize, symbol, id,min_change,max_change,gettrend)
        else:
            storetarget[index_to_update]['targetprice'] += 10
            storetarget[index_to_update]['stolossprice'] = ltp - 5
    elif ltp <= stoploss_price or (ltp <= mar_profit_value['max_ltp'] - int(min_change)
                                   and mar_profit_value['max_ltp'] - buyprice >= int(max_change)):
        status = "Trailing Stoploss Hit"
        max_profit_value = mar_profit_value['profit'] if mar_profit_value else 0

        profit_order = (
            f"Time: {date} | Symbol: {symbol} | Exit Price: {ltp} | Buy Price: {buyprice} | "
            f"Trailing Stoploss Price: {stoploss_price} | Target Price: {target_price} | "
            f"Profit/Loss: {profit_or_loss} | Max Profit: {max_profit_value} | Max LTP: {mar_profit_value['max_ltp']}"
        )

        # crete_update_table.updateorderplace(id, 0, profit_order)
        # sendAlert(profit_order)
        enteryexit(profit_order,index_to_update,index_to_profit,ltp, buyprice, lotsize, symbol, id,min_change,max_change,gettrend)

        if (ltp <= mar_profit_value['max_ltp'] - 5 and mar_profit_value['max_ltp'] - buyprice >= 10):
                sendAlert(f"Exit triggered: LTP dropped below max LTP ---- exit-ltp:{ltp} buyprice:{buyprice} maxltp:{mar_profit_value['max_ltp']} diff.:{mar_profit_value['max_ltp'] - buyprice} pnl-diff:{ltp - buyprice}")
                # crete_update_table.updateorderplace(id, 0, profit_order)

        # del storetarget[index_to_update]  # Remove exited position
        # del maxprofit[index_to_profit]
    elif mar_profit_value['max_ltp'] == 0 and ltp < (buyprice - 4) or mar_profit_value['max_ltp'] > (buyprice + 4) and ltp < (buyprice + 3):
            # if gettrend == 'no_trade':
            if True:
                max_profit_value = mar_profit_value['profit'] if mar_profit_value else 0

                profit_order = (
                    f"Time: {date} | Symbol: {symbol} | Exit Price: {ltp} | Buy Price: {buyprice} | "
                    f"Trailing Stoploss Price: {stoploss_price} | Target Price: {target_price} | "
                    f"Profit/Loss: {profit_or_loss} | Max Profit: {max_profit_value} | Max LTP: {mar_profit_value['max_ltp']}"
                )
                sendalertdata = f"Exit triggered: LTP dropped below max LTP ---- exit-ltp:{ltp} buyprice:{buyprice} maxltp:{mar_profit_value['max_ltp']} diff.:{mar_profit_value['max_ltp'] - buyprice} pnl-diff:{ltp - buyprice}"
                sendAlert(f"Exit triggered: LTP dropped below max LTP ---- exit-ltp:{ltp} buyprice:{buyprice} maxltp:{mar_profit_value['max_ltp']} diff.:{mar_profit_value['max_ltp'] - buyprice} pnl-diff:{ltp - buyprice}")
                enteryexit(profit_order,index_to_update,index_to_profit,ltp, buyprice, lotsize, symbol, id,min_change,max_change,gettrend)

        # crete_update_table.updateorderplace(id, 0, profit_order)
        # del storetarget[index_to_update]  # Remove exited position
        # del maxprofit[index_to_profit]
        # enteryexit(profit_order,index_to_update,index_to_profit)
    elif (ltp <= atrstoploss) or (ltp >= atrtarget):
        profit_order = (
                    f"Exit by ATR Time: {date} | Symbol: {symbol} | Exit Price: {ltp} | Buy Price: {buyprice} | "
                    f" Stoploss Price: {atrtarget} | Target Price: {atrtarget} | "
                    f"Profit/Loss: {profit_or_loss} "
                )
        sendAlert(f"Exit triggered: LTP dropped below max LTP ---- exit-ltp:{ltp} buyprice:{buyprice} maxltp:{mar_profit_value['max_ltp']} diff.:{mar_profit_value['max_ltp'] - buyprice} pnl-diff:{ltp - buyprice}")
        enteryexit(profit_order,index_to_update,index_to_profit,ltp, buyprice, lotsize, symbol, id,min_change,max_change,gettrend)

    else:
        status = "In Trade"
        if mar_profit_value:
            mar_profit_value['profit'] = max(profit_or_loss, mar_profit_value['profit'])
        else:
            maxprofit.append({'symbol': symbol, 'profit': profit_or_loss, 'max_ltp': ltp})

    # Print alert summary
    alert = {
        'maxprofit': mar_profit_value['profit'] if mar_profit_value else profit_or_loss,
        'ltp':ltp,
        'max_ltp': mar_profit_value['max_ltp'] if mar_profit_value else ltp,
        'profit_or_loss': profit_or_loss
    }

    print(alert)



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
schedule.every().day.at("15:27").do(set_timecomplete)

while True:
    # print("start tym , CURRENT TIME:{}".format(datetime.datetime.now()))
    try:
        schedule.run_pending()
        time.sleep(5)
    except Exception as e:
        raise e


# Optionally, join the thread if you want to wait for it to complete
# thread.join()


