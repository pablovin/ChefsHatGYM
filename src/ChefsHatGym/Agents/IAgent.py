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

        :param observations: The observation is an int data-type ndarray. 
                            The observation array has information about the board game, the player's hand, and possible actions.
                            This array must have the shape of (228, ) as follows:
                            The first 11 elements represent the board game card placeholder (the pizza area). 
                            The game cards are represented by an integer, where 0 (zero) means no card.
                            The following 17 elements (from index 11 to 27) represent the player hand cards in the sequence.
                            By the end, the last 200 elements (from index 28 to 227) represent all possible actions in the game. 
                            The allowed actions are filled with one, while invalid actions are filled with 0.
        :type observations: ndarray
        :return: The action array with 200 elements, where the choosen action is the index of the highest value
        :rtype: ndarray
        """  
        pass

    @abstractmethod
    def getReward(self,observationBefore, observationAfter, possibleActions, info):
        """The Agent reward method, called inside each evironment step.

        :param observationBefore: The observationBefore is an int data-type ndarray. 
                            The observationBefore array has information (before the player's action) about the board game, the player's hand, and possible actions.
                            This array must have the shape of (228, ) as follows:
                            The first 11 elements represent the board game card placeholder (the pizza area). 
                            The game cards are represented by an integer, where 0 (zero) means no card.
                            The following 17 elements (from index 11 to 27) represent the player hand cards in the sequence.
                            By the end, the last 200 elements (from index 28 to 227) represent all possible actions in the game. 
                            The allowed actions are filled with one, while invalid actions are filled with 0.
        :type observationBefore: ndarray
        :param observationAfter: The observationAfter is an int data-type ndarray. 
                            The observationBefore array has information (after the player's action) about the board game, the player's hand, and possible actions.
                            This array must have the shape of (228, ) as follows:
                            The first 11 elements represent the board game card placeholder (the pizza area). 
                            The game cards are represented by an integer, where 0 (zero) means no card.
                            The following 17 elements (from index 11 to 27) represent the player hand cards in the sequence.
                            By the end, the last 200 elements (from index 28 to 227) represent all possible actions in the game. 
                            The allowed actions are filled with one, while invalid actions are filled with 0.
        :type observationAfter: ndarray
        :param possibleActions: The possibleActions is an int data-type ndarray with shape (200, ). Each element represent all possible actions in the game. 
                            The allowed actions are filled with one, while invalid actions are filled with 0.
        :type possibleActions: ndarray
        :param info: [description]
        :type info: dict
        """
        pass

    @abstractmethod
    def observeOthers(self, envInfo):
        """This method gives the agent information of other playes actions. It is called after each other player action.

        :param envInfo: [description]
        :type envInfo: [type]
        """        
        pass

    @abstractmethod
    def actionUpdate(self,  observation, nextObservation, action, envInfo):
        """This method that is called after the Agent's action.

        :param observation: The observation is an int data-type ndarray. 
                            The observation array has information about the board game, the player's hand, and possible actions.
                            This array must have the shape of (228, ) as follows:
                            The first 11 elements represent the board game card placeholder (the pizza area). 
                            The game cards are represented by an integer, where 0 (zero) means no card.
                            The following 17 elements (from index 11 to 27) represent the player hand cards in the sequence.
                            By the end, the last 200 elements (from index 28 to 227) represent all possible actions in the game. 
                            The allowed actions are filled with one, while invalid actions are filled with 0.
        :type observation: ndarray
        :param nextObservation: The nextObservation is an int data-type ndarray. 
                            The nextObservation array has information about the board game, the player's hand, and possible actions.
                            This array must have the shape of (228, ) as follows:
                            The first 11 elements represent the board game card placeholder (the pizza area). 
                            The game cards are represented by an integer, where 0 (zero) means no card.
                            The following 17 elements (from index 11 to 27) represent the player hand cards in the sequence.
                            By the end, the last 200 elements (from index 28 to 227) represent all possible actions in the game. 
                            The allowed actions are filled with one, while invalid actions are filled with 0.
        :type nextObservation: ndarray
        :param action: [description]
        :type action: [type]
        :param envInfo: [description]
        :type envInfo: [type]
        """
        pass

    @abstractmethod
    def matchUpdate(self,  envInfo):
        """This method that is called by the end of each match. This is an oportunity to update the Agent with information gathered in the match.

        :param envInfo: [description]
        :type envInfo: [type]
        """        
        pass
