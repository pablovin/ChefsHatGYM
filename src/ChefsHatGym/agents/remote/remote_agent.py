# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod

from ChefsHatGym.agents.chefs_hat_agent import ChefsHatAgent
import redis
import json

import numpy

from ChefsHatGym.gameRooms.chefs_hat_room_remote import REQUEST_TYPE
import ChefsHatGym.utils.utils as utils


class ChefsHatAgentRemote(ChefsHatAgent):
    """This is the Remote Agent class interface. Every new Agent must inherit from this class and implement the methods below, when using the Redis type of room."""

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
        super().__init__(agent_suffix, name, saveModelIn)

        self.stop_actions = False

    def joinGame(
        self,
        room_id: str,
        redis_url: str = "localhost",
        redis_port: str = "6379",
        verbose=False,
    ):
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
        self.log("---------------------------")
        self.log("Connecting with Redis")
        self.log(f"  - Connecting to Redis Server: {self.redis_url}:{self.redis_port}")

        self.redis_server = redis.Redis(
            self.redis_url, self.redis_port, charset="utf_8", decode_responses=True
        )
        self.log(f"--------------     -------------")

    def _subscribe_in_room(self):
        self.log("---------------------------")
        self.log("Connecting to the room")

        subscribeData = {}
        subscribeData["playerName"] = self.name
        self.redis_server.publish(f"{self.room_id}subscribe", json.dumps(subscribeData))
        self.log(f"  - Registered to the room: {self.room_id}")
        self.log(f"---------------------------")

    @utils.threaded
    def _prepare_to_receive_request(self):
        self.log("---------------------------")
        self.log("Waiting requests from the room...")

        while True:
            self.send_action_subscriber.get_message()
            if self.stop_actions:
                break

    def _read_request(self, message: str):
        data = json.loads(message["data"])
        type = data["type"]

        self.log(f"-- Request received: {type}")
        # If the received message is a request for an action, do the action and return it
        if type == REQUEST_TYPE["requestAction"]:
            observations = data["observations"]
            action = self.getAction(observations)

            self.log(f"-- Sending action: {numpy.argmax(action)}")

            self._send_message_to_server(action.tolist())

        # If the received message is a request for updating the agent, update the agent
        elif type == REQUEST_TYPE["actionUpdate"]:
            self.log(f"-- Updating the agent after the action was performed!")
            self.actionUpdate(data)

        # If the received message is a request for observing others, call the observe others function
        elif type == REQUEST_TYPE["updateOthers"]:
            self.log(f"-- Updating the agent based on other player turn!")
            self.observeOthers(data)

        # If the received message is an information that the match is over, update the agent
        elif type == REQUEST_TYPE["matchOver"]:
            self.log(f"-- Match over! Updating the agent.")
            self.matchUpdate(data)

        # If the received message is an information that the match is over, update the agent
        elif type == REQUEST_TYPE["gameOver"]:
            self.log(f"-- Game over! Turning off the agent!")
            self.close()

        # If the received message is a request for special action
        elif type == REQUEST_TYPE["doSpecialAction"]:
            special_action = data["special_action"]
            action = self.doSpecialAction(data, action)

            self.log(f"-- Doing Special action {special_action}: {action}")

            self._send_message_to_server(action)

        # If the received message is a exchange cards action
        elif type == REQUEST_TYPE["exchangeCards"]:
            cards = data["cards"]
            amount = data["amount"]
            cards = self.exchangeCards(cards, amount)

            self.log(f"-- Exchanging {amount} cards: {cards}")

            self._send_message_to_server(cards)

    def _send_message_to_server(self, agent_action):
        sendAction = {}
        sendAction["agent_action"] = agent_action
        self.redis_server.publish(
            f"{self.room_id}{self.name}Agent", json.dumps(sendAction)
        )

    def close(self):
        self.stop_actions = True
