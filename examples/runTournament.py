from ChefsHatGym.Evaluation import Tournament
from ChefsHatGym.env import ChefsHatEnv
import random
from ChefsHatGym.Agents import AgentNaive_Random, RemoteAgent
import time
import os
import sys
from multiprocessing import Process

"""Agents Factory"""


def getCompAgents(totalAgents):
    agents = [AgentNaive_Random("COMP_" + str(i)) for i in range(totalAgents)]
    random.shuffle(agents)
    return agents


def getCoopAgents(totalAgents):
    agents = [AgentNaive_Random("COOP_" + str(i)) for i in range(totalAgents)]
    random.shuffle(agents)
    return agents


def getCompCoop(totalAgents):
    agents = [AgentNaive_Random("COMPCOOP_" + str(i)) for i in range(totalAgents)]
    random.shuffle(agents)
    return agents


# self, playersAgents, gameType=ChefsHatEnv.GAMETYPE["MATCHES"], gameStopCriteria=10, rewardFunction=RewardOnlyWinning, verbose=False
class SimpleTournament:
    def __init__(
        self,
        compAgents=[],
        compCoopAgents=[],
        verbose=True,
        gameType=ChefsHatEnv.GAMETYPE["MATCHES"],
        gameStopCriteria=1,
        path="examples/tournament_0",
    ):
        self.compCoopAgents = compCoopAgents
        self.compAgents = compAgents
        self.verbose = verbose
        self.gameType = gameType
        self.gameStopCriteria = gameStopCriteria
        self.path = path

    def run(self):
        os.mkdir(self.path)
        sys.stdout = open(os.devnull, "w")
        self.tournament = Tournament(
            self.path,
            self.verbose,
            self.compAgents,
            [],
            self.compCoopAgents,
            self.gameType,
            self.gameStopCriteria,
        )
        self.tournament.runTournament()
        sys.stdout = sys.__stdout__
