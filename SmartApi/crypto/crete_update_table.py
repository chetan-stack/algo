import datetime
import json
import re
import sqlite3
from typing import List, Union


conn = sqlite3.connect('database.db')
print(conn)





conn.execute('''CREATE TABLE IF NOT EXISTS cryptoorderbook(
        id INTEGER PRIMARY KEY,
        symbol TEXT NOT NULL,
        exchange TEXT NOT NULL,
        token TEXT NOT NULL,
        ltp REAL NOT NULL,
        lotsize INTEGER NOT NULL,
        profit REAL NOT NULL
    )''')




# conn.execute('''ALTER TABLE cryptoorderbook ADD COLUMN createddate timestamp''')



def insertcryptoorder(symbol,exchange,token,lotsize,ltp,profit):
    date = datetime.datetime.now()
    query = 'INSERT INTO cryptoorderbook(symbol,exchange,token,lotsize,ltp,profit,createddate) VALUES(?,?,?,?,?,?,?);'
    conn.execute(query,(symbol,exchange,token,lotsize,ltp,profit,date))
    conn.commit()





def updatecrypto(id,lotsize,profit):
    # conn = sqlite3.connect('database.db')
    # cursor = conn.cursor()
    query = 'UPDATE cryptoorderbook SET lotsize = ?,profit  = ? WHERE id = ?'
    conn.execute(query,(lotsize,profit,id))
    print(f"Updated record with id {id}: lotsize={lotsize}, profit={profit}")

     # Commit the transaction
    conn.commit()




def fetchtcryptoorderbook():
    fetch = conn.execute('SELECT * FROM cryptoorderbook')
    data = []
    for id,symbol,exchange,token,ltp,lotsize,profit,createddate in fetch:
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
    # print('data',data)
    return data

def fetchtcryptoorderbookweb():
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cursor = conn.cursor()

    fetch = cursor.execute('SELECT * FROM cryptoorderbook')
    data = []
    for id,symbol,exchange,token,ltp,lotsize,profit,createddate in fetch:
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
    # print('data',data)
    return data



def deletecrypto(delete_id):
    query = 'DELETE FROM cryptoorderbook WHERE id = ?;'
    conn.execute(query, (delete_id,))
    conn.commit()






# insertcryptoorder('BTCUSD','nfo','26000','50','135','0')
# fetchtcryptoorderbook()

def deleteall():
    fetch = fetchtcryptoorderbook()
    array = []
    for item in fetch:
        deletecrypto(item['id'])
# deleteall()
def lot():
    order_book = fetchtcryptoorderbook()
    filtered_orders = [entry for entry in order_book if entry['ltp'] > 0]
    return filtered_orders

def getcvon():
    fetchdata = fetchtcryptoorderbook()
    extractsymbol = 'BTC'
    filteristoken = [
        item for item in fetchdata
        if extractsymbol in item['script'] and int(item['lotsize']) == 0
    ]
    print('filteristoken',fetchdata,'len',len(filteristoken))

def updateall():
    fetchdata = fetchtcryptoorderbook()
    print(fetchdata)
    for item in fetchdata:
        updatecrypto(item['id'],0,item['profit'])

def todayorderdata():
    date = datetime.datetime.now()
    fetch = fetchtcryptoorderbookweb()
    order = 0
    totalprofit = 0
    stoplossorder = 0
    returndata = {}
    for item in fetch:
        if item['createddate']:
            currentdate = datetime.datetime.strptime(item['createddate'], "%Y-%m-%d %H:%M:%S.%f").date()
            if date.date() == currentdate:
                order += 1
                if item['profit']:

                    totalprofit += item['profit']
                    stoplossorder += 1 if item['profit'] < 0 else 0
    returndata['totalOrder'] = order
    returndata['stoplossOrder'] = stoplossorder
    returndata['totalProfit'] = totalprofit
    return returndata
# print(getcvon())
# updateall()
# deletecrypto(455)
# updatecrypto(439,0,0)

