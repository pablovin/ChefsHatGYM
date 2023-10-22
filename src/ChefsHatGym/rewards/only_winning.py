class RewardOnlyWinning():
    rewardName = "OnlyWinning"
    getReward = lambda self, thisPlayerPosition, matchFinished: 1 if matchFinished and thisPlayerPosition == 0 else -0.001
