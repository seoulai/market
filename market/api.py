"""
Cinyoung Hur, cinyoung.hur@gmail.com
seoulai.com
2018
"""
from flask import Blueprint, request, jsonify, make_response
import numpy as np
from market.base import fee_rt, Constants
from market.model import Agents
from market import db

api_route = Blueprint(
    "api_route",
    __name__,
    url_prefix="/api"
)

max_qty = 10_000_000


@api_route.route("/select", methods=["GET"])
def select():
    get_data = request.get_json()
    exchange = get_data.get("exchange")
    if exchange != "Upbit":
        return make_response(jsonify({"msg": "exchange is not supported"}), 400)
    return jsonify(fee_rt=fee_rt)


@api_route.route("/reset", methods=["POST"])
def reset():
    get_data = request.get_json()
    agent_id = get_data.get("agent_id")

    agent_data = _add_agent(agent_id)
    if agent_data:
        state = dict(
            order_book=np.sort(np.random.random_sample(21) * 100).tolist(),
            statistics=dict(ma10=100.0, std10=5.0),
        )

        state.update(agent_data)
        return jsonify(state=state)
    else:
        return make_response(jsonify({"msg": "agent is already registered"}), 400)


@api_route.route("/scrap", methods=["GET"])
def scrap():
    # get_data = request.get_json()
    # start_time = get_data.get("start_time")
    # end_time= get_data.get("end_time")

    # if start_time == "hh:mm:ss" and end_time == "hh:mm:ss":
    #     select state from redis cache table
    # else
    #     select state from log_table where time_stamp >= start_time and time_stamp <= end_time

    scraped_data = dict(
        order_book=np.sort(np.random.random_sample(21) * 100).tolist(),
        statistics=dict(ma10=100.0, std10=5.0),
    )

    return jsonify(scraped_data=scraped_data)


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

    _conclude(agent, ticker, decision, trad_qty, trad_price)
    reward = _simulate(agent, ticker, decision, trad_qty, trad_price)
    done = _gameover(agent, ticker, decision, trad_qty, trad_price)

    next_state = dict(
        order_book=np.sort(np.random.random_sample(21) * 100).tolist(),
        statistics=dict(ma10=100.0, std10=5.0),
    )
    next_state.update(agent._asdict())

    return jsonify(next_state=next_state,
                   reward=reward,
                   done=done,
                   info="info"
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
    cur_price = np.random.randint(100)
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

    # FIXME: read price from database
    # we just observe state_size time series data.
    next_state = dict(
        order_book=np.sort(np.random.random_sample(21) * 100).tolist(),
        agent_info=dict(cash=agent.cash,
                        asset_qtys=dict(ticker="KRW-BTC",
                                        asset_qty=max_qty)),
        statistics=dict(ma10=100.0, std10=5.0),
        portfolio_ret=dict(value=10_000_000, mdd=0.0, sharp=0.0),
    )

    info["priv_pflo_value"] = priv_pflo_value
    info["cur_pflo_value"] = cur_pflo_value
    info["1t_return"] = cur_pflo_value - priv_pflo_value
    info["1t_ret_ratio"] = ((cur_pflo_value / priv_pflo_value) - 1) * 100
    info["fee"] = fee
    info["portfolio_value"] = cur_pflo_value
    info["msg"] = msg

    return next_state, reward, done, info


def _get_agent(agent_id):
    agent = Agents.query.filter_by(name=agent_id).first()
    return agent


def _add_agent(agent_id):
    ret = Agents.query.filter_by(name=agent_id).scalar()
    if ret is not None:
        return None

    db.session.add(Agents(name=agent_id))
    db.session.commit()

    agent_data = dict(
        agent_info={"cash": 100_000_000, "asset_qtys": {"KRW-BTC": 0.0}},
        portfolio_rets={"val": 100_000_000, "mdd": 0.0, "sharp": 0.0})
    return agent_data
