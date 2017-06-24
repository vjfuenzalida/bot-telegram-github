import requests
import os
import json
import re

class Github:
    def __init__(self, address, url, owner, repo, hook):
        self.address = address
        self.owner = owner
        self.repo = repo
        self.url = url
        self.hook = hook
        self.session = requests.Session()
        self.session.auth = (os.environ["USERNAME"], os.environ["PASSWORD"])
        self.issues = []
        self.webhook_url = self.address + "/repos/{}/{}/hooks".format(self.owner, self.repo)
        self.labels_url = self.address + "/repos/{}/{}/labels".format(self.owner, self.repo)
        self.setWebhook()

    def setWebhook(self):
        # Delete existing hooks
        hooks = list(map(lambda x: str(x["id"]), self.session.get(url=self.webhook_url).json()))
        for h in hooks:
            x = self.session.delete(url=self.webhook_url + "/" + h)
        # Set new hook
        config = {"url": self.url + self.hook, "content_type": "json"}
        data = {"name": "web", "events": ["issues"], "config": config}
        x = self.session.post(url=self.webhook_url, json=data)

    def issue_url(self,number):
        return self.address + "/repos/{}/{}/issues/{}".format(self.owner, self.repo, number)

    def get(self, url):
        return self.session.get(url)

    def post(self, url, json):
        return self.session.post(url=url, json=json)

    def patch(self, url, json):
        return self.session.patch(url=url, json=json)

    def get_issues(self):
        if len(self.issues) == 0:
            get_issues = "/repos/{}/{}/issues".format(self.owner, self.repo)
            get_issues += "?{}={}".format("state","all")
            data = self.get(url=self.address + get_issues)
            self.issues = data.json()
        return self.issues

class Issue:
    all = []
    def __init__(self, json, git):
        self.title = json["title"]
        self.body = json["body"]
        self.assignee = json["assignee"]
        self.assignees = json["assignees"]
        self.milestone = json["milestone"]
        self.state = json["state"]
        self.labels  = json["labels"]
        self.number = json["number"]
        self.ide = json["id"]
        self.author = json["user"]["login"]
        self.git = git
        # url to the issue
        self.url = self.git.address + "/repos/{}/{}/issues/{}".format(git.owner, git.repo, self.number)
        Issue.all.append(self)

    def add_label(self, label):
        all_labels = self.git.get(self.git.labels_url).json()
        names = list(map(lambda x: x["name"], all_labels))
        repo_labels = self.git.labels_url
        issue_labels = self.url + "/labels"
        labels = list(map(lambda x: x["name"], self.git.get(url=issue_labels).json()))
        # print(label)
        if label["name"] in names:
            # update label
            self.git.patch(url=repo_labels + "/{}".format(label["name"]), json=label)
            # print("patched")
        else:
            # create label
            self.git.post(url=repo_labels, json=label)
            # print("posted")
            labels.append(label["name"])
        x = self.git.post(url=issue_labels, json=[label["name"]])
        # print(x)
        # print("Issue {} updated with label {} and color {}".format(self.number, label["name"], label["color"]))
    def close(self):
        self.state = "closed"
        response = self.git.patch(url=self.url, json={"state": self.state})
        # print("Issue {} closed!".format(self.number))

    def open(self):
        self.state = "open"
        response = self.git.patch(url=self.url, json={"state": self.state})
        # print("Issue {} opened!".format(self.number))

    def post_answer(self, body):
        data = {"body": body}
        response = self.git.post(url=self.url+"/comments", json=data)
        # print("Issue {} commented with: {}".format(self.number, body))

    def get_comments(self, number=0):
        # GET /repos/:owner/:repo/issues/:number/comments
        url = self.url + "/comments"
        response = self.git.get(url=url).json()
        comments = list(map(lambda x: (x["user"]["login"], x["body"]), response))
        number = min(int(number), len(comments))
        if number > 0:
            return comments[(number*-1-1):]
        else:
            return comments

    def __repr__(self):
        text = self.title.upper()
        text += " (by: " + self.author + ")\n"
        text += "description: " + self.body
        return text

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

def create_label(params):
    result = {}
    attribs = list(params.keys())
    valid = False
    colors = {"bug": "ee0701", "duplicate": "cccccc", "enhancement": "84b6eb", "help wanted": "128A0C", "invalid": "e6e6e6", "question": "cc317c", "wontfix": "ffffff"}
    if "name" in attribs:
        result.update({"name": params["name"]})
        valid = True
    if "color" in attribs:
        if re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', "#" + params["color"]):
            result.update({"color": params["color"]})
        else:
            result.update({"color": colors["bug"]})
    else:
        if valid and params["name"] in list(colors.keys()):
            result.update({"color": colors[params["name"]]})
    if valid:
        return result
    return False
