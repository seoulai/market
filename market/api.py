"""
Cinyoung Hur, cinyoung.hur@gmail.com
seoulai.com
2018
"""
from flask import Blueprint, request, jsonify
from market.base import fee_rt, Constants, DotDict
from market.agents import ConcreteAgent, agent_list
import numpy as np

api_route = Blueprint(
    "api_route",
    __name__,
    url_prefix="/api"
)


@api_route.route("/register", methods=["POST"])
def register():
    post_data = request.get_json()
    agent = ConcreteAgent(post_data)
    agent_list.add(agent)
    return "Agent is registered"


@api_route.route("/step", methods=["POST"])
def step():
    post_data = request.get_json()
    agent = DotDict(post_data.get("agent"))
    decision = post_data.get("decision")
    price = post_data.get("price")
    qty = post_data.get("qty")

    new_state, reward, done, info = _step(
        agent,
        decision,
        price,
        qty)
    return jsonify(new_state=new_state,
                   reward=reward,
                   done=done,
                   info=info
                   )


@api_route.route("/reset")
def reset():
    pass


def _step(
        agent,
        decision,
        price: float,
        qty: int):
    new_state = {}
    reward = 0
    done = False
    info = {}
    msg = ""

    # concluded price.
    # 체결가격
    ccld_price = price
    # concluded quantity.
    # 체결수량
    ccld_qty = qty

    # total amount of moved money.
    # 거래금액
    trading_amt = ccld_price * ccld_qty
    fee = trading_amt * fee_rt

    # previus potfolio value(previous cash+asset_value)
    # 이전 포트폴리오 가치(이전 현금 + 이전 자산 가치)
    priv_pflo_value = agent.cash+agent.asset_val

    if decision == Constants.BUY:
        # after buying, cash will decrease.
        # 매수 후, 현금은 줄어든다.
        agent.cash = agent.cash-trading_amt-fee
        # quantity of asset will increase.
        # 매수 후, 자산 수량은 늘어난다.
        agent.asset_qty = agent.asset_qty + ccld_qty
    elif decision == Constants.SELL:
        # after selling, cash will increase.
        # 매도 후, 현금은 증가한다.
        agent.cash = agent.cash+(trading_amt-fee)
        # quantity of asset will decrease.
        # 매도 후, 자산 수량은 줄어든다.
        agent.asset_qty = agent.asset_qty - ccld_qty

    # FIXME: read price from database
    # current price
    # 현재가
    cur_price = np.random.randint(100)
    # current asset value is asset_qty x current price
    # 현재 자산 가치 = 자산 수량 x 현재가
    agent.asset_val = agent.asset_qty*cur_price
    # current potfolio value(current cash+asset_value)
    # 현재 포트폴리오 가치(현재 현금, 현재 자산 가치)
    cur_pflo_value = agent.cash+agent.asset_val

    # money that you earn or lose in 1 t.
    # (1 t 동안의 decision으로 변화한 포트폴리오 가치를 reward로 잡음)
    reward = cur_pflo_value-priv_pflo_value

    if cur_pflo_value < 0:
        done = True
        msg = "you bankrupt"

    # FIXME: read price from database
    # we just observe state_size time series data.
    new_state = dict(
        columns=list("abcdefghij"),
        data=np.random.random_sample((20, 10)).tolist(),
        fee_rt=fee_rt)

    info["priv_pflo_value"] = priv_pflo_value
    info["cur_pflo_value"] = cur_pflo_value
    info["1t_return"] = cur_pflo_value-priv_pflo_value
    info["1t_ret_ratio"] = ((cur_pflo_value/priv_pflo_value)-1)*100
    info["fee"] = fee
    info["portfolio_value"] = cur_pflo_value
    info["msg"] = msg

    return new_state, reward, done, info
