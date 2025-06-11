from datetime import datetime
import xlwings as xsw
import requests
import pandas as pd

def getparams(symbol,target,type):
    try:
        url = f"https://www.nseindia.com/api/option-chain-equities?symbol={symbol}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en-US,en;q=0.9,bs;q=0.8',
            'Cookie': '_ga=GA1.1.675642401.1705814844; defaultLang=en; _ga_QJZ4447QD3=GS1.1.1714116048.13.0.1714116048.0.0.0; _abck=D488772C69D5F3C3DD75BC55150754B4~0~YAAQnG4/F6FG1COPAQAAvPOSLQtvas/TK985Gpel9c2rpe5EvujwXYJalth+GMxKcy+zj051dJAWCQZdyCGUcIb7JpgGHF6LQg2dSM5VE+iPmJPjWNPuH41ziwm3jesP26IBj4A8e2IW9joZz5A3fCf73VLeBvqp7HTTFULimjOrJMvVFpQPlE/0HIg/3u5HJMQwci8j2MMj6+NJ2e9m8cPFCpFLTMZ+mIjmQFFCojsJGd0hB/JcYSbiEGOWEbzS0wQ5/dS79AbdKQzAW0CisQ8MEIjCO/5GizHm9wWrXhOIQSqAvAa8fRqimO5+NzTRkptnQfHy4mCGXbQeWzSQ2muTT7maFwmvgIerG9eDRm4eLqVk+O/8zXvqr2LSebubXLHf8I0mJOJhtjvdi/NcxRl5lT9wp2jxIT4=~-1~-1~-1; nsit=NQNqylWdXRJdQLuNelhnULI3; nseappid=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhcGkubnNlIiwiYXVkIjoiYXBpLm5zZSIsImlhdCI6MTcxNDQ2NjUxNywiZXhwIjoxNzE0NDczNzE3fQ.D-38L1NUijEqYR5xaaTX2zD9Nyj-HaeFUQ_XsaQ71lk; AKA_A2=A; bm_mi=FD02C86B965847E3FD9D512BC73EB800~YAAQnG4/Fw/W1iOPAQAAMPEqLhew1V/sVGjCFyM0ASkLNhGnevmXRuPsQutFIBGED8bWHdSLQ+FfS5lXwapGoOOBBMdWGNl8cKHiyEia5wlSpFTIo252CVM16Iu4R/gBo9FZcd9lRnMe4LYEe/yU2mf3ysC+A21S4CkQy5X5Hy0ILuCE8ZuxuP6A8sGYjH0MI8o3zYOz3TSoJLzhxtv6qUsDs9OSOiCSe8/yVogcfvGsNJVqYSm9x2cPH1S8//k3xNSoaZTrQbE7sJpI+RS9L0Qu7o+zadYmf7us6qGppONGgx7Fy9aBIVp/WQ4iuwmcc1RhX3ODryr6kLU=~1; bm_sz=31E39A3A95F9AFF38F360A738C8CC893~YAAQnG4/FxHW1iOPAQAAMPEqLhcfFSc/5zVQYx8sqILan7CcfAiWfwGndCf+dFriP9jycDNPJ84qhlWOyaegbJRazE4kHX/BvSxa8YTq0SMeHXR9vkoypPXtWY2Nnoih+CQd9x7jl608Q6UbGD5dXh21lDT//b4Ija+9QfTpB7gtc0XfdmJTWSvPpwZlvDTDFv25Q640AGJGy9I4Y7IpC3w81NbCxn7Kase6W/R31nyYOEa+C4S8CrbL7dgruEyoPsMfJmHhDszsD9Tbdo3wh8lEgxynxfttC3ecPveBKuMlmPt4Q8CMmWxd1ivl+O/cd0nmLiEbDJUTm+rQ0jfP0CUv+NRjvJrHdr7jfzyA+FmHXX7Qs47KvRI2HPOOskt2SwWV1BZjmlN3/e4GrVadvHDz51HEin7MnN2Xgz0t3l19pg==~3224884~3749431; _ga_87M7PJ3R97=GS1.1.1714466517.17.1.1714466518.0.0.0; ak_bmsc=A714EDD06B60A0B21FD8C00831B5F501~000000000000000000000000000000~YAAQnG4/F0DW1iOPAQAA/vkqLhc1Xl2sncTpi/ESCee2C1PGucHqtciy399kSz1mbIks5w5mCqLnDg7RrGSCZcMysQJrklAoHXPvEkfcPi98E8VFdqsUi/suf4l+GthDFQHb5jVBRmhV0m73o8GLCnzxpB94RZE/aTv0wo+jjVvQFFkGtHgLc5O3OnD5xzXUXurj9MRKilCBjro325qhRWxx/gLrcapomLRAEgbcNAQVQuXTOJjEOVTQcddh5VHrR9rz9lAWHH0bKm7+3nEIS6FgsqA+EXNcFSmWIt25tJ/nmzlM+AhTUCz6kfGvjDLzarqmvOrPKgFkJE5alo4QDWQJeDQLgLk60wazhsA+9pBmZlpJk78Y48Sm2COKg/nuxUGBRlQwJsVvzXXuvk3IOS9jLqWYTTKvciGapP+MGT6mK3Bf8qI3umaTO/bvdBLGY/e5dptctOAXsudIASTaGTAqIoG7TyK+6rRaDBPFF9J2W+yyIG7s6Ts+CGU=; RT="z=1&dm=nseindia.com&si=75ef1f4e-13b3-4c37-ab90-9ff7735372a2&ss=lvlztvrl&sl=1&se=8c&tt=1yo&bcn=%2F%2F684d0d4b.akstat.io%2F&ld=59qc2"; bm_sv=42D8935DD984211D855107A38E700B7A~YAAQnG4/F6DW1iOPAQAA6hYrLhcJU7bilKNjwsISFmtGajktdP9MkUkfP52mn/q1sHLP7sJeKo9RzB71uUGktVkOxIzxlBD8hzTTjba0pXpRjTkQ1ghkAM/MLZ4PuvZEz6FUJ83NeF6OCAPbXunZd3qPws7dfirQ5620hYiVjc3UOxIVDbip/G6a9+Af/YMawn1ES9Mhr4yz5CWElG8RTl+47g/M7oZYk4YCwKUwfoyOMToqsFTzugq4Cptt2B23f1juzA==~1'
                             }
        session = requests.session()
        request = session.get(url,headers=headers)
        cookies = dict(request.cookies)
        #print(cookies)
        # print(session.get(url,headers=headers,cookies=cookies))
        response = session.get(url,headers=headers,cookies=cookies).json()['filtered']['data']
        rawdata = pd.DataFrame(response)
        #print(response,'response')
        docdata = []
        for i in response:
            for j,k in i.items():
                if j=='CE' or j=='PE':
                    info = k
                    info['instrumenet Type'] = j
                    docdata.append(info)
        df = pd.DataFrame(docdata)
        target = int(target)
        today_date = datetime.today().date().strftime('%d-%b-%Y')  # Get today's date
        # print(df['openInterest'].max())
        # print(df['openInterest'].idxmax())
        max_open_interest_index = df['openInterest'].idxmax()
        # print(df.loc[max_open_interest_index, 'strikePrice'])
        # print(df.loc[max_open_interest_index, 'instrumenet Type'])
        closest_strike_price = min(df['strikePrice'], key=lambda x: abs(x - target))
        setdf = df[(df['strikePrice'] == closest_strike_price)]
        #print(setdf)
        # print(setdf['openInterest'].values[-1], '--', setdf['changeinOpenInterest'].values[-1], '----',
        #       setdf['expiryDate'].values[-1], setdf['instrumenet Type'].values[-1], '----',
        #       setdf['openInterest'].values[-1], '--', setdf['changeinOpenInterest'].values[0], '----',
        #       setdf['expiryDate'].values[0], setdf['instrumenet Type'].values[0])
        data = {
            'pe_oi': setdf['openInterest'].values[-1],
            'ce_oi': setdf['openInterest'].values[0],
            'pe_change': setdf['changeinOpenInterest'].values[-1],
            'ce_change': setdf['changeinOpenInterest'].values[0],
            'strick': closest_strike_price,
            'max oi': df['openInterest'].max(),
            'max oi type': df.loc[max_open_interest_index, 'instrumenet Type'],
            'max oi strick': df.loc[max_open_interest_index, 'strikePrice']
        }
        #print(setdf)
        return data
    except Exception as e:
        print(e)
    # wb = xsw.Book("angeone.xlsx")
    # st = wb.sheets('nifty')
    # st.range('A1').value = setdf
# Index(['strikePrice', 'expiryDate', 'underlying', 'identifier', 'openInterest',
#        'changeinOpenInterest', 'pchangeinOpenInterest', 'totalTradedVolume',
#        'impliedVolatility', 'lastPrice', 'change', 'pChange',
#        'totalBuyQuantity', 'totalSellQuantity', 'bidQty', 'bidprice', 'askQty',
#        'askPrice', 'underlyingValue', 'instrumenet Type'],
#       dtype='object')


# getparams('NIFTY','22500','pe')


#getparams('ACC','2532','pe')
