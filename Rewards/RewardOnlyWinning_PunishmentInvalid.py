from Rewards import iReward

class RewardOnlyWinning_PunishmentInvalid(iReward.IReward):


    rewardName = "OnlyWinning_PunishmentInvalid"

    def getRewardOnlyPass(self, params=[]):
        return -0.01

    def getRewardPass(self, params=[]):
        return -0.01

    def getRewardInvalidAction(self, params=[]):
        return -0.5

    def getRewardDiscard(self, params=[]):
        return -0.01

    def getRewardFinish(self, params=[]):
        position = params
        if position == 0:
            return 1  # experiment 3
        else:
           return -0.01
