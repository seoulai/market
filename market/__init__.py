"""
Cinyoung Hur, cinyoung.hur@gmail.com
seoulai.com
2018
"""
import os
from flask import Flask, render_template
from flask_compress import Compress
from flask_sqlalchemy import SQLAlchemy
from threading import Thread, Event
from pathlib import Path

"""Create and configure an instance of the Flask application."""

app = Flask(__name__)

if Path("market/env.cfg").exists():
    app.config.from_pyfile("env.cfg")
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = ""

app.config["APP_ROOT"] = os.path.abspath(os.path.dirname(__file__))
app.config["SECRET_KEY"] = "key"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# socketio = SocketIO(app)


db = SQLAlchemy(app)

# Compress text, css, xml, json responeses
Compress(app)


# routes
from market.api import api_route

# routes api
app.register_blueprint(api_route)


from market.orderbook import OrderbookThread

# random number Generator Thread
thread = Thread()
thread_stop_event = Event()


@app.route("/")
def index():
    # need visibility of the global thread object
    global thread
    if not thread.isAlive():
        print("Starting Thread")
        thread = OrderbookThread()
        thread.start()
    return render_template("index.html")
