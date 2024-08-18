# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod

import json
import numpy
from ChefsHatGym.gameRooms.chefs_hat_room_server import REQUEST_TYPE, MESSAGE_TYPE
import ChefsHatGym.utils.utils as utils
import socket
import json


class ChefsHatSpectator:
    """This is the Spectator class interface. Every new Spectator must inherit from this class and implement the methods below.

    The class is ready to be used in both local and server rooms. When using a server room, the agent must be initialized, and the .join() method must be called.


    """

    __metaclass__ = ABCMeta

    name = ""  #: Class attribute to store the name of the spectator
    saveModelIn = ""  #: Class attribute path to a folder acessible by this agent to save/load from

    messages_q = []

    def __init__(
        self,
        agent_suffix,
        name,
        this_agent_folder: str = "",
        verbose_console: bool = False,
        verbose_log: bool = False,
        log_directory: str = "",
    ):
        """Constructor method. Initializes the agent name.

        :param agent_suffix: The name suffix of the agent name.
        :type agent_suffix: str

        :param name: The name of the Agent (must be a unique name).
        :type name: str

        :param this_agent_folder: a folder acessible by this agent to save/load from
        :type this_agent_folder: str

        :param verbose_console: If the agent will print or not the logs in the console
        :type verbose_console: bool

        :param verbose_console: If the agent will print or not the logs in the log file
        :type verbose_log: bool

        logDirectory (_type_): directory where the agent log will be saved

        """
        self.name = f"{agent_suffix}_{name}"

        self.saveModelIn = this_agent_folder
        self.stop_actions = False

        self.logger = utils.get_logger(
            f"SPECTATOR_{self.name}",
            log_directory,
            f"SPECTATOR_{self.name}.log",
            verbose_console,
            verbose_log,
        )

        self.log("---------------------------")
        self.log(f"Spectator {self.name} created!")
        self.log(f"  - Agent folder: {self.saveModelIn}")
        self.log("---------------------------")

    def get_name(self):
        """Get the agent name.

        :return: The agent name
        :rtype: ndarray
        """

        return self.name

    def log(self, message):
        """Log a certain message, if the verbose is True

        Args:
            message (_type_): _description_
        """
        self.logger.info(f"[Agent {self.name}]:  {message}")

    # Remote agent functions
    def joinGame(
        self,
        room_pass: str = "",
        room_url: str = "localhost",
        room_port: int = 10000,
        connection_timeout: int = 300,
    ):
        """
        Allows an agent to spectate a server room, using a specific url and port.

        Args:
            room_pass (str): Password fo the room you wanna conntect to
            redis_url (str, optional): _description_. Defaults to "localhost".
            redis_port (str, optional): _description_. Defaults to "10000".
        """

        self.room_url = room_url
        self.room_port = room_port
        self.room_pass = room_pass
        self.connection_timeout = connection_timeout

        # Connect to the room server
        try:
            self._connect_to_room()

            # Register the player to the room
            self._join_room()
        except Exception as e:
            self.log(f"[ERROR!] {e}")

        # Listen to requests from the server room

        self._receive_requests()

    def _connect_to_room(self):
        """Connect to a room server"""

        self.log("---------------------------")
        self.log("Connecting with Room server")
        self.log(f"  - Room address: {self.room_url}:{self.room_port}")

        # Create a TCP/IP socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect the socket to the port where the server is listening
        server_address = (self.room_url, self.room_port)
        self.socket.connect(server_address)
        self.socket.settimeout(self.connection_timeout)
        self.log(f"--------------     -------------")

    def _join_room(self):
        """Join room with this spectator"""
        self.log("---------------------------")
        self.log("Joining room...")

        message = {}
        message["author"] = "Spectator"
        message["spectatorName"] = self.name
        message["password"] = self.room_pass
        message = json.dumps(message)

        self.socket.sendall(bytes(message, encoding="utf-8"))
        while True:
            room_message = self.socket.recv(1024)
            if room_message:
                break

        room_message = json.loads(room_message.decode())

        if room_message["type"] == MESSAGE_TYPE["ERROR"]:
            self.log(f"[Error] {room_message['message']}")
        else:
            self.log(f"  - Registered to the room: {self.room_url}:{self.room_port}")
        self.log(f"---------------------------")

    @utils.threaded
    def _receive_requests(self):
        """
        threaded listener to the communication room.ddddd

        """
        self.log("---------------------------")
        self.log("Waiting requests from the room...")

        while not self.stop_actions:
            room_message = self.socket.recv(12288)

            if room_message:
                # Decode the message string to a regular string

                room_message = room_message.decode()
                # Split the string into separate JSON objects
                received_messages = [f"{{{s}}}" for s in room_message.split("}{")]
                for message in received_messages:
                    message = message.replace("{{", "{").replace("}}", "}")
                    self._read_message(message)

    def _read_message(self, room_message: str):
        """Handler to parse a received message, and call the specific method.

        Args:
            message (str): _description_
        """

        # print(f"Received message: {room_message}")
        room_message = json.loads(room_message)
        type = room_message["type"]

        # print(f"All request types: {REQUEST_TYPE[type]} ")

        self.log(f"-- Request received: {REQUEST_TYPE[type]}")
        # If the received message is a request for an action, do the action and return it

        if type == REQUEST_TYPE["updateOthers"]:
            self.log(f"-- Updating the agent based on other player turn!")
            self.update_action_others(room_message)

        # If the received message is an information that the match is over, update the agent
        elif type == REQUEST_TYPE["matchOver"]:
            self.log(f"-- Match over! Updating the agent.")
            self.update_end_match(room_message)

        # If the received message is an information that the match is over, update the agent
        elif type == REQUEST_TYPE["gameOver"]:
            self.update_game_over()
            self.log(f"-- Game over! Turning off the agent!")
            self.close()

        if type == REQUEST_TYPE["specialActionUpdate"]:

            special_action = room_message["special_action"]
            player = room_message["player"]

            self.log(f"-- Player {player} did a special action: {special_action}")
            self.observe_special_action(special_action, player)

        # If the received message is a update the begining of the match
        elif type == REQUEST_TYPE["updateMatchStart"]:

            players = room_message["players"]
            starting_player = room_message["starting_player"]

            self.log(f"-- Match started!")

            self.update_start_match(players, starting_player)

    def close(self):
        """Close the receive message handler"""
        self.stop_actions = True

    # Abstract methods that need to be implemented

    @abstractmethod
    def update_start_match(self, players, starting_player):
        """This method updates the agent about the begining of the match.

        :param starting_player: the names of the starting players
        :type starting_player: list[str]

        :param starting_player: the index of the starting player
        :type starting_player: list[float]

        """
        pass

    @abstractmethod
    def observe_special_action(self, action_type, player):
        """This method updates the agent if an special action was done.

        :param action_type: [description]
        :type player: [type]

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
    def update_game_over(self):
        """This method that is called after the game is over."""

        pass
