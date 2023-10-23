from ChefsHatGym.rewards.reward import Reward


class RewardPerformanceScore(Reward):
    """A reward that is weighted based on the agent`s performance at the end of a match"""

    rewardName = "PerformanceScore"

    def getReward(self, thisPlayerPosition, performanceScore, matchFinished):
        reward = -0.001
        if matchFinished:
            finalPoints = (3 - thisPlayerPosition) / 3
            reward = finalPoints + performanceScore

        return reward
