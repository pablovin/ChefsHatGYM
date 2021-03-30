# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod

class IAgent():

    __metaclass__ = ABCMeta

    name = ""

    @abstractmethod
    def train(self,  observation, nextObservation, action, envInfo):
        pass

    @abstractmethod
    def getAction(self, observations):
        pass

    @abstractmethod
    def __init__(self, name, _):
        pass

    def getReward(self,observationBefore, observationAfter, possibleActions, info):
        pass


