from Rewards import iReward
from keras.models import load_model

class RewardAIRL(iReward.IReward):


    rewardName = "OnlyWinning"

    def getRewardOnlyPass(self, params=[]):
        return -0.01

    def getRewardPass(self, params=[]):
        return -0.01

    def getRewardInvalidAction(self, params=[]):
        return -1.0

    def getRewardDiscard(self, params=[]):
        return -0.01

    def getRewardFinish(self, params=[]):
        position, rounds = params

        if position == 0:
            return 1  # experiment 3
        else:
           return -0.1
