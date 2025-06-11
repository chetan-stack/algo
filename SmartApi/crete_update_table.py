import datetime
import json
import re
import sqlite3
from typing import List, Union


conn = sqlite3.connect('database.db')
print(conn)

conn.execute('''CREATE TABLE IF NOT  EXISTS ORDERCONDITION(
        id INTEGER PRIMARY KEY,
        condition TEXT NOT NULL
    )''')

conn.execute('''CREATE TABLE IF NOT  EXISTS intradayorder(
        id INTEGER PRIMARY KEY,
        script TEXT NOT NULL
    )''')

conn.execute('''CREATE TABLE IF NOT  EXISTS supportset(
        id INTEGER PRIMARY KEY,
        timeframe TEXT NOT NULL,
        supportlist TEXT NOT NULL,
        symboltype TEXT NOT NULL
    )''')

conn.execute('''CREATE TABLE IF NOT EXISTS ordertoken(
        id INTEGER PRIMARY KEY,
        symbol TEXT NOT NULL,
        exchange TEXT NOT NULL,
        token TEXT NOT NULL,
        ltp REAL NOT NULL,
        lotsize INTEGER NOT NULL,
        profit REAL NOT NULL
    )''')

conn.execute('''CREATE TABLE IF NOT EXISTS cryptoorderbook(
        id INTEGER PRIMARY KEY,
        symbol TEXT NOT NULL,
        exchange TEXT NOT NULL,
        token TEXT NOT NULL,
        ltp REAL NOT NULL,
        lotsize INTEGER NOT NULL,
        profit REAL NOT NULL
    )''')

conn.execute('''CREATE TABLE IF NOT EXISTS placeorder (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        exchange TEXT NOT NULL,
        token TEXT NOT NULL,
        delta TEXT NOT NULL,
        closeprice REAL NOT NULL,
        ltp REAL NOT NULL,
        target REAL NOT NULL,
        stoploss REAL NOT NULL,
        lotsize INTEGER NOT NULL,
        profit REAL NOT NULL,
        createddate DATETIME DEFAULT CURRENT_TIMESTAMP
    );''')

conn.execute('''CREATE TABLE IF NOT EXISTS hight_achieve (
        id INTEGER PRIMARY KEY,
        symbol TEXT NOT NULL,
        exchange TEXT NOT NULL,
        lotsize INTEGER NOT NULL,
        profit REAL NOT NULL,
        createddate DATETIME DEFAULT CURRENT_TIMESTAMP
    );''')



# conn.execute('''ALTER TABLE hight_achieve ADD COLUMN token TEXT''')

def insertdata(data):
    query = 'INSERT INTO ORDERCONDITION(condition) VALUES(?);'
    conn.execute(query,(data,))
    conn.commit()

def inserttokenns(symbol,exchange,token,lotsize,ltp,profit):
    date = datetime.datetime.now()
    query = 'INSERT INTO ordertoken(symbol,exchange,token,lotsize,ltp,profit,createddate) VALUES(?,?,?,?,?,?,?);'
    conn.execute(query,(symbol,exchange,token,lotsize,ltp,profit,date))
    conn.commit()

def inserthigh_cross(id,symbol,exchange,token,lotsize,profit):
    date = datetime.datetime.now()
    query = 'INSERT INTO hight_achieve(id,symbol,exchange,token,lotsize,profit,createddate) VALUES(?,?,?,?,?,?,?);'
    conn.execute(query,(id,symbol,exchange,token,lotsize,profit,date))
    conn.commit()



def insert_place_order(symbol, exchange, token, delta, closeprice, ltp, target, stoploss, lotsize, profit):
    date = datetime.datetime.now()
    query = '''INSERT INTO placeorder(symbol, exchange, token, delta, closeprice, ltp, target, stoploss, lotsize, profit, createddate)
               VALUES(?,?,?,?,?,?,?,?,?,?,?);'''
    conn.execute(query, (symbol, exchange, token, delta, closeprice, ltp, target, stoploss, lotsize, profit, date))
    conn.commit()

def insertcryptoorder(symbol,exchange,token,lotsize,ltp,profit):
    date = datetime.datetime.now()
    query = 'INSERT INTO cryptoorderbook(symbol,exchange,token,lotsize,ltp,profit,createddate) VALUES(?,?,?,?,?,?,?);'
    conn.execute(query,(symbol,exchange,token,lotsize,ltp,profit,date))
    conn.commit()

def createupport(time,support,symbol):
    query = 'INSERT INTO supportset(timeframe,supportlist,symboltype) VALUES(?,?,?);'
    conn.execute(query,(time,support,symbol,))
    conn.commit()

def insertscript(data,ordertype):
    query = 'INSERT INTO intradayorder(script,ordertype) VALUES(?,?);'
    conn.execute(query,(data,ordertype,))
    conn.commit()

def updatedata(id,data):
    query = 'UPDATE ORDERCONDITION SET condition = ? WHERE id = ?'
    conn.execute(query,(data,id))
    conn.commit()



def updatesupport(id,data):
    query = 'UPDATE supportset SET supportlist = ? WHERE id = ?'
    conn.execute(query,(data,id))
    conn.commit()

def updateorderplace(id,lotsize,profit):
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cursor = conn.cursor()
    query = 'UPDATE ordertoken SET lotsize = ?,profit  = ? WHERE id = ?'
    cursor.execute(query,(lotsize,profit,id))
     # Commit the transaction
    conn.commit()

    # Close the connection
    conn.close()


def update_high(id,profit):
    date = datetime.datetime.now()
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cursor = conn.cursor()
    query = '''
        UPDATE hight_achieve
        SET profit = ?,createddate = ? WHERE id = ?;
        '''
    cursor.execute(query, (profit, date, id))
    conn.commit()
     # Commit the transaction
    conn.commit()

    # Close the connection
    conn.close()

def updatecrypto(id,lotsize,profit):
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cursor = conn.cursor()
    query = 'UPDATE cryptoorderbook SET lotsize = ?,profit  = ? WHERE id = ?'
    cursor.execute(query,(lotsize,profit,id))
     # Commit the transaction
    conn.commit()

    # Close the connection
    conn.close()


#updatedata(1,'2')
def fetchdata():
    fetch = conn.execute('SELECT * FROM ORDERCONDITION')
    data = []
    for row in fetch:
        data.append(row)
        print(data)
    return data

def orderbook():
    fetch = conn.execute('SELECT * FROM intradayorder')
    data = []
    for id,script,ordertype in fetch:
        addvalue = {
            'script':script,
            'ordertype':ordertype
        }
        data.append(addvalue)
    print(data)
    return data

def fetchtokennbook():
    fetch = conn.execute('SELECT * FROM ordertoken')
    data = []
    for id,symbol,exchange,token,lotsize,ltp,profit,createddate in fetch:
        addvalue = {
            'id':id,
            'script':symbol,
            'token':token,
            'lotsize':lotsize,
            'ltp':ltp,
            'profit':profit,
            'createddate':createddate
        }
        data.append(addvalue)
    print(data)
    return data

def fetchtcryptoorderbook():
    fetch = conn.execute('SELECT * FROM cryptoorderbook')
    data = []
    for id,symbol,exchange,token,lotsize,ltp,profit,createddate in fetch:
        addvalue = {
            'id':id,
            'script':symbol,
            'token':token,
            'lotsize':lotsize,
            'ltp':ltp,
            'profit':profit,
            'createddate':createddate
        }
        data.append(addvalue)
    print(data)
    return data


def fetchtokennbook():
    fetch = conn.execute('SELECT * FROM ordertoken')
    data = []
    for id,symbol,exchange,token,lotsize,ltp,profit,createddate in fetch:
        addvalue = {
            'id':id,
            'script':symbol,
            'token':token,
            'lotsize':lotsize,
            'ltp':ltp,
            'profit':profit,
            'createddate':createddate
        }
        data.append(addvalue)
    # print(data)
    return data

def fetchsupport():
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cursor = conn.cursor()
    fetch = cursor.execute('SELECT * FROM ordertoken')
    data = []
    for id,symbol,exchange,token,lotsize,ltp,profit,createddate in fetch:
        addvalue = {
            'id':id,
            'script':symbol,
            'token':token,
            'lotsize':lotsize,
            'ltp':ltp,
            'profit':profit,
            'createddate':createddate
        }
        data.append(addvalue)
    # print(data)
    return data

def fetch_all_orders():
    conn = sqlite3.connect('database.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Enables dict-like row access
    query = 'SELECT * FROM placeorder ORDER BY createddate DESC'
    cursor = conn.execute(query)
    rows = cursor.fetchall()

    orders = [dict(row) for row in rows]
    return orders

def fetch_order_by_id(order_id):
    conn = sqlite3.connect('database.db', check_same_thread=False)
    query = 'SELECT * FROM placeorder WHERE id = ?'
    cursor = conn.execute(query, (order_id,))
    return cursor.fetchone()

def fetchsupportforweb():
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cursor = conn.cursor()
    fetch = conn.execute('SELECT * FROM ordertoken')
    data = []
    for id,symbol,exchange,token,lotsize,ltp,profit,createddate in fetch:
        addvalue = {
            'id':id,
            'script':symbol,
            'token':token,
            'lotsize':lotsize,
            'ltp':ltp,
            'profit':profit,
            'createddate':createddate
        }
        data.append(addvalue)
    return data

def fetchhightaregt():
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cursor = conn.cursor()
    fetch = conn.execute('SELECT * FROM hight_achieve')
    data = []
    for id,symbol,exchange,token,ltp,profit,createddate in fetch:
        addvalue = {
            'id':id,
            'script':symbol,
            'token':token,
            'ltp':ltp,
            'profit':profit,
            'createddate':createddate
        }
        data.append(addvalue)
        print(data)
    return data


def fetchhightaregtid(id):
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cursor = conn.cursor()
    query = "SELECT id, symbol, exchange, ltp, profit, createddate, token FROM hight_achieve WHERE id = ?;"

    try:
        cursor.execute(query, (id,))
        rows = cursor.fetchall()  # Fetch all matching rows
        data = []

        for row in rows:
            addvalue = {
                'id': row[0],
                'script': row[1],
                'token': row[6],
                'ltp': row[3],
                'profit': row[4],
                'createddate': row[5]
            }
            data.append(addvalue)

        return data

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        conn.close()  # Ensure connection is closed

def deletedata(delete_id):
    query = 'DELETE FROM ORDERCONDITION WHERE id = ?;'
    conn.execute(query, (delete_id,))
    conn.commit()

def delete_place_order(order_id):
    query = 'DELETE FROM placeorder WHERE id = ?'
    conn.execute(query, (order_id,))
    conn.commit()

def deletesupport(delete_id):
    query = 'DELETE FROM supportset WHERE id = ?;'
    conn.execute(query, (delete_id,))
    conn.commit()

def deletescript(delete_id):
    query = 'DELETE FROM intradayorder WHERE script = ?;'
    conn.execute(query, (delete_id,))
    conn.commit()

def deleteordertoken(delete_id):
    query = 'DELETE FROM ordertoken WHERE id = ?;'
    conn.execute(query, (delete_id,))
    conn.commit()

def deletecrypto(delete_id):
    query = 'DELETE FROM cryptoorderbook WHERE id = ?;'
    conn.execute(query, (delete_id,))
    conn.commit()





def get_data(script):
    query = 'SELECT * FROM intradayorder WHERE script = ?;'
    fetch = conn.execute(query, (script,))
    data = []
    for row in fetch:
        data.append(row)
        print(data)
    return data

#deletescript('NCC-EQ')
#get_data('abc')
#insertscript('RALLIS-EQ','BUY')
#insertscript('abc')
#fetchdata()
# orderbook()
# def deletealldata():
#      fetch = fetchsupport()
#      for item in fetch:
#         deletesupport(item['id'])

#createupport("30min","24832.6 24723.7 23893.7 24999.75 24971.75 25078.3 25030.85 24382.6","NIFTY")
#deletesupport(4)
#deletealldata()
# fetchsupport()
#inserttokenns('nifty','nfo','26000','50','135','49076')
# fetchtokennbook()

# def checkcondition():
#      symbol = 'NIFTY'
#      fetchdata = fetchtokennbook()
#      filteristoken = [item for item in fetchdata if re.match(r'^[A-Za-z]+', item['script']).group() == symbol and item['lotsize'] == 0]
#      print('filter',filteristoken)
#
# checkcondition()

# deleteordertoken(2071)

def createmaxprofit(id,symbol,token,lotsize,profit_or_loss):
    fetch = fetchhightaregtid(id)
    if len(fetch) == 0:
        inserthigh_cross(id,symbol,token,lotsize,profit_or_loss)
    else:
        update_high(id,profit_or_loss)

def checkprofit():
    fetch = fetchsupportforweb()
    profit = [item['profit'] for item in fetch]
    total_profit = extract_and_sum_profits(profit)
    print(total_profit)
    return total_profit



def extract_and_sum_profits(data: List[Union[str, float]]) -> float:
    total_profit = 0.0

    # Regular expression to extract profit values from strings
    profit_pattern = re.compile(r'profit\s*-\s*(-?\d+(\.\d+)?)')

    for item in data:
        if isinstance(item, str):
            # Find profit values in the string
            matches = profit_pattern.findall(item)
            for match in matches:
                total_profit += float(match[0])
        elif isinstance(item, (int, float)):
            total_profit += float(item)

    return total_profit


# checkprofit()

# checkprofit# deleteordertoken(41)
# def deletestock():
#      fetch = fetchsupportforweb()
#      for item in fetch:
#          if item['script'] == 'BANKNIFTY04SEP2451400PE':
#              deleteordertoken(item['id'])
# #
# #
# #
# deletestock()
# deleteordertoken(152)

# insertcryptoorder('BTCUSD','nfo','26000','50','135','0')
# fetchtcryptoorderbook()

# insert_place_order('AAPL', 'NASDAQ', '123456', '1.5', 150.25, 152.30, 155.00, 148.00, 10, 500.00)
# delete_place_order(1)
# fetch_all_orders()
# updateorderplace(40472,-20,0)
# fetchsupport()



def deleteall(symbol):
    fetchdata = fetchsupportforweb()
    filteristoken = [item for item in fetchdata if re.match(r'^[A-Za-z]+', item['script']).group() == symbol and item['lotsize'] > 0]
    print(filteristoken)
    fetch = fetchsupportforweb()
    array = []
    for item in fetch:
        if item['lotsize'] < 0:
            deleteordertoken(item['id'])
            array.append(item)
#deleteall('BANKNIFTY')

# inserthigh_cross(3,'abc','nse','123','lotsize',200)
# fetchhightaregtid(3)



# def todayorderdata():
#     date = datetime.datetime.now()
#     fetch = fetchsupportforweb()
#     order = 0
#     totalprofit = 0
#     stoplossorder = 0
#     returndata = {}
#
#     for item in fetch:
#         if item['createddate']:
#             currentdate = datetime.datetime.strptime(item['createddate'], "%Y-%m-%d %H:%M:%S.%f").date()
#             if date.date() == currentdate:
#                 order += 1
#                 profit = item.get('profit')
#
#                 if profit:
#                     try:
#                         # If profit is a number (not a string), use directly
#                         if isinstance(profit, (int, float)):
#                             floatvalue = float(profit)
#                         else:
#                             # Else extract from string using regex
#                             pattern = r"Profit/Loss:\s*(-?\d+\.\d+)"
#                             match = re.search(pattern, profit)
#                             if not match:
#                                 continue  # Ignore this case if pattern doesn't match
#                             floatvalue = float(match.group(1))
#
#                         totalprofit += floatvalue
#                         stoplossorder += 1 if floatvalue < 0 else 0
#                     except Exception as e:
#                         print(f"Skipping item due to error: {e}")
#                         continue
#
#     returndata['totalOrder'] = order
#     returndata['stoplossOrder'] = stoplossorder
#     returndata['totalProfit'] = totalprofit
#     return returndata


def todayorderdata():
    date = datetime.datetime.now()
    formatted_data = fetchsupportforweb()
    totalprofit = 0.0
    today = datetime.date.today()
    order = 0
    stoplossorder = 0
    returndata = {}

    for item in formatted_data:
        try:
            created_date = item.get('createddate')

            if created_date and created_date != 'None':
                item_date = created_date.split(" ")[0]

                if item_date == str(today):
                    order += 1
                    profit_or_loss = item.get('profit', 'N/A')

                    if profit_or_loss != 'N/A':
                        pattern = r"Profit/Loss:\s*(-?\d+\.\d+)"
                        match = re.search(pattern, profit_or_loss)
                        if match:
                            floatvalue = float(match.group(1))
                            totalprofit += floatvalue
                            if floatvalue < 0:
                                stoplossorder += 1

        except (ValueError, TypeError) as e:
            print()

    returndata['totalOrder'] = order
    returndata['stoplossOrder'] = stoplossorder
    returndata['totalProfit'] = round(totalprofit, 2)

    return returndata

import datetime
import re
from collections import defaultdict

def month_order_data():
    today = datetime.date.today()
    formatted_data = fetchsupportforweb()

    totalprofit = 0.0
    total_order = 0
    total_stoploss_order = 0
    daily_summary = defaultdict(lambda: {'orders': 0, 'stoplosses': 0, 'profit': 0.0})

    for item in formatted_data:
        try:
            created_date = item.get('createddate')
            if created_date and created_date != 'None':
                # Convert to datetime object
                item_datetime = datetime.datetime.strptime(created_date, "%Y-%m-%d %H:%M:%S.%f")

                if item_datetime.month == today.month and item_datetime.year == today.year:
                    day_key = item_datetime.date().isoformat()  # Format: 'YYYY-MM-DD'
                    total_order += 1
                    daily_summary[day_key]['orders'] += 1

                    profit_or_loss = item.get('profit', 'N/A')
                    if profit_or_loss != 'N/A':
                        pattern = r"Profit/Loss:\s*(-?\d+\.\d+)"
                        match = re.search(pattern, profit_or_loss)
                        if match:
                            floatvalue = float(match.group(1))
                            totalprofit += floatvalue
                            daily_summary[day_key]['profit'] += floatvalue
                            if floatvalue < 0:
                                total_stoploss_order += 1
                                daily_summary[day_key]['stoplosses'] += 1

        except (ValueError, TypeError):
            continue

    returndata = {
        'totalOrder': total_order,
        'stoplossOrder': total_stoploss_order,
        'totalProfit': round(totalprofit, 2),
        'dailyBreakdown': {
            date: {
                'orders': data['orders'],
                'stoplosses': data['stoplosses'],
                'profit': round(data['profit'], 2)
            }
            for date, data in sorted(daily_summary.items())
        }
    }

    return returndata


# print(month_order_data())
