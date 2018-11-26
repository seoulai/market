from market import db
from datetime import datetime


class Agents(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    cash = db.Column(db.Float, default=100000000)
    asset_qtys_currency = db.Column(db.String(100), default="KRW-BTC")
    asset_qtys = db.Column(db.Float, default=0.0)
    portfolio_rets_val = db.Column(db.Float, default=100000000)
    portfolio_rets_mdd = db.Column(db.Float, default=0.0)
    portfolio_rets_sharp = db.Column(db.Float, default=0.0)

    def __repr__(self):
        return "<Agent %r>" % self.name

    def _asdict(self):
        return dict(
            agent_info={
                "cash": self.cash,
                "asset_qtys": {self.asset_qtys_currency: self.asset_qtys}},
            portfolio_rets={
                "val": self.portfolio_rets_val,
                "mdd": self.portfolio_rets_mdd,
                "sharp": self.portfolio_rets_sharp})


class ProxyOrderBook(db.Model):
    """ Realtime orderbook
    ask/bid size is replaced to 999999999999
    maintain only limited size of data
    """
    timestamp = db.Column(db.DateTime, primary_key=True)
    ask_price = db.Column(db.Float)
    bid_price = db.Column(db.Float)
    ask_size = db.Column(db.BigInteger, default=999999999999)
    bid_size = db.Column(db.BigInteger, default=999999999999)

    def __init__(self, obj):
        self.timestamp = datetime.fromtimestamp(
            obj["timestamp"] / 1000)
        self.ask_price = obj["askPrice"]
        self.bid_price = obj["bidPrice"]
        self.ask_size = obj["askSize"]
        self.bid_size = obj["bidSize"]


class UpbitTradeHistory(db.Model):
    """ Price history 업비트의 체결 히스토리
    This records are used to generate indicators in the following:
    - Overlap Studies
    - Momentum Indicators
    """
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    trade_date = db.Column(db.String)
    trade_time = db.Column(db.String)
    trade_timestamp = db.Column(db.DateTime)
    trade_price = db.Column(db.String)
    trade_volume = db.Column(db.Float)

    def __init__(self, obj):
        self.trade_date = obj["tradeDate"]
        self.trade_time = obj["tradeTime"]
        self.trade_timestamp = datetime.fromtimestamp(
            obj["tradeTimestamp"] / 1000)
        self.trade_price = obj["tradePrice"]
        self.trade_volume = obj["tradeVolume"]


class TradeHistory(db.Model):
    """ Seoul AI Market 체결 히스토리
        Conclude history
    """
    ts = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer)
    trade_decision = db.Column(db.String)
    trade_price = db.Column(db.Float)
    trade_qty = db.Column(db.Float)
    coin_name = db.Column(db.String, default="KRW-BTC")
