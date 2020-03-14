# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod, abstractproperty


class IAgent():

    __metaclass__ = ABCMeta

    @abstractmethod
    def train(self, params):
        pass

    @abstractmethod
    def loadModel(self, params):
        pass

    @abstractmethod
    def getAction(self, params):
        pass

    @abstractmethod
    def buildModel(self):
        pass

    @abstractmethod
    def startAgent(self, params):
        pass

    # @abstractmethod
    # def __init__(self, params):
    #     pass


