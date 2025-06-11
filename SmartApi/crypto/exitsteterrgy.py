from datetime import datetime

import websocket
import json


import crete_update_table

# Define the instrument names (multiple tokens)
# INSTRUMENT_NAMES = ["C-BTC-103400-210125", "C-BTC-102200-210125", "P-BTC-102200-210125"]
storetarget = []


def formatdata(data):
    # print(data['last_traded_price']/100)
    ltp = data['close']
    print('ltp',ltp)
    getbook = crete_update_table.fetchtcryptoorderbook()
    # ignoretoke = check_headage_data(getbook,data['token'])
    # print('ignore token',ignoretoke)
    filtertoken = [token for token in getbook if token['script'] == data['symbol'] and token['lotsize'] > 0]
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

        getstoredata = [item for item in storetarget if item['symbol'] == symbol]
        # print(getdata)
        if len(getstoredata) == 0:
            data = {
            "symbol": symbol,
            'targetprice' : filterdbuyltp + 10,
            'stolossprice' : filterdbuyltp + 5
            }
            storetarget.append(data)
        exitontarget(ltp, filterdbuyltp, buylotsize, symbol, id)

def exitontarget(ltp, buyprice, lotsize, symbol, id):
    date = datetime.datetime.now()
    getvale = next((item for item in storetarget if item['symbol'] == symbol), None)
    index_to_update = next((index for index, item in enumerate(storetarget) if item['symbol'] == symbol), None)
    if getvale:
        targetprice = getvale['targetprice']
        stolossprice = getvale['stolossprice']
    else:
        print('Error : symbol missing')
    # Print the current target and stoploss prices
    print('ltp :',ltp,'Current target price:', targetprice, 'Current stoploss price:', stolossprice)


    if ltp >= targetprice:
        status = "Trailing Target"
        profit_or_loss = (ltp - buyprice) * lotsize
        storetarget[index_to_update]['targetprice'] = ltp + 5
        storetarget[index_to_update]['stolossprice'] = ltp - 3

    elif ltp <= stolossprice:
        status = "Trailing Stoploss hit"
        profit_or_loss = (ltp - buyprice) * lotsize
        profitorder = f'Time: {date} - Symbol: {symbol} - Exit Price: {ltp} - Buy Price: {buyprice} - Trailing Stoploss Price: {stolossprice} - Target Price: {targetprice} - Profit/Loss: {profit_or_loss}'
        crete_update_table.updatecrypto(id, 0, profitorder)
        sendAlert(profitorder)
        del storetarget[index_to_update]

    else:
        status = "In trade"
        profit_or_loss = (ltp - buyprice) * lotsize
        print(profit_or_loss)


def insialisetoken():
    print('start')
    global token_list
    global getbook
    getbook = crete_update_table.fetchtcryptoorderbook()
    store = []
    for item in getbook:
        if item is not None:
            if item['lotsize'] > 0:
                store.append(item['script'])

    # sws.on_open = on_open
    print(store)
    return store

INSTRUMENT_NAMES = insialisetoken()
print('INSTRUMENT_NAMES',INSTRUMENT_NAMES)

def sendAlert(message):
    print(message)
# Callback when a message is received
def on_message(ws, message):
    data = json.loads(message)
    convertdata =json.dumps(data, indent=2)
    if "close" in data:  # Adjust based on the exact structure of your WebSocket response
        print(f"Received data: {convertdata['close']}")
        formatdata(convertdata['close'])
    else:
        print(f"Received message check: {convertdata}")

# Callback when there's an error
def on_error(ws, error):
    print(f"Error: {error}")

# Callback when the WebSocket connection is closed
def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed")

# Callback when the WebSocket connection is opened
def on_open(ws):
    print("WebSocket connection opened")
    INSTRUMENT_NAMES = insialisetoken()

    # Subscribe to the ticker for multiple instruments
    subscription_message = {
        "type": "subscribe",
        "payload": {
            "channels": [
                {
                    "name": "v2/ticker",
                    "symbols": INSTRUMENT_NAMES
                }
            ]
        }
    }
    ws.send(json.dumps(subscription_message))
    print(f"Subscribed to updates for: {', '.join(INSTRUMENT_NAMES)}")

# Delta Exchange WebSocket endpoint
delta_ws_url = "wss://socket.delta.exchange"

# Create and run the WebSocket
ws = websocket.WebSocketApp(
    delta_ws_url,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)
ws.on_open = on_open
ws.run_forever()
