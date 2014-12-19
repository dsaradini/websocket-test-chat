from uuid import uuid4
from pbkdf2 import crypt

from flask import (Flask, render_template, redirect, jsonify, request,
                   abort, json, session, flash, url_for)
import redis
import settings as ws_const


SECRET_KEY = 'development key'
DEBUG = True


client = redis.StrictRedis(host='localhost', port=6379, db=0)

app = Flask(__name__)
app.config.from_object(__name__)


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
    if "logged_user" not in session:
        return redirect(url_for("login"))
    return redirect(url_for("tchat"))


@app.route("/token", methods=['POST'])
def token():
    username = request.json['username']
    password = request.json['password']
    user = authenticate(username, password)
    if not user:
        abort(401)
    ticket = create_ticker(user['username'])
    return jsonify({
        "ticket": ticket
    })


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = authenticate(
            request.form['username'],
            request.form['password']
        )
        if not user:
            error = 'Invalid username/password'
        else:
            session['logged_user'] = user
            flash('You were logged in')
            return redirect(url_for('tchat'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_user', None)
    flash('You were logged out')
    return redirect(url_for('login'))


@app.route("/tchat")
def tchat():
    if "logged_user" not in session:
        return redirect(url_for('login'))
    username = session['logged_user']['username']
    ctx = {
        'ws_url': "ws://{}:{}".format(ws_const.CONNECT_ADDRESS, ws_const.PORT),
        'ws_ticket': create_ticker(username),
        'name': username
    }
    return render_template("tchat.html", **ctx)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
