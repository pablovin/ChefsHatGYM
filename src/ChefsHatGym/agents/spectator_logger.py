from ChefsHatGym.agents.base_classes.chefs_hat_spectator import ChefsHatSpectator
from ChefsHatGym.rewards.only_winning import RewardOnlyWinning


class SpectatorLogger(ChefsHatSpectator):
    suffix = "LOGGER"

    def __init__(
        self,
        name,
        this_agent_folder: str = "",
        verbose_console: bool = False,
        verbose_log: bool = False,
        log_directory: str = "",
    ):
        super().__init__(
            self.suffix,
            name,
            this_agent_folder,
            verbose_console,
            verbose_log,
            log_directory,
        )

        self.reward = RewardOnlyWinning()

    def update_start_match(self, players, starting_player):
        self.log("---------------------------------")
        self.log("A new match has started!")
        self.log(f"These are the players of today`s match: {players}")
        self.log(f"And we start the match with {starting_player}!")

    def observe_special_action(self, action_type, player):
        self.log("---------------------------------")
        self.log(f"And looks like {player} is doing an special action!")
        self.log(f"Yes, the brave player is declaring {action_type}!")

    def update_end_match(self, envInfo):
        score = envInfo["Game_Score"]
        players = envInfo["Player_Names"]

        self.log("---------------------------------")
        self.log("This match is over!")
        self.log("This is the current score:")

        for score, player in zip(score, players):
            self.log(f"{player}: {score} points")

    def update_action_others(self, envInfo):
        players = envInfo["Player_Names"]
        boardBefore = envInfo["Board_Before"]
        boardAfter = envInfo["Board_After"]
        thisPlayer = envInfo["Author_Index"]
        action = envInfo["Action_Decoded"]
        remaining_cards = envInfo["Cards_Per_Player"]
        is_pizza_ready = envInfo["Is_Pizza"]
        this_player_finished = thisPlayer in envInfo["Finished_Players"]

        player_name = players[thisPlayer]

        self.log("---------------------------------")
        self.log(f"This is the current state of the board: {boardBefore}.")
        self.log(f"Now, it appears that player {player_name} just did: {action}! ")
        self.log(f"That made the board looks like that: {boardAfter}.")

        if this_player_finished:
            self.log(f"And the player discard all cards! Congratulations!")
        else:
            self.log(
                f"And the player now the player has {remaining_cards[thisPlayer]} cards at hand!"
            )

        if is_pizza_ready:
            self.log(f"And the player declared Pizza! What a move!")
