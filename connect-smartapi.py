from tvDatafeed import TvDatafeed, Interval
from SmartApi import SmartConnect #or from SmartApi.smartConnect import SmartConnect

username = 'YourTradingViewUsername'
password = 'YourTradingViewPassword'

tv = TvDatafeed(username, password)
nifty_index_data = tv.get_hist(symbol='NIFTY',exchange='NSE',interval=Interval.in_1_hour,n_bars=1000)

print(nifty_index_data)
