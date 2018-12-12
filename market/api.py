"""
Cinyoung Hur, cinyoung.hur@gmail.com
seoulai.com
2018
"""
from flask import Blueprint, request, jsonify, make_response
import numpy as np
import pandas as pd
from datetime import datetime
from talib import abstract
from market.base import fee_rt, Constants
from market.model import Agents, TradeHistory
from market import db
from itertools import islice

api_route = Blueprint(
    "api_route",
    __name__,
    url_prefix="/api"
)


@api_route.route("/m/trade", methods=["GET"])
def trade():
    agent_id = request.args.get("agent_id")
    quantity = request.args.get("quantity", 0)
    decision = request.args.get("decision", Constants.HOLD)
    price = request.args.get("price", 0)
    if agent_id is None:
        return make_response(jsonify({"msg": "no agent_id provided"}), 400)

    agent = _get_agent(agent_id)
    if agent is None:
        agent = _add_agent(agent_id)

    _conclude(agent, "KRW-BTC", int(decision), float(quantity), int(price))
    print(_get_avg_buy())
    return jsonify()


@api_route.route("/select", methods=["GET"])
def select():
    exchange = request.args.get("exchange")
    if exchange != "Upbit":
        return make_response(jsonify({"msg": "exchange is not supported"}), 400)
    return jsonify(fee_rt=fee_rt)


@api_route.route("/reset", methods=["GET"])
def reset():
    agent_id = request.args.get("agent_id")
    if agent_id is None:
        return make_response(jsonify({"msg": "no agent_id provided"}), 400)

    agent_data = _add_agent(agent_id)
    if agent_data:
        obs = dict(
            order_book=_get_orderbook_by_tick(),
            trade=_get_recent_price_vol_by_tick()
        )

        obs.update(agent_data._asdict())
        return jsonify(obs=obs)
    else:
        return make_response(jsonify({"msg": "agent is not registered"}), 400)


@api_route.route("/scrap", methods=["GET"])
def scrap():
    n = request.args.get("n", 5)
    window = request.args.get("window", 2)
    n = int(n)
    window = int(window)

    history = dict(
        order_book=_get_orderbook_by_tick(n=n),
        trade=_get_recent_price_vol_by_tick(n=n)
    )

    history_list = []
    df1 = pd.DataFrame(history["order_book"])
    df2 = pd.DataFrame(history["trade"])
    for start, end in _window(range(n), n=window):
        df1_tmp = df1.loc[start:end]
        df2_tmp = df2.loc[start:end]
        history_list.append(
            dict(
                order_book=dict(
                    timestamp=df1_tmp.timestamp.tolist(),
                    ask_price=df1_tmp.ask_price.tolist(),
                    bid_price=df1_tmp.bid_price.tolist(),
                    ask_size=df1_tmp.ask_size.tolist(),
                    bid_size=df1_tmp.bid_size.tolist()),
                trade=dict(
                    timestamp=df2_tmp.timestamp.tolist(),
                    price=df2_tmp.price.tolist(),
                    volume=df2_tmp.volume.tolist(),
                    sid=df2_tmp.sid.tolist(),
                    ask_bid=df2_tmp.ask_bid.tolist())))
    del df1
    del df2
    del history
    return jsonify(history_list)


@api_route.route("/step", methods=["POST"])
def step():
    post_data = request.get_json()
    agent_id = post_data.get("agent_id")
    ticker = post_data.get("ticker")
    decision = post_data.get("decision")
    trad_qty = post_data.get("trad_qty")
    trad_price = post_data.get("trad_price")

    agent = _get_agent(agent_id)
    if agent is None:
        return make_response(jsonify({"msg": "agent is not exist"}), 400)

    if trad_qty < 0:
        return make_response(jsonify({"msg": "wrong quantity (less than zero)"}), 400)

    next_obs, rewards, done, info = _conclude(
        agent, ticker, decision, trad_qty, trad_price)

    return jsonify(next_obs=next_obs,
                   rewards=rewards,
                   done=done,
                   info=info
                   )


def _conclude(
        agent,
        ticker,
        decision,
        trad_qty,
        trad_price):

    rewards = {}
    done = False
    info = {}
    BASE = Constants.BASE

    ccld_price = int(trad_price)
    ccld_qty = trad_qty

    next_obs = dict(
        order_book=_get_orderbook_by_tick(),
        trade=_get_recent_price_vol_by_tick()
    )

    cash = agent.cash
    asset_qty = agent.asset_qtys
    portfolio_val = agent.portfolio_rets_val

    trading_amt = round(ccld_price * ccld_qty, BASE)
    fee = round(trading_amt * fee_rt, BASE)    # fee = trading_amt x 0.0005

    if decision == Constants.BUY:
        if cash < (trading_amt + fee):
            next_obs.update(agent._asdict())
            return next_obs, rewards, done, info

        asset_val = round(trading_amt + fee, BASE)
        cash = round(cash - asset_val, BASE)    # after buying, cash will decrease.
        asset_qty = round(asset_qty + ccld_qty, BASE)

    elif decision == Constants.SELL:
        if asset_qty < ccld_qty:
            next_obs.update(agent._asdict())
            return next_obs, rewards, done, info

        asset_qty = round(asset_qty - ccld_qty, BASE)    # quantity of asset will decrease.
        asset_val = round(trading_amt - fee, BASE)
        cash = round(cash + asset_val, BASE)    # after selling, cash will increase.


    cur_price = next_obs["trade"]["price"][0]
    asset_val = round(asset_qty * cur_price, BASE)
    next_portfolio_val = round(cash + asset_val, BASE)

    # update portfolio_val
    agent.cash = cash
    agent.asset_qtys = asset_qty
    agent.portfolio_rets_val = next_portfolio_val
    if (asset_qty == 0.):
        agent.asset_qtys_zero_updated = datetime.utcnow()
    transaction = TradeHistory(agent.id, decision, ccld_price, ccld_qty, next_portfolio_val)
    db.session.add(transaction)
    db.session.commit()  # update agent's asset, portfolio

    # we just observe state_size time series data.
    next_obs.update(agent._asdict())

    return_amt = round((next_portfolio_val - portfolio_val), BASE)
    return_per = (return_amt/portfolio_val)*100.0
    return_per = int(return_per*10000)/10000.0
    return_sign = np.sign(return_amt)
    buy_ccld_price = round(ccld_price * (1 + fee_rt), BASE)
    sell_ccld_price = round(ccld_price * (1 - fee_rt), BASE)
    buy_change_price = round(cur_price - buy_ccld_price, BASE)
    sell_change_price = round(cur_price - sell_ccld_price, BASE)
    change_price = cur_price-ccld_price
    change_price_sign = np.sign(change_price)
    hit = 1.0 if (decision == Constants.BUY and change_price_sign > 0) or (decision == Constants.SELL and change_price_sign < 0) else 0.0
    real_hit = 1.0 if (decision == Constants.BUY and np.sign(buy_change_price) > 0) or (decision == Constants.SELL and np.sign(sell_change_price) < 0) else 0.0
    score_amt = round(next_portfolio_val - 100000000.0, BASE)
    score = (score_amt/100000000.0)*100.0
    score = int(score*10000)/10000.0


    rewards = dict(
        return_amt=return_amt,
        fee=fee,
        return_per=return_per,
        return_sign=return_sign,
        hit=hit,
        real_hit=real_hit,
        score_amt=score_amt,
        score=score,
        )

    # 8. Time sleep
    # time.sleep(0.3)

    return next_obs, rewards, done, info


def _get_agent(agent_id):
    agent = Agents.query.filter_by(name=agent_id).first()
    return agent


def _add_agent(agent_id):
    agent_data = Agents.query.filter_by(name=agent_id).first()
    if agent_data is not None:
        return agent_data
    new_agent = Agents(name=agent_id)
    db.session.add(new_agent)
    db.session.commit()
    return new_agent


def _get_avg_buy():
    sql = """
    select a.name as agent_id, sum(t.trade_price*t.trade_qty)/sum(t.trade_qty) as avg_buy
    from (
        select agent_id
            , trade_price
            , trade_decision
            , CASE
                WHEN trade_decision = 'buy'  THEN trade_qty
                ELSE trade_qty * (-1)
            END as trade_qty
            , ts
        from trade_history
    ) t
    join agents a on t.agent_id=a.id
    where
        t.trade_decision='buy'
        and t.ts > asset_qtys_zero_updated
    group by a.name
    """
    result = pd.read_sql(sql, db.engine).set_index("agent_id")
    return result.to_dict(orient="index")


def _get_orderbook(n=1):
    sql = """
    select avg(ask_price) as ask_price, avg(bid_price) as bid_price
        , avg(ask_size) as ask_size, avg(bid_size) as bid_size
    from proxy_order_book
    GROUP BY to_timestamp(floor((extract('epoch' from timestamp) / {tick} )) * {tick})
        AT TIME ZONE 'UTC'
    order by to_timestamp(floor((extract('epoch' from timestamp) / {tick} )) * {tick})
        AT TIME ZONE 'UTC' desc
    limit {limit}
    """.format(limit=n, tick=3 * 60)
    result = pd.read_sql(sql, db.engine)
    if n == 1:
        return result.to_dict(orient="record")[0]
    else:
        return dict(ask_price=result.ask_price.tolist(),
                    bid_price=result.bid_price.tolist(),
                    ask_size=result.ask_size.tolist(),
                    bid_size=result.bid_size.tolist())


def _get_orderbook_by_tick(n=200):
    sql = """
    select timestamp, ask_price, bid_price, ask_size, bid_size
    from proxy_order_book
    order by timestamp desc
    limit {limit}
    """.format(limit=n)
    result = pd.read_sql(sql, db.engine)
    if n == 1:
        return result.to_dict(orient="record")[0]
    else:
        return dict(timestamp=result.timestamp.tolist(),
                    ask_price=result.ask_price.tolist(),
                    bid_price=result.bid_price.tolist(),
                    ask_size=result.ask_size.tolist(),
                    bid_size=result.bid_size.tolist())


def _get_orderbook_n_hour_bf(h=1):
    sql = """
    select timestamp, ask_price, bid_price, ask_size, bid_size
    from proxy_order_book
    where timestamp > ((
        select max(trade_timestamp) from upbit_trade_history) - INTERVAL '{h} HOUR')
    """.format(h=h)
    result = pd.read_sql(sql, db.engine)
    return dict(timestamp=result.timestamp.tolist(),
                ask_price=result.ask_price.tolist(),
                bid_price=result.bid_price.tolist(),
                ask_size=result.ask_size.tolist(),
                bid_size=result.bid_size.tolist())


def _get_recent_price_vol(n=1):
    sql = """
    select avg(trade_price) as cur_price, avg(trade_volume) as cur_volume
    from upbit_trade_history
    GROUP BY to_timestamp(floor((extract('epoch' from trade_timestamp) / {tick} )) * {tick})
        AT TIME ZONE 'UTC'
    order by to_timestamp(floor((extract('epoch' from trade_timestamp) / {tick} )) * {tick})
        AT TIME ZONE 'UTC' desc
    limit {limit}
    """.format(limit=n, tick=3 * 60)
    result = pd.read_sql(sql, db.engine)
    result.price = result.price.astype(int)  # .astype(int)
    if n == 1:
        return result.to_dict("record")[0]
    else:
        return dict(price=result.cur_price.tolist(),
                    volume=result.cur_volume.tolist())


def _get_recent_price_vol_by_tick(n=200):
    sql = """
    select trade_timestamp as timestamp,
        trade_price as price,
        trade_volume as volume,
        sequential_id as sid,
        ask_bid
    from upbit_trade_history
    order by trade_timestamp desc
    limit {limit}
    """.format(limit=n)
    result = pd.read_sql(sql, db.engine)
    result.price = result.price.astype(int)
    if n == 1:
        return result.to_dict("record")[0]
    else:
        return dict(timestamp=result.timestamp.tolist(),
                    price=result.price.tolist(),
                    volume=result.volume.tolist(),
                    sid=result.sid.tolist(),
                    ask_bid=result.ask_bid.tolist())


def _get_recent_price_vol_n_hour_bf(h=2):
    sql = """
    select trade_timestamp as timestamp, trade_price as price, trade_volume as volume,
        sequential_id as sid, ask_bid
    from upbit_trade_history
    where trade_timestamp > ((
        select max(trade_timestamp) from upbit_trade_history) - INTERVAL '{h} HOUR')
    """.format(h=h)
    result = pd.read_sql(sql, db.engine)
    return dict(timestamp=result.timestamp.tolist(),
                price=result.price.tolist(),
                volume=result.volume.tolist(),
                sid=result.sid.tolist(),
                ask_bid=result.ask_bid.tolist())


def _get_prices():
    # this data for main UI
    # TODO: use upbit_trade_history model?
    sql = """
    select ts, open
    from (
        SELECT
            COALESCE(to_char(min(trade_timestamp), 'YYYY-MM-DD HH24:MI:SS'), '') as ts
            , (array_agg(trade_price ORDER BY trade_timestamp ASC))[1] as open
        FROM upbit_trade_history
        GROUP BY to_timestamp(floor((extract('epoch' from trade_timestamp) / 10 )) * 10)
        AT TIME ZONE 'UTC'
    ) t
    order by t.ts desc
    limit 100
    """

    result = pd.read_sql(sql, db.engine)
    return result.to_dict("split")["data"]


def _get_ohlc(tick_in_min=3, start_time=None, end_time=None):
    # TODO: use upbit_trade_history model?
    # TODO: slice data from start_time to end_time
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
    return ohlc


def _get_statistics(n=1, start_time=None, end_time=None):
    ohlc = _get_ohlc(3, start_time, end_time)
    # TODO: maybe handle nan differently
    limit = n * -1
    stoch = np.nan_to_num(abstract.STOCH(ohlc))
    macd = np.nan_to_num(abstract.MACD(ohlc))
    output = dict(
        macd=macd[0][limit:].tolist(),
        macd_signal=macd[1][limit:].tolist(),
        macd_hist=macd[2][limit:].tolist(),
        stoch_slowk=stoch[0][limit:].tolist(),
        stoch_slowd=stoch[1][limit:].tolist(),
        vave=np.nan_to_num(abstract.MA(ohlc)[limit:]).tolist(),
        sma=np.nan_to_num(abstract.SMA(ohlc)[limit:]).tolist(),
        rsi=np.nan_to_num(abstract.RSI(ohlc)[limit:]).tolist(),
        stddev=np.nan_to_num(abstract.STDDEV(ohlc)[limit:]).tolist())
    return output


def _window(seq, n=200):
        it = iter(seq)
        result = tuple(islice(it, n))
        if len(result) == n:
            yield min(result), max(result)
        for elem in it:
            result = result[1:] + (elem,)
            yield min(result), max(result)
