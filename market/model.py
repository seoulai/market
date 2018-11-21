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
