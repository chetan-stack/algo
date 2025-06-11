import requests

def telegrameBot(bot_message):
    bot_token = "5707293106:AAEPkxexnIdoUxF5r7hpCRS_6CHINgU4HTw"
    bot_chatid = "2027669179"
    send_message = "https://api.telegram.org/bot" + bot_token + "/sendMessage?chat_id=" + bot_chatid +\
                   "&parse_mode=MarkdownV2&text=" + bot_message

    response = requests.get(send_message)
    print(response)
    return response.json()

telegrameBot("greate work done")