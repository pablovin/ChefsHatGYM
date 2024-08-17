from ChefsHatGym.agents.chefs_hat_agent import ChefsHatAgent
import numpy
import random
from ChefsHatGym.rewards.only_winning import RewardOnlyWinning


class AgentRandon(ChefsHatAgent):
    suffix = "RANDOM"

    def __init__(
        self, name, saveModelIn: str = "", verbose: bool = False, logDirectory: str = ""
    ):
        super().__init__(
            self.suffix,
            name,
            saveModelIn,
        )

        self.reward = RewardOnlyWinning()

        if verbose:
            self.startLogging(logDirectory)

    def get_action(self, observations):
        possibleActions = observations[28:]

        itemindex = numpy.array(numpy.where(numpy.array(possibleActions) == 1))[
            0
        ].tolist()

        random.shuffle(itemindex)
        aIndex = itemindex[0]
        a = numpy.zeros(200)
        a[aIndex] = 1

        return a

    def get_exhanged_cards(self, cards, amount):
        selectedCards = sorted(cards[-amount:])
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
        thisPlayer = envInfo["thisPlayerPosition"]
        matchFinished = envInfo["thisPlayerFinished"]

        return self.reward.getReward(thisPlayer, matchFinished)
