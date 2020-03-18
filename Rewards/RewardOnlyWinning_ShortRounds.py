from Rewards import iReward

class RewardOnlyWinning_ShortRounds(iReward.IReward):


    rewardName = "RewardOnlyWinning_ShortRounds"

    def getRewardOnlyPass(self, params=[]):
        return -0.01

    def getRewardPass(self, params=[]):
        return -0.01

    def getRewardInvalidAction(self, params=[]):
        return -0.5

    def getRewardDiscard(self, params=[]):
        return -0.01

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
