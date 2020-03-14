# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod, abstractproperty


class IReward():

    __metaclass__ = ABCMeta

    @abstractmethod
    def getRewardOnlyPass(self, params): #Only the pass action was allowed
        pass

    @abstractmethod
    def getRewardPass(self, params): #the pass action was chosen even if it was not allowed
        pass

    @abstractmethod
    def getRewardInvalidAction(self, params):
        pass

    @abstractmethod
    def getRewardDiscard(self, params):
        pass

    @abstractmethod
    def getRewardFinish(self, params):
        pass


