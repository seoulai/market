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

    next_obs, reward, done, info = _conclude(
        agent, ticker, decision, trad_qty, trad_price)
    reward = _simulate(agent, ticker, decision, trad_qty, trad_price)
    done = _gameover(agent, ticker, decision, trad_qty, trad_price)

    next_obs = dict(
        order_book=_get_orderbook(),
        statistics=_get_statistics(tick_in_min=3),
    )
    next_obs.update(agent._asdict())

    return jsonify(next_obs=next_obs,
                   reward=reward,
                   done=done,
                   info=info
                   )


def _gameover(agent_id, ticker, decision, trad_qty, trad_price):
    return False


def _simulate(agent_id, ticker, decision, trad_qty, trad_price):
    return 1.0


def _conclude(
        agent,
        ticker,
        decision,
        trad_price,
        trad_qty):

    reward = 0
    done = False
    info = {}
    msg = ""

    # concluded price.
    # 체결가격
    ccld_price = trad_price
    # concluded quantity.
    # 체결수량
    ccld_qty = trad_qty

    # total amount of moved money.
    # 거래금액
    trading_amt = ccld_price * ccld_qty
    fee = trading_amt * fee_rt

    # previus potfolio value(previous cash+asset_value)
    # 이전 포트폴리오 가치(이전 현금 + 이전 자산 가치)
    priv_pflo_value = agent.cash + agent.portfolio_rets_val

    if decision == Constants.BUY:
        # after buying, cash will decrease.
        # 매수 후, 현금은 줄어든다.
        agent.cash = agent.cash - trading_amt - fee
        # quantity of asset will increase.
        # 매수 후, 자산 수량은 늘어난다.
        agent.asset_qtys = agent.asset_qtys + ccld_qty
    elif decision == Constants.SELL:
        # after selling, cash will increase.
        # 매도 후, 현금은 증가한다.
        agent.cash = agent.cash + (trading_amt - fee)
        # quantity of asset will decrease.
        # 매도 후, 자산 수량은 줄어든다.
        agent.asset_qtys = agent.asset_qtys - ccld_qty

    # FIXME: read price from database
    # current price
    # 현재가
    cur_price = _get_orderbook()["ask_price"]
    # current asset value is asset_qty x current price
    # 현재 자산 가치 = 자산 수량 x 현재가
    agent.portfolio_rets_val = agent.asset_qtys * cur_price
    # current potfolio value(current cash+asset_value)
    # 현재 포트폴리오 가치(현재 현금, 현재 자산 가치)
    cur_pflo_value = agent.cash + agent.portfolio_rets_val

    # money that you earn or lose in 1 t.
    # (1 t 동안의 decision으로 변화한 포트폴리오 가치를 reward로 잡음)
    reward = cur_pflo_value - priv_pflo_value

    if cur_pflo_value < 0:
        done = True
        msg = "you bankrupt"

    # we just observe state_size time series data.
    next_obs = dict(
        order_book=_get_orderbook(),
        statistics=_get_statistics(tick_in_min=3)
    )
    next_obs.update(agent._asdict())

    info["priv_pflo_value"] = priv_pflo_value
    info["cur_pflo_value"] = cur_pflo_value
    info["1t_return"] = cur_pflo_value - priv_pflo_value
    info["1t_ret_ratio"] = ((cur_pflo_value / priv_pflo_value) - 1) * 100
    info["fee"] = fee
    info["portfolio_value"] = cur_pflo_value
    info["msg"] = msg

    db.session.commit()  # update agent's asset, portfolio
    return next_obs, reward, done, info


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


def _get_statistics(tick_in_min, start_time=None, end_time=None):
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
    # TODO: maybe handle nan differently
    output = dict(ma=np.nan_to_num(abstract.MA(ohlc)).tolist(),
                  sma=np.nan_to_num(abstract.SMA(ohlc, timeperiod=25)).tolist())
    return output
