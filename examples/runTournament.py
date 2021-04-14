from ChefsHatGym.Evaluation import Tournament
from ChefsHatGym.env import ChefsHatEnv
import random
from ChefsHatGym.Agents import Agent_Naive_Random
import time


"""Agents Factory"""
def getCompAgents(totalAgents):
    agents = []
    for i in range(totalAgents):
        agents.append(Agent_Naive_Random.AgentNaive_Random("COMP_"+str(i)))

    random.shuffle(agents)
    return agents


def getCoopAgents(totalAgents):
    agents = []
    for i in range(totalAgents):
        agents.append(Agent_Naive_Random.AgentNaive_Random("COOP_"+str(i)))

    random.shuffle(agents)
    return agents

def getCompCoop(totalAgents):
    agents = []
    for i in range(totalAgents):
        agents.append(Agent_Naive_Random.AgentNaive_Random("COMPCOOP"+str(i)))

    random.shuffle(agents)
    return agents

start_time = time.time()
"""Tournament parameters"""
saveTournamentDirectory = "/home/pablo/Documents/Datasets/ChefsHatCompetition/testing" #Where all the logs will be saved
compAgents = getCompAgents(5)
coopAgents = getCoopAgents(5)
compCoopAgents = getCompCoop(5)
tournament = Tournament.Tournament(saveTournamentDirectory, opponentsComp=compAgents,  oponentsCompCoop=compCoopAgents, verbose=True, threadTimeOut=5, actionTimeOut=5, gameType=ChefsHatEnv.GAMETYPE["MATCHES"], gameStopCriteria=1)
tournament.runTournament()

print("--- %s seconds ---" % (time.time() - start_time))



