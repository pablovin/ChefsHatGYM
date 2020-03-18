from Rewards import iReward

class RewardValidAction(iReward.IReward):


    rewardName = "ValidAction"

    def getRewardOnlyPass(self, params=[]):
        return 0.01

    def getRewardPass(self, params=[]):
        return 1.0

    def getRewardInvalidAction(self, params=[]):
        return -1.0

    def getRewardDiscard(self, params=[]):
        return 1

    def getRewardFinish(self, params=[]):
        position, rounds = params
        return 1

        # if position == 0:
        #     return 1  # experiment 3
        # else:
        #    return -0.01
