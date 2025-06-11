import pandas_datareader as pdr
import datetime

start_date = datetime.datetime.now() - datetime.timedelta(days=30)
end_date = datetime.datetime.now()

# Retrieve historical data for Nifty50
try:
    nifty_data = pdr.get_data_yahoo('SPY', start=start_date, end=end_date)
except Exception as e:
     print(e)


# Print the last 10 rows of the DataFrame
print(nifty_data)