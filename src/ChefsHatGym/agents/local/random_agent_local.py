from ChefsHatGym.agents.chefs_hat_agent import ChefsHatAgent
import numpy
import random
from ChefsHatGym.rewards.only_winning import RewardOnlyWinning


class AgentRandonLocal(ChefsHatAgent):
    suffix = "RANDOM"

    def __init__(
        self,
        name,
        saveModelIn: str = "",
    ):
        super().__init__(
            self.suffix,
            name,
            saveModelIn,
        )

        self.reward = RewardOnlyWinning()

    def getAction(self, observations):
        possibleActions = observations[28:]

        itemindex = numpy.array(numpy.where(numpy.array(possibleActions) == 1))[
            0
        ].tolist()

        random.shuffle(itemindex)
        aIndex = itemindex[0]
        a = numpy.zeros(200)
        a[aIndex] = 1

        return a

    def exchangeCards(self, cards, amount):
        selectedCards = sorted(cards[-amount:])
        return selectedCards

    def doSpecialAction(self, info, specialAction):
        return True

    def actionUpdate(self, envInfo):
        pass

    def observeOthers(self, envInfo):
        pass

    def matchUpdate(self, envInfo):
        pass

    def getReward(self, envInfo):
        thisPlayer = envInfo["thisPlayerPosition"]
        matchFinished = envInfo["thisPlayerFinished"]

        return self.reward.getReward(thisPlayer, matchFinished)
