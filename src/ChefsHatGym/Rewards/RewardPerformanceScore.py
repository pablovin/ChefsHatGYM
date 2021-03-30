class RewardPerformanceScore():

    rewardName = "PerformanceScore"

    def getReward(self, thisPlayerPosition, performanceScore, matchFinished):

        reward = - 0.001
        if matchFinished:
            finalPoints = (3 - thisPlayerPosition)/3
            reward = finalPoints + performanceScore

        return reward
