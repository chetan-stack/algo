from flask import Flask, render_template, request
import pandas as pd
import mplfinance as mpf
from tvDatafeed import TvDatafeed, Interval
# import stocks_select_to_trade
import io
import base64
app = Flask(__name__)

# Replace with your TradingView credentials
username = 'YourTradingViewUsername'
password = 'YourTradingViewPassword'

tv = TvDatafeed(username, password)

# List of available symbols and their display names
symbols = {
    "NIFTY": 'NIFTY',
    "BANKNIFTY": 'BANKNIFTY',
    "AARTIIND": "Aarti Industries Limited",
    "ABB": "ABB India Limited",
    "ABBOTINDIA": "Abbott India Limited",
    "ABCAPITAL": "Aditya Birla Capital Limited",
    "ABFRL": "Aditya Birla Fashion and Retail Limited",
    "ACC": "ACC Limited",
    "ADANIENT": "Adani Enterprises Limited",
    "ADANIPORTS": "Adani Ports and Special Economic Zone Limited",
    "ALKEM": "Alkem Laboratories Limited",
    "AMBUJACEM": "Ambuja Cements Limited",
    "APOLLOHOSP": "Apollo Hospitals Enterprise Limited",
    "APOLLOTYRE": "Apollo Tyres Limited",
    "ASHOKLEY": "Ashok Leyland Limited",
    "ASIANPAINT": "Asian Paints Limited",
    "ASTRAL": "Astral Limited",
    "ATUL": "Atul Limited",
    "AUBANK": "AU Small Finance Bank Limited",
    "AUROPHARMA": "Aurobindo Pharma Limited",
    "AXISBANK": "Axis Bank Limited",
    "BAJAJ-AUTO": "Bajaj Auto Limited",
    "BAJAJFINSV": "Bajaj Finserv Limited",
    "BAJFINANCE": "Bajaj Finance Limited",
    "BALKRISIND": "Balkrishna Industries Limited",
    "BALRAMCHIN": "Balrampur Chini Mills Limited",
    "BANDHANBNK": "Bandhan Bank Limited",
    "BANKBARODA": "Bank of Baroda",
    "BATAINDIA": "Bata India Limited",
    "BEL": "Bharat Electronics Limited",
    "BERGEPAINT": "Berger Paints India Limited",
    "BHARATFORG": "Bharat Forge Limited",
    "BHARTIARTL": "Bharti Airtel Limited",
    "BHEL": "Bharat Heavy Electricals Limited",
    "BIOCON": "Biocon Limited",
    "BOSCHLTD": "Bosch Limited",
    "BPCL": "Bharat Petroleum Corporation Limited",
    "BRITANNIA": "Britannia Industries Limited",
    "BSOFT": "Birlasoft Limited",
    "CANBK": "Canara Bank",
    "CANFINHOME": "Can Fin Homes Limited",
    "CHAMBLFERT": "Chambal Fertilizers & Chemicals Limited",
    "CHOLAFIN": "Cholamandalam Investment and Finance Company Limited",
    "CIPLA": "Cipla Limited",
    "COALINDIA": "Coal India Limited",
    "COFORGE": "Coforge Limited",
    "COLPAL": "Colgate-Palmolive (India) Limited",
    "CONCOR": "Container Corporation of India Limited",
    "COROMANDEL": "Coromandel International Limited",
    "CROMPTON": "Crompton Greaves Consumer Electricals Limited",
    "CUB": "City Union Bank Limited",
    "CUMMINSIND": "Cummins India Limited",
    "DABUR": "Dabur India Limited",
    "DALBHARAT": "Dalmia Bharat Limited",
    "DEEPAKNTR": "Deepak Nitrite Limited",
    "DIVISLAB": "Divi's Laboratories Limited",
    "DIXON": "Dixon Technologies (India) Limited",
    "DLF": "DLF Limited",
    "DRREDDY": "Dr. Reddy's Laboratories Limited",
    "EICHERMOT": "Eicher Motors Limited",
    "ESCORTS": "Escorts Limited",
    "EXIDEIND": "Exide Industries Limited",
    "FEDERALBNK": "Federal Bank Limited",
    "GAIL": "GAIL (India) Limited",
    "GLENMARK": "Glenmark Pharmaceuticals Limited",
    "GMRINFRA": "GMR Infrastructure Limited",
    "GNFC": "Gujarat Narmada Valley Fertilizers & Chemicals Limited",
    "GODREJCP": "Godrej Consumer Products Limited",
    "GODREJPROP": "Godrej Properties Limited",
    "GRANULES": "Granules India Limited",
    "GRASIM": "Grasim Industries Limited",
    "GUJGASLTD": "Gujarat Gas Limited",
    "HAL": "Hindustan Aeronautics Limited",
    "HAVELLS": "Havells India Limited",
    "HCLTECH": "HCL Technologies Limited",
    "HDFCAMC": "HDFC Asset Management Company Limited",
    "HDFCBANK": "HDFC Bank Limited",
    "HDFCLIFE": "HDFC Life Insurance Company Limited",
    "HEROMOTOCO": "Hero MotoCorp Limited",
    "HINDALCO": "Hindalco Industries Limited",
    "HINDCOPPER": "Hindustan Copper Limited",
    "HINDPETRO": "Hindustan Petroleum Corporation Limited",
    "HINDUNILVR": "Hindustan Unilever Limited",
    "ICICIBANK": "ICICI Bank Limited",
    "ICICIGI": "ICICI Lombard General Insurance Company Limited",
    "ICICIPRULI": "ICICI Prudential Life Insurance Company Limited",
    "IDEA": "Vodafone Idea Limited",
    "IDFC": "IDFC Limited",
    "IDFCFIRSTB": "IDFC First Bank Limited",
    "IEX": "Indian Energy Exchange Limited",
    "IGL": "Indraprastha Gas Limited",
    "INDHOTEL": "The Indian Hotels Company Limited",
    "INDIACEM": "The India Cements Limited",
    "INDIAMART": "Indiamart Intermesh Limited",
    "INDIGO": "InterGlobe Aviation Limited",
    "INDUSINDBK": "IndusInd Bank Limited",
    "INDUSTOWER": "Indus Towers Limited",
    "INFY": "Infosys Limited",
    "IOC": "Indian Oil Corporation Limited",
    "IPCALAB": "Ipca Laboratories Limited",
    "IRCTC": "Indian Railway Catering and Tourism Corporation Limited",
    "ITC": "ITC Limited",
    "JINDALSTEL": "Jindal Steel & Power Limited",
    "JKCEMENT": "JK Cement Limited",
    "JSWSTEEL": "JSW Steel Limited",
    "JUBLFOOD": "Jubilant Foodworks Limited",
    "KOTAKBANK": "Kotak Mahindra Bank Limited",
    "LALPATHLAB": "Dr. Lal Path Labs Limited",
    "LAURUSLABS": "Laurus Labs Limited",
    "LICHSGFIN": "LIC Housing Finance Limited",
    "LT": "Larsen & Toubro Limited",
    "LTF": "L&T Finance Holdings Limited",
    "LTIM": "L&T Infrastructure Finance Company Limited",
    "LTTS": "L&T Technology Services Limited",
    "LUPIN": "Lupin Limited",
    "M&M": "Mahindra & Mahindra Limited",
    "M&MFIN": "Mahindra & Mahindra Financial Services Limited",
    "MANAPPURAM": "Manappuram Finance Limited",
    "MARICO": "Marico Limited",
    "MARUTI": "Maruti Suzuki India Limited",
    "MCDOWELL-N": "United Spirits Limited",
    "MCX": "Multi Commodity Exchange of India Limited",
    "METROPOLIS": "Metropolis Healthcare Limited",
    "MFSL": "Max Financial Services Limited",
    "MGL": "Mahanagar Gas Limited",
    "MOTHERSON": "Motherson Sumi Systems Limited",
    "MPHASIS": "Mphasis Limited",
    "MRF": "MRF Limited",
    "MUTHOOTFIN": "Muthoot Finance Limited",
    "NATIONALUM": "National Aluminium Company Limited",
    "NAUKRI": "Info Edge (India) Limited",
    "NAVINFLUOR": "Navin Fluorine International Limited",
    "NESTLEIND": "Nestle India Limited",
    "NMDC": "NMDC Limited",
    "NTPC": "NTPC Limited",
    "OBEROIRLTY": "Oberoi Realty Limited",
    "OFSS": "Oracle Financial Services Software Limited",
    "ONGC": "Oil and Natural Gas Corporation Limited",
    "PAGEIND": "Page Industries Limited",
    "PEL": "Piramal Enterprises Limited",
    "PERSISTENT": "Persistent Systems Limited",
    "PETRONET": "Petronet LNG Limited",
    "PFC": "Power Finance Corporation Limited",
    "PIDILITIND": "Pidilite Industries Limited",
    "PIIND": "PI Industries Limited",
    "PNB": "Punjab National Bank",
    "POLYCAB": "Polycab India Limited",
    "POWERGRID": "Power Grid Corporation of India Limited",
    "PVRINOX": "PVR Limited",
    "RAMCOCEM": "The Ramco Cements Limited",
    "RBLBANK": "RBL Bank Limited",
    "RECLTD": "REC Limited",
    "RELIANCE": "Reliance Industries Limited",
    "SAIL": "Steel Authority of India Limited",
    "SBICARD": "SBI Cards and Payment Services Limited",
    "SBILIFE": "SBI Life Insurance Company Limited",
    "SBIN": "State Bank of India",
    "SHREECEM": "Shree Cement Limited",
    "SHRIRAMFIN": "Shriram Transport Finance Company Limited",
    "SIEMENS": "Siemens Limited",
    "SRF": "SRF Limited",
    "SUNPHARMA": "Sun Pharmaceutical Industries Limited",
    "SUNTV": "Sun TV Network Limited",
    "SYNGENE": "Syngene International Limited",
    "TATACHEM": "Tata Chemicals Limited",
    "TATACOMM": "Tata Communications Limited",
    "TATACONSUM": "Tata Consumer Products Limited",
    "TATAMOTORS": "Tata Motors Limited",
    "TATAPOWER": "Tata Power Company Limited",
    "TATASTEEL": "Tata Steel Limited",
    "TCS": "Tata Consultancy Services Limited",
    "TECHM": "Tech Mahindra Limited",
    "TITAN": "Titan Company Limited",
    "TORNTPHARM": "Torrent Pharmaceuticals Limited",
    "TRENT": "Trent Limited",
    "TVSMOTOR": "TVS Motor Company Limited",
    "UBL": "United Breweries Limited",
    "ULTRACEMCO": "UltraTech Cement Limited",
    "UPL": "UPL Limited",
    "VEDL": "Vedanta Limited",
    "VOLTAS": "Voltas Limited",
    "WIPRO": "Wipro Limited",
    "ZEEL": "Zee Entertainment Enterprises Limited",
    "ZYDUSLIFE": "Cadila Healthcare Limited"


    # Add more symbols as needed
}

# Map string time frames to Interval objects
timeframe_map = {
    '1m': Interval.in_1_minute,
    '3m': Interval.in_3_minute,
    '5m': Interval.in_5_minute,
    '15m': Interval.in_15_minute,
    '30m': Interval.in_30_minute,
    '45m': Interval.in_45_minute,
    '1h': Interval.in_1_hour,
    '2h': Interval.in_2_hour,
    '3h': Interval.in_3_hour,
    '4h': Interval.in_4_hour,
    '1d': Interval.in_daily,
    '1w': Interval.in_weekly,
    '1M': Interval.in_monthly,
}

# List of available time frames and their display names
timeframes = {
    '1m': '1 Minute',
    '3m': '3 Minutes',
    '5m': '5 Minutes',
    '15m': '15 Minutes',
    '30m': '30 Minutes',
    '45m': '45 Minutes',
    '1h': '1 Hour',
    '2h': '2 Hours',
    '3h': '3 Hours',
    '4h': '4 Hours',
    '1d': '1 Day',
    '1w': '1 Week',
    '1M': '1 Month',
}
readeddata = ''
def readfile():
    file_path = "stocklistedwithsupport.txt"
    with open(file_path, "r") as file:
        while True:
            line = file.readline()
            if not line:
                break
            print(line.strip())
            return line.strip()

def fetch_and_process_data(symbol, interval, n_bars, rolling_window, level_diff_threshold):
    try:
        df = tv.get_hist(symbol=symbol, exchange='NSE', interval=interval, n_bars=n_bars)

        resistancelevel = []
        supportlevel = []
        itemclose = df.close.values[-1]

        supports = df[df.low == df.low.rolling(rolling_window, center=True).min()].low
        resistances = df[df.high == df.high.rolling(rolling_window, center=True).max()].high

        level = pd.concat([supports, resistances])
        level = level[abs(level.diff()) > level_diff_threshold]

        for a in level:
            if a > itemclose:
                resistancelevel.append(a)
            else:
                supportlevel.append(a)

        # Handle empty lists
        if resistancelevel:
            registance_item = max(resistancelevel, key=lambda x: x if x > itemclose else float('-inf'))
        else:
            registance_item = None

        if supportlevel:
            support_item = max(supportlevel, key=lambda x: x if x < itemclose else float('-inf'))
        else:
            support_item = None

        return df, level, registance_item, support_item
    except Exception as e:
        print('error',e)

def plot_to_base64(df, level):
    # Create a bytes buffer for the plot
    buffer = io.BytesIO()

    # Plotting the candlestick chart with horizontal lines
    mpf.plot(df, type='candle', hlines=level.to_list(), style='charles', title='Nifty Historical Candlestick Chart', ylabel='Price', savefig=buffer)

    # Seek to the beginning of the buffer
    buffer.seek(0)

    # Convert the buffer to a base64 string
    img_base64 = base64.b64encode(buffer.read()).decode('utf-8')

    # Close the buffer
    buffer.close()

    return img_base64

@app.route('/', methods=['GET', 'POST'])
def index():
    symbol = 'ICICIBANK'  # Default symbol
    selectedstock = ''
    interval_str = '30m'  # Default interval
    n_bars = 100  # Default number of bars
    rolling_window = 10  # Default rolling window size
    level_diff_threshold = 10  # Default level difference threshold

    if request.method == 'POST':
        symbol = request.form.get('symbol')
        selectedstock = request.form.get('selectedstock')
        interval_str = request.form.get('timeframe')
        n_bars = int(request.form.get('n_bars'))
        rolling_window = int(request.form.get('rolling_window'))
        level_diff_threshold = int(request.form.get('level_diff_threshold'))

    interval = timeframe_map[interval_str]
    df, level, registance_item, support_item = fetch_and_process_data(symbol, interval, n_bars, rolling_window,level_diff_threshold)
    # if selectedstock != '':
    #     df, level, registance_item, support_item = fetch_and_process_data(selectedstock, interval, n_bars, rolling_window,
    #                                                                       level_diff_threshold)
    selectedstocks = readfile()
    # Save the chart as an image
    if not df.empty and not level.empty:
        try:
            # Plot the data
            img_base64 = plot_to_base64(df, level)
            # mpf.plot(df, type='candle', hlines=level.to_list(), style='charles', savefig='static/chart.png')
            print("Plot saved successfully.")
        except Exception as e:
            print(f"An error occurred while plotting: {e}")
    else:
        print("DataFrame or level data is empty.")

    return render_template('index.html', symbols=symbols, symbol=symbol, timeframes=timeframes, timeframe=interval_str,
                           n_bars=n_bars, rolling_window=rolling_window, level_diff_threshold=level_diff_threshold,
                           registance_item=registance_item, support_item=support_item,readeddata=selectedstocks.split(","))



if __name__ == '__main__':
    app.run(debug=True,port=5002)
