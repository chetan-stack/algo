# from tvDatafeed import TvDatafeed, Interval
import pandas as pd
import numpy as np

# ✅ Step 1: Initialize tvDatafeed
# tv = TvDatafeed()
#
# # ✅ Step 2: Fetch historical data (Example: NIFTY 1-minute chart)
# symbol = "Nifty"
# exchange = "NSE"
# df = tv.get_hist(symbol=symbol, exchange=exchange, interval=Interval.in_1_minute, n_bars=100)
def checktrend(df):
    # ✅ Step 3: Ensure data is not empty
    # if df is None or df.empty:
    #     print("No data fetched. Check symbol or login status.")
    #     exit()
    #
    # # ✅ Step 4: Calculate Wick and Body Sizes
    # df["Body"] = abs(df["close"] - df["open"])
    # df["Upper Wick"] = df["high"] - df[["open", "close"]].max(axis=1)
    # df["Lower Wick"] = df[["open", "close"]].min(axis=1) - df["low"]
    # df["Total Wick"] = df["Upper Wick"] + df["Lower Wick"]
    # df["Noise Ratio"] = df["Total Wick"] / df["Body"].replace(0, np.nan)  # Avoid divide by zero
    #
    # # ✅ Step 5: Define Market Noise vs Trend
    # noise_threshold = 1.5  # If wick is 1.5x or more of body, it's noisy
    # df["Market Noise"] = df["Noise Ratio"] > noise_threshold
    # df["Trending"] = df["Noise Ratio"] < 1.0  # If wick is small relative to body, it's trending
    #
    # # ✅ Step 6: Identify Range-bound Market (Sideways)
    # df["Prev High"] = df["high"].rolling(5).max().shift(1)
    # df["Prev Low"] = df["low"].rolling(5).min().shift(1)
    # df["Body Avg"] = df["Body"].rolling(5).mean().shift(1)
    # df["Sideways"] = (df["Body"] < df["Body Avg"] * 0.7) & (df["high"] < df["Prev High"]) & (df["low"] > df["Prev Low"])
    #
    # # ✅ Step 7: Analyze last 5 candles for confirmation
    # df["Noise Count"] = df["Market Noise"].rolling(5).sum()
    # df["Trend Count"] = df["Trending"].rolling(5).sum()
    # df["Sideways Count"] = df["Sideways"].rolling(5).sum()
    #
    # # ✅ Step 8: Define Market Condition (Noise, Trending, Sideways, Mixed)
    # df["Market Condition"] = np.where(df["Noise Count"] >= 3, "Noise",
    #                          np.where(df["Trend Count"] >= 3, "Trending",
    #                          np.where(df["Sideways Count"] >= 3, "Sideways", "Mixed")))
    # # ✅ Step 9: Print last 10 rows with Market Condition
    # print(df[["open", "close", "high", "low", "Noise Ratio", "Market Condition"]].tail(30))
    # return df["Market Condition"].values[-1]
    if df is None or df.empty:
            df["Market Condition"] = 'no data'

    df["Body"] = abs(df["close"] - df["open"])
    df["High-Low"] = df["high"] - df["low"]
    window_size = 10
    df["Max High"] = df["high"].rolling(window_size).max()
    df["Min Low"] = df["low"].rolling(window_size).min()
    df["Range"] = df["Max High"] - df["Min Low"]
    df["Sideways"] = (df["Range"] < df["Range"].rolling(window_size).mean()) & \
                     (df["Body"].rolling(window_size).mean() < df["Body"].rolling(window_size).mean().shift(1))
    df["Trending"] = (df["Range"] > df["Range"].rolling(window_size).mean() * 1) & \
                     (df["Body"].rolling(window_size).mean() > df["Body"].rolling(window_size).mean().shift(
                         1) * 1)
    df["Market Condition"] = np.where(df["Sideways"], "Sideways",
                                      np.where(df["Trending"], "Trending", "Mixed"))
    df["Market Condition"] = df["Market Condition"].iloc[-1]
    # print(df)
    return df["Market Condition"].values[-1]

