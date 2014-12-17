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


Run python client
-----------------

	> source env/bin/activate
	> python ws_client.py


Websocket message API
=====================

	{
		"cmd": "command_uri",
		"data" : <any:payload json serializable>
	}

Demo API
--------


Sent message

	{
		"cmd": "ch.exodoc.send_message",
		"data": <string:message>
	}

Receive message

	{
		"cmd": "ch.exodoc.new_message",
		"data": {
			"user": "User name",
			"text": "Text from user"
		}
	}