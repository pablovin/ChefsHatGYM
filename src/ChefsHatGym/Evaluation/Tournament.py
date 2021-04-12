from ChefsHatGym.Agents import Agent_Naive_Random

import gym
import numpy
import random
import math
import copy



class Tournament():


    def __init__(self, opponents, savingDirectory, verbose=True, threadTimeOut=5, actionTimeOut=5,  gameType=["POINTS"], gameStopCriteria=15):
        self.savingDirectory = savingDirectory
        self.verbose= verbose
        self.threadTimeOut = threadTimeOut
        self.actionTimeout = actionTimeOut
        self.gameType = gameType
        self.gameStopCriteria = gameStopCriteria

        """Complement the group of agents to be a number pow 2"""

        self.opponents = self.complementGroups(opponents)
        if self.verbose:
            print("--- Complementing the opponents with random agents to a total of " + str(len(opponents)) + " agents!")

    def runTournament(self):
        """Tournament parameters"""
        saveTournamentDirectory = self.savingDirectory  # Where all the logs will be saved
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



    """Get Random action"""
    def getRandomAction(self, possibleActions):
        itemindex = numpy.array(numpy.where(numpy.array(possibleActions) == 1))[0].tolist()

        random.shuffle(itemindex)
        aIndex = itemindex[0]
        a = numpy.zeros(200)
        a[aIndex] = 1

        return a

    """Complement the opponents with random agents until we have enough to create two brackets"""
    def complementGroups(self, group):


        difference = float(math.log(len(group),2))

        if difference.is_integer():
            if len(group) < 8:
                for n in range(int(8-len(group))):
                    group.append(Agent_Naive_Random.AgentNaive_Random("Random" + str(n)))

            return group
        else:
            intDiff = math.modf(difference)[1]

            newAdditions = int(math.pow(2,intDiff+1) - len(group))

            for n in range(newAdditions):
                group.append(Agent_Naive_Random.AgentNaive_Random("Random"+str(n)))

        return group


    """Playing a Game"""
    def playGame(self, group, bracket, round, saveDirectory):

        """Experiment parameters"""
        saveDirectory = saveDirectory+"/Bracket_"+str(bracket)+"/Round_"+str(round)
        verbose = False
        saveLog = True
        saveDataset = True

        agentNames = [agent.name for agent in group]

        if self.verbose:
            print("-------------")
            print ("--- Opponents:" + str(agentNames))

        rewards = []
        for agent in group:
            rewards.append(agent.getReward)

        """Setup environment"""
        env = gym.make('chefshat-v0') #starting the game Environment
        env.startExperiment(rewardFunctions=rewards, gameType=self.gameType, stopCriteria=self.gameStopCriteria, playerNames=agentNames, logDirectory=saveDirectory, verbose=verbose, saveDataset=saveDataset, saveLog=saveLog)

        observations = env.reset()

        while not env.gameFinished:
            currentPlayer = group[env.currentPlayer]

            observations = env.getObservation()

            action = []
            with currentPlayer.timeout(self.actionTimeout):
                action = currentPlayer.getAction(observations)
            if len(action) == 0:
                action = self.getRandomAction(observations[28:])

            info = {"validAction": False}
            while not info["validAction"]:
                nextobs, reward, isMatchOver, info = env.step(action)

            # Training will be called in a thread, that will be killed inself.threadTimes
            # self.runUpdateAction(currentPlayer, args=(observations, nextobs, action, reward, info) )
            with currentPlayer.timeout(self.threadTimeOut):
                currentPlayer.actionUpdate(observations, nextobs, action, reward, info)

            # self.startThread(currentPlayer.actionUpdate, args=(observations, nextobs, action, reward, info))
            # currentPlayer.actionUpdate(observations, nextobs, action, reward, info)


            # Observe others
            for p in group:
                # Observe Others will be called in a thread, that will be killed in self.threadTimes
                with p.timeout(self.threadTimeOut):
                    p.observeOthers(info)
            #
            if isMatchOver:
                # Update the match info as a thread that will be killed in self.threadTimes
                for p in group:
                    with p.timeout(self.threadTimeOut):
                        p.matchUpdate(info)




        sortedScore = copy.copy(info["score"])
        sortedScore.sort()

        winner = group[info["score"].index(sortedScore[-1])]
        second = group[info["score"].index(sortedScore[-2])]
        third = group[info["score"].index(sortedScore[-3])]
        fourth = group[info["score"].index(sortedScore[-4])]

        if self.verbose:
            print("--- Bracket:" + str(bracket))
            print("--- Round:" + str(round))
            print("--- Group:" + str(agentNames))
            print("--- Score:" + str(info["score"]))
            print("--- Performance:" + str(info["performanceScore"]))
            print("--- Positions:" + winner.name+","+second.name+","+third.name+","+fourth.name)
            print("-------------")

        return winner, second, third, fourth






