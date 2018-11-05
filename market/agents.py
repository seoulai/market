"""
Cinyoung Hur, cinyoung.hur@gmail.com
seoulai.com
2018
"""
from abc import ABC
from abc import abstractmethod


class Agent(ABC):
    @abstractmethod
    def __init__(
        self,
        name: str,
    ):
        self._name = name

    @property
    def name(self, _name):
        return _name

    def __str__(self):
        return self._name


class ConcreteAgent(Agent):
    def __init__(
            self,
            info: dict
    ):
        """Initialize random agent.

        Args:
            name: name of agent.
            ptype: type of piece that agent is responsible for.
        """
        super().__init__(info["name"])
        self.init_cash = info["cash"]
        self.cash = info["cash"]
        self.asset_qty = info["asset_qty"]
        self.asset_val = info["asset_val"]
        self.invested = info["invested"]
        self.bah_base = info["bah_base"]


class AgentList():
    def __init__(self):
        self.agent_list = {}

    def add(self, agent: ConcreteAgent):
        self.agent_list[str(agent)] = agent

    def remove(self, agent: ConcreteAgent):
        del self.agent_list[str(agent)]

    def count(self):
        return len(self.agent_list)


agent_list = AgentList()
