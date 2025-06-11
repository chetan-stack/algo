# package import statement
from SmartApi import SmartConnect #or from SmartApi.smartConnect import SmartConnect
import pyotp


api_key = "pMZtYR5S"
user_id = "c182721"
password = "1108"
totp = "ELAC7LJCYC6ENWQBWNEGRGV66U"

api_key = 'pMZtYR5S'
clientId = 'c182721'
pwd = '1108'
smartApi = SmartConnect(api_key)
token = "ELAC7LJCYC6ENWQBWNEGRGV66U"
totp=pyotp.TOTP(token).now()
correlation_id = "abc123"

# login api call

data = smartApi.generateSession(clientId, pwd, totp)
print(data)

authToken = data['data']['jwtToken']
refreshToken = data['data']['refreshToken']

# fetch the feedtoken
feedToken = smartApi.getfeedToken()

print(feedToken)
