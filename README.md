# Telegram Bot linked to GitHub Repository

Open, comment and close issues from a specific GitHub repository by passing simple commands to a Telegram Bot.

## 1. Requierements
  The application is based on Python's Flask framework, interacting with both Telegram and GitHub APIs. Here is the minimum software to try it:

#### 1.1. Python 3.5.1

#### 1.2. Python Packages
  * Flask == 0.12.2
  * requests==2.18.1
  * os

## 2. Setup
#### 2.1. Clone the repository
  ```
  git clone https://github.com/vjfuenzalida/bot-telegram-github.git
  ```
#### 2.2. Create a Telegram Bot

  talk to *BotFather*, and follow the instructions:
  1. ```/newbot```
  2. submit a **name** for your bot.
  3. submit a **username** (it must end in 'bot').

A token like ```110201543:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw``` will be retrieved. Save it for later use.

#### 2.3. Create Heroku application
  ```
  heroku login
  heroku create
  ```

#### 2.4. Set the minimum environment variables in Heroku by simply running this lines (Ubuntu):

  ```
  heroku config:set HEROKU_URL=<your heroku app URL (end it with a slash ("/")>
  heroku config:set TELEGRAM=<the token generated at the Bot creation>
  heroku config:set FLASK_APP=main.py
  heroku config:set USERNAME=<github username>
  heroku config:set PASSWORD=<github password>
  heroku config:set REPOSITORY=<github repository name>
  ```

  P.S.: The username and password are the ones from the repository owner's github account.
  The repository is the one you want to manage with this bot.

#### 2.5. Deploy to Heroku (account needed)
  Follow this steps or read Heroku's *Deploying with Git* [tutorial](https://devcenter.heroku.com/articles/git)

```
git push heroku master
```  

#### 2.5. Start using your bot to handle the selected repository's issues.
  * `/get #issue_number` : The Bot will send the basic information about the issue selected.
  * `/post #issue_number *answer` : The bot will post the answer in the corresponding issue.
  * `/label #issue_number *label_name *label_color` : The bot will create or update the selected label with the color passed. If no color passed, default color is setted.
  * `/close #issue_number` : The bot will close the selected issue.

Note that "#issue_number" is an integer number, starting in 1, "label_name" can be any string phrase, and "label_color" is a hex color without # (for example: f1bd3a).

## 3. To run the application locally
  To test the application, the following environment variables must be set first:
   * HEROKU_URL=localhost:5000
   * TELEGRAM_TOKEN=[Provided by BotFather]
   * FLASK_APP=python-3.5.1

Start Flask Server typing:
```
path/to/application$ flask run
```
To send messages you can try by sending POST HTTP requests from Postman to the endpoint `http://127.0.0.1:5000/botsito` with the following structure:
```json
{"update_id": 1234,
	"message": {
		"message_id":123,
		"from": {
			"id":1234,
			"first_name":"Test",
      "last_name":"User"},
    "chat": {
      "id":224235976,
      "first_name":"Test",
      "last_name":"User",
      "type":"private"},
    "date":1498098541,
    "text":"/command 1111 some_text",
    "entities":[{
      "type":"bot_command",
      "offset":0,
      "length":6}]
	}
}
```
