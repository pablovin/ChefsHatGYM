from ChefsHatGym.Evaluation import Tournament
from ChefsHatGym.env import ChefsHatEnv
import random
from ChefsHatGym.Agents import Agent_Naive_Random
import time


"""Agents Factory"""
def getAgents(totalAgents):
    agents = []
    for i in range(totalAgents):
        agents.append(Agent_Naive_Random.AgentNaive_Random("R_"+str(i)))

    random.shuffle(agents)
    return agents


start_time = time.time()
"""Tournament parameters"""
saveTournamentDirectory = "/home/pablo/Documents/Datasets/ChefsHatCompetition/testing" #Where all the logs will be saved
agents = getAgents(35)
tournament = Tournament.Tournament(agents, saveTournamentDirectory, verbose=True, threadTimeOut=5, actionTimeOut=5, gameType=ChefsHatEnv.GAMETYPE["MATCHES"], gameStopCriteria=1)
first, second, third, fourth = tournament.runTournament()

print("--- %s seconds ---" % (time.time() - start_time))
print ("Winner:" + str(first.name))
print ("Second:" + str(second.name))
print ("Third:" + str(third.name))
print ("Fourth:" + str(fourth.name))


