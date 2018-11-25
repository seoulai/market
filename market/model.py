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


class PriceHistory(db.Model):
    """ Price history including indicators
    Current Price: 가장 최근 체결가
    Start/Close/High/Low
    Overlap Studies:
    Momentum Indicators
    """
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    curr_price = db.Column(db.Integer)
    BBANDS = db.Column(db.Float)  # Bollinger Bands
    DEMA = db.Column(db.Float)  # Double Exponential Moving Average
    EMA = db.Column(db.Float)  # Exponential Moving Average

    # Hilbert Transform - Instantaneous Trendline
    HT_TRENDLINE = db.Column(db.Float)
    KAMA = db.Column(db.Float)  # Kaufman Adaptive Moving Average
    MA = db.Column(db.Float)  # Moving average
    MAMA = db.Column(db.Float)  # MESA Adaptive Moving Average
    MAVP = db.Column(db.Float)  # Moving average with variable period
    MIDPOINT = db.Column(db.Float)  # MidPoint over period
    MIDPRICE = db.Column(db.Float)  # Midpoint Price over period
    SAR = db.Column(db.Float)  # Parabolic SAR
    SAREXT = db.Column(db.Float)  # Parabolic SAR - Extended
    SMA = db.Column(db.Float)  # Simple Moving Average
    T3 = db.Column(db.Float)  # Triple Exponential Moving Average (T3)
    TEMA = db.Column(db.Float)  # Triple Exponential Moving Average
    TRIMA = db.Column(db.Float)  # Triangular Moving Average
    WMA = db.Column(db.Float)  # Weighted Moving Average
    ADX = db.Column(db.Float)  # Average Directional Movement Index
    ADXR = db.Column(db.Float)  # Average Directional Movement Index Rating
    APO = db.Column(db.Float)  # Absolute Price Oscillator
    AROON = db.Column(db.Float)  # Aroon
    AROONOSC = db.Column(db.Float)  # Aroon Oscillator
    BOP = db.Column(db.Float)  # Balance Of Power
    CCI = db.Column(db.Float)  # Commodity Channel Index
    CMO = db.Column(db.Float)  # Chande Momentum Oscillator
    DX = db.Column(db.Float)  # Directional Movement Index
    MACD = db.Column(db.Float)  # Moving Average Convergence/Divergence
    MACDEXT = db.Column(db.Float)  # MACD with controllable MA type

    # Moving Average Convergence/Divergence Fix 12/26
    MACDFIX = db.Column(db.Float)
    MFI = db.Column(db.Float)  # Money Flow Index
    MINUS_DI = db.Column(db.Float)  # Minus Directional Indicator
    MINUS_DM = db.Column(db.Float)  # Minus Directional Movement
    MOM = db.Column(db.Float)  # Momentum
    PLUS_DI = db.Column(db.Float)  # Plus Directional Indicator
    PLUS_DM = db.Column(db.Float)  # Plus Directional Movement
    PPO = db.Column(db.Float)  # Percentage Price Oscillator
    ROC = db.Column(db.Float)  # Rate of change : ((price/prevPrice)-1)*100

    # Rate of change Percentage: (price-prevPrice)/prevPrice
    ROCP = db.Column(db.Float)
    ROCR = db.Column(db.Float)  # Rate of change ratio: (price/prevPrice)
    # Rate of change ratio 100 scale: (price/prevPrice)*100
    ROCR100 = db.Column(db.Float)
    RSI = db.Column(db.Float)  # Relative Strength Index
    STOCH = db.Column(db.Float)  # Stochastic
    STOCHF = db.Column(db.Float)  # Stochastic Fast
    STOCHRSI = db.Column(db.Float)  # Stochastic Relative Strength Index
    # 1-day Rate-Of-Change (ROC) of a Triple Smooth EMA
    TRIX = db.Column(db.Float)
    ULTOSC = db.Column(db.Float)  # Ultimate Oscillator
    WILLR = db.Column(db.Float)  # Williams' %R


class TradeHistory(db.Model):
    """ 체결 히스토리
        Conclude history
    """
    ts = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer)
    trade_decision = db.Column(db.String)
    trade_price = db.Column(db.Float)
    trade_qty = db.Column(db.Float)
    coin_name = db.Column(db.String, default="KRW-BTC")
