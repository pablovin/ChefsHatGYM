class RewardOnlyWinning():

    rewardName = "OnlyWinning"

    def getReward(self, action, validAction, possibleActions, score, rounds, isPizza, matchFinished, gameFinished, thisPlayer):

        reward = - 0.001
        if matchFinished:
            playerPosition = score[thisPlayer]
            if playerPosition == 0:
                reward = 1

        return reward
