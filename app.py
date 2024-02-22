#app.py
import os
import random 

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
    msg = []
    if("運勢" | "吃") in event.message.text:
        if "運勢" in event.message.text:
            fortune = random.choice(['大凶', '凶', '末吉', '吉','中吉','大吉'])
            msg.append(TextSendMessage(text=fortune))  
        if "吃" in event.message.text:
            eat = random.choice(['水餃', '小7', '火鍋', '炒飯','拉麵','陽春麵'])
            msg.append(TextSendMessage(text=eat)) 
    else:
        msg.append(TextSendMessage(text=event.message.text))

    line_bot_api.reply_message(event.reply_token, messages=msg)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)