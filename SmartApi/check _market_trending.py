
import pandas as pd
import pandas_ta as ta
from tvDatafeed import TvDatafeed, Interval

# Initialize TradingView data feed
tv = TvDatafeed()



# Fetch NIFTY 50 data for the last 3 days (1-minute interval)
def fetch_nifty_data():
    hist = tv.get_hist(symbol='NIFTY', exchange='NSE', interval=Interval.in_1_minute, n_bars=3 * 390)
    df = pd.DataFrame(hist, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
    df['date'] = pd.to_datetime(df['date'])
    return df

# Function to identify market condition
def identify_market_condition(df):
    # Compute RSI (Relative Strength Index)
    df['RSI'] = df.ta.rsi(length=14)

    # Compute ADX (Average Directional Index)
    adx = df.ta.adx(length=14)
    df['ADX'] = adx['ADX_14']

    # Compute Bollinger Bands width
    bb = df.ta.bbands(length=20, std=2)
    df['BB_Width'] = bb['BBU_20_2.0'] - bb['BBL_20_2.0']

    # Compute Volume Moving Average (10-period)
    df['Volume_MA'] = df['volume'].rolling(window=10).mean()

    # Initialize market signal column
    df['Signal'] = "Unclear"

    # Identify Sideways Market
    sideways_condition = (df['ADX'] < 20) & (df['RSI'].between(40, 60)) & (df['BB_Width'] < df['BB_Width'].mean())
    df.loc[sideways_condition, 'Signal'] = "Sideways"

    # Identify Trending Market
    trending_condition = (df['ADX'] > 25) & ((df['RSI'] > 70) | (df['RSI'] < 30))
    df.loc[trending_condition, 'Signal'] = "Trending"

    # Identify Possible False Breakout
    false_breakout_condition = trending_condition & (df['volume'] < df['Volume_MA'])
    df.loc[false_breakout_condition, 'Signal'] = "Possible False Breakout"

    return df



# Run analysis
df = fetch_nifty_data()
df = identify_market_condition(df)
print(df[df['Signal'] == "Trending"][['close', 'Signal']].tail())
