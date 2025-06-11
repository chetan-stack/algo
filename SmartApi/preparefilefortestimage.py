import io
import base64
import numpy as np
import pandas as pd
import mplfinance as mpf
import requests
from tvDatafeed import TvDatafeed, Interval
username = 'YourTradingViewUsername'
password = 'YourTradingViewPassword'

tv = TvDatafeed(username, password)
def fetch_and_process_data(symbol, interval, n_bars, rolling_window, level_diff_threshold):
    try:
        df = tv.get_hist(symbol=symbol, exchange='NSE', interval=interval, n_bars=100)

        # print(df)
        if df is not None:
            # df.ema = ta.ema(df.close, length=9)
            # print('ema', df.ema.values[-1])
            resistancelevel = []
            supportlevel = []
            itemclose = df.close.values[-1]

            supports = df[df.low == df.low.rolling(rolling_window, center=True).min()].close
            resistances = df[df.high == df.high.rolling(rolling_window, center=True).max()].close

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
            return True, level, df
            # return df, level, registance_item, support_item,itemclose
        else:
            return False, 'no', df
    except Exception as e:
        print('error', e)


def sendAlert(bot_message, image_path=None):
    bot_token = "5707293106:AAEPkxexnIdoUxF5r7hpCRS_6CHINgU4HTw"
    bot_chatid = "2027669179"

    if image_path:
        # Send image
        url = f'https://api.telegram.org/bot{bot_token}/sendPhoto'
        with open(image_path, 'rb') as photo:
            response = requests.post(url, data={'chat_id': bot_chatid}, files={'photo': photo})
    else:
        # Send text message
        url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
        response = requests.post(url, data={'chat_id': bot_chatid, 'text': bot_message, 'parse_mode': 'MarkdownV2'})

    print(response)
    return response.json()


def main():
    result, level, df = fetch_and_process_data('BANKNIFTY', Interval.in_5_minute, '100', 20, 20)
    if result:
        mpf.plot(df, type='candle', hlines=level.to_list(), style='charles', savefig='static/chart.png')
        sendAlert("Here is an image:", "static/chart.png")

if __name__ == '__main__':
    main()
