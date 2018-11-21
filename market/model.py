from market import db


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


class OrderBook(db.Model):
    ts = db.Column(db.Integer, primary_key=True)
    buy10 = db.Column(db.Float)
    buy9 = db.Column(db.Float)
    buy8 = db.Column(db.Float)
    buy7 = db.Column(db.Float)
    buy6 = db.Column(db.Float)
    buy5 = db.Column(db.Float)
    buy4 = db.Column(db.Float)
    buy3 = db.Column(db.Float)
    buy2 = db.Column(db.Float)
    buy1 = db.Column(db.Float)
    current = db.Column(db.Float)
    sell1 = db.Column(db.Float)
    sell2 = db.Column(db.Float)
    sell3 = db.Column(db.Float)
    sell4 = db.Column(db.Float)
    sell5 = db.Column(db.Float)
    sell6 = db.Column(db.Float)
    sell7 = db.Column(db.Float)
    sell8 = db.Column(db.Float)
    sell9 = db.Column(db.Float)
    sell10 = db.Column(db.Float)
