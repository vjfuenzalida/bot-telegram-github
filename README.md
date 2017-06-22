# Telegram Bot linked to GitHub Repository

Open, comment and close issues from a specific GitHub repository by passing simple commands to a Telegram Bot.

## 1. Requierements
  The application is based on Python's Flask framework, interacting with both Telegram and GitHub APIs. Here is the minimum software to try it:

#### 1.1. Python 3.5.1

#### 1.2. Python Packages
  * Flask == 0.12.2
  * requests==2.18.1
  * os

## 2. Instructions
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
