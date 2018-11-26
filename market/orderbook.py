"""
Long-lived connection.
"""
import websocket
import json
from market.model import UpbitTradeHistory, ProxyOrderBook
from market import db
from threading import Thread


class OrderbookThread(Thread):
    def __init__(self):

        url_websocket = r"wss://crix-websocket.upbit.com/sockjs/774/bw4tu4s3/websocket"
        websocket.enableTrace(True)
        self.ws_payload = self.preprare_req_data()
        self.ws = websocket.WebSocketApp(url_websocket,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws.on_open = self.on_open
        super(OrderbookThread, self).__init__()

    def preprare_req_data(self):
        prefix = "CRIX.UPBIT"
        currency_list = ["KRW-BTC"]
        response_types = ["crixOrderbook", "crixTrade"
                          #   , "recentCrix"
                          ]

        req_item = [dict(type=response_type,
                         codes=["{}.{}".format(prefix, code)
                                for code in currency_list],
                         isOnlyRealtime=True) for response_type in response_types]
        req_data = [dict(ticket="ram macbook"),
                    *req_item]
        return json.dumps(json.dumps(req_data))

    def on_message(self, message):
        raw_data = message[1:]  # trim prefix "a"
        if raw_data:
            body = json.loads(json.loads(raw_data)[0])
            if body["type"] == "crixOrderbook":
                latest_orderbooks = body["orderbookUnits"][-1]
                latest_orderbooks["askSize"] = 999999999999
                latest_orderbooks["bidSize"] = 999999999999
                latest_orderbooks["timestamp"] = body["timestamp"]
                db.session.add(ProxyOrderBook(latest_orderbooks))
                db.session.commit()

            elif body["type"] == "crixTrade":
                db.session.add(UpbitTradeHistory(body))
                db.session.commit()

    def on_error(self, error):
        print(error)

    def on_close(self):
        print("close")

    def on_open(self):
        self.ws.send(self.ws_payload)

    def pull_upbit_data(self):
        """
        Generate a random number every 1 second and emit to a socketio instance (broadcast)
        Ideally to be run in a separate thread?
        """
        # while not thread_stop_event.isSet():
        try:
            self.ws.run_forever()
        except Exception as e:
            print(e)

    def run(self):
        self.pull_upbit_data()
