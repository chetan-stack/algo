import pandas as pd
import requests
from bs4 import BeautifulSoup as bs

url = "https://chartink.com/screener/process"
condition = {
    'top-gainers-and-losers':"( {cash} ( latest volume > 100000 and latest open > 10 and latest open < 500 ) ) ",
    '15minute-stock-breakouts':"( {33619} ( [0] 15 minute close > [-1] 15 minute supertrend( 7,3 ) and [0] 15 minute volume > [0] 15 minute sma( volume,20 ) ) )",
    'intradaystock':"( {cash} ( [0] 10 minute sma( close,8 ) > [-1] 10 minute sma( close,34 ) and [0] 15 minute close > [0] 15 minute sma( close,200 ) and latest macd line( 12,26,9 ) >= 0.25 and latest volume > 500000 and latest close > 100 and latest rsi( 14 ) > 40 and latest rsi( 14 ) < 60 and [0] 15 minute volume > [0] 15 minute sma( close,20 ) * 1.5 ) ) ",
    'intradaystocksell':"( {cash} ( latest rsi( 14 ) < 52 and 1 day ago  rsi( 14 ) >= 52 and latest close <= 1 day ago parabolic sar( 0.02,0.02,0.2 ) and latest stochrsi( 14 ) <= 1 day ago stochrsi( 14 ) and latest cci( 20 ) <= 1 day ago cci( 20 ) and latest williams %r( 14 ) <= 1 day ago williams %r( 14 ) ) ) ",
    'pennystocks':'( {cash} ( latest close <= 20 and latest open >= 5 ) ) ',
    "weekly-value-investing-king-research":"( {33489} ( weekly open >= weekly ema( weekly close , 20 ) and weekly rsi( 14 ) < 65 and weekly rsi( 14 ) >= 60 ) ) ",
    "penny-stocks-strong-fundamentals":'( {cash} ( yearly book value > 0 and reserves > 0 and net profit[yearly] > 0 and total loans = 0 and latest volume >= 150000 and market cap >= 1800 and latest close <= 60 ) )',
    'fundamentally-strong-stocks':'( {cash} ( latest close < yearly book value and dividend > 0 and net profit[yearly] > 0 and net profit[quarter] > 0 ) ) ',
    'support-and-resistance-levels':'( {33489} ( 2 * ( ( 1 day ago high + 1 day ago low + 1 day ago close ) / 3 ) - 1 day ago low < latest close and( 1 day ago high + 1 day ago low + 1 day ago close ) / 3 < latest close and latest open >= 110 and latest open <= 600 and latest volume >= 300000 and [0] 10 minute close >= latest ema( close,13 ) ) ) ',
    'swing-trading-stock':'( {cash} ( latest close > latest sma( close,200 ) and latest close > latest sma( close,100 ) and latest volume > 200000 and [0] 1 hour close > [0] 1 hour sma( close,100 ) and latest close < 1 day ago close ) ) ',
    'fii-invested-stocks': '( {33489} ( quarterly foreign institutional investors percentage > 1 quarter ago foreign institutional investors percentage and 1 quarter ago foreign institutional investors percentage > 2 quarter ago foreign institutional investors percentage and 2 quarter ago foreign institutional investors percentage > 3 quarter ago foreign institutional investors percentage and latest close > 200 ) ) ',
    'fii-dii-buying':'( {cash} ( ( {cash} ( quarterly indian promoter and group percentage > 1 quarter ago indian promoter and group percentage and quarterly foreign institutional investors percentage > 1 quarter ago foreign institutional investors percentage ) ) and( {cash} ( latest close > latest max( 250 , latest high ) * 0.90 ) ) and( {cash} ( latest ema( latest close , 20 ) > latest ema( latest close , 50 ) and latest ema( latest close , 50 ) > latest ema( latest close , 100 ) and latest ema( latest close , 100 ) > latest ema( latest close , 150 ) and latest ema( latest close , 150 ) > latest ema( latest close , 200 ) and weekly close > 1 week ago ema( 1 week ago close , 20 ) and earning per share[eps] > 0 ) ) ) ) '
}
# condition = "( {33619} ( [0] 15 minute close > [-1] 15 minute supertrend( 7,3 ) and [0] 15 minute volume > [0] 15 minute sma( volume,20 ) ) )"
def get_data(condition):
  with requests.session() as s:
    r_data = s.get(url)
    soup = bs(r_data.text, 'html.parser')
    meta = soup.find_all('meta', {'name': "csrf-token"})[0]['content']
    # print(meta)
    header = {"x-csrf-token":meta}
    data = s.post(url,headers=header,data={'scan_clause':condition}).json()
    stocklist = pd.DataFrame(data['data'])
    stocklist_sorted = stocklist.sort_values(by='per_chg', ascending=False)
    assigndata = stocklist_sorted.to_dict(orient="records")
    # print(stock    # print(assigndata)list_sorted)
    return assigndata
# get_data(condition['support-and-resistance-levels'])
