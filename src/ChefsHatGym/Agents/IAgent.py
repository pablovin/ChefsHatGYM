# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod

class IAgent():
    """This is the Agent class interface. Every new Agent must inherit from this class and implement the methods below.
    """
    __metaclass__ = ABCMeta

    name = ""

    @abstractmethod
    def __init__(self, name, _):
        """Constructor method.

        :param name: The name of the Agent (must be a unique name).
        :type name: str
        :param _: Other parameters that your Agent must need
        :type _: obj, optional 
        
        """
        pass

    @abstractmethod
    def getAction(self, observations):
        """This method returns one action given the observation parameter.

        :param observations: The observation is a int data-type ndarray. 
                            The observation array has information about the board game, the player hand, and possible actions.
                            This array must have shape of (228, ) as follows:
                            The first 11 elements represents the board game (the pizza area). 
                            The game cards are represented by an interger, where 0 (zero) means no card in the table position.
                            In the sequence, the next 17 elements (from index 11 to 27) represents the player cards.
                            By the end, the last 200 elements (from index 28 to 227) represets all possible actions in the game. 
                            The allowed actions are filled with 1 while invalid actions are filled with 0.
        :type observations: ndarray
        :return: The action array with 200 elements, where the choosen action is the index of the highest value
        :rtype: ndarray
        """  
        pass

    @abstractmethod
    def getReward(self,observationBefore, observationAfter, possibleActions, info):
        """[summary]

        :param observationBefore: [description]
        :type observationBefore: ndarray
        :param observationAfter: [description]
        :type observationAfter: ndarray
        :param possibleActions: [description]
        :type possibleActions: list
        :param info: [description]
        :type info: dict
        """
        pass

    @abstractmethod
    def observeOthers(self, envInfo):
        """[summary]

        :param envInfo: [description]
        :type envInfo: [type]
        """        
        pass

    @abstractmethod
    def actionUpdate(self,  observation, nextObservation, action, envInfo):
        """This method that is called after the Agent's action

        :param observation: It is a ndarray 
        :type observation: ndarray
        :param nextObservation: [description]
        :type nextObservation: ndarray
        :param action: [description]
        :type action: [type]
        :param envInfo: [description]
        :type envInfo: [type]
        """
        pass

    @abstractmethod
    def matchUpdate(self,  envInfo):
        """[summary]

        :param envInfo: [description]
        :type envInfo: [type]
        """        
        pass
