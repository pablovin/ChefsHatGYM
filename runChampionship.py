from ExperimentHandler import ChefsHatExperimentHandler

from Agents.agentList import  getAgent, AGENTTYPE
from KEF.PlotManager import plots

from Rewards import RewardOnlyWinning
import tensorflow as tf
from keras import backend as K
import numpy
import pandas as pd

from Adaptive_Agents import AIRL


import random

import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

def runModel():

    # #Reward function
    reward = RewardOnlyWinning.RewardOnlyWinning()

    # #Experimental parameters
    numberOfGroups = 8
    maximumScore = 15 # maximumScore to be reached
    experimentDescriptor = "TournamentExperiment" #Experiment name

    isLogging = False # create a .txt file with the experiment log
    isPlotting = False #Create plots of the experiment
    createDataset = True # Create a .pkl dataset of the experiemnt
    saveExperimentsIn = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/Tournament/Adapting/"

    #Groups definition

    availableAgents = [AGENTTYPE["DQL"], AGENTTYPE["A2C"], AGENTTYPE["PPO"], AGENTTYPE["LilDJ"], AGENTTYPE["RANDOM"]]

    # availableAgents = [AGENTTYPE["DQL"], AGENTTYPE["RANDOM"], AGENTTYPE["PPO"]]
    # availableAgents = [AGENTTYPE["DQL"], AGENTTYPE["RANDOM"]]

    groups = []

    #Plots
    plotsToGenerate = []

    # Setup all groups
    print ("---- CREATING GROUPS ----")
    agentNumber = 0
    for groupNumber in range(numberOfGroups):
        group = []

        for a in range(4):
            # shuffle the decks
            order = numpy.array(range(len(availableAgents)))
            index = numpy.array(range(len(availableAgents)))
            random.shuffle(order)
            random.shuffle(index)

            agentType = availableAgents[order[index[0]]]
            agentName = agentType+"_"+str(agentNumber)
            agent = getAgent(agentType,agentName,loadTrainedModel=True,trainable=True)
            group.append(agent)
            agentNumber +=1

        groups.append(group)


    #Separation of the brackets
    random.shuffle(groups)
    halfGroupSize = int(len(groups)/2)
    bracket1 = groups[0:halfGroupSize]
    bracket2 = groups[halfGroupSize:len(groups)]


    #Start of the tournament

    #function Play the game get winners

    def playGame(group, bracket, round):

        saveCurrentGame = saveExperimentsIn+"/Bracket_"+str(bracket+1)+"/Match_"+str(round)+"/"  # Directory where the experiment will be saved

        loadModel = [group[0][1], group[1][1], group[2] [1], group[3] [1]]

        playersAgents = [group[0] [0], group[1][ 0], group[2][ 0], group[3][ 0]]


        metrics = ChefsHatExperimentHandler.runExperiment(maximumScore=maximumScore, playersAgents=playersAgents,
                                                          experimentDescriptor=experimentDescriptor,
                                                          isLogging=isLogging,
                                                          isPlotting=isPlotting, createDataset=createDataset,
                                                          saveExperimentsIn=saveCurrentGame, loadModel=loadModel,
                                                          rewardFunction=reward, plots=plotsToGenerate)
        score = metrics[-2]
        winners = numpy.argpartition(score, -2)[-2:]
        # winner = numpy.argmax(score)
        # secondPLace = numpy.unique(score)[-2]

        return winners[1], winners[0]

    finalGroup = []
    for indexBracket, bracket in enumerate([bracket1,bracket2]): # for every bracket
        currentBracket = bracket
        newGroup = []
        currentRound = 1
        numberOfGroupsInThisRound = len(bracket)
        removedGroups = 0


        # print ("Bracket: " + str(indexBracket))
        #Initial groups
        while len(currentBracket) > 0:
            group = currentBracket[0].copy()
            first,second = playGame(group, indexBracket,currentRound)

            newGroup.append(group[first])
            newGroup.append(group[second])

            if len(newGroup) == 4:
                currentBracket.append(newGroup)
                newGroup = []

            del currentBracket[0]
            removedGroups += 1

            if removedGroups == numberOfGroupsInThisRound:
                currentRound +=currentRound
                removedGroups = 0
                numberOfGroupsInThisRound = numberOfGroupsInThisRound/2

        finalGroup.append(group[first])
        finalGroup.append(group[second])

    #Playing the final game!
    first, second = playGame(group, 3, 0)

    print ("Winner of the championship:" + str(first))

config = tf.ConfigProto()
config.gpu_options.allow_growth = True

sess = tf.Session(config=config)
# from keras import backend as K
K.set_session(sess)

with tf.device('/gpu:0'):
    runModel()