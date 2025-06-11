import pandas as pd
import matplotlib.pyplot as plt
from tvDatafeed import TvDatafeed, Interval
import matplotlib.dates as mdates

# Function to create Renko bricks
def create_renko(data, brick_size):
    data['Renko'] = 0
    data['Direction'] = ''
    previous_close = data['close'].iloc[0]
    renko_price = previous_close

    for i in range(1, len(data)):
        price_diff = data['close'].iloc[i] - renko_price

        if price_diff >= brick_size:
            data.loc[data.index[i], 'Renko'] = 1  # Up brick
            data.loc[data.index[i], 'Direction'] = 'Up'
            renko_price += brick_size
        elif price_diff <= -brick_size:
            data.loc[data.index[i], 'Renko'] = -1  # Down brick
            data.loc[data.index[i], 'Direction'] = 'Down'
            renko_price -= brick_size

    # Filter out rows where Renko is 0
    renko_data = data[data['Renko'] != 0].reset_index(drop=True)

    return renko_data

# Initialize tvDatafeed and login to TradingView
tv = TvDatafeed()

# Fetch NIFTY 5-minute data from NSE exchange
data = tv.get_hist(symbol='NIFTY', exchange='NSE', interval=Interval.in_5_minute, n_bars=100)

# Check if data is fetched correctly
if data.empty:
    print("No data retrieved. Please check the symbol and your internet connection.")
else:
    # Define brick size (you can adjust this based on your needs)
    brick_size = 10  # Example: 10 points per brick

    # Generate Renko data
    renko_data = create_renko(data, brick_size)

    # Plot Renko chart
    plt.figure(figsize=(12, 8))

    # Set up the plot with better formatting
    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    plt.xticks(rotation=45)

    for i in range(len(renko_data)):
        if renko_data['Renko'][i] == 1:
            plt.bar(renko_data.index[i], renko_data['close'][i], width=0.4, color='green', align='center', edgecolor='black')
        elif renko_data['Renko'][i] == -1:
            plt.bar(renko_data.index[i], renko_data['close'][i], width=0.4, color='red', align='center', edgecolor='black')

    plt.title('Renko Chart (NIFTY 5min)')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.show()
