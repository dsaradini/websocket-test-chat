from uuid import uuid4
from pbkdf2 import crypt

from flask import (Flask, render_template, redirect, jsonify, request,
                   abort, json)
import redis
import settings as ws_const


app = Flask(__name__)
client = redis.StrictRedis(host='localhost', port=6379, db=0)


def authenticate(username, password):
    with open("users.json", mode="r") as f:
        users = json.loads(f.read())
        user = users.get(username, None)
    if user:
        if user['password'] == crypt(password, user['password']):
            return {
                "username": username,
                "full_name": user['full_name']
            }
    else:
        # constant time checker
        crypt(password)
    abort(401, "Bad username or password")


def create_ticker(username):
    ticket = str(uuid4())
    redis_data = {
        "username": username
    }
    client.set("ch.exodoc:{}".format(ticket), json.dumps(redis_data),
               ex=ws_const.WS_TICKET_TT)
    return ticket


@app.route("/")
def root():
    return redirect("/anonymous")


@app.route("/token", methods=['POST'])
def _():
    username = request.json['username']
    password = request.json['password']
    user = authenticate(username, password)
    if not user:
        abort(401)
    ticket = create_ticker(user['username'])
    return jsonify({
        "ticket": ticket
    })


@app.route("/<name>")
def application(name="anonymous"):
    ctx = {
        'ws_url': "ws://{}:{}".format(ws_const.CONNECT_ADDRESS, ws_const.PORT),
        'ws_ticket': create_ticker(name),
        'name': name
    }
    return render_template("index.html", **ctx)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
