from smartapi import SmartConnect
# import document_detail_Lax
import time
import datetime
import talib as ta
import pandas as pd
import numpy as np
import json

api_key = document_detail_Lax.api_key
secret_key = document_detail_Lax.secret_key
user_id = document_detail_Lax.user_id
password = document_detail_Lax.password


script_list = {
	"IDFCFIRSTB-EQ" : "11184",
	"SAIL-EQ" : "2963",
	"ICICIPRULI-EQ" : "18652",
	"BEL-EQ" : "383",
	"PNB-EQ" : "10666",
	"NATIONALUM-EQ" : "6364",
	"DELTACORP-EQ" : "15044",
	"FEDERALBNK-EQ" : "1023",
	"AMBUJACEM-EQ" : "1270",
	"NMDC-EQ" : "15332",
	"BHEL-EQ" : "438",
	"M&MFIN-EQ" : "13285",
	"SUNTV-EQ" : "13404",
	"STAR-EQ" : "7374",
	"GRANULES-EQ" : "11872",
	"INDHOTEL-EQ" : "1512",
	"INDUSTOWER-EQ" : "29135",
	"VEDL-EQ" : "3063",
	"IOC-EQ" : "1624",
	"BANKBARODA-EQ" : "4668",
	"DABUR-EQ" : "772",
	"LAURUSLABS-EQ" : "19234",
	"FSL-EQ" : "14304",
	"TORNTPOWER-EQ" : "13786",
	"GMRINFRA-EQ" : "13528",
	"MARICO-EQ" : "4067",
	"INDIACEM-EQ" : "1515",
	"BANDHANBNK-EQ" : "2263",
	"BPCL-EQ" : "526",
	"HINDALCO-EQ" : "1363",
	"ITC-EQ" : "1660",
	"CADILAHC-EQ" : "7929",
	"TATAPOWER-EQ" : "3426",
	"SBIN-EQ" : "3045",
	"HINDPETRO-EQ" : "1406",
	"POWERGRID-EQ" : "14977",
	"ABFRL-EQ" : "30108",
	"LICHSGFIN-EQ" : "1997",
	"GAIL-EQ" : "4717",
	"CANBK-EQ" : "10794",
	"EXIDEIND-EQ" : "676",
	"IEX-EQ" : "220",
	"CHAMBLFERT-EQ" : "637",
	"WIPRO-EQ" : "3787",
	"L&TFH-EQ" : "24948",
	"MOTHERSUMI-EQ" : "4204",
	"NTPC-EQ" : "11630",
	"TATAMOTORS-EQ" : "3456",
	"PFC-EQ" : "14299",
	"CUB-EQ" : "5701",
	"MANAPPURAM-EQ" : "19061",
	"IBULHSGFIN-EQ" : "30125",
	"ZEEL-EQ" : "3812",
	"SYNGENE-EQ" : "10243",
	"RECLTD-EQ" : "15355",
	"CROMPTON-EQ" : "17094",
	"RBLBANK-EQ" : "18391",
	"PETRONET-EQ" : "11351",
	"JINDALSTEL-EQ" : "6733",
	"GLENMARK-EQ" : "7406",
	"GSPL-EQ" : "13197",
	"COALINDIA-EQ" : "20374",
	"ONGC-EQ" : "2475",
	"APOLLOTYRE-EQ" : "163",
	"BIOCON-EQ" : "11373",
	"DLF-EQ" : "14732",
	"IGL-EQ" : "11262",
	"BSOFT-EQ" : "6994",
	"ASHOKLEY-EQ" : "212",
}

newlist = {
	"SUNTV-EQ" : "13404",
	"DABUR-EQ" : "772",
	"LAURUSLABS-EQ" : "19234",
	"TORNTPOWER-EQ" : "13786",
	"TATAMOTORS-EQ" : "3456",
	"GLENMARK-EQ" : "7406",
	"DLF-EQ" : "14732",
	"IGL-EQ" : "11262",
	"ICICIPRULI-EQ" : "18652",
	"STAR-EQ" : "7374",
	"WIPRO-EQ" : "3787",
	"BSOFT-EQ" : "6994",
}

obj = SmartConnect(api_key=api_key)
token = obj.generateToken(
	obj.generateSession(user_id, password)["data"]["refreshToken"])
jwtToken = token['data']["jwtToken"]
refreshToken = token['data']['refreshToken']
feedToken = token['data']['feedToken']

fromdate = "2022-01-01 09:15"  # The difference between Fromdate to Todate should not be more than 100 days;
# todate = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")[:-1]}5'
# interval = "FIFTEEN_MINUTE"
# interval = "FIVE_MINUTE"
interval = "ONE_MINUTE"
script_profit = {}
quantity = 100
initial_value = 100000
try:
	for script, token in script_list.items():
		historicParam = {
			"exchange": "NSE",
			"symboltoken": token,
			"interval": interval,
			"fromdate": fromdate,
			"todate": "2022-02-02 11:45"
		}
		try:
			hist_data = obj.getCandleData(historicParam)["data"]
		except Exception as e:
			raise e

		if hist_data != None:
			df = pd.DataFrame(
				hist_data,
				columns=['date', 'open', 'high', 'low', 'close', 'volume'])
			if not df.empty:
				totalPnl = 0
				params = {}
				order = ""

				for i in df.index:
					if (df["date"][i][11:-9] == "09:30") and (order == "buy" or order == ""):
						order = "sell"
						ltp = max(df["high"].loc[i-15:i])
						target = round(ltp*0.99, 1)
						stoploss = round(ltp*1.010, 1)
						params[script] = {
							"price":ltp,
							"target": target,
							"stoploss": stoploss,
							"quantity" : quantity
						}
						print(f"Sell order placed for {script} at {ltp} time: {df['date'][i]} ")

					if (df["date"][i][11:-9] > "09:30") and (order == "sell"):
						if len(params) != 0:

							if (int(params[script]["target"]) == int(df["low"][i])) and (df["date"][i][11:-9] < "13:30"):
								order = "buy"
								pnl = ((params[script]["price"] - params[script]["target"]) * quantity) * 0.90
								totalPnl = int(totalPnl + pnl)
								print(f'Target order placed for {script} at {params[script]["target"]} time: {df["date"][i]}, totalPnl : {totalPnl}')
							
							if (int(params[script]["stoploss"]) == int(df["high"][i])) and (df["date"][i][11:-9] < "13:30"):
								order = "buy"
								pnl = ((params[script]["price"] - params[script]["stoploss"]) * quantity) * 0.90
								totalPnl = int(totalPnl + pnl)
								print(f'Stoploss order placed for {script} at {params[script]["target"]} time: {df["date"][i]}, totalPnl : {totalPnl}')

							if (df["date"][i][11:-9] == "13:30"):
								order = "buy"
								pnl = ((params[script]["price"] - df["close"][i]) * quantity) * 0.90
								totalPnl = int(totalPnl + pnl)
								print(f'Position closed for {script} at {df["close"][i]} time: {df["date"][i]}, totalPnl : {totalPnl}')

					if len(df) == i+1:
						initial_value = initial_value + totalPnl
						script_profit[script] = totalPnl
						print(script_profit)
		else:
			print("No Historic Data")

	print(f"{script_profit}, Final Value : {initial_value}")

except Exception as e:
	print("Historic Api failed: {}".format(e.message))

try:
	logout = obj.terminateSession(user_id)
	print("Logout Successfull")
except Exception as e:
	print("Logout failed: {}".format(e.message))
