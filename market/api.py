"""
Cinyoung Hur, cinyoung.hur@gmail.com
seoulai.com
2018
"""
from flask import Blueprint, request, jsonify
from market.base import fee_rt
from market.agents import ConcreteAgent, agent_list


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
    agent = post_data.get("agent")
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

    # concluded price. (체결가격)
    ccld_price = price
    # concluded quantity. (체결수량)
    ccld_qty = qty

    # total amount of moved money. (거래금액)
    trading_amt = ccld_price * ccld_qty
    fee = trading_amt * fee_rt
    if fee > 0:
        pass

    return new_state, reward, done, info
