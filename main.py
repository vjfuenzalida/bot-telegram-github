import re
import os
import json
from flask import Flask, request
import requests
from github import Issue, Github, create_label

class Telegram:
    def __init__(self, token, url, hook):
        self.token = token
        self.path = "https://api.telegram.org/bot{}".format(token)
        self.url = url
        self.hook = hook
        self.setWebhook()
        self.commands = {"/get": "#issue",
                            "/post": "#issue *comment",
                            "/label": "#issue *name *color(hex)",
                            "/close": "#issue",
                            "/open": "#issue",
                            "/comments": "#issue #quantity"}

    def sendMessage(self, chat_id, text):
        data = {"chat_id": chat_id, "text": text}
        requests.post(url=self.path + "/sendMessage", data=data)
        # print("sent message to {} !".format(chat_id))

    def setWebhook(self):
        data = {"url": self.url + self.hook}
        requests.post(url=self.path + "/setWebhook", data=data)
        # print(data)

class Notification:
    def __init__(self, data, git):
        self.issue = Issue(data['issue'], git)
        self.repository = data['repository']
        self.action = data["action"]
        self.sender = data["sender"]

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
        else:
            return False
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
hook_telegram = "bot_hook"

bot = Telegram(token, url, hook_telegram)

address = "https://api.github.com"
owner = os.environ["USERNAME"]
repo = os.environ["REPOSITORY"]
hook_git = "new_issue"

git = Github(address, url, owner, repo, hook_git)

@app.route("/" + bot.hook, methods=['POST'])
def webhook_handler():
    if request.method == "POST":
        update = Update(request.get_json(force=True))
        command = update.get_command()
        if command:
            issue_url = git.issue_url(command.issue_id)
            api_response = git.get(issue_url)
            if api_response.status_code == 200:
                issue = Issue(api_response.json(), git)
            else:
                return str(api_response.status_code)
            # bot.sendMessage(update.chat_id, command)
            if command.name == "/get":
                bot.sendMessage(update.chat_id, issue)
            elif command.name == "/post":
                issue.post_answer(command.params)
                bot.sendMessage(update.chat_id, "comment posted")
            elif command.name == "/label":
                items = command.params.split(" ")
                if len(items) > 1:
                    label = create_label({"name": " ".join(items[:-1]),"color": items[-1]})
                elif len(items) == 1:
                    label = create_label({"name": items[0]})
                else:
                    return "404"
                issue.add_label(label)
                bot.sendMessage(update.chat_id, "label added")
            elif command.name == "/close":
                issue.close()
                bot.sendMessage(update.chat_id, "issue closed")
            elif command.name == "/open":
                issue.open()
                bot.sendMessage(update.chat_id, "issue reopened")
            elif command.name == "/comments":
                if re.search(r'^[0-9]+$', command.params):
                    comments = issue.get_comments(command.params)
                else:
                    comments = issue.get_comments()
                comments = list(map(lambda x: "\t{}: '{}'".format(x[0],x[1].strip()), comments))
                output = issue.__repr__()
                output += "\n\nList of comments: \n"
                output += "\n".join(comments)
                bot.sendMessage(update.chat_id, output)
        else:
            comms = "Try these commands: \n\n"
            comms += "\n".join(list(map(lambda x, y: "{} {}".format(x,y), bot.commands.items())))
            bot.sendMessage(update.chat_id, comms)
    return "200"

@app.route("/" + git.hook, methods=['POST'])
def git_webhook_handler():
    if request.method == "POST":
        print(json.dumps(request.get_json(force=True), indent=2))
        notification = Notification(request.get_json(force=True), git)
        if notification.action == "opened":
            "IT WORKS!!!!"
            bot.sendMessage(update.chat_id, "New issue '{}' created.".format(notification.issue))
    return "200"

@app.route('/')
def index():
    return 'By Vicente Fuenzalida'
