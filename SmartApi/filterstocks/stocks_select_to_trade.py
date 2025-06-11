import time
import datetime
from tvDatafeed import TvDatafeed, Interval
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
username = 'YourTradingViewUsername'
password = 'YourTradingViewPassword'

symbols = [


        "AARTIIND",
        "ABB",
        "ABBOTINDIA",
        "ABCAPITAL",
        "ABFRL",
        "ACC",
        "ADANIENT",
        "ADANIPORTS",
        "ALKEM",
        "AMBUJACEM",
        "APOLLOHOSP",
        "APOLLOTYRE",
        "ASHOKLEY",
        "ASIANPAINT",
        "ASTRAL",
        "ATUL",
        "AUBANK",
        "AUROPHARMA",
        "AXISBANK",
        "BAJAJ-AUTO",
        "BAJAJFINSV",
        "BAJFINANCE",
        "BALKRISIND",
        "BALRAMCHIN",
        "BANDHANBNK",
        "BANKBARODA",
        "BATAINDIA",
        "BEL",
        "BERGEPAINT",
        "BHARATFORG",
        "BHARTIARTL",
        "BHEL",
        "BIOCON",
        "BOSCHLTD",
        "BPCL",
        "BRITANNIA",
        "BSOFT",
        "CANBK",
        "CANFINHOME",
        "CHAMBLFERT",
        "CHOLAFIN",
        "CIPLA",
        "COALINDIA",
        "COFORGE",
        "COLPAL",
        "CONCOR",
        "COROMANDEL",
        "CROMPTON",
        "CUB",
        "CUMMINSIND",
        "DABUR",
        "DALBHARAT",
        "DEEPAKNTR",
        "DIVISLAB",
        "DIXON",
        "DLF",
        "DRREDDY",
        "EICHERMOT",
        "ESCORTS",
        "EXIDEIND",
        "FEDERALBNK",
        "GAIL",
        "GLENMARK",
        "GMRINFRA",
        "GNFC",
        "GODREJCP",
        "GODREJPROP",
        "GRANULES",
        "GRASIM",
        "GUJGASLTD",
        "HAL",
        "HAVELLS",
        "HCLTECH",
        "HDFCAMC",
        "HDFCBANK",
        "HDFCLIFE",
        "HEROMOTOCO",
        "HINDALCO",
        "HINDCOPPER",
        "HINDPETRO",
        "HINDUNILVR",
        "ICICIBANK",
        "ICICIGI",
        "ICICIPRULI",
        "IDEA",
        "IDFC",
        "IDFCFIRSTB",
        "IEX",
        "IGL",
        "INDHOTEL",
        "INDIACEM",
        "INDIAMART",
        "INDIGO",
        "INDUSINDBK",
        "INDUSTOWER",
        "INFY",
        "IOC",
        "IPCALAB",
        "IRCTC",
        "ITC",
        "JINDALSTEL",
        "JKCEMENT",
        "JSWSTEEL",
        "JUBLFOOD",
        "KOTAKBANK",
        "LALPATHLAB",
        "LAURUSLABS",
        "LICHSGFIN",
        "LT",
        "LTF",
        "LTIM",
        "LTTS",
        "LUPIN",
        "M&M",
        "M&MFIN",
        "MANAPPURAM",
        "MARICO",
        "MARUTI",
        "MCDOWELL-N",
        "MCX",
        "METROPOLIS",
        "MFSL",
        "MGL",
        "MOTHERSON",
        "MPHASIS",
        "MRF",
        "MUTHOOTFIN",
        "NATIONALUM",
        "NAUKRI",
        "NAVINFLUOR",
        "NESTLEIND",
        "NMDC",
        "NTPC",
        "OBEROIRLTY",
        "OFSS",
        "ONGC",
        "PAGEIND",
        "PEL",
        "PERSISTENT",
        "PETRONET",
        "PFC",
        "PIDILITIND",
        "PIIND",
        "PNB",
        "POLYCAB",
        "POWERGRID",
        "PVRINOX",
        "RAMCOCEM",
        "RBLBANK",
        "RECLTD",
        "RELIANCE",
        "SAIL",
        "SBICARD",
        "SBILIFE",
        "SBIN",
        "SHREECEM",
        "SHRIRAMFIN",
        "SIEMENS",
        "SRF",
        "SUNPHARMA",
        "SUNTV",
        "SYNGENE",
        "TATACHEM",
        "TATACOMM",
        "TATACONSUM",
        "TATAMOTORS",
        "TATAPOWER",
        "TATASTEEL",
        "TCS",
        "TECHM",
        "TITAN",
        "TORNTPHARM",
        "TRENT",
        "TVSMOTOR",
        "UBL",
        "ULTRACEMCO",
        "UPL",
        "VEDL",
        "VOLTAS",
        "WIPRO",
        "ZEEL",
        "ZYDUSLIFE"


]

def main():
  for symbol in symbols:
    fechdata(symbol)
    time.sleep(1)

def fechdata(interval):
    print(interval)
    for symbol in symbols:
        try:
              tv = TvDatafeed(username, password)
              # index
              nifty_index_data = tv.get_hist(symbol=symbol,exchange='NSE',interval=interval,n_bars=100)

              resistancelevel = []
              supportlevel = []
              df = nifty_index_data
              print(df)
              itemclose = df.close.values[-1]
              itemclose
              supports = df[df.low == df.low.rolling(10, center=True).min()].low
              resistances = df[df.high == df.high.rolling(10, center=True).min()].high
              supports
              level = pd.concat([supports,resistances])
              level = level[abs(level.diff()) > 10]
              print('data',level.diff())

              # mpf.plot(df,type='candle',hlines=level.to_list(),style='charles')
              registance_item = ''
              support_item = ''
              for a in level:

                if a > itemclose:
                  resistancelevel.append(a)
                  registance_item = max(resistancelevel, key=lambda x: x if x > itemclose else float('-inf'))

                else:
                  supportlevel.append(a)
                  support_item = max(supportlevel, key=lambda x: x if x < itemclose else float('-inf'))

              # File path
              file_path = "stocklistedwithsupport.txt"
              print(sorted(resistancelevel,reverse = True),'resistannce')
              print(sorted(supportlevel ,reverse=True),'support')
              print(registance_item,support_item)

              if df.low.values[-2] < int(support_item) and df.close.values[-1] > int(support_item) or df.high.values[-2] > int(registance_item) and df.close.values[-1] < int(registance_item):
                  # Append additional text to the file
                  with open(file_path, "a") as file:
                        file.write(f"{symbol}-{datetime.datetime.time()}-{interval},\n")
                  print(f"Additional text has been appended to {file_path}")

        except Exception as e:
                print(e)
        time.sleep(2)


# fechdata(Interval.in_30_minute)
