from abc import ABCMeta, abstractmethod


class Reward:
    """Reward interface, used to implement your own rewards"""

    __metaclass__ = ABCMeta

    @abstractmethod
    def getReward(self, _):
        """Generate your own reward"""
        pass
