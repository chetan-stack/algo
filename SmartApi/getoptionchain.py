from datetime import datetime
import requests
import pandas as pd
import xlwings as xsw

def getparams(symbol,target,type):
    return True
def getparamsold(symbol,target,type):
    print('option chain check with price : ',target, 'order type : ',type)
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9,bs;q=0.8',
        'cookie': '_ga=GA1.1.675642401.1705814844; _ga_QJZ4447QD3=GS1.1.1717332664.20.0.1717332664.0.0.0; AKA_A2=A; defaultLang=en; nsit=t3ZaEkWxKo5v6VsaAOCQ6f86; nseappid=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhcGkubnNlIiwiYXVkIjoiYXBpLm5zZSIsImlhdCI6MTczMTc0MDcyMSwiZXhwIjoxNzMxNzQ3OTIxfQ.KgBln2aX8iKSrC8WGxDQ2Rds2a-z2oHmcGgiRVinTuk; bm_mi=16E205A1A3D2DC376BF4810D39BCCB05~YAAQ3QVaaIRqyh+TAQAArmHKMxmYIH8kQ7WJjZ7Uv+8qep1+la1mIujowCDrfB22TnQEsSv+O42iIbMzp8OXbPzLfyeZT5wrPPnlhcZsgozdQ7Zl8pEDD2Nh/uqzdsGyt6P4g/AoFXayWXAAqEYTtyFYa7rAwqw//3XZis1AZjBXRIsRcjQEgPTbvGSTEjntiE3BBrK5qt3PfYv7LVS4cg+HFeKz6VYrTxUR8C1hhpAnpw0FVzUcKukuNo/EfsM4LpxDZlW9pYw3DqMqlCW6hRe7KUAEcONL8Mkj9lRHo3dIlmMg4vTgwG8II5epbhxm/XbapGCc9m7hqUc=~1; bm_sz=5A6EA9099DFC58417A9FF58E525D5708~YAAQ3QVaaIZqyh+TAQAArmHKMxkx5nr9mYeU77QJi8OT93SofmIGxJq5ZjVfemOZ68objKkKBpc98kk1SXowuD/YpkdmWDkrF0Lgjzp2bq3RJ8gvx7WwDCJ+mRXMejW+JJ4SokWa5Z5dHAuakZ23JQ69hQepMHHGUDXK1EjN3Dv7SiJ+w8Qcd6Dj9jTevJmRJPoiRl6ZZYe2YaioWsaMx60uhxXjDc+IGrPRTuE6OAKMXWlUpEpUkD8+oolRuXSCIc/+RKHrLSRAACreKCgyDnNhUofo5v1f6hdI240OBkJjKTh9BxkBnRIVUZIMvv02o0GaVbN732iGaSBJs4xM8t37FR2KFk1zBscuVG4T68zTQhnCwUZAoGojCJgkBHDcu50NjaJGNGymZ7HGDi/FEkouOc3m~3552305~4539191; RT="z=1&dm=nseindia.com&si=17ee68d9-e033-4ad0-89e1-cd670ccce115&ss=m3jtpfpj&sl=1&se=8c&tt=22h&bcn=%2F%2F684d0d49.akstat.io%2F"; ak_bmsc=0425DE37B19F327DF7AFF7812CF34CF5~000000000000000000000000000000~YAAQ3QVaaNFqyh+TAQAAo2TKMxkW/Ag/tTp6icQGnbsdPKxLUB8twXzRtw5ppkHRXyLIkZMQjcH/zXWJanyqQguwtpzCl//8Zrw9liZHTKu2Hp4PV+i7nD3Iic/urEUy9EVsWXW0SwTo3lRdRErV3Ke+mtD/N547H2x9C1mnpkz3Zkst9GRyN99/i/EtyxkRF+/eGUAMvEO6iu8vx/LNmYZZyvoN8k8RUDNXffIuyCHSIgREZQ0haeGYBO1tGeg0MnfHUCIcHiiW+gTMetD1XJIFakT4Cl7CyMRKHaXhqOooOUFTpcNsPISTfyTfTm1KX0nI6ZEblX4zhYaaZiXk3QfhfyKxfgH9MUcTJ24H8IDo582Yq04rrepJvFYxSDjNBkpzCzKN9hbwpsitH1TEHNLVXT3xeBpQd6j9MbScUjoOClSovLZhBRSumwThXhOZ+acmUJP8nqYaBBuHsBSlH4kCVzUwo2Ll47mhcv7PjhAmg4RO5E8Tcm49EBulOW1B6eI=; _ga_87M7PJ3R97=GS1.1.1731740711.33.1.1731740722.49.0.0; _ga_WM2NSQKJEK=GS1.1.1731740711.1.1.1731740722.0.0.0; _abck=D488772C69D5F3C3DD75BC55150754B4~0~YAAQ3QVaaOdqyh+TAQAAOGbKMwyhXfbUavHGu86yiatDdF8jNVECO8tPgoyop/AeNP/paQCk7MBE82engaX68k7jvxmyBUeje0kUjy/3m5ImUFn2qj54oLSK8qc8IZkBqWmQNCCRXSRyVVZZqgDahmj3FCNSd2te8VPTWIptNwVkECtaMfbJTaXVUNDStCwow7MVgQI6aFCZI5yUX8u6zPxwLMjsU09r5VMejxZFPAk0MMdPo6KITNX2CbzwxzDcvOfiYg0WzUQGQMj9qOtCxOtSD4PcpQS4OxpaeopblXiDvTQr7YFx4chLy01E5dpox+uzQ1wKPfyIvdidm6iYLfoxaeH6NXDSxXAHfJ2p48UHVN/7qkUCUN4uRr3lfydojPrJXBCFSbDlf4ElLK4Gh+2k3N26N40=~-1~-1~-1; bm_sv=1B98CC537E44882359CEB8CB90B8162C~YAAQ3QVaaOhqyh+TAQAAOGbKMxmgBmu/QedHXoRTv8LA2/5QQ1xUMacF8lYx6GN3mKlkx1ZP3VKNsQHr8waIk9E+UQFH1HtIFGQyJbkTOxyM0Q+vmpK344yn0mOIkWZ0DJ7I6eJC7WXzq+cfE4omyc/6UjfdQHDQaGwSsrDHM2HB2DaCd9UIJiZz9GxUTseaVSy78R1X2nLy0QgiqsuYPuDaKYXIsBQ7wFQpjj7KR87Px+bkeS+uSkU9HFJsQ0PLfgk=~1'
     }


    session = requests.session()
    request = session.get(url,headers=headers)
    cookies = dict(request.cookies)
    print('cok',headers)
    response = session.get(url,headers=headers).json()
    rawdata = pd.DataFrame(response)
    print('row',rawdata)
    docdata = []
    for i in response:
        for j,k in i.items():
            if j=='CE' or j=='PE':
                info = k
                info['instrumenet Type'] = j
                docdata.append(info)
    df = pd.DataFrame(docdata)
        # wb = xsw.Book("angle_excel.xlsx")
        # st = wb.sheets('nifty')
        # st.range('A1').value = df
    target = int(target)
    today_date = datetime.today().date().strftime('%d-%b-%Y')  # Get today's date
    # print(df)
    closest_strike_price = min(df['strikePrice'], key=lambda x: abs(x - target))
    unique_strike_prices = sorted(df['strikePrice'].unique())

    # Find the index of the closest strike price in the unique strike prices list
    closest_index = unique_strike_prices.index(closest_strike_price)

    # Find the strike prices before and after the closest one
    previous_strike_price = unique_strike_prices[closest_index - 1] if closest_index > 0 else None
    next_strike_price = unique_strike_prices[closest_index + 1] if closest_index < len(
        unique_strike_prices) - 1 else None

    print("Closest strike price:", closest_strike_price)
    print("Strike price before:", previous_strike_price)
    print("Strike price after:", next_strike_price)
    setdf = df[(df['strikePrice'] == closest_strike_price)]
    minsetdf = df[(df['strikePrice'] == previous_strike_price)]
    maxset = df[(df['strikePrice'] == next_strike_price)]
    # print(setdf,minsetdf,maxset)
    print('strick price',setdf[setdf['instrumenet Type'] == 'PE']['strikePrice'].values[-1],'---',setdf[setdf['instrumenet Type'] == 'PE']['openInterest'].values[-1], '--', setdf[setdf['instrumenet Type'] == 'PE']['changeinOpenInterest'].values[-1], '----',
      setdf['expiryDate'].values[-1], 'PE', '----', setdf[setdf['instrumenet Type'] == 'CE']['openInterest'].values[-1],
      '--', setdf[setdf['instrumenet Type'] == 'CE']['changeinOpenInterest'].values[-1], '----', setdf['expiryDate'].values[0],
      'CE')

    if type == 'ce' and int(setdf[setdf['instrumenet Type'] == 'PE']['changeinOpenInterest'].values[-1]) > int(setdf[setdf['instrumenet Type'] == 'CE']['changeinOpenInterest'].values[-1]):
         return True
    elif type == 'pe' and int(setdf[setdf['instrumenet Type'] == 'PE']['changeinOpenInterest'].values[-1]) < int(setdf[setdf['instrumenet Type'] == 'CE']['changeinOpenInterest'].values[-1]):
         return True
    else:
         return True


def placeorderwhenconfermation(symbol,target,type):
    print('option chain check with price : ',target, 'order type : ',type)
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9,bs;q=0.8'
     }


    session = requests.session()
    request = session.get(url,headers=headers)
    cookies = dict(request.cookies)
    # print(cookies)
    response = session.get(url,headers=headers,cookies=cookies).json()['filtered']['data']
    rawdata = pd.DataFrame(response)
    # print(rawdata)
    docdata = []
    for i in response:
        for j,k in i.items():
            if j=='CE' or j=='PE':
                info = k
                info['instrumenet Type'] = j
                docdata.append(info)
    df = pd.DataFrame(docdata)
        # wb = xsw.Book("angle_excel.xlsx")
        # st = wb.sheets('nifty')
        # st.range('A1').value = df
    target = int(target)
    today_date = datetime.today().date().strftime('%d-%b-%Y')  # Get today's date
    # print(df)
    closest_strike_price = min(df['strikePrice'], key=lambda x: abs(x - target))
    unique_strike_prices = sorted(df['strikePrice'].unique())

    # Find the index of the closest strike price in the unique strike prices list
    closest_index = unique_strike_prices.index(closest_strike_price)

    # Find the strike prices before and after the closest one
    previous_strike_price = unique_strike_prices[closest_index - 1] if closest_index > 0 else None
    next_strike_price = unique_strike_prices[closest_index + 1] if closest_index < len(
        unique_strike_prices) - 1 else None

    print("Closest strike price:", closest_strike_price)
    print("Strike price before:", previous_strike_price)
    print("Strike price after:", next_strike_price)
    setdf = df[(df['strikePrice'] == closest_strike_price)]
    minsetdf = df[(df['strikePrice'] == previous_strike_price)]
    maxset = df[(df['strikePrice'] == next_strike_price)]
    # print(setdf,minsetdf,maxset)
    print('strick price',setdf[setdf['instrumenet Type'] == 'PE']['strikePrice'].values[-1],'---',setdf[setdf['instrumenet Type'] == 'PE']['openInterest'].values[-1], '--', setdf[setdf['instrumenet Type'] == 'PE']['changeinOpenInterest'].values[-1], '----',
      setdf['expiryDate'].values[-1], 'PE', '----', setdf[setdf['instrumenet Type'] == 'CE']['openInterest'].values[-1],
      '--', setdf[setdf['instrumenet Type'] == 'CE']['changeinOpenInterest'].values[-1], '----', setdf['expiryDate'].values[0],
      'CE')
    print(int(setdf[setdf['instrumenet Type'] == 'PE']['changeinOpenInterest'].values[-1]) , int(setdf[setdf['instrumenet Type'] == 'CE']['changeinOpenInterest'].values[-1]) , int(maxset[maxset['instrumenet Type'] == 'PE']['changeinOpenInterest'].values[-1]) , int(maxset[maxset['instrumenet Type'] == 'CE']['changeinOpenInterest'].values[-1]))
    if int(setdf[setdf['instrumenet Type'] == 'PE']['changeinOpenInterest'].values[-1]) > int(setdf[setdf['instrumenet Type'] == 'CE']['changeinOpenInterest'].values[-1]) and int(maxset[maxset['instrumenet Type'] == 'PE']['changeinOpenInterest'].values[-1]) > int(maxset[maxset['instrumenet Type'] == 'CE']['changeinOpenInterest'].values[-1]):
         return 'ce'
    elif int(setdf[setdf['instrumenet Type'] == 'PE']['changeinOpenInterest'].values[-1]) < int(setdf[setdf['instrumenet Type'] == 'CE']['changeinOpenInterest'].values[-1]) and int(minsetdf[minsetdf['instrumenet Type'] == 'PE']['changeinOpenInterest'].values[-1]) < int(minsetdf[minsetdf['instrumenet Type'] == 'CE']['changeinOpenInterest'].values[-1]):
         return 'pe'
    else:
         return 'no order'


def exitorder(symbol,target,type):
    print('option chain check with price : ',target, 'order type : ',type)
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9,bs;q=0.8'
     }


    session = requests.session()
    request = session.get(url,headers=headers)
    cookies = dict(request.cookies)
    # print(cookies)
    response = session.get(url,headers=headers,cookies=cookies).json()['filtered']['data']
    rawdata = pd.DataFrame(response)
    # print(rawdata)
    docdata = []
    for i in response:
        for j,k in i.items():
            if j=='CE' or j=='PE':
                info = k
                info['instrumenet Type'] = j
                docdata.append(info)
    df = pd.DataFrame(docdata)
        # wb = xsw.Book("angle_excel.xlsx")
        # st = wb.sheets('nifty')
        # st.range('A1').value = df
    target = int(target)
    today_date = datetime.today().date().strftime('%d-%b-%Y')  # Get today's date
    # print(df)
    closest_strike_price = min(df['strikePrice'], key=lambda x: abs(x - target))
    unique_strike_prices = sorted(df['strikePrice'].unique())

    # Find the index of the closest strike price in the unique strike prices list
    closest_index = unique_strike_prices.index(closest_strike_price)

    # Find the strike prices before and after the closest one
    previous_strike_price = unique_strike_prices[closest_index - 1] if closest_index > 0 else None
    next_strike_price = unique_strike_prices[closest_index + 1] if closest_index < len(
        unique_strike_prices) - 1 else None

    # print("Closest strike price:", closest_strike_price)
    # print("Strike price before:", previous_strike_price)
    # print("Strike price after:", next_strike_price)
    setdf = df[(df['strikePrice'] == closest_strike_price)]
    minsetdf = df[(df['strikePrice'] == previous_strike_price)]
    maxset = df[(df['strikePrice'] == next_strike_price)]
    # print(setdf,minsetdf,maxset)
    print('strick price',setdf[setdf['instrumenet Type'] == 'PE']['strikePrice'].values[-1],'---',setdf[setdf['instrumenet Type'] == 'PE']['openInterest'].values[-1], '--', setdf[setdf['instrumenet Type'] == 'PE']['changeinOpenInterest'].values[-1], '----',
      setdf['expiryDate'].values[-1], 'PE', '----', setdf[setdf['instrumenet Type'] == 'CE']['openInterest'].values[-1],
      '--', setdf[setdf['instrumenet Type'] == 'CE']['changeinOpenInterest'].values[-1], '----', setdf['expiryDate'].values[0],
      'CE')

    if type == 'ce' and int(setdf[setdf['instrumenet Type'] == 'PE']['changeinOpenInterest'].values[-1]) > int(setdf[setdf['instrumenet Type'] == 'CE']['changeinOpenInterest'].values[-1]):
         return True
    elif type == 'pe' and int(setdf[setdf['instrumenet Type'] == 'PE']['changeinOpenInterest'].values[-1]) < int(setdf[setdf['instrumenet Type'] == 'CE']['changeinOpenInterest'].values[-1]):
         return True
    else:
         return False



# print(getparams('BANKNIFTY',50000,'ce'))
