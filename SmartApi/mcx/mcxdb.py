import sqlite3
import datetime

# Connect to SQLite database
conn = sqlite3.connect('ordertoken.db', check_same_thread=False)
cursor = conn.cursor()

# Drop and recreate table with updated_at column
# cursor.execute('DROP TABLE IF EXISTS ordertoken')

cursor.execute('''
CREATE TABLE IF NOT EXISTS ordertoken (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT,
    exchange TEXT,
    token TEXT,
    lotsize INTEGER,
    ltp REAL,
    profit REAL,
    updated_at TIMESTAMP
);
''')
conn.commit()

# 2. Insert data
def inserttokenns(symbol, exchange, token, lotsize, ltp, profit):
    now = datetime.datetime.now()
    query = '''
    INSERT INTO ordertoken(symbol, exchange, token, lotsize, ltp, profit, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    '''
    conn.execute(query, (symbol, exchange, token, lotsize, ltp, profit, now))
    conn.commit()
    print("✅ Data inserted.")

# 3. Fetch all data
def fetch_all_tokens():
    cursor.execute('SELECT * FROM ordertoken')
    fetch = cursor.fetchall()

    data = []
    for id, symbol, exchange, token, lotsize, ltp, profit, createddate in fetch:
        addvalue = {
            'id': id,
            'script': symbol,
            'exchange':exchange,
            'token': token,
            'lotsize': lotsize,
            'ltp': ltp,
            'profit': profit,
            'createddate': str(createddate)
        }
        data.append(addvalue)
    print(data)
    return data
# 4. Delete by ID
def delete_token_by_id(order_id):
    cursor.execute('DELETE FROM ordertoken WHERE id = ?', (order_id,))
    conn.commit()
    print(f"🗑️ Deleted record with ID {order_id}.")

# 5. Update lotsize, profit and updated_at
def updateorderplace(id, lotsize, profit):
    now = datetime.datetime.now()
    query = '''
    UPDATE ordertoken 
    SET lotsize = ?, profit = ?, updated_at = ?
    WHERE id = ?;
    '''
    cursor.execute(query, (lotsize, profit, now, id))
    conn.commit()
    print(f"🔁 Updated record ID {id} with lotsize={lotsize}, profit={profit}, updated_at={now}")

# delete_token_by_id(2)
# fetch_all_tokens()
# # ✅ Example usage
# if __name__ == "__main__":
    # # Insert sample
    # inserttokenns("INFY", "NSE", "INFY456", 1, 1500.00, 120.0)
    #
    # # Fetch current records
    # print("\n📋 Records:")

    #
    # # Update record
    # updateorderplace(1, 2, 180.0)
    #
    # # Verify update
    # print("\n📋 After Update:")
    # fetch_all_tokens()

