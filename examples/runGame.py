from ChefsHatGym.Agents import Agent_Naive_Random

from ChefsHatGym.Rewards import RewardOnlyWinning

from ChefsHatGym.env import ChefsHatEnv

import gym

"""Game parameters"""
gameType = ChefsHatEnv.GAMETYPE["MATCHES"]
gameStopCriteria = 10
rewardFunction = RewardOnlyWinning.RewardOnlyWinning()

"""Player Parameters"""
agent1 = Agent_Naive_Random.AgentNaive_Random("Random1")
agent2 = Agent_Naive_Random.AgentNaive_Random("Random2")
agent3 = Agent_Naive_Random.AgentNaive_Random("Random3")
agent4 = Agent_Naive_Random.AgentNaive_Random("Random4")
agentNames = [agent1.name, agent2.name, agent3.name, agent4.name]
playersAgents = [agent1, agent2, agent3, agent4]

rewards = []
for r in playersAgents:
    rewards.append(r.getReward)

"""Experiment parameters"""
saveDirectory = "examples/"
verbose = False
saveLog = False
saveDataset = False
episodes = 1


"""Setup environment"""
env = gym.make('chefshat-v0') #starting the game Environment
env.startExperiment(rewardFunctions=rewards, gameType=gameType, stopCriteria=gameStopCriteria, playerNames=agentNames, logDirectory=saveDirectory, verbose=verbose, saveDataset=True, saveLog=True)

"""Start Environment"""

for a in range(episodes):

    observations = env.reset()

    while not env.gameFinished:
        currentPlayer = playersAgents[env.currentPlayer]

        observations = env.getObservation()
        action = currentPlayer.getAction(observations)

        info = {"validAction":False}
        while not info["validAction"]:
            nextobs, reward, isMatchOver, info = env.step(action)

        if isMatchOver:
            print ("-------------")
            print ("Match:" + str(info["matches"]))
            print ("Score:" + str(info["score"]))
            print("Performance:" + str(info["performanceScore"]))
            print("-------------")

