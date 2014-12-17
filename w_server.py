from flask import Flask, render_template, redirect
import settings as ws_const

app = Flask(__name__)


@app.route("/")
def root():
    return redirect("/anonymous")


@app.route("/<name>")
def application(name="anonymous"):
    ctx = {
        'ws_url': "ws://{}:{}".format(ws_const.CONNECT_ADDRESS, ws_const.PORT),
        'name': name
    }
    return render_template("index.html", **ctx)

if __name__ == "__main__":
    app.run(debug=True)
