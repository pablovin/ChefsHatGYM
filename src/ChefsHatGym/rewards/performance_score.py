class RewardPerformanceScore():
    rewardName = "PerformanceScore"
    getReward = lambda self, thisPlayerPosition, performanceScore, matchFinished: (((3 - thisPlayerPosition) / 3) + performanceScore) if matchFinished else -0.001
