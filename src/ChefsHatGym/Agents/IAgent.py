# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod

class IAgent():

    __metaclass__ = ABCMeta

    name = ""

    @abstractmethod
    def __init__(self, name, _):
        pass

    @abstractmethod
    def getAction(self, observations):
        pass

    @abstractmethod
    def getReward(self,observationBefore, observationAfter, possibleActions, info):
        pass

    @abstractmethod
    def observeOthers(self, envInfo):
        pass

    @abstractmethod
    def actionUpdate(self,  observation, nextObservation, action, envInfo):
        pass

    @abstractmethod
    def matchUpdate(self,  envInfo):
        pass
