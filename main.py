import os
from flask import Flask, request
import requests

class Telegram:
    def __init__(self, token, url):
        self.token = token
        self.path = "https://api.telegram.org/bot{}".format(token)
        self.url = url
        self.setWebhook()

    def sendMessage(self, chat_id, text):
        data = {"chat_id": chat_id, "text": text}
        requests.post(url=self.path + "/sendMessage", data=data)
        print("sent message to {} !".format(chat_id))

    def setWebhook(self):
        requests.post(url=self.path + "/setWebhook", data={"url": self.url})


class Update:
    def __init__(self, update):
        self.chat_id = update['message']['chat']['id']
        self.text = update['message']['text']

    def get_command(self):
        if len(self.text) == 0:
            return False
        parts = self.text.split(" ")
        name = parts[0]
        issue_id = False
        params = False
        if name[0] != "/":
            return False
        if len(parts) > 1:
            issue_id = parts[1]
            try:
                params = " ".join(parts[2:])
            except:
                pass
        return Command(name, issue_id, params)

class Command:
    def __init__(self, name, issue_id, params):
        self.name = name
        self.issue_id = issue_id
        self.params = params

    def __repr__(self):
        text = []
        if self.name:
            text.append(self.name)
        if self.issue_id:
            text.append(self.issue_id)
        if self.params:
            text.append(self.params)
        return " ".join(text)


app = Flask(__name__)

token = os.environ["TELEGRAM_TOKEN"]
url = os.environ["HEROKU_URL"]

bot = Telegram(token, url)

@app.route("/botsito", methods=['POST'])
def webhook_handler():
    if request.method == "POST":
        update = Update(request.get_json(force=True))
        command = update.get_command()
        if command:
            bot.sendMessage(update.chat_id, command)
            if command.name == "/get":
                pass
            elif command.name == "/post":
                pass
            elif command.name == "/label":
                pass
            elif command.name == "/close":
                pass
        else:
            bot.sendMessage(update.chat_id, "jajaja")
    return "200"


@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('{}/{}'.format(url, hook))
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"


@app.route('/')
def index():
    return 'Hola, soy consu valencia hehe'
