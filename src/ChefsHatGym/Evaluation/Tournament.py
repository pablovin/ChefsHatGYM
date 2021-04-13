from ChefsHatGym.Agents import Agent_Naive_Random
from ChefsHatGym.KEF import LogManager


import gym
import numpy
import random
import math
import copy



class Tournament():


    def __init__(self, opponents, savingDirectory, verbose=True, threadTimeOut=5, actionTimeOut=5,  gameType=["POINTS"], gameStopCriteria=15, tournamentType="COMP"):
        self.savingDirectory = savingDirectory
        self.verbose= verbose
        self.threadTimeOut = threadTimeOut
        self.actionTimeout = actionTimeOut
        self.gameType = gameType
        self.gameStopCriteria = gameStopCriteria
        self.tournamentType = tournamentType

        """Complement the group of agents to be a number pow 2"""


        self.opponents = self.complementGroups(opponents)


    def runTournament(self):
        """Tournament parameters"""
        saveTournamentDirectory = self.savingDirectory  # Where all the logs will be saved
        agents = self.opponents

        groups = [agents[g:g + 4] for g in list(range(len(agents)))[::4]]  # Create groups of 4 players
        random.shuffle(groups)

        brackets = [groups[0:int(len(groups) / 2)], groups[int(len(groups) / 2):]]

        phases = int(math.log(len(brackets[0]),2))+1

        logger = LogManager.Logger(saveTournamentDirectory+"/Log.txt", verbose=True)

        names = [a.name for g in brackets[0] for a in g]

        logger.newLogSession("Tournament starting!")
        logger.write("Total players:" + str(len(self.opponents)))
        logger.write("Total groups:" + str(len(groups)))
        for bIndex, b in enumerate(brackets):
            logger.write("Bracket "+str(bIndex)+":")
            for gIndex, g in enumerate(b):
                names = [a.name for a in b[gIndex]]
                logger.write(" -Group "+str(gIndex)+":"+str(names))

        logger.write("Phases per Bracket:" + str(phases))

        bWinners = []
        for b in range(len(brackets)):
            logger.newLogSession("Starting Games from Bracket:" + str(b+1))
            thisPhaseGroup = brackets[b]
            for p in range(phases):
                logger.newLogSession("Starting Phase:" + str(p+1))
                names = [a.name for g in thisPhaseGroup for a in g]
                logger.write("- Participants:" + str(names))
                newPhaseGroups = []
                for game in range(len(thisPhaseGroup)):
                    names = [a.name for a in thisPhaseGroup[game]]
                    logger.write("- Game:" + str(game) + " - "+str(names))
                    first, second, _, _ = self.playGame(thisPhaseGroup[game], b+1, p+1, game,saveTournamentDirectory, logger)
                    logger.write("-- First:" + str(first.name) + " - Second:" + str(second.name))
                    newPhaseGroups.append(first)
                    newPhaseGroups.append(second)
                if p == phases-1:
                    bWinners.append(newPhaseGroups[0])
                    bWinners.append(newPhaseGroups[1])
                else:
                   thisPhaseGroup = [newPhaseGroups[g:g + 4] for g in list(range(len(newPhaseGroups)))[::4]]

                names = [a.name for a in bWinners if len(bWinners) > 0]
                print ("bWinners:" + str(names))

        logger.newLogSession("Final match!")
        logger.write("- Participants:" + str(names))
        first, second, third, fourth = self.playGame(bWinners, 3, 1, 1, saveTournamentDirectory, logger)
        logger.write("-- Final position:")
        logger.write("-- 1)" + str(first.name))
        logger.write("-- 2)" + str(second.name))
        logger.write("-- 3)" + str(third.name))
        logger.write("-- 4)" + str(fourth.name))
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
    def playGame(self, group, bracket, round, gameNumber, saveDirectory, logger):

        """Experiment parameters"""
        saveDirectory = saveDirectory+"/Bracket_"+str(bracket)+"/Phase_"+str(round)+"/Game_"+str(gameNumber)
        verbose = False
        saveLog = True
        saveDataset = True

        agentNames = [agent.name for agent in group]

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
            logger.write("-- Performance:" + str(info["performanceScore"]))
            logger.write("-- Points:" + str(info["score"]))

        return winner, second, third, fourth






