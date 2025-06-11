import pandas as pd
import pandas_ta as ta
from pandas_datareader import data as pdr
from datetime import datetime, timedelta
import yfinance as yf

# Define a function to get the average true range of a stock
def get_atr(df, period=14):
    atr_value = ta.atr(df.High, df.Low, df.Close, length=period)
    return atr_value

# Define a function to get the historical volatility of a stock
def get_hv(df, period=30):
    hv = ta.volatility.historical(df.close, window=period, annualize=False)
    return hv

# Define a function to filter intraday highly volatile stocks
def get_intraday_highly_volatile_stocks(nse_stocks, date, lookback_days=30):
    results = []
    for stock in nse_stocks['SYMBOL']:
        # Load historical data using pandas_datareader
        try:
            yf.pdr_override()  # Override pandas_datareader's default method
            df = pdr.get_data_yahoo(stock, start=date - timedelta(days=lookback_days), end=date, interval='1m')
        except ValueError:
            continue

        # Calculate average true range and historical volatility
        atr_value = get_atr(df)
        hv = get_hv(df)

        # Check if the stock is highly volatile
        if hv.tail(1).values[0] > atr_value.tail(1).values[0]:
            results.append(stock)
    return results

# Example usage
nse_stocks = pd.read_csv('EQUITY_L.csv')
date = datetime.now().date()
results = get_intraday_highly_volatile_stocks(nse_stocks, date)
print(results)
