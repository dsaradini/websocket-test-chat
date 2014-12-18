from uuid import uuid4

from flask import (Flask, render_template, redirect, jsonify, request,
                   abort, json)
import redis
import settings as ws_const

app = Flask(__name__)
client = redis.StrictRedis(host='localhost', port=6379, db=0)


def create_ticker(username):
    ticket = str(uuid4())
    redis_data = {
        "username": username
    }
    client.set("ch.exodoc:{}".format(ticket), json.dumps(redis_data), ex=60)
    return ticket


@app.route("/")
def root():
    return redirect("/anonymous")


@app.route("/token", methods=['POST'])
def _():
    username = request.json['username']
    password = request.json['password']
    if password != "cool":
        abort(401)
    ticket = create_ticker(username)
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

