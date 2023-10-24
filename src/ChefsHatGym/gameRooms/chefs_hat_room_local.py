from datetime import datetime
import os
import time
from ChefsHatGym.env import ChefsHatEnv
from ChefsHatGym.agents.chefs_hat_agent import ChefsHatAgent
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
        verbose: bool = True,
        save_dataset: bool = True,
        save_game_log: bool = True,
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
        self.verbose = verbose
        self.save_dataset = save_dataset
        self.save_game_log = save_game_log

        self.timeout_player_response = timeout_player_response

        # In-game parameters
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
        self.logger = utils.logging.getLogger("ROOM")
        self.logger.addHandler(
            utils.logging.FileHandler(
                os.path.join(self.log_directory, "rom_log.log"),
                mode="w",
                encoding="utf-8",
            )
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
        if self.verbose:
            self.logger.info(f"[Room]: {message}")

    def error(self, message: str):
        """log errors

        Args:
            message (str): error
        """
        if self.verbose:
            self.logger.critical(f"[Room]: {message}")

    def add_player(self, player: ChefsHatAgent):
        """Add a player to the room

        Args:
            player (ChefsHatAgent): a Player that has to implement the ChefsHatAgent class

        Raises:
            Exception: the room cannot have two players with the same name
        """

        if len(self.players) < 4:
            if player.get_name() in self.players_names:
                self.error(
                    f"[Room][ERROR]: Player names must be unique! Trying to add {[player.get_name()]} to existing players: {self.players_names}!"
                )
                raise Exception("Players with the same name!")

            self.players.append(player)
            self.players_names.append(player.get_name())
            self.log(
                f"[Room]:  - Player {player.get_name()} connected! Current players: {self.players_names}"
            )
        else:
            self.error(
                f"[Room][ERROR]: Room is full!! Player not added! Current players: {self.players_names}!"
            )

    def start_new_game(self, game_verbose: bool = False) -> dict:
        """Start the game in the room

        Args:
            game_verbose (bool): Verbose of the game environment

        Returns:
            dict: the game info
        """

        if len(self.players) < 4:
            self.error(
                f"[Room][ERROR]: Not enough players to start the game! Total current players: {len(self.players_names)}"
            )
        else:
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
                verbose=game_verbose,
                saveDataset=self.save_dataset,
                saveLog=self.save_game_log,
            )

            self.log(" - Environment initialized!")
            observations = self.env.reset()

            # Update each player about the begining of the match
            for p_index, p in enumerate(self.players):
                p.update_start_match(
                    self.env.playersHand[p_index],
                    self.players_names,
                    self.env.currentPlayer,
                )

            while not self.env.gameFinished:
                currentPlayer = self.players[self.env.currentPlayer]
                self.log(
                    f"[Room]:  -- Round {self.env.rounds} -  Current player: {currentPlayer.get_name()}"
                )
                observations = self.env.getObservation()

                info = {"validAction": False}
                while not info["validAction"]:
                    timeNow = datetime.now()
                    action = currentPlayer.get_action(observations)

                    self.log(
                        f"[Room]:  ---- Round {self.env.rounds} Action: {np.argmax(action)}"
                    )
                    nextobs, reward, isMatchOver, truncated, info = self.env.step(
                        action
                    )

                    if not info["validAction"]:
                        self.error(f"[Room][ERROR]: ---- Invalid action!")

                # Send action update to the current agent
                info["observation"] = observations.tolist()
                info["nextObservation"] = nextobs.tolist()
                currentPlayer.update_my_action(info)

                info["observation"] = ""
                info["nextObservation"] = ""

                info["actionIsRandom"] = ""
                info["possibleActions"] = ""
                # Observe others
                for p in self.players:
                    if p != currentPlayer:
                        p.update_action_others(info)

                # Match is over
                if isMatchOver:
                    self.log(f"[Room]:  -- Match over! Total rounds: {self.env.rounds}")

                    # Players are updated that the match is over
                    for p in self.players:
                        p.update_end_match(info)

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
                                    break

                        # Once the cards are handled again, the chef and sous-chef have to choose which cards to give
                        (
                            player_sourchef,
                            sc_cards,
                            player_chef,
                            chef_cards,
                        ) = self.env.get_chef_souschef_roles_cards()
                        souschefCard = self.players[player_sourchef].get_exhanged_cards(
                            sc_cards, 1
                        )
                        chefCards = self.players[player_chef].get_exhanged_cards(
                            chef_cards, 2
                        )
                        self.env.exchange_cards(
                            souschefCard,
                            chefCards,
                            doSpecialAction,
                            playerSpecialAction,
                        )

            # Game over!
            self.room_finished = True
            return info
