class RewardOnlyWinning():

    rewardName = "OnlyWinning"

    def getReward(self,  thisPlayerPosition, matchFinished):

        reward = - 0.001
        if matchFinished:
            if thisPlayerPosition == 0:
                reward = 1

        return reward
