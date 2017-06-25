from flask import Flask, render_template, request
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.heroku import Heroku
from classes import *
import os
import re
import json
import requests
import sqlite3

app = Flask(__name__)

################
## COMPONENTS ##
################

## TELEGRAM
token = os.environ["TELEGRAM_TOKEN"]
url = os.environ["HEROKU_URL"]
hook_telegram = "bot_hook"
bot = Telegram(token, url, hook_telegram)

## GITHUB
address = "https://api.github.com"
owner = os.environ["USERNAME"]
repo = os.environ["REPOSITORY"]
hook_git = "new_issue"
git = Github(address, url, owner, repo, hook_git)

## DATABASE
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///chats'
heroku = Heroku(app)
db = SQLAlchemy(app)

# Create our database model
class Chat(db.Model):
    __tablename__ = "chats"
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, unique=True)

    def __init__(self, chat_id):
        self.chat_id = chat_id

    def __repr__(self):
        return '<Chat ID %r>' % str(self.chat_id)

@app.route("/" + bot.hook, methods=['POST'])
def webhook_handler():
    if request.method == "POST":
        data = request.get_json(force=True)
        if "zen" in data.keys():
            return "200"
        update = Update(data)
        chat_id = int(update.chat_id)
        if not db.session.query(Chat).filter(Chat.chat_id == chat_id).count():
            reg = Chat(chat_id)
            db.session.add(reg)
            db.session.commit()
            # print("id {} saved".format(chat_id))
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
            lines = ["{} {}".format(key, value) for key, value in bot.commands.items()]
            comms += "\n".join(lines)
            bot.sendMessage(update.chat_id, comms)
    return "200"

@app.route("/" + git.hook, methods=['POST'])
def git_webhook_handler():
    if request.method == "POST":
        data = request.get_json(force=True)
        if "zen" in data.keys():
            return "200"
        notification = Notification(data, git)
        action = notification.action
        if action in ["opened", "reopened", "closed"]:
            # print("IT WORKS!!!!")
            if action == "opened":
                for chat in db.session.query(Chat.chat_id).distinct():
                    bot.sendMessage(chat, "New issue '{}' created.".format(notification.issue.title))
            else:
                for chat in db.session.query(Chat.chat_id).distinct():
                    bot.sendMessage(chat, "Issue '{}' is {}.".format(notification.issue.title, action))
    return "200"

@app.route('/')
def index():
    return render_template('index.html')
