from datetime import datetime
import os
import time
from ChefsHatGym.env import ChefsHatEnv
import gym
import json
import numpy as np

import socket
import sys
import json

import ChefsHatGym.utils.utils as utils

REQUEST_TYPE = {
    "requestAction": "requestAction",
    "sendAction": "sendAction",
    "actionUpdate": "actionUpdate",
    "updateOthers": "updateOthers",
    "matchOver": "matchOver",
    "gameOver": "gameOver",
    "doSpecialAction": "doSpecialAction",
    "specialActionUpdate": "specialActionUpdate",
    "exchangeCards": "exchangeCards",
    "updateMatchStart": "updateMatchStart",
}

MESSAGE_TYPE = {"OK": "OK", "ERROR": "ERROR"}

ROOM_STATUS = {
    "waiting_players": "waiting_players",
    "ready_to_start": "ready_to_start",
    "game_started": "game_started",
    "game_finished": "game_finished",
}


class ChefsHatRoomServer:
    """
    Room environment where a game will be played with agents in different processes.
    """

    def get_room_name(self) -> str:
        """ge the room id

        Returns:
            str: room id
        """
        return self.room_name

    def get_log_directory(self) -> str:
        """get the directory where the log is saved

        Returns:
            str: log directory
        """
        return self.log_directory

    def get_number_players(self) -> int:
        """get the number of players in the room

        Returns:
            int: number of players
        """
        return len(self.players_names)

    def get_room_finished(self) -> bool:
        """Is the game finished

        Returns:
            bool: is the game finished
        """
        return self.room_finished

    def __init__(
        self,
        room_name: str,
        room_pass: str = "",
        room_url: str = "localhost",
        room_port: int = 10000,
        game_type: str = ChefsHatEnv.GAMETYPE["MATCHES"],
        stop_criteria: int = 10,
        max_rounds: int = -1,
        verbose_console: bool = True,
        verbose_log: bool = True,
        game_verbose_console: bool = True,
        game_verbose_log: bool = True,
        save_dataset: bool = True,
        log_directory: str = None,
        timeout_player_subscribers: int = 30,
        timeout_player_response: int = 5,
    ) -> None:
        """Initialize the room`
        Args:
            room_name (str): name of the room
            room_pass (str): password of the room
            room_url (str, optional): url to be binded to the room. Defaults to "localhost".
            room_port (str, optional): port to be binded to the room. Defaults to "6379".
            room_name (str): name of the room, no special character is allowed.
            game_type (str, optional): game type, defined as ChefsHatEnv.GAMETYPE. Defaults to ChefsHatEnv.GAMETYPE["MATCHES"].
            stop_criteria (int, optional): stop criteria for the game. Defaults to 10.
            max_rounds (int, optional): maximum rounds of the game, if -1 the game will play until it ends. Defaults to -1.
            verbose_console (bool, optional): room verbose on the console. Defaults to True.
            verbose_log (bool, optional): room verbose on the log file. Defaults to True.
            game_verbose_console (bool, optional): game verbose on the console. Defaults to True.
            game_verbose_log (bool, optional): game verbose on the log. Defaults to True.
            save_dataset (bool, optional): save the game dataset .pkl. Defaults to True.
            save_game_log (bool, optional): save the game log. Defaults to True.
            log_directory (str, optional): directory to save the log. Defaults to None.
            timeout_player_subscribers (int, optional): timeout of the player subscriptions to the room in seconds. Defaults to 30.
            timeout_player_response (int, optional): timeout of the player response in seconds. Defaults to 5.
        """
        # Room parameters
        self.room_url = room_url
        self.room_port = room_port
        self.room_name = room_name
        self.room_pass = room_pass

        # Game type parameters
        self.game_type = game_type
        self.stop_criteria = stop_criteria
        self.max_rounds = max_rounds
        self.game_verbose_console = game_verbose_console
        self.save_dataset = save_dataset
        self.game_verbose_log = game_verbose_log

        self.timeout_player_subscribers = timeout_player_subscribers
        self.timeout_player_response = timeout_player_response

        # In-room parameters
        self.players = {}
        self.spectators = {}
        self.receive_messages_subs = {}
        self.room_finished = False
        self.ready_to_start = False
        self.room_status = ROOM_STATUS["waiting_players"]

        # Create the log directory
        if not log_directory:
            log_directory = "temp/"

        self.log_directory = os.path.join(
            log_directory, f"{datetime.now().strftime('%H%M%S')}_{room_name}"
        )

        os.makedirs(self.log_directory)

        self.logger = utils.get_logger(
            f"ROOM_{room_name}",
            self.log_directory,
            "room_log.log",
            verbose_console,
            verbose_log,
        )

        self.log("[Room]: ---------------------------")
        self.log("[Room]: Creating logger")
        self.log(f"[Room]:  - folder: { self.log_directory}")

        # Create the room server
        self._create_server()

    def log(self, message):
        self.logger.info(f"[Room]: {message}")

    def error(self, message):
        self.logger.critical(f"[Room]: {message}")

    def start_room(self):
        # Change the room status to expecting players to connect
        self._prepare_connect_player()

        # Keep listening for connections
        self._receiving_connections()

        # # Start the game when there are 4 players connected
        self._start_new_game()

    def _create_server(self):
        self.log("[Room]: ---------------------------")
        self.log(
            f"[Room]: Creating room {self.room_name} at: {self.room_url}:{self.room_port}"
        )
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (self.room_url, self.room_port)
        self.server_socket.bind(server_address)
        self.server_socket.settimeout(self.timeout_player_subscribers)
        self.log(f"[Room]: --- Room up and running!")

    def _prepare_connect_player(self):
        self.log("[Room]: ---------------------------")
        self.log("[Room]: Waiting for players and spectators to connect...")

        self.room_status = ROOM_STATUS["waiting_players"]

        # self._wait_for_players()

    def _ready_to_start_game(self):
        self.log("[Room]: ---------------------------")
        self.log(f"[Room]: - All four players online, starting the game!")

        self.room_status = ROOM_STATUS["ready_to_start"]

        # self._wait_for_players()

    def _process_connection_request(self, connection):
        # Receive the data in small chunks and retransmit it
        while True:
            agent_message = connection.recv(3076)

            if agent_message:
                break

        agent_message = agent_message.decode()
        json_response = json.loads(agent_message)
        return json_response

    @utils.threaded
    def _receiving_connections(self):

        self.log("[Room]: Receiving connections...")
        self.server_socket.listen(4)
        while not self.room_status == ROOM_STATUS["game_finished"]:
            self.log(f"[Room]: Room Status: {self.room_status}")
            try:

                connection, client_address = self.server_socket.accept()
                self.log(
                    f"[Room]: - Received a connection request from {client_address}"
                )

                message = self._process_connection_request(connection)
                if "author" in message.keys():
                    if message["author"] == "Player":
                        self._add_player(connection, message)
                    elif message["author"] == "Spectator":
                        self._add_spectator(connection, message)

                time.sleep(0.001)
            except socket.timeout:
                self.error(
                    f"[Room][ERROR]: Agent subscription timeout! Current playes: {self.players.keys()}. Current spectators: {self.spectators.keys()}"
                )

        # self.log(f"[Room]: - All four players online, starting the game!")
        # self.ready_to_start = True

    @utils.threaded
    def _add_spectator(self, connection, spectator_message):

        if "spectatorName" in spectator_message.keys():
            spectator_name = spectator_message.get("spectatorName")

            room_message = {}
            if spectator_message["password"] == self.room_pass:

                if spectator_name in self.spectators.keys():
                    room_message["type"] = MESSAGE_TYPE["ERROR"]
                    room_message["message"] = "Spectator Name Already Used!"

                    self.error(
                        f"[Room]: - Spectator {spectator_name} not conntected: Spectator Name Already Used!"
                    )

                else:
                    self.spectators[spectator_name] = connection
                    room_message["type"] = MESSAGE_TYPE["OK"]
                    self.log(
                        f"[Room]: - Spectator {len(self.players)} ({spectator_name}) connected!"
                    )

            else:
                room_message["type"] = MESSAGE_TYPE["ERROR"]
                room_message["message"] = "Wrong password!"

                self.error(
                    f"[Room]: - Spectator {spectator_name} not conntected: wrong password!"
                )

            room_message = json.dumps(room_message)
            connection.sendall(bytes(room_message, encoding="utf-8"))

    @utils.threaded
    def _add_player(self, connection, player_message):

        if "playerName" in player_message.keys():
            player_name = player_message.get("playerName")

            room_message = {}
            if player_message["password"] == self.room_pass:

                if len(self.players) >= 4:
                    room_message["type"] = MESSAGE_TYPE["ERROR"]
                    room_message["message"] = "The room is full!"

                    self.error(
                        f"[Room]: - Player {player_name} not conntected: Room is full!"
                    )

                else:

                    if player_name in self.players.keys():
                        room_message["type"] = MESSAGE_TYPE["ERROR"]
                        room_message["message"] = "Player Name Already Used!"

                        self.error(
                            f"[Room]: - Player {player_name} not conntected: Player Name Already Used!"
                        )

                    else:
                        self.players[player_name] = connection
                        room_message["type"] = MESSAGE_TYPE["OK"]
                        self.log(
                            f"[Room]: - Player {len(self.players)} ({player_name}) connected!"
                        )

                        # Indicate that the game is ready to start if we have 4 players!
                        if len(self.players) == 4:
                            self._ready_to_start_game()

            else:
                room_message["type"] = MESSAGE_TYPE["ERROR"]
                room_message["message"] = "Wrong password!"

                self.error(
                    f"[Room]: - Player {player_name} not conntected: wrong password!"
                )

            room_message = json.dumps(room_message)
            connection.sendall(bytes(room_message, encoding="utf-8"))

    # def _wait_for_players(self):
    #     self.log("[Room]: - Waiting for players to connect...")

    #     self.server_socket.listen(4)

    #     while len(self.players) < 4:
    #         try:
    #             connection, client_address = self.server_socket.accept()
    #             self.log(
    #                 f"[Room]: - Received a connection request from {client_address}"
    #             )

    #             # verify if message comes from players

    #             self._add_player(connection)
    #             time.sleep(0.001)
    #         except socket.timeout:
    #             self.error(
    #                 f"[Room][ERROR]: Players subscription timeout! Current playes: {self.players.keys()}"
    #             )

    #             raise Exception("Player subscription timeout!")

    #     self.log(f"[Room]: - All four players online, starting the game!")
    #     self.ready_to_start = True

    def _broadcast_message(self, list, player, info):

        connection = list[player]
        info = json.dumps(info)

        try:
            connection.sendall(bytes(info, encoding="utf-8"))
        except:
            self.error(f"[Room]: - Player {[player]} Disconnected!")

        time.sleep(0.0001)

    def _get_random_action(self, info):

        action_type = info["type"]
        if action_type == REQUEST_TYPE["requestAction"]:
            action = np.zeros(200)
            action[-1] = 1
        elif action_type == REQUEST_TYPE["doSpecialAction"]:
            action = False
        elif action_type == REQUEST_TYPE["exchangeCards"]:
            cards = info["cards"]
            amount = info["amount"]
            action = sorted(cards[-amount:])

    def _request_message(self, player, info):

        connection = self.players[player]
        # print(f"Message sent: {info}")
        info = json.dumps(info)
        player_online = True
        try:
            connection.sendall(bytes(info, encoding="utf-8"))
        except:
            self.error(
                f"[Room]: - Player {[player]} Disconnected! Doing random actions!"
            )

        time.sleep(0.0001)

        time_start = datetime.now()
        if player_online:
            while True:
                timenow = datetime.now()
                try:
                    player_message = connection.recv(3072)
                    time.sleep(0.01)
                    if player_message:
                        player_message = json.loads(player_message.decode())
                        agent_action = player_message.get("agent_action")
                        break
                except socket.timeout:
                    agent_action = self._get_random_action(info)
                    break
        timeElapsed = (datetime.now() - time_start).total_seconds()
        return agent_action, timeElapsed

    def _start_new_game(self):

        while not self.room_status == ROOM_STATUS["ready_to_start"]:
            time.sleep(5)
            self.error(
                f"[Room][ERROR]: Not enough players to start the game! Total current players: {len(self.players)}. Will try again in 5 seconds!"
            )

        self.room_status = ROOM_STATUS["game_started"]
        time_start = datetime.now()

        self.log("[Room]: ---------------------------")
        self.log("[Room]: Initializing a game")

        """Setup environment"""
        self.env = gym.make("chefshat-v1")  # starting the game Environment
        self.env.startExperiment(
            gameType=self.game_type,
            stopCriteria=self.stop_criteria,
            maxRounds=self.max_rounds,
            playerNames=list(self.players.keys()),
            logDirectory=self.log_directory,
            verbose=self.game_verbose_console,
            saveDataset=self.save_dataset,
            saveLog=self.game_verbose_log,
        )

        self.log("[Room]:  - Environment initialized!")

        observations = self.env.reset()

        # Update each player about the begining of the match
        self.log("[Room]:  - Informing players about game start!")

        for p_index, p in enumerate(self.players.keys()):
            sendInfo = {}
            sendInfo["type"] = "updateMatchStart"
            sendInfo["cards"] = self.env.playersHand[p_index]
            sendInfo["players"] = list(self.players.keys())
            sendInfo["starting_player"] = list(self.players.keys())[
                self.env.currentPlayer
            ]
            self.log(f"[Room]:  ---- Player {p} informed!")

            self._broadcast_message(self.players, p, sendInfo)

        # Update the spectators about the game start
        if len(self.spectators) > 0:
            self.log("[Room]:  - Informing spectators about game start!")

        for p_index, p in enumerate(self.spectators.keys()):
            sendInfo = {}
            sendInfo["type"] = "updateMatchStart"
            sendInfo["players"] = list(self.players.keys())
            sendInfo["starting_player"] = list(self.players.keys())[
                self.env.currentPlayer
            ]
            self.log(f"[Room]:  ---- Spectator {p} informed!")

            self._broadcast_message(self.spectators, p, sendInfo)

        while not self.env.gameFinished:

            currentPlayer = list(self.players.keys())[self.env.currentPlayer]

            self.log(f"[Room]:  -- Current player: {currentPlayer}")
            observations = self.env.getObservation()

            info = {"validAction": False}
            while not info["validAction"]:

                sendInfo = {}
                sendInfo["observations"] = observations.tolist()
                sendInfo["possibleActionsDecoded"] = self.env.decode_possible_actions(
                    sendInfo["observations"][28:]
                )
                sendInfo["type"] = REQUEST_TYPE["requestAction"]
                action, time_action = self._request_message(currentPlayer, sendInfo)

                self.log(
                    f"[Room]:  ---- Action (duration: {time_action}s): {np.argmax(action)}"
                )
                nextobs, reward, isMatchOver, truncated, info = self.env.step(action)

                if not info["validAction"]:
                    self.error(f"[Room][ERROR]: ---- Invalid action!")

            # break
            # Send action update to the current agent
            # self._send_action_update(currentPlayer, info)
            info["observation"] = observations.tolist()
            info["nextObservation"] = nextobs.tolist()
            info["type"] = REQUEST_TYPE[
                "actionUpdate"
            ]  # Update the agents after the action was done
            self.log("[Room]:  - Informing the agent about his own action!")
            self._broadcast_message(
                self.players, currentPlayer, info
            )  # update the current player, with the information about his hand

            info["observation"] = ""
            info["nextObservation"] = ""

            info["actionIsRandom"] = ""
            info["possibleActions"] = ""
            info["possibleActionsDecoded"] = ""
            info["type"] = REQUEST_TYPE[
                "updateOthers"
            ]  # Update the othe players after the action was done
            # Observe others
            self.log("[Room]:  - Informing other players about this action!")
            for p in self.players.keys():
                if p != currentPlayer:
                    self.log(f"[Room]:  ---- Player {p} informed!")
                    self._broadcast_message(
                        self.players, p, info
                    )  # Update the other players removing the information about the current player`s hand

            # Update the spectators about the game start
            if len(self.spectators) > 0:
                self.log("[Room]:  - Informing spectators about this action!")

            for p_index, p in enumerate(self.spectators.keys()):
                self.log(f"[Room]:  ---- Spectator {p} informed!")
                self._broadcast_message(self.spectators, p, info)

            # Match is over
            if isMatchOver:
                self.log(f"[Room]:  -- Match over!")

                info["type"] = REQUEST_TYPE[
                    "matchOver"
                ]  # Update all players informing that the match is over!
                # print (f"Match over! Current roles: {info["currentRoles"]}")
                self.log("[Room]:  - Informing players about match over!")
                for p in self.players.keys():
                    self.log(f"[Room]:  ---- Player {p} informed!")
                    self._broadcast_message(self.players, p, info)

                # Update the spectators about the game start
                if len(self.spectators) > 0:
                    self.log("[Room]:  - Informing spectators about match over!")

                for p_index, p in enumerate(self.spectators.keys()):
                    self.log(f"[Room]:  ---- Spectator {p} informed!")
                    self._broadcast_message(self.spectators, p, info)
                # A new match is started, with the cards at hand being reshuffled
                # Check if any player is capable of doing a special action
                # Sinalize the player that he can do a special action, wait for reply

                if not self.env.gameFinished:
                    players_actions = self.env.list_players_with_special_actions()
                    doSpecialAction = False
                    playerSpecialAction = -1
                    action_type = ""
                    if len(players_actions) > 1:
                        for player_action in players_actions:
                            player_special = player_action[0]
                            action_type = player_action[1]

                            info_special = {}
                            info_special["special_action"] = action_type
                            info_special["type"] = REQUEST_TYPE["doSpecialAction"]

                            player_name = list(self.players.keys())[player_special]

                            self.log(
                                f"[Room]:  - Requesting special action from: {player_name}!"
                            )
                            doSpecialAction, time_action = self._request_message(
                                player_name, sendInfo
                            )

                            if doSpecialAction:
                                self.env.doSpecialAction(player_special, action_type)
                                playerSpecialAction = player_special

                                # Inform all players a special action was done!
                                info_special_did = {}
                                info_special_did["special_action"] = action_type
                                info_special_did["player"] = player_special
                                info_special_did["type"] = REQUEST_TYPE[
                                    "specialActionUpdate"
                                ]

                                self.log(
                                    "[Room]:  - Informing players about special action!"
                                )
                                for p in self.players.keys():
                                    self._broadcast_message(
                                        self.players, p, info_special_did
                                    )
                                    self.log(f"[Room]:  ---- Player {p} informed!")

                                # Update the spectators about the game start
                                if len(self.spectators) > 0:
                                    self.log(
                                        "[Room]:  - Informing spectators about special action!"
                                    )

                                for p_index, p in enumerate(self.spectators.keys()):
                                    self.log(f"[Room]:  ---- Spectator {p} informed!")
                                    self._broadcast_message(
                                        self.spectators, p, info_special_did
                                    )
                                break
                    if not action_type == "Dinner served!":
                        # Once the cards are handled again, the chef and sous-chef have to choose which cards to give
                        player_sourchef, sc_cards, player_chef, chef_cards = (
                            self.env.get_chef_souschef_roles_cards()
                        )

                        info_special = {}
                        info_special["cards"] = sc_cards
                        info_special["amount"] = 1
                        info_special["type"] = REQUEST_TYPE["exchangeCards"]

                        self.log("[Room]:  - Requesting card exchange from souschef!")
                        souschefCard, time_action = self._request_message(
                            list(self.players.keys())[player_sourchef],
                            info_special,
                        )

                        info_special = {}
                        info_special["cards"] = chef_cards
                        info_special["amount"] = 2
                        info_special["type"] = REQUEST_TYPE["exchangeCards"]

                        self.log("[Room]:  - Requesting card exchange from chef!")

                        chefCards, time_action = self._request_message(
                            list(self.players.keys())[player_chef],
                            info_special,
                        )

                        self.env.exchange_cards(
                            souschefCard,
                            chefCards,
                            doSpecialAction,
                            playerSpecialAction,
                        )

        # Game over!
        self.room_finished = True
        info_end = {}
        info_end["type"] = REQUEST_TYPE["gameOver"]

        self.log("[Room]:  - Updating players about game over!")
        for p in self.players.keys():
            self._broadcast_message(self.players, p, info_end)
            self.log(f"[Room]:  ---- Player {p} informed!")

        # Update the spectators about the game start
        if len(self.spectators) > 0:
            self.log("[Room]:  - Updating spectators about game over!")

        for p_index, p in enumerate(self.spectators.keys()):
            self.log(f"[Room]:  ---- Spectator {p} informed!")
            self._broadcast_message(self.spectators, p, info_end)

        timeElapsed = (datetime.now() - time_start).total_seconds()

        self.log(f"[Room]:  -- Game over! Total game duration: {timeElapsed} seconds!")
        self.room_status = ROOM_STATUS["game_finished"]

        player_names = list(self.players.keys())

        scores = {}
        for player_index, s in enumerate(zip(info["score"], info["performanceScore"])):
            scores[player_names[player_index]] = [s[0], s[1]]

        sorted_scores = sorted(scores.items(), key=lambda x: x[1])
        self.log(f"[Room]:  -- Final Scores:")
        for p in sorted_scores:
            self.log(
                f"[Room]:  ---- {p[0]}: Score: {p[1][0]} (Performance Score: {p[1][1]})"
            )

        self.log(f"[Room]:  -- Closing the Room!")
