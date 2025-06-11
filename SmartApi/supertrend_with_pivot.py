from tvDatafeed import TvDatafeed,Interval
from SmartApi import SmartConnect #or from SmartApi.smartConnect import SmartConnect
import time
from datetime import datetime,timedelta
import datetime
import pandas_ta as ta
import pandas as pd
import numpy as np
import os
import sys
import pyotp
import schedule
import math
import requests
import crete_update_table
import document
import stock_token_list

current_date_time = datetime.datetime.now()
form_date = current_date_time - timedelta(days = 10)
traded_list_exit = []
print("current tym",current_date_time)
placeOREDR = True

tradtestocks = {
    "ACC-EQ": "22",
    "AMBUJACEM-EQ": "1270",
    "ADANIPORTS-EQ": "15083",
    "ADANIENT-EQ": "25",
    "AWL-EQ" : "8110",
    'RALLIS-EQ' : "2816",
    'CESC':'628'
}
script_list = {
    'RELIANCE-EQ': '2885',
    'TCS-EQ': '11536',
    'ICICIBANK-EQ': '4963',
    'HDFCBANK-EQ': '1333',
    'SBIN-EQ': '3045',
};

store_order_data = []

buy_traded_stock = []
sell_traded_stock = []

exchange = "NSE"
per_trade_fund = 10000
ma_short = 13
ma_long = 22
runcount = 0




def fetchdataandreturn_pivot(symbol):
    print(symbol)
    username = 'YourTradingViewUsername'
    password = 'YourTradingViewPassword'

    tv = TvDatafeed(username, password)
    # index
    nifty_index_data = tv.get_hist(symbol=symbol, exchange='NSE', interval=Interval.in_daily, n_bars=3)
    data = nifty_index_data
    if data is not None:
        # print(data['high'].values[-2], data['low'].values[-2], data['close'].values[-2])
        high_price = data['high'].values[-2]
        low_price = data['low'].values[-2]
        close_price = data['close'].values[-2]
        datafile = []
        # print(high_price, low_price, close_price)
        # Calculate Fibonacci Levels
        pi = (high_price + low_price + close_price) / 3
        R1 = pi + (0.382 * (high_price - low_price))
        R2 = pi + (0.6182 * (high_price - low_price))
        R3 = R2 + (R2 - R1)
        S1 = pi - (0.382 * (high_price - low_price))
        S2 = pi - (0.6182 * (high_price - low_price))
        S3 = S2 - (R1 - S1)
        fibonacci_levels = {
            'p': round(pi,2),
            's1': round(S1,2),
            'r1': round(R1,2),
            's2': round(S2,2),
            'r2': round(R2,2),
            'r3': round(R3,2),
            's3': round(S3,2)
        }
        global pivot_fibo_level
        pivot_fibo_level = fibonacci_levels


def setAlreadyBuySellRecord(data):

    if data is not None:
        for a in data:
            #print(int(a['netqty']),a['tradingsymbol'] )
            if a['netqty'] != '0' and int(a['netqty']) > 0 and (a['tradingsymbol'] not in buy_traded_stock):
                buy_traded_stock.append(a['tradingsymbol'])
            elif a['netqty'] != '0' and int(a['netqty']) < 1 and (a['tradingsymbol'] not in sell_traded_stock):
                sell_traded_stock.append(a['tradingsymbol'])

        print('buy_traded_stock',buy_traded_stock)
        print('sell_traded_stock',sell_traded_stock)

    else:
        print('data is null')


def storeorderdata(alldata):
    totalprice = ((int(float(alldata.avgnetprice)) / 100) * 20) * int(alldata.netqty)
    stoploss = float((totalprice / 100) * 2)
    tergetorder = float((totalprice / 100) * 5)
    pnltype = 'profit' if int(float(alldata.pnl)) > 0 else 'loss'
    # if  netqty is greater than 0  its means that buy order placed. so, we have placed sell order if buy exit and wisevewrsa.
    buysell = "SELL" if int(alldata.netqty) > 0 else "BUY"
    data = {
        'symbol': alldata.symbolname,
        'qty': alldata.netqty,
        'totalprice': totalprice,
        'stoploss': stoploss,
        'targetorder': tergetorder,
        'pnl': alldata.pnl,
        'pnltype': pnltype,
        "transactiontype": buysell
    }
    store_order_data.append(data)


def getorderBook(symbol,orderbook):
    tradebook = orderbook
    isscript = crete_update_table.get_data(symbol)
    global store_order_data
    store_order_data = []
    #optenPosition = crete_update_table.orderbook()
    #isscript = len(optenPosition) == 0 if True else any(item['script'] != symbol for item in optenPosition)
    print(len(isscript),symbol,crete_update_table.get_data(symbol),' is script' )
    if tradebook['data'] is not None:
        for a in tradebook['data']:
            storeorderdata(a)
            if a['instrumenttype'] != 'OPTIDX' and a['tradingsymbol'] not in script_list and a['tradingsymbol'] in stock_token_list.scripts:
                    #print('data------true',a['tradingsymbol'],stock_token_list.scripts[a['tradingsymbol']])
                    appendkey = str(a['tradingsymbol'])
                    script_list[appendkey] = stock_token_list.scripts[a['tradingsymbol']]
            elif a['tradingsymbol'] in script_list and int(a['netqty']) == 0:
                del script_list[a['tradingsymbol']]
            else:
                print('script not available : ',a['tradingsymbol'])
            # print('quantity : ',a['netqty'], 'script : ',a['tradingsymbol'],int(a['netqty']) <= 0)
            if a['netqty'] != '0' and len(isscript) == 0 and a['tradingsymbol'] == symbol:
                ordertype = a['netqty']
                crete_update_table.insertscript(a['tradingsymbol'],ordertype)
            elif int(a['netqty']) == 0 and a['tradingsymbol'] == symbol:
                print('delete run')
                crete_update_table.deletescript(a['tradingsymbol'])

        print('not action found : ', symbol)
    else:
        print('no order found for script : ',symbol)


def defineresistancelevel(fibo_level,close):
  data = fibo_level
  filter_value = close

  matching_keys = [key for key, value in data.items() if value >= filter_value]
  max_key = min(matching_keys, key=lambda k: data[k], default='p')
  return max_key

def definesupportlevel(fibo_level,close):
  data = fibo_level
  filter_value = close

  matching_keys = [key for key, value in data.items() if value <= filter_value]
  max_key = max(matching_keys, key=lambda k: data[k], default='p')
  return max_key


def orderplacewithpivot(df, param):
    print(pivot_fibo_level)
    Method = 'pe' if param == 'buy' else ('ce' if param == 'sell' else None)
    r_level = defineresistancelevel(pivot_fibo_level, df.close.values[-1])
    s_level = definesupportlevel(pivot_fibo_level, df.close.values[-1])

    # print('resistance', r_level, 'supports', s_level,'close',df.close.values[-1],'second-right-high',df.high.values[-2] )

    if r_level in pivot_fibo_level or s_level in pivot_fibo_level:
        print(param,df.low.values[-2] <= pivot_fibo_level[s_level] and df.close.values[-1] > pivot_fibo_level[s_level])
        if param == 'buy':
            if df.high.values[-2] >= pivot_fibo_level[r_level] and df.close.values[-1] < pivot_fibo_level[r_level]:

                return 'pe'

            elif df.low.values[-2] <= pivot_fibo_level[s_level] and df.close.values[-1] > pivot_fibo_level[s_level]:

                return 'ce'

        elif param == 'sell':
            if df.high.values[-2] >= pivot_fibo_level[r_level] and df.close.values[-1] < pivot_fibo_level[s_level]:
                return 'ce'

            elif df.low.values[-2] <= pivot_fibo_level[s_level] and df.close.values[-1] > pivot_fibo_level[s_level]:

                 return 'pe'

    else:
        print("nothing")


def PlaceOredrExit():
    placeOREDR = False

def checkorderlimit():
    try:
        getposition = obj.position()
        if getposition['data'].len >= 5:
           placeOREDR = False


    except Exception as e:
        print("error in check number in Position: {}".format(e))
        sendAlert("error in check number in Position: {}".format(e))



def sendAlert(bot_message):
    get_message = format(bot_message)
    print(get_message)

    bot_token = "5707293106:AAEPkxexnIdoUxF5r7hpCRS_6CHINgU4HTw"
    bot_chatid = "2027669179"
    send_message = "https://api.telegram.org/bot" + bot_token + "/sendMessage?chat_id=" + bot_chatid + \
                   "&parse_mode=MarkdownV2&text=" + bot_message

    # response = requests.get(send_message)
    response = requests.post(f'https://api.telegram.org/bot{bot_token}/sendMessage', data={'chat_id': bot_chatid, 'text': bot_message})

    print(response)
    return response.json()


def GettingLtpData(script, token, order,stoploss,squaroff):
    LTP = obj.ltpData(exchange, script, token)
#     print(LTP)
    ltp = LTP["data"]["ltp"]
    # quantity = int(per_trade_fund * 10 / ltp)    # quantity = int(per_trade_fund / ltp)
    quantity = 1


    orderparams = {
        "variety": "NORMAL",
        "tradingsymbol": script,
        "symboltoken": token,
        "transactiontype": order,
        "exchange": exchange,
        "ordertype": "LIMIT",
        "producttype": "INTRADAY",
        "duration": "DAY",
        "price": ltp,
        "squareoff": '0',
        "stoploss": '0',
        "quantity": quantity
    }

    if placeOREDR:
        orderId = obj.placeOrder(orderparams)
        # orderId = 1
        print(
                f"{order} order Place for {script} at : {datetime.datetime.now()} with Order id {orderId}"
            )


    bot_message = f'order status:{order} for {script} with price {ltp:.1f} and the time is {datetime.datetime.now()}'
    sendAlert(bot_message)



def exitQuert():
    api_key = document.api_key
    user_id = document.user_id
    password = document.password
    totp = pyotp.TOTP(document.totp).now()

    try:
        obj = SmartConnect(api_key=api_key)
        token = obj.generateToken(obj.generateSession(user_id, password, totp)["data"]["refreshToken"])
        getposition = obj.position()

        for a in getposition['data']:
            LTP = obj.ltpData(a["exchange"], a["tradingsymbol"], a["symboltoken"])
            getltp = LTP["data"]["ltp"]

            if (a["tradingsymbol"] not in traded_list_exit):

                traded_list_exit.append(a["tradingsymbol"])
                transactionType = "SELL" if int(a['netqty']) > 0 else "BUY"

                orderparams3 = {"variety": "NORMAL", "tradingsymbol": a["tradingsymbol"], "symboltoken": a["symboltoken"],
                                "transactiontype": transactionType, "exchange": a["exchange"], "ordertype": "LIMIT",
                                "producttype": a["producttype"], "duration": "DAY", "price": getltp, "squareoff": "0",
                                "stoploss": "0", "quantity": abs(int(a["netqty"]))}
                orderId3=obj.placeOrder(orderparams3)
                print(f"{orderparams3} order Place for {a['symboltoken']} at : {datetime.datetime.now()} with Order id {orderId3} order id quantity :{a['netqty']} ")

                time.sleep(2)

    except Exception as e:
        print("error: {}".format(e))
        bot_message = f"error when exit {e}"
        sendAlert(bot_message)

def strategy():
    print('check stetergy')
    global obj

    current_date_time = datetime.datetime.now()
    form_date = current_date_time - timedelta(days=10)

    api_key = document.api_key
    user_id = document.user_id
    password = document.password
    totp = pyotp.TOTP(document.totp).now()


    # print(feedToken)

    try:
        obj = SmartConnect(api_key=api_key)
        token = obj.generateToken(obj.generateSession(user_id, password, totp)["data"]["refreshToken"])
        jwtToken = token['data']["jwtToken"]
        refreshToken = token['data']['refreshToken']
        feedToken = token['data']['feedToken']
        orderbook = obj.position()
        print(token,script_list)
        for script, token in script_list.items():
            historicParam = {
                "exchange": exchange,
                "symboltoken": token,
                "interval": "FIVE_MINUTE",
                "fromdate": form_date.strftime("%Y-%m-%d 09:15"),
                "todate": current_date_time.strftime("%Y-%m-%d %H:%M")
            }
            hist_data = obj.getCandleData(historicParam)["data"]
            LTP = obj.ltpData(exchange, script, token)
            getorderBook(script,orderbook)

            # print(LTP)
            # print("__________hist",hist_data)
            if hist_data != None:
                df = pd.DataFrame(
                    hist_data,
                    columns=['date', 'open', 'high', 'low', 'close', 'volume'])
                df["sup"] = ta.supertrend(df['high'], df['low'], df['close'], length=10, multiplier=3)['SUPERT_10_3.0']
                # df["sup"] = ta.supertrend(df['high'], df['low'], df['close'], length=10, multiplier=3)['SUPERT_10_3.0']
                df["ema"] = ta.ema(df["close"], length=200)
                df["ema10"] = ta.ema(df["close"], length=10)

                df['stx'] = np.where((df['sup'] > 0.00), np.where((df['close'] > df['sup']), 'up', 'down'), np.NaN)

                # df['stx'] = 'down' if df['sup'].values > df['close'].values else 'up'
                df.dropna(inplace=True)
                # print(df.tail(40))
                print('#------------------------------' ,script,df.close.values[-5],df.close.values[-4],df.close.values[-3],df.close.values[-2],"----",df.sup.values[-1],'-----------------------#',format(datetime.datetime.now()))

                sup_cl = df.stx.values[-1]
                sup_pre = df.stx.values[-2]
                if not df.empty:

                    sup_cl = df.sup.values[-1]
                    close_cl = df.close.values[-1]
                    # pre close
                    sup_pre = df.sup.values[-2]
                    close_pre = df.close.values[-2]

                    # 3 close
                    sup_pre3 = df.sup.values[-3]
                    close_pre3 = df.close.values[-3]

                    words = script[:-3] if script.endswith("-EQ") else script
                    fetchdataandreturn_pivot(words)

                    r_level = defineresistancelevel(pivot_fibo_level,df.close.values[-1])
                    s_level = definesupportlevel(pivot_fibo_level,df.close.values[-1])
                    stoplossbuy = df.close.values[-1] - df.low.values[-1]
                    stoplosssell = df.high.values[-1] - df.close.values[-1]
                    squaroff = "100"
                    optenPosition = crete_update_table.orderbook()
                    isscript = crete_update_table.get_data(script)
                    print(len(isscript),'script length')
                    condition_buy = len(isscript) == 0

                    condition_exit_sell = any(item['script'] == script and int(item['ordertype']) < 0 for item in optenPosition)
                    condition_exit_buy = any(item['script'] == script and int(item['ordertype']) > 0 for item in optenPosition)

                    setExitCondition = [item for item in store_order_data if item['symbolname'] == script]


                    print('tradeBook for script',setExitCondition)
                    print('condition_buy',condition_buy,'condition_exit_buy',condition_exit_buy,'condition_exit_sell',condition_exit_sell)


                    if not df.empty:
                        #print(script,sell_traded_stock)
                        #print(script in sell_traded_stock)
                        print('resistance:',r_level,'support',s_level, 'script is not in trade:',optenPosition,condition_buy)

                        if close_pre >= sup_pre and close_cl < sup_cl and condition_buy:
                            sell_traded_stock.append(script)
                            print(script, token, "SELL")
                            f = open("storeStock.txt", "a")
                            f.write(str(script) + "----" + str(token) + "---------SELL-----------" + "----" + str(LTP['data']['ltp'])+ str(current_date_time) + '\n')
                            f.close()
                            GettingLtpData(script, token, "SELL",stoplosssell,squaroff)

                            # getposition = obj.position()
                            # print("Holding______",getposition.data)
                            # if script in getposition['data']['tradingsymbol']:
                            #     GettingLtpData(script, token, "SELL")

                        elif close_pre <= sup_pre and close_cl > sup_cl and condition_buy:
                            buy_traded_stock.append(script)
                            print(script, token, "BUY")
                            f = open("storeStock.txt", "a")
                            f.write(str(script) + "----" + str(token) + "---------BUY-----------" + "----" + str(LTP['data']['ltp'])+ str(current_date_time) + '\n')
                            f.close()
                            GettingLtpData(script, token, "BUY",stoplossbuy,squaroff)
                            # getposition = obj.position()
                            # if script in getposition['data']['tradingsymbol']:
                            #     GettingLtpData(script, token, "BUY")

                        # elif checktradebook and close_pre < sup_pre and df.high.values[-2] >= pivot_fibo_level[r_level] and df.close.values[-1] < pivot_fibo_level[r_level] and (script not in sell_traded_stock):
                        #     # sell_traded_stock.append(script)
                        #     print(script, token, "SELL")
                        #     f = open("storeStock.txt", "a")
                        #     f.write(str(script) + "----" + str(token) + "---------SELL-----------" + "----" + str(LTP['data']['ltp'])+ str(current_date_time) + '\n')
                        #     f.close()
                        #     GettingLtpData(script, token, "SELL")
                        #
                        elif condition_buy and close_pre > sup_pre and df.low.values[-2] <= pivot_fibo_level[s_level] and df.close.values[-1] > pivot_fibo_level[s_level]:
                        #     # buy_traded_stock.append(script)
                        #     print(script, token, "BUY")
                        #     f = open("storeStock.txt", "a")
                        #     f.write(str(script) + "----" + str(token) + "---------BUY-----------" + "----" + str(LTP['data']['ltp'])+ str(current_date_time) + '\n')
                        #     f.close()
                            GettingLtpData(script, token, "BUY",stoplossbuy,squaroff)

                        #exit----
                        elif condition_exit_sell and close_pre < sup_pre and df.low.values[-2] <= pivot_fibo_level[s_level] and df.close.values[-1] > pivot_fibo_level[s_level]:
                            buy_traded_stock.append(script)
                            print('exit 1')
                            print(script, token, "BUY")
                            f = open("storeStock.txt", "a")
                            f.write(str(script) + "----" + str(token) + "---------BUY-----------" + "----" + str(LTP['data']['ltp'])+ str(current_date_time) + '\n')
                            f.close()
                            GettingLtpData(script, token, "BUY",'0','0')

                        elif condition_exit_buy  and close_pre > sup_pre and df.high.values[-2] >= pivot_fibo_level[r_level] and df.close.values[-1] < pivot_fibo_level[r_level]:
                            sell_traded_stock.append(script)
                            print('exit 2')
                            print(script, token, "SELL")
                            f = open("storeStock.txt", "a")
                            f.write(str(script) + "----" + str(token) + "---------SELL-----------" + "----" + str(LTP['data']['ltp'])+ str(current_date_time) + '\n')
                            f.close()
                            GettingLtpData(script, token, "SELL",'0',squaroff)

                        elif df.close.values[-1] < df.ema.values[-1] and condition_exit_buy:
                             sell_traded_stock.append(script)
                             print('exit 3')
                             GettingLtpData(script, token, "SELL",'0',squaroff)

                        elif df.close.values[-1] > df.ema.values[-1] and condition_exit_sell:
                             buy_traded_stock.append(script)
                             print('exit 4')
                             GettingLtpData(script, token, "BUY",'0',squaroff)

                        # set terget and stoploss to exit

                        elif setExitCondition and setExitCondition['pnltype'] == 'loss' and abs(int(setExitCondition['pnl'])) > int(setExitCondition['stoploss']) or setExitCondition and setExitCondition['pnltype'] == 'profit' and int(setExitCondition['pnl']) > int(setExitCondition['target']):
                            print('Hit stoploss or target')
                            transtype = setExitCondition['transactiontype']
                            GettingLtpData(script, token, transtype,'0',squaroff)

                        else:
                            print(script,'not match')

                    else:
                       print(script,'not match')
            else:
                print('not done')
            time.sleep(5)

    except Exception as e:
        print("Historic Api failed: {}".format(e),format(datetime.datetime.now()))
        bot_message = f"Historic Api failed {e}"
        sendAlert(bot_message)
        strategy()
        time.sleep(5)

    try:
        logout = obj.terminateSession(user_id)
        print("Logout Successfull")
    except Exception as e:
        print("Logout failed: {}".format(e))
        bot_message = f"Logout failed {e}"
        sendAlert(bot_message)




strategy()
schedule.every(1).minutes.do(strategy)
# schedule.every(5).minutes.do(checkorderlimit)
schedule.every().day.at("15:05").do(exitQuert)
schedule.every().day.at("15:00").do(PlaceOredrExit)




while True:
        # print("start tym , CURRENT TIME:{}".format(datetime.datetime.now()))
        try:
            schedule.run_pending()
            time.sleep(2)
        except Exception as e:
            raise e
