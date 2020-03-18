from Rewards import iReward

class RewardIROSPaper(iReward.IReward):


    rewardName = "RewardIROSPaper"

    def getRewardOnlyPass(self, params=[]):
        return 0.01

    def getRewardPass(self, params=[]):
        return -0.5

    def getRewardInvalidAction(self, params=[]):
        return -0.5

    def getRewardDiscard(self, params=[]):
        cardsInHand, playerHand = params
        return(1 - cardsInHand*100 / playerHand * 0.01) *0.7

    def getRewardFinish(self, params=[]):
        position, rounds = params

        if rounds > 50:
            rewardRounds = 0
        else:
            rewardRounds = 0.3

        if position == 0:
            return rewardRounds + 0.7  # experiment 3
        else:
           return -0.01
