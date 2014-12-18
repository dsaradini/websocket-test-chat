Install
=======

> pyvenv env

> source env/bin/activate

> pip install -r requirments.txt


Run
====


Run Server
----------

> source env/bin/activate

> Make run


Run web client
--------------

Open browser at http://localhost:5000/<my_user_nam>


**For HTTP client, the ticket is generated server side, there is no need for authentication**


Run python client
-----------------

> source env/bin/activate

> python ws_client.py

Enter your username and start chatting...


Websocket API
==============

Getting login ticket
--------------------

POST on http://localhost:5000/token

with application/json content

```javascript
{
	'username': "Your username"
	'password': "cool" <-- Static password to be able to connect
}
```

result

```javascript
{
	'ticket': "MY_SECRET_TICKET"
}
```
And use the ticket to connect ot the websocket.

**Ticket is valid 1 minutes**

Websocket url: http://localhost:8128/ws?ticket=<login-ticket>


Websocket messages
------------------

```javascript
{
	"cmd": "command_uri",
	"data" : <any:payload json serializable>
}
```


Demo API
--------


Sent message

```javascript
{
	"cmd": "ch.exodoc.send_message",
	"data": "<string:message>"
}
```

Receive message

```javascript
{
	"cmd": "ch.exodoc.new_message",
	"data": {
		"user": "User name",
		"text": "Text from user"
	}
}
```
