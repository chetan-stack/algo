# from alpha_vantage.timeseries import TimeSeries
# import matplotlib.pyplot as plt
#
# ts = TimeSeries(key='M4M49WSJI71HP2X4', output_format='pandas')
# # data = ts.get_intraday(symbol='NSE:NIFTY', interval='60min', outputsize='full')
# # data['4. close'].plot()
# # plt.title('Intraday Times Series for the NIFTY index')
# # plt.show()
#
# data = ts.get_intraday(symbol = 'NIFTY',interval = '1min')
# print(data[0])

import requests
import json

# Define the API key
api_key = "your_api_key_here"

# Define the list of stock symbols to retrieve data for
symbols = ["symbol1", "symbol2", ..., "symbolN"]

# Initialize a dictionary to store the stock data
stock_data = {}

# Loop through the list of symbols to retrieve the real-time data for each stock
for symbol in symbols:
    # Make a GET request to the Alpha Vantage API to get the real-time data for the stock
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
    response = requests.get(url)

    # Parse the JSON response into a Python dictionary
    data = json.loads(response.text)

    # Get the real-time data for the stock
    stock_data[symbol] = data["Global Quote"]

# Sort the stock data by percentage change to get the top gainers
top_gainers = sorted(stock_data.items(), key=lambda x: x[1]["09. change percent"], reverse=True)

# Print the top gainers
print("Top Gainers:")
for symbol, data in top_gainers:
    print(f"{symbol}: {data['09. change percent']}")
