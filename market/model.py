from market import db
from datetime import datetime
from market.base import Constants


class Agents(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    cash = db.Column(db.Float, default=100000000)
    asset_qtys_currency = db.Column(db.String(100), default="KRW-BTC")
    asset_qtys = db.Column(db.Float, default=0.0)
    portfolio_rets_val = db.Column(db.Float, default=100000000)
    portfolio_rets_mdd = db.Column(db.Float, default=0.0)
    portfolio_rets_sharp = db.Column(db.Float, default=0.0)
    asset_qtys_zero_updated = db.Column(db.DateTime, default=datetime.utcnow)

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

    def _asrank(self):
        cur_price = UpbitTradeHistory.query.first().trade_price
        
        asset_val = round(self.asset_qtys * cur_price, Constants.BASE)
        portfolio_val = round(self.cash + asset_val, Constants.BASE)
        print(cur_price, asset_val, portfolio_val)

        profit_ratio = ((portfolio_val / 100000000.0) - 1) * 100.0
        return dict(name=self.name,
                    cash=self.cash,
                    asset_qtys=self.asset_qtys,
                    portfolio_val=portfolio_val,
                    profit=int(profit_ratio * 10_000) / 10000.0)


class PortfolioLog(db.Model):
    timestamp = db.Column(db.DateTime, primary_key=True, default=datetime.utcnow)
    id = db.Column(db.Integer, nullable=False)
    portfolio_rets_val = db.Column(db.Float, nullable=False)


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

    def _asdict(self):
        return dict(sell_price=self.ask_price,
                    buy_price=self.bid_price,
                    sell_size=self.ask_size,
                    buy_size=self.bid_size)


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
    trade_price = db.Column(db.Integer)
    trade_volume = db.Column(db.Float)
    sequential_id = db.Column(db.BigInteger)
    ask_bid = db.Column(db.String(3))

    def __init__(self, obj):
        self.trade_date = obj["tradeDate"]
        self.trade_time = obj["tradeTime"]
        self.trade_timestamp = datetime.fromtimestamp(
            obj["timestamp"] / 1000)
        self.trade_price = obj["tradePrice"]
        self.trade_volume = obj["tradeVolume"]
        self.sequential_id = obj["sequentialId"]
        self.ask_bid = obj["askBid"]

    def _aslist(self):
        return [self.trade_timestamp.timestamp(),
                self.trade_price]


class TradeHistory(db.Model):
    """ Seoul AI Market 체결 히스토리
        Conclude history
    """
    id = db.Column(db.Integer, primary_key=True)
    ts = db.Column(db.DateTime, default=datetime.utcnow)
    agent_id = db.Column(db.Integer)
    trade_decision = db.Column(db.String)
    trade_price = db.Column(db.Float)
    trade_qty = db.Column(db.Float)
    portfolio_rets_val = db.Column(db.Float, nullable=False)

    def __init__(self, agent_id, decision, price, qty, portfolio_rets_val):
        # self.ts = obj["tradeDate"]
        self.agent_id = agent_id
        self.trade_decision = Constants.DECISION[decision]
        self.trade_price = price
        self.trade_qty = qty
        self.portfolio_rets_val = portfolio_rets_val
