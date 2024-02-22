#app.py
import os
import random 
import twstock

from datetime import datetime
from flask import Flask, request, abort

#載入.env
#from dotenv import load_dotenv
#load_dotenv()

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

# 確認 token
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
# 確認 secret
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text=event.message.text
    msg = []
    if "運勢" in text:
        fortune = random.choice(['大凶', '凶', '末吉', '吉','中吉','大吉'])
        msg.append(TextSendMessage(text=fortune))
    elif "吃什麼" in text:
        eat = random.choice(['水餃', '小7', '火鍋', '炒飯','拉麵','陽春麵'])
        msg.append(TextSendMessage(text=eat)) 
    #股票
    #https://github.com/maloyang/stock-line-bot/blob/master/line_stock_tutorial%20-%20Copy2git/app.py
    elif(text.startswith('#')):
            text = text[1:]
            content = ''

            stock_rt = twstock.realtime.get(text)
            my_datetime = datetime.fromtimestamp(stock_rt['timestamp']+8*60*60)
            my_time = my_datetime.strftime('%H:%M:%S')

            content += '%s (%s) %s\n' %(
                stock_rt['info']['name'],
                stock_rt['info']['code'],
                my_time)
            content += '現價: %s / 開盤: %s\n'%(
                stock_rt['realtime']['latest_trade_price'],
                stock_rt['realtime']['open'])
            content += '最高: %s / 最低: %s\n' %(
                stock_rt['realtime']['high'],
                stock_rt['realtime']['low'])
            content += '量: %s\n' %(stock_rt['realtime']['accumulate_trade_volume'])

            stock = twstock.Stock(text)#twstock.Stock('2330')
            content += '-----\n'
            content += '最近五日價格: \n'
            price5 = stock.price[-5:][::-1]
            date5 = stock.date[-5:][::-1]
            for i in range(len(price5)):
                #content += '[%s] %s\n' %(date5[i].strftime("%Y-%m-%d %H:%M:%S"), price5[i])
                content += '[%s] %s\n' %(date5[i].strftime("%Y-%m-%d"), price5[i])
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=content)
            )
    line_bot_api.reply_message(event.reply_token, messages=msg[:2])


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)