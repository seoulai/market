"""
Long-lived connection.
"""
import websocket
import json
import traceback
from market.model import UpbitTradeHistory
from market import db
import pandas as pd
from talib import abstract

prefix = "CRIX.UPBIT"
currency_list = ["KRW-BTC"]
response_types = ["crixOrderbook", "crixTrade"
                  #   , "recentCrix"
                  ]

url_websocket = r"wss://crix-websocket.upbit.com/sockjs/774/bw4tu4s3/websocket"


req_item = [dict(type=response_type,
                 codes=["{}.{}".format(prefix, code)
                        for code in currency_list],
                 isOnlyRealtime=True) for response_type in response_types]
req_data = [dict(ticket="ram macbook"),
            *req_item]

ws_payload = json.dumps(json.dumps(req_data))


def gen_indicators(tick_in_min=1):
    sql = """
    SELECT
        min(trade_price) low
        , max(trade_price) high
        , (array_agg(trade_price ORDER BY trade_timestamp ASC))[1] open
        , ((array_agg(trade_price ORDER BY trade_timestamp DESC))[1]) as close
        , sum(trade_volume) volume
    FROM upbit_trade_history
    GROUP BY to_timestamp(floor((extract('epoch' from trade_timestamp) / {tick} )) * {tick})
    AT TIME ZONE 'UTC'
    """.format(tick=tick_in_min * 60)

    result = pd.read_sql(sql, db.engine).astype(float)
    ohlc = dict(open=result.open,
                close=result.close,
                low=result.low,
                high=result.high,
                volume=result.volume)
    # print(d.dtypes)
    output = dict(ma=abstract.MA(ohlc),
                  sma=abstract.SMA(ohlc, timeperiod=25))
    print(output)


def on_message(ws, message):
    raw_data = message[1:]  # trim prefix "a"
    if raw_data:
        body = json.loads(json.loads(raw_data)[0])
        if body["type"] == "crixOrderbook":
            latest_orderbooks = body["orderbookUnits"][-1]
            latest_orderbooks["askSize"] = 999999999999
            latest_orderbooks["bidSize"] = 999999999999
        elif body["type"] == "crixTrade":
            db.session.add(UpbitTradeHistory(body))
            db.session.commit()
            gen_indicators()


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("close")


def on_open(ws):
    ws.send(ws_payload)


try:
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(url_websocket,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

    ws.on_open = on_open
    ws.run_forever()

except Exception as e:
    print(e)
    traceback.print_exc
