"""
Cinyoung Hur, cinyoung.hur@gmail.com
seoulai.com
2018
"""
import os
from flask import Flask, render_template
from flask_compress import Compress
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from random import random
from time import sleep
from threading import Thread, Event

# def create_app(test_config=None):
"""Create and configure an instance of the Flask application."""

app = Flask(__name__)
app.config.from_pyfile("env.cfg")
app.config["APP_ROOT"] = os.path.abspath(os.path.dirname(__file__))
app.config["SECRET_KEY"] = "key"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

socketio = SocketIO(app)


db = SQLAlchemy(app)

# Compress text, css, xml, json responeses
Compress(app)


# routes
from market.api import api_route

# routes api
app.register_blueprint(api_route)


# random number Generator Thread
thread = Thread()
thread_stop_event = Event()


class RandomThread(Thread):
    def __init__(self):
        self.delay = 1
        super(RandomThread, self).__init__()

    def randomNumberGenerator(self):
        """
        Generate a random number every 1 second and emit to a socketio instance (broadcast)
        Ideally to be run in a separate thread?
        """
        # infinite loop of magical random numbers
        print("Making random numbers")
        while not thread_stop_event.isSet():
            number = round(random() * 10, 3)
            print(number)
            socketio.emit("newnumber", {"number": number}, namespace="/test")
            sleep(self.delay)

    def run(self):
        self.randomNumberGenerator()


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("connect", namespace="/test")
def test_connect():
    # need visibility of the global thread object
    global thread
    print("Client connected")

    # Start the random number generator thread only if the thread has not been started before.
    if not thread.isAlive():
        print("Starting Thread")
        thread = RandomThread()
        thread.start()


@socketio.on("disconnect", namespace="/test")
def test_disconnect():
    print("Client disconnected")
