# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod

import signal
from contextlib import contextmanager


class IAgent():
    """This is the Agent class interface. Every new Agent must inherit from this class and implement the methods below.
        """

    __metaclass__ = ABCMeta

    name = "" #: Class attribute to store the name of the agent
    saveModelIn = "" #: Class attribute path to a folder acessible by this agent to save/load from
    
    @abstractmethod
    def __init__(self, name, saveModelIn, _):
        """Constructor method.

        :param name: The name of the Agent (must be a unique name).
        :type name: str

        :param saveModelIn: a folder acessible by this agent to save/load from
        :type saveModelIn: str

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
    def getReward(self, info, stateBefore, stateAfter):
        """The Agent reward method, called inside each evironment step.

                :param info: [description]
                :type info: dict

                :param stateBefore: The observation before the action happened is an int data-type ndarray.
                                    The observationBefore array has information (before the player's action) about the board game, the player's hand, and possible actions.
                                    This array must have the shape of (228, ) as follows:
                                    The first 11 elements represent the board game card placeholder (the pizza area).
                                    The game cards are represented by an integer, where 0 (zero) means no card.
                                    The following 17 elements (from index 11 to 27) represent the player hand cards in the sequence.
                                    By the end, the last 200 elements (from index 28 to 227) represent all possible actions in the game.
                                    The allowed actions are filled with one, while invalid actions are filled with 0.
                :type stateBefore: ndarray

                :param stateAfter: The observation after the action happened is an int data-type ndarray.
                                    The observationBefore array has information (after the player's action) about the board game, the player's hand, and possible actions.
                                    This array must have the shape of (228, ) as follows:
                                    The first 11 elements represent the board game card placeholder (the pizza area).
                                    The game cards are represented by an integer, where 0 (zero) means no card.
                                    The following 17 elements (from index 11 to 27) represent the player hand cards in the sequence.
                                    By the end, the last 200 elements (from index 28 to 227) represent all possible actions in the game.
                                    The allowed actions are filled with one, while invalid actions are filled with 0.
                :type stateAfter: ndarray

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
                :param action: The action array with 200 elements, where the choosen action is the index of the highest value
                :type action: ndarray
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


    @contextmanager
    def timeout(self,time):
        """This method can be called to make any action of the agent timed out. It adds a timeout for the action function

                :param time: time in seconds
                :type time: int
                """
        # Register a function to raise a TimeoutError on the signal.
        signal.signal(signal.SIGALRM, self.raise_timeout)
        # Schedule the signal to be sent after ``time``.
        signal.alarm(time)

        try:
            yield
        except TimeoutError:
            pass
        finally:
            # Unregister the signal so it won't be triggered
            # if the timeout is not reached.
            signal.signal(signal.SIGALRM, signal.SIG_IGN)


    def raise_timeout(self, signum, frame):
        """[summary]

        :param signum: [description]
        :type signum: int
        :param frame: ???
        :type frame: int

        Raises:
            TimeoutError: [description]
        """        
        raise TimeoutError
