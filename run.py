from flask import render_template, jsonify
from flask_socketio import SocketIO, emit
from threading import Thread, Event
import json
from random import random
from time import sleep
from market import app
from market.model import Agents, ProxyOrderBook, UpbitTradeHistory
from market.orderbook import OrderbookThread

# upbit data pulling Thread
thread = Thread()
thread_stop_event = Event()
socketio = SocketIO(app)


# ui data Thread
ui_thread = Thread()
ui_thread_stop_event = Event()


class UIThread(Thread):
    def __init__(self):
        self.delay = 1
        super(UIThread, self).__init__()

    def uiDataGenerator(self):
        """
        """
        # infinite loop
        while not ui_thread_stop_event.isSet():
            data = dict(
                rank=[x._asdict() for x in Agents.query.all()],
                orderbook=ProxyOrderBook.query.order_by(
                    ProxyOrderBook.timestamp.desc()).first()._asdict(),
                prices=[x._asdict() for x in UpbitTradeHistory.query.order_by(
                    UpbitTradeHistory.trade_timestamp.desc()).limit(10).all()]
            )
            socketio.emit('leaderboard',
                          {'data': json.dumps(data)},
                          namespace='/market')
            sleep(self.delay)

    def run(self):
        self.uiDataGenerator()


@app.route("/")
def index():
    # need visibility of the global thread object
    global thread
    if not thread.isAlive():
        print("Starting Thread")
        thread = OrderbookThread()
        thread.start()

    return render_template("index.html")


@socketio.on('connect', namespace='/market')
def test_connect():
    # need visibility of the global thread object
    global ui_thread
    if not ui_thread.isAlive():
        print("Starting Thread")
        ui_thread = UIThread()
        ui_thread.start()


@socketio.on('disconnect', namespace='/market')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0")
