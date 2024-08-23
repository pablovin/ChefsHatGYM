from ChefsHatGym.agents.base_classes.chefs_hat_player import ChefsHatPlayer
import numpy
import random
from ChefsHatGym.rewards.only_winning import RewardOnlyWinning


class AgentRandon(ChefsHatPlayer):
    suffix = "RANDOM"

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

    def get_action(self, observations):

        possibleActions = observations[28:]

        itemindex = numpy.array(numpy.where(numpy.array(possibleActions) == 1))[
            0
        ].tolist()

        random.shuffle(itemindex)
        aIndex = itemindex[0]
        a = numpy.zeros(200)
        a[aIndex] = 1

        self.log("---------------------------------")
        self.log("        I did an action!")
        self.log("---------------------------------")
        self.log(f"Cards in the board: {observations[0:11]}")
        self.log(f"Cards at hand: {observations[11:28]}")
        self.log(f"Possible Actions: {observations[28:]}")
        self.log(f"Chosen Action: {a}")

        return a

    def get_exhanged_cards(self, cards, amount):
        selectedCards = sorted(cards[-amount:])

        self.log("---------------------------------")
        self.log("        I did a card exchange!")
        self.log("---------------------------------")
        self.log(f"Cards in my hand: {cards}")
        self.log(f"I need to select: {amount} cards")
        self.log(f"My choice: {selectedCards} ")

        return selectedCards

    def do_special_action(self, info, specialAction):
        return True

    def update_my_action(self, envInfo):
        pass

    def update_action_others(self, envInfo):
        pass

    def update_end_match(self, envInfo):
        pass

    def update_start_match(self, cards, players, starting_player):
        pass

    def get_reward(self, envInfo):
        this_player = envInfo["Author_Index"]
        this_player_position = 3 - envInfo["Match_Score"][this_player]
        this_player_finished = this_player in envInfo["Finished_Players"]

        return self.reward.getReward(this_player_position, this_player_finished)
