import requests
import os
import json
import re

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

    def __repr__(self):
        text = self.title.upper()
        text += " (by: " + self.author + ")\n"
        text += "description: " + self.body
        return text


class Github:
    def __init__(self, address, owner, repo):
        self.address = address
        self.owner = owner
        self.repo = repo
        self.session = requests.Session()
        self.session.auth = (os.environ["USERNAME"], os.environ["PASSWORD"])
        self.issues = []
        self.labels_url = self.address + "/repos/{}/{}/labels".format(self.owner, self.repo)

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
