"""
Cinyoung Hur, cinyoung.hur@gmail.com
James Park, laplacian.k@gmail.com
seoulai.com
2018
"""
fee_rt = 0.01


class Constants(object):
    """
        TODO:
        This class will be removed after gym/market branch is merged.

        Constants to share between classes and functions for market game.
        Actually It is not used now.
    """
    HOLD = 0
    BUY = 1
    SELL = 2
    DECISION = ["hold", "buy", "sell"]


class DotDict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
