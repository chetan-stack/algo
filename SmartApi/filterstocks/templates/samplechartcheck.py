import mplfinance as mpf
import pandas as pd
from datetime import datetime

# Create a sample DataFrame
data = {
    'Date': [datetime(2023, 1, 1), datetime(2023, 1, 2), datetime(2023, 1, 3), datetime(2023, 1, 4), datetime(2023, 1, 5)],
    'Open': [100, 101, 102, 103, 104],
    'High': [101, 102, 103, 104, 105],
    'Low': [99, 100, 101, 102, 103],
    'Close': [100.5, 101.5, 102.5, 103.5, 104.5],
    'Volume': [1000, 1100, 1200, 1300, 1400]
}

df = pd.DataFrame(data)
df.set_index('Date', inplace=True)

# Plot using mplfinance
mpf.plot(df, type='candle', volume=True)
