# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
import logging
import os


class ChefsHatAgent:
    """This is the Agent class interface. Every new Agent must inherit from this class and implement the methods below."""

    __metaclass__ = ABCMeta

    name = ""  #: Class attribute to store the name of the agent
    saveModelIn = ""  #: Class attribute path to a folder acessible by this agent to save/load from

    def get_name(self):
        return self.name

    def __init__(
        self,
        agent_suffix,
        name,
        saveModelIn: str = "",
    ):
        """Constructor method.

        :param agent_suffix: The name suffix of the agent name.
        :type agent_suffix: str

        :param name: The name of the Agent (must be a unique name).
        :type name: str

        :param room_id: The id of the room the agent will send/get data from.
        :type room_id: str

        :param saveModelIn: a folder acessible by this agent to save/load from
        :type saveModelIn: str

        :param redis_url: URL of the redis server
        :type redis_url: str: obj

        :param redis_port: URL of the redis port
        :type redis_port: str: obj

        :param agent_log_directory: Directory to save the agent log
        :type agent_log_directory: str: obj

        """
        self.name = f"{agent_suffix}_{name}"

        self.saveModelIn = saveModelIn
        self.verbose = False

    def startLogging(self, logDirectory):
        self.agent_log_directory = logDirectory
        self.updateLogDirectory()
        self.verbose = True

    def updateLogDirectory(
        self,
    ):
        self.logger = logging.getLogger(f"Agent_{self.name}")

        self.logger.addHandler(
            logging.FileHandler(
                os.path.join(self.agent_log_directory, f"Agent_{self.name}_log.log"),
                mode="w",
                encoding="utf-8",
            )
        )

    def log(self, message):
        if self.verbose:
            self.logger.info(f"[Agent {self.name}]:  {message}")

    @abstractmethod
    def doSpecialAction(self, info, specialAction):
        """This method returns a boolean to represent if the player want to do the special action or not.


        :param envInfo: [description]
        :type envInfo: [type]

        :return: The decision to do or not the special action
        :rtype: ndarray
        """
        pass

    @abstractmethod
    def exchangeCards(self, cards, amount):
        """This method returns the selected cards when exchanging them at the begining of the match.


        :param envInfo: [description]
        :type envInfo: [type]

        :return: The decision to do or not the special action
        :rtype: ndarray
        """
        pass

    @abstractmethod
    def getAction(self, observations):
        """This method returns one action given the observation parameter.

        :
        :param envInfo: [description]
        :type envInfo: [type]

        :rtype: ndarray
        """
        pass

    @abstractmethod
    def getReward(self, info):
        """The Agent reward method, called inside each evironment step.

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
    def actionUpdate(self, envInfo):
        """This method that is called after the Agent's action.

        :param envInfo: [description]
        :type envInfo: [type]
        """

        pass

    @abstractmethod
    def matchUpdate(self, envInfo):
        """This method that is called by the end of each match. This is an oportunity to update the Agent with information gathered in the match.

        :param envInfo: [description]
        :type envInfo: [type]
        """
        pass
