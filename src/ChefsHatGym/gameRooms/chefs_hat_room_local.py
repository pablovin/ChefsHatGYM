from datetime import datetime
import os
import time
from ChefsHatGym.env import ChefsHatEnv
from ChefsHatGym.agents.base_classes.chefs_hat_player import ChefsHatPlayer
from ChefsHatGym.agents.base_classes.chefs_hat_spectator import ChefsHatSpectator
import gym
import numpy as np

import ChefsHatGym.utils.utils as utils


class ChefsHatRoomLocal:
    """
    Room environment where a game will be played locally.
    """

    def get_room_id(self) -> str:
        """ge the room id

        Returns:
            str: room id
        """
        return self.room_id

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
        game_type: str = ChefsHatEnv.GAMETYPE["MATCHES"],
        stop_criteria: int = 10,
        max_rounds: int = -1,
        save_dataset: bool = True,
        verbose_console: bool = True,
        verbose_log: bool = True,
        game_verbose_console: bool = True,
        game_verbose_log: bool = True,
        log_directory: str = None,
        timeout_player_response: int = 5,
    ) -> None:
        """Initialize the room

        Args:
            room_name (str): name of the room, no special character is allowed.
            game_type (str, optional): game type, defined as ChefsHatEnv.GAMETYPE. Defaults to ChefsHatEnv.GAMETYPE["MATCHES"].
            stop_criteria (int, optional): stop criteria for the game. Defaults to 10.
            max_rounds (int, optional): maximum rounds of the game, if -1 the game will play until it ends. Defaults to -1.
            verbose (bool, optional): room verbose. Defaults to True.
            save_dataset (bool, optional): save the game dataset .pkl. Defaults to True.
            save_game_log (bool, optional): save the game log. Defaults to True.
            log_directory (str, optional): directory to save the log. Defaults to None.
            timeout_player_response (int, optional): timeout for the player responses. Defaults to 5.
        """
        # game type parameters
        self.room_name = room_name
        self.game_type = game_type
        self.stop_criteria = stop_criteria
        self.max_rounds = max_rounds
        self.game_verbose_console = game_verbose_console
        self.save_dataset = save_dataset
        self.game_verbose_log = game_verbose_log

        self.timeout_player_response = timeout_player_response

        # In-game parameters
        self.spectators = {}
        self.players = []
        self.players_names = []
        self.receive_messages_subs = {}
        self.room_finished = False
        self.ready_to_start = False

        # Create the log directory
        if not log_directory:
            log_directory = "temp/"

        self.log_directory = os.path.join(
            log_directory, f"{datetime.now().strftime('%H-%M%S')}_{room_name}"
        )
        os.makedirs(self.log_directory)

        # Creating logger
        self.logger = utils.get_logger(
            f"ROOM_{room_name}",
            self.log_directory,
            "room_log.log",
            verbose_console,
            verbose_log,
        )

        self.log("---------------------------")
        self.log("Creating logger")
        self.log(f"[Room]:  - folder: { self.log_directory}")

        # Create a room
        self.room_id = room_name

    def log(self, message: str):
        """log messages

        Args:
            message (str): message
        """
        self.logger.info(f"[Room]: {message}")

    def error(self, message: str):
        """log errors

        Args:
            message (str): error
        """

        self.logger.critical(f"[Room]: {message}")

    def add_spectator(self, spectator: ChefsHatSpectator):
        """Add a spectator to the room

        Args:
            spectator (ChefsHatSpectator): a Spectator that has to implement the ChefsHatSpectator class

        Raises:
            Exception: the room cannot have two players with the same name
        """

        if spectator.get_name() in self.spectators:
            self.error(
                f"[Room][ERROR]: Spectator names must be unique! Trying to add {spectator.get_name()} to existing spectators: {self.spectators}!"
            )
            raise Exception(f"Duplicated spectator name: {spectator.get_name()} !")

        self.spectators[spectator.get_name()] = spectator

        self.log(
            f"[Room]:  - Spectator {spectator.get_name()} connected! Current spectators: {self.spectators}"
        )

    def add_player(self, player: ChefsHatPlayer):
        """Add a player to the room

        Args:
            player (ChefsHatPlayer): a Player that has to implement the ChefsHatPlayer class

        Raises:
            Exception: the room cannot have two players with the same name
        """

        if len(self.players) < 4:
            if player.get_name() in self.players_names:
                self.error(
                    f"[Room][ERROR]: Player names must be unique! Trying to add {[player.get_name()]} to existing players: {self.players_names}!"
                )
                raise Exception("Duplicated player name!")

            self.players.append(player)
            self.players_names.append(player.get_name())
            self.log(
                f"[Room]:  - Player {player.get_name()} connected! Current players: {self.players_names}"
            )
        else:
            self.error(
                f"[Room][ERROR]: Room is full!! Player not added! Current players: {self.players_names}!"
            )

    def start_new_game(self) -> dict:
        """Start the game in the room

        Returns:
            dict: the game info
        """

        if len(self.players) < 4:
            self.error(
                f"[Room][ERROR]: Not enough players to start the game! Total current players: {len(self.players_names)}"
            )
        else:
            time_start = datetime.now()
            self.log("---------------------------")
            self.log("Initializing a game")

            """Setup environment"""
            self.env = gym.make("chefshat-v1")  # starting the game Environment
            self.env.startExperiment(
                gameType=self.game_type,
                stopCriteria=self.stop_criteria,
                maxRounds=self.max_rounds,
                playerNames=self.players_names,
                logDirectory=self.log_directory,
                verbose=self.game_verbose_console,
                saveDataset=self.save_dataset,
                saveLog=self.game_verbose_log,
            )

            self.log(" - Environment initialized!")
            observations = self.env.reset()

            # Update each player about the begining of the match
            for p_index, p in enumerate(self.players):
                p.update_start_match(
                    self.env.players[p_index].cards,
                    self.players_names,
                    self.players_names[self.env.currentPlayer],
                )

                # Update each spectator about the begining of the match
            for name, spectator in self.spectators.items():
                spectator.update_start_match(
                    self.players_names,
                    self.players_names[self.env.currentPlayer],
                )

            while not self.env.gameFinished:
                currentPlayer = self.players[self.env.currentPlayer]
                self.log(
                    f"[Room]:  -- Round {self.env.rounds} -  Current player: {currentPlayer.get_name()}"
                )
                observations = self.env.getObservation()

                info = {"Action_Valid": False}
                while not info["Action_Valid"]:
                    timeNow = datetime.now()
                    action = currentPlayer.get_action(observations)

                    nextobs, reward, isMatchOver, truncated, info = self.env.step(
                        action
                    )

                    self.log(
                        f"[Room]:  ---- Round {self.env.rounds} Action: {info['Action_Decoded']}"
                    )
                    if info["Is_Pizza"]:
                        self.log(
                            f"[Room]:  ---- Round {info['Pizza_Author']} Made a Pizza!!"
                        )

                    if not info["Action_Valid"]:
                        self.error(f"[Room][ERROR]: ---- Invalid action!")

                # Send action update to the current agent
                info["Observation_Before"] = observations.tolist()
                info["Observation_After"] = nextobs.tolist()
                currentPlayer.update_my_action(info)

                info["Observation_Before"] = ""
                info["Observation_After"] = ""

                info["Action_Random"] = ""
                info["Author_Possible_Actions"] = ""
                # Observe others
                for p in self.players:
                    if p != currentPlayer:
                        p.update_action_others(info)

                # Update spectators
                for name, spectator in self.spectators.items():
                    spectator.update_action_others(info)

                # Match is over
                if isMatchOver:
                    if self.env.matches % 100 == 0:
                        print(f"{datetime.now()} - Match {self.env.matches} done!")
                    self.log(f"[Room]:  -- Match over! Total rounds: {self.env.rounds}")

                    # Players are updated that the match is over
                    for p in self.players:
                        p.update_end_match(info)

                    # Update spectators that the match is over
                    for name, spectator in self.spectators.items():
                        spectator.update_end_match(info)

                    # A new match is started, with the cards at hand being reshuffled
                    # Check if any player is capable of doing a special action
                    # Sinalize the player that he can do a special action, wait for reply

                    if not self.env.gameFinished:
                        players_actions = self.env.list_players_with_special_actions()
                        doSpecialAction = False
                        playerSpecialAction = -1
                        if len(players_actions) > 1:
                            for player_action in players_actions:
                                player = player_action[0]
                                action = player_action[1]
                                doSpecialAction = self.playersp[
                                    player
                                ].do_special_action(info, action)
                                if doSpecialAction:
                                    self.env.doSpecialAction(player, action)
                                    playerSpecialAction = player

                                    # Update players about a special action
                                    for p in self.players:
                                        p.observe_special_action(action, player)

                                    # Update spectators about a special action
                                    for name, spectator in self.spectators.items():
                                        spectator.observe_special_action(action, player)
                                    break

                        # Once the cards are handled again, the chef and sous-chef have to choose which cards to give
                        (
                            player_dishwasher,
                            dishCards,
                            player_waiter,
                            waiterCards,
                            player_sourchef,
                            sc_cards,
                            player_chef,
                            chef_cards,
                        ) = self.env.get_chef_souschef_roles_cards()

                        self.log("[Room]:  - Requesting card exchange from souschef!")
                        souschefCard = self.players[player_sourchef].get_exhanged_cards(
                            sc_cards, 1
                        )[0]

                        self.log("[Room]:  - Requesting card exchange from chef!")
                        chefCards = self.players[player_chef].get_exhanged_cards(
                            chef_cards, 2
                        )

                        # Update each player about the card exchange results
                        # Chef
                        self.log("[Room]:  - Informing Chef about cards exchanged!")
                        self.players[player_chef].update_exchange_cards(
                            chefCards, dishCards
                        )

                        # Souschef
                        self.log("[Room]:  - Informing Souschef about cards exchanged!")
                        self.players[player_waiter].update_exchange_cards(
                            souschefCard, waiterCards
                        )

                        # Waiter
                        self.log("[Room]:  - Informing Waiter about cards exchanged!")
                        self.players[player_sourchef].update_exchange_cards(
                            waiterCards, souschefCard
                        )

                        # Dishwasher
                        self.log(
                            "[Room]:  - Informing Dishwasher about cards exchanged!"
                        )
                        self.players[player_dishwasher].update_exchange_cards(
                            dishCards, chefCards
                        )

                        self.env.exchange_cards(
                            chefCards,
                            souschefCard,
                            waiterCards,
                            dishCards,
                            doSpecialAction,
                            playerSpecialAction,
                        )

            # Game over!

            self.room_finished = True
            # inform agents that the game is over
            for p in self.players:
                p.update_game_over()

            # inform spectators that the game is over
            for name, spectator in self.spectators.items():
                spectator.update_game_over()

            timeElapsed = (datetime.now() - time_start).total_seconds()

            self.log(
                f"[Room]:  -- Game over! Total game duration: {timeElapsed} seconds!"
            )
            return info
