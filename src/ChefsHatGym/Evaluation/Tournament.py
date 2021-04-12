from ChefsHatGym.env import ChefsHatEnv

import gym
import numpy
import random
import multiprocessing
import time


class Tournament():


    def __init__(self, opponents, savingDirectory, verbose=True):
        self.opponents = opponents
        self.savingDirectory = savingDirectory
        self.verbose= verbose

    def runTournament(self):
        """Tournament parameters"""
        saveTournamentDirectory = self.savingDirectory  # Where all the logs will be saved
        totalAgents = 32  # Has to be a compatible number, i.e 2^X
        agents = self.opponents

        groups = [agents[g:g + 4] for g in list(range(len(agents)))[::4]]  # Create groups of 4 players
        random.shuffle(groups)

        brackets = [groups[0:int(len(groups) / 2)], groups[int(len(groups) / 2):]]

        """Start each game of each bracket"""
        finalGroup = []
        for indexBracket, bracket in enumerate(brackets):  # for every bracket
            currentBracket = bracket
            newGroup = []
            currentRound = 1
            numberOfGroupsInThisRound = len(bracket)
            removedGroups = 0

            while len(currentBracket) > 0:
                group = currentBracket[0].copy()
                first, second, _, _ = self.playGame(group, indexBracket, currentRound, saveTournamentDirectory)

                newGroup.append(first)
                newGroup.append(second)

                if len(newGroup) == 4:
                    currentBracket.append(newGroup)
                    newGroup = []

                del currentBracket[0]
                removedGroups += 1

                if removedGroups == numberOfGroupsInThisRound:
                    currentRound += currentRound
                    removedGroups = 0
                    numberOfGroupsInThisRound = numberOfGroupsInThisRound / 2

            finalGroup.append(first)
            finalGroup.append(second)

        indexBracket = 3
        currentRound = 1
        first, second, third, fourth = self.playGame(group, indexBracket, currentRound, saveTournamentDirectory)

        return first, second, third, fourth


    """Starting and killing a Thread"""

    def startThread(self,funtion, args):
        proc = multiprocessing.Process(target=funtion,
                                       args=args)
        proc.start()

        killProc = multiprocessing.Process(target=self.killThread,
                                       args=[proc])

        killProc.start()

    """Kill a thread after 15 seconds"""
    def killThread(self,proc):
        time.sleep(15)
        proc.terminate()

    """Playing a Game"""
    def playGame(self, group, bracket, round, saveDirectory):

        """Experiment parameters"""
        saveDirectory = saveDirectory+"/Bracket_"+str(bracket)+"/Round_"+str(round)
        verbose = False
        saveLog = True
        saveDataset = True

        gameType = ChefsHatEnv.GAMETYPE["MATCHES"]
        gameStopCriteria = 1

        agentNames = [agent.name for agent in group]

        rewards = []
        for agent in group:
            rewards.append(agent.getReward)

        """Setup environment"""
        env = gym.make('chefshat-v0') #starting the game Environment
        env.startExperiment(rewardFunctions=rewards, gameType=gameType, stopCriteria=gameStopCriteria, playerNames=agentNames, logDirectory=saveDirectory, verbose=verbose, saveDataset=saveDataset, saveLog=saveLog)

        observations = env.reset()

        while not env.gameFinished:
            currentPlayer = group[env.currentPlayer]

            observations = env.getObservation()
            action = currentPlayer.getAction(observations)

            info = {"validAction": False}
            while not info["validAction"]:
                nextobs, reward, isMatchOver, info = env.step(action)

            # Training will be called in a thread, that will be killed in 15s
            self.startThread(currentPlayer.actionUpdate, args=(observations, nextobs, action, reward, info))

            # Observe others
            for p in group:
                # Observe Others will be called in a thread, that will be killed in 15s
                self.startThread(p.observeOthers, args=(info))

            if isMatchOver:
                for p in group:
                    self.startThread(p.matchUpdate, args=(info))

        if self.verbose:
            print("-------------")
            print("Bracket:" + str(bracket))
            print("Round:" + str(round))
            print("Group:" + str(agentNames))
            print("Score:" + str(info["score"]))
            print("Performance:" + str(info["performanceScore"]))
            print("-------------")

        sortedScore = info["score"]
        sortedScore.sort()

        winner = group[info["score"].index(sortedScore[-1])]
        second = group[info["score"].index(sortedScore[-2])]
        third = group[info["score"].index(sortedScore[-3])]
        fourth = group[info["score"].index(sortedScore[-4])]

        return winner, second, third, fourth






