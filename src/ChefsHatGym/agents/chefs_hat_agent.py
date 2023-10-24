# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
import logging
import os

import redis
import json
import numpy

from ChefsHatGym.gameRooms.chefs_hat_room_remote import REQUEST_TYPE
import ChefsHatGym.utils.utils as utils


class ChefsHatAgent:
    """This is the Agent class interface. Every new Agent must inherit from this class and implement the methods below.

    The class is ready to be used in both local and remote rooms. When using a remote room, the agent must be initialized, and the .join() method must be called.


    """

    __metaclass__ = ABCMeta

    name = ""  #: Class attribute to store the name of the agent
    saveModelIn = ""  #: Class attribute path to a folder acessible by this agent to save/load from

    def __init__(
        self,
        agent_suffix,
        name,
        saveModelIn: str = "",        
    ):
        """Constructor method. Initializes the agent name.

        :param agent_suffix: The name suffix of the agent name.
        :type agent_suffix: str

        :param name: The name of the Agent (must be a unique name).
        :type name: str

        :param saveModelIn: a folder acessible by this agent to save/load from
        :type saveModelIn: str

        """
        self.name = f"{agent_suffix}_{name}"

        self.saveModelIn = saveModelIn
        self.verbose = False
        self.stop_actions = False

    def get_name(self):
        """Get the agent name.

        :return: The agent name
        :rtype: ndarray
        """

        return self.name

    # Logging functions
    def startLogging(self, logDirectory):
        """Start the logging function

        Args:
            logDirectory (_type_): _description_
        """
        if logDirectory =="":
            logDirectory = "temp/"
            
        self.agent_log_directory = logDirectory
        self.updateLogDirectory()
        self.verbose = True

    def updateLogDirectory(
        self,
    ):
        """Update the log directory, generating the correct log file."""
        self.logger = logging.getLogger(f"Agent_{self.name}")

        self.logger.addHandler(
            logging.FileHandler(
                os.path.join(self.agent_log_directory, f"Agent_{self.name}_log.log"),
                mode="w",
                encoding="utf-8",
            )
        )

    def log(self, message):
        """Log a certain message, if the verbose is True

        Args:
            message (_type_): _description_
        """
        if self.verbose:
            self.logger.info(f"[Agent {self.name}]:  {message}")

    # Remote agent functions
    def joinGame(
        self,
        room_id: str,
        redis_url: str = "localhost",
        redis_port: str = "6379",
        verbose=False,
    ):
        """
        Allows an agent to enter a remote room, using a specific url and port to a redis server.

        Args:
            room_id (str): _description_
            redis_url (str, optional): _description_. Defaults to "localhost".
            redis_port (str, optional): _description_. Defaults to "6379".
            verbose (bool, optional): _description_. Defaults to False.
        """

        self.room_id = room_id
        self.redis_url = redis_url
        self.redis_port = redis_port

        # Connect to Redis
        self._connect_to_redis()

        # Register to the room
        self._subscribe_in_room()

        # Prepare to receive requests from the room

        self.send_action_subscriber = self.redis_server.pubsub(
            ignore_subscribe_messages=True
        )
        self.send_action_subscriber.subscribe(
            **{f"{self.room_id}{self.name}Server": self._read_request}
        )

        if verbose:
            logDirectory = self.redis_server.get(self.room_id)
            self.startLogging(logDirectory)

        self._prepare_to_receive_request()

    def _connect_to_redis(self):
        """Connect to a redis server"""

        self.log("---------------------------")
        self.log("Connecting with Redis")
        self.log(f"  - Connecting to Redis Server: {self.redis_url}:{self.redis_port}")

        self.redis_server = redis.Redis(
            self.redis_url, self.redis_port, charset="utf_8", decode_responses=True
        )
        self.log(f"--------------     -------------")

    def _subscribe_in_room(self):
        """Send a subscriber message to the room channel"""
        self.log("---------------------------")
        self.log("Connecting to the room")

        subscribeData = {}
        subscribeData["playerName"] = self.name
        self.redis_server.publish(f"{self.room_id}subscribe", json.dumps(subscribeData))
        self.log(f"  - Registered to the room: {self.room_id}")
        self.log(f"---------------------------")

    @utils.threaded
    def _prepare_to_receive_request(self):
        """
        threaded listener to the communication room.

        """
        self.log("---------------------------")
        self.log("Waiting requests from the room...")

        while True:
            self.send_action_subscriber.get_message()
            if self.stop_actions:
                break

    def _read_request(self, message: str):
        """Handler to parse a received message, and call the specific method.

        Args:
            message (str): _description_
        """
        data = json.loads(message["data"])
        type = data["type"]

        self.log(f"-- Request received: {type}")
        # If the received message is a request for an action, do the action and return it
        if type == REQUEST_TYPE["requestAction"]:
            observations = data["observations"]
            action = self.get_action(observations)

            self.log(f"-- Sending action: {numpy.argmax(action)}")

            self._send_message_to_server(action.tolist())

        # If the received message is a request for updating the agent, update the agent
        elif type == REQUEST_TYPE["actionUpdate"]:
            self.log(f"-- Updating the agent after the action was performed!")
            self.update_my_action(data)

        # If the received message is a request for observing others, call the observe others function
        elif type == REQUEST_TYPE["updateOthers"]:
            self.log(f"-- Updating the agent based on other player turn!")
            self.update_action_others(data)

        # If the received message is an information that the match is over, update the agent
        elif type == REQUEST_TYPE["matchOver"]:
            self.log(f"-- Match over! Updating the agent.")
            self.update_end_match(data)

        # If the received message is an information that the match is over, update the agent
        elif type == REQUEST_TYPE["gameOver"]:
            self.log(f"-- Game over! Turning off the agent!")
            self.close()

        # If the received message is a request for special action
        elif type == REQUEST_TYPE["doSpecialAction"]:
            special_action = data["special_action"]
            action = self.do_special_action(data, action)

            self.log(f"-- Doing Special action {special_action}: {action}")

            self._send_message_to_server(action)

        # If the received message is a exchange cards action
        elif type == REQUEST_TYPE["exchangeCards"]:
            cards = data["cards"]
            amount = data["amount"]
            cards = self.get_exhanged_cards(cards, amount)

            self.log(f"-- Exchanging {amount} cards: {cards}")

            self._send_message_to_server(cards)
        
         # If the received message is a update the begining of the match
        elif type == REQUEST_TYPE["updateMatchStart"]:

            cards = data["cards"]
            players = data["players"]
            starting_player = data["starting_player"]
            cards = self.update_start_match(cards, players, starting_player)

            self.log(f"-- Updating the start of the match")

            self._send_message_to_server(cards)

    def _send_message_to_server(self, agent_action):
        """Send a message to the communication channel.

        Args:
            agent_action (_type_): _description_
        """

        sendAction = {}
        sendAction["agent_action"] = agent_action
        self.redis_server.publish(
            f"{self.room_id}{self.name}Agent", json.dumps(sendAction)
        )

    def close(self):
        """Close the receive message handler"""
        self.stop_actions = True


    #Abstract methods that need to be implemented
 
    @abstractmethod
    def update_start_match(self, cards, players, starting_player):
        """This method updates the agent about the begining of the match. It contains the cards that the player has at hand.

        :param cards: Cards at hand at the begining of the match
        :type cards: list[float]

        
        :param starting_player: the names of the starting players
        :type starting_player: list[str]        

        :param starting_player: the index of the starting player
        :type starting_player: list[float]        

        """
        pass

    @abstractmethod
    def get_exhanged_cards(self, cards, amount):
        """This method returns the selected cards when exchanging them at the begining of the match.

        :param envInfo: [description]
        :type envInfo: [type]

        :return: The decision to do or not the special action
        :rtype: ndarray
        """
        pass

    @abstractmethod
    def do_special_action(self, info, specialAction):
        """This method returns a boolean to represent if the player want to do the special action or not.

        :param envInfo: [description]
        :type envInfo: [type]

        :return: The decision to do or not the special action
        :rtype: ndarray
        """
        pass


    @abstractmethod
    def get_action(self, observations):
        """This method returns one action given the observation parameter.

        :
        :param envInfo: [description]
        :type envInfo: [type]

        :rtype: ndarray
        """
        pass

    @abstractmethod
    def get_reward(self, info):
        """The Agent reward method, called inside each evironment step.

        :param info: [description]
        :type info: dict


        """

        pass
    
    @abstractmethod
    def update_end_match(self, envInfo):
        """This method that is called by the end of each match. This is an oportunity to update the Agent with information gathered in the match.

        :param envInfo: [description]
        :type envInfo: [type]
        """
        pass

    @abstractmethod
    def update_action_others(self, envInfo):
        """This method gives the agent information of other playes actions. It is called after each other player action.

        :param envInfo: [description]
        :type envInfo: [type]
        """

        pass

    @abstractmethod
    def update_my_action(self, envInfo):
        """This method that is called after the Agent's action.

        :param envInfo: [description]
        :type envInfo: [type]
        """

        pass

