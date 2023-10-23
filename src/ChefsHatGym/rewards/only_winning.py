from ChefsHatGym.rewards.reward import Reward


class RewardOnlyWinning(Reward):
    """A reward that only produces a maximum value once the action leads to a victory."""

    rewardName = "OnlyWinning"

    def getReward(self, thisPlayerPosition, matchFinished):
        reward = -0.001
        if matchFinished:
            if thisPlayerPosition == 0:
                reward = 1

        return reward
