"""
Cinyoung Hur, cinyoung.hur@gmail.com
seoulai.com
2018
"""
from flask import Blueprint, request, jsonify, make_response
import numpy as np
import pandas as pd
from talib import abstract
from market.base import fee_rt, Constants
from market.model import Agents
from market import db

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
    agent = _get_agent(agent_id)
    return jsonify(agent._asrank())


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
            order_book=_get_orderbook(),
            **_get_recent_price_vol(),
            statistics=_get_statistics(tick_in_min=3)
        )

        obs.update(agent_data._asdict())
        return jsonify(obs=obs)
    else:
        return make_response(jsonify({"msg": "agent is not registered"}), 400)


@api_route.route("/scrap", methods=["GET"])
def scrap():
    start_time = request.args.get("start_time")
    end_time = request.args.get("end_time")

    if start_time == "hh:mm:ss" and end_time == "hh:mm:ss":
        pass
    #     select state from redis cache table
    # else
    #     select state from log_table where time_stamp >= start_time and time_stamp <= end_time

    history = dict(
        order_book=_get_orderbook(),
        **_get_recent_price_vol(),
        statistics=_get_statistics(tick_in_min=3,
                                   start_time=start_time,
                                   end_time=end_time)
    )

    return jsonify(history=history)


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

    next_obs, rewards, done, info = _conclude(
        agent, ticker, decision, trad_qty, trad_price)

    done = _gameover(agent, ticker, decision, trad_qty, trad_price)

    next_obs = dict(
        order_book=_get_orderbook(),
        **_get_recent_price_vol(),
        statistics=_get_statistics(tick_in_min=3),
    )
    next_obs.update(agent._asdict())

    return jsonify(next_obs=next_obs,
                   rewards=rewards,
                   done=done,
                   info=info
                   )


def _gameover(agent_id, ticker, decision, trad_qty, trad_price):
    return False


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
    FEE_BASE = Constants.FEE_BASE

    ccld_price = trad_price
    ccld_qty = trad_qty

    next_obs = dict(
        order_book=_get_orderbook(),
        statistics=_get_statistics(tick_in_min=3)
    )
    cash = agent.cash
    asset_qty = agent.asset_qtys
    portfolio_val = agent.portfolio_rets_val
    trading_amt = ccld_price * ccld_qty
    fee = round(ccld_price * ccld_qty * fee_rt, FEE_BASE)

    if decision == Constants.BUY:
        # after buying, cash will decrease.
        cash = round((cash - trading_amt - fee), BASE)
        # quantity of asset will increase.
        asset_qty = round((asset_qty + ccld_qty), BASE)

        if cash < (trading_amt + fee):
            next_obs.update(agent._asdict())
            return next_obs, rewards, done, info
    elif decision == Constants.SELL:
        # after selling, cash will increase.
        cash = round((cash + trading_amt - fee), BASE)
        # quantity of asset will decrease.
        print(asset_qty, ccld_qty, asset_qty < ccld_qty)
        if asset_qty < ccld_qty:
            next_obs.update(agent._asdict())
            return next_obs, rewards, done, info
        asset_qty = round((asset_qty - ccld_qty), BASE)
        print(asset_qty)

    cur_price = _get_recent_price_vol()["cur_price"]
    asset_val = asset_qty * cur_price
    next_portfolio_val = round((cash + asset_val), BASE)

    # update portfolio_val
    agent.cash = cash
    agent.asset_qtys = asset_qty
    agent.portfolio_rets_val = next_portfolio_val
    db.session.commit()  # update agent's asset, portfolio

    return_amt = round((next_portfolio_val - portfolio_val), BASE)
    return_per = round(
        (next_portfolio_val / float(portfolio_val) - 1) * 100.0, BASE)
    return_sign = np.sign(return_amt)
    score_amt = round((next_portfolio_val - 100_000_000), BASE)
    score = round(((next_portfolio_val / 100_000_000) - 1) * 100, BASE)

    rewards = dict(
        return_amt=return_amt,
        return_per=return_per,
        return_sign=return_sign,
        score_amt=score_amt,
        score=score)

    # we just observe state_size time series data.
    next_obs.update(agent._asdict())

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


def _get_orderbook():
    sql = """
    select ask_price, bid_price, ask_size, bid_size
    from proxy_order_book
    order by timestamp desc
    limit 1
    """
    result = pd.read_sql(sql, db.engine)
    return result.to_dict(orient="record")[0]


def _get_recent_price_vol():
    sql = """
    select trade_price as cur_price, trade_volume as cur_volume
    from upbit_trade_history
    order by trade_timestamp desc
    limit 1
    """
    result = pd.read_sql(sql, db.engine)
    result.cur_price = result.cur_price.astype(float)  # .astype(int)
    return result.to_dict("record")[0]


def _get_prices():
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


def _get_ohlc(tick_in_min, start_time=None, end_time=None):
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


def _get_statistics(tick_in_min, start_time=None, end_time=None):
    ohlc = _get_ohlc(tick_in_min, start_time, end_time)
    # TODO: maybe handle nan differently
    stoch = np.nan_to_num(abstract.STOCH(ohlc))
    macd = np.nan_to_num(abstract.MACD(ohlc))
    output = dict(
        macd_first=macd[0][-1],
        macd_second=macd[1][-1],
        macd_third=macd[2][-1],
        stoch_first=stoch[0][-1],
        stoch_second=stoch[1][-1],
        ma=np.nan_to_num(abstract.MA(ohlc)[-1]).tolist(),
        sma=np.nan_to_num(abstract.SMA(ohlc)[-1]).tolist(),
        rsi=np.nan_to_num(abstract.RSI(ohlc)[-1]).tolist(),
        std=np.nan_to_num(abstract.MA(ohlc)[-1]).tolist())
    return output
