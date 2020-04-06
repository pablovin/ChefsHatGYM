from ExperimentHandler import ChefsHatExperimentHandler

from Agents import  AgentRandom, AgentDQL, AgentA2C, AgentDDPG

from Rewards import RewardOnlyWinning
import tensorflow as tf
from keras import backend as K
import numpy

import random

import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"


def runModel():
    #Parameters for the game
    agent1 = AgentDQL.AgentDQL([True, 1.0]) #training agent
    agent2 = AgentDQL.AgentDQL([True, 1.0])
    agent3 = AgentDQL.AgentDQL([True, 1.0])
    agent4 = AgentDQL.AgentDQL([True, 1.0])

     # if training specific agents
    playersAgents = [agent1, agent2, agent3, agent4]

    reward = RewardOnlyWinning.RewardOnlyWinning()

    numExperiments = 50 # number of experiments. At the end of each experiment, we copy the best player and make them play against each other.
    numGames = 1000# amount of training games

    experimentDescriptor = "Training"


    loadModelAgent1 =""#""#""  #DQLModel #[actorModelA2C,criticModelA2c] #[actorModelDDPG,criticModelDDPG]

    loadModelAgent2 =""#""# ""#[actorModel,criticModel]

    loadModelAgent3 =""#""# ""
    loadModelAgent4 =""#""# ""

    #
    # loadModel = [loadModelAgent1,loadModelAgent2, loadModelAgent3, loadModelAgent4] #indicate where the saved model is
    loadModel = [loadModelAgent1,loadModelAgent2, loadModelAgent3, loadModelAgent4] #indicate where the saved model is
    #
    # loadModel = "" #indicate where the saved model is

    # #Parameters for controling the experiment
    isLogging = False #Logg the experiment

    isPlotting = True #plot the experiment

    plotFrequency = 1000 #plot the plots every X games

    createDataset = False # weather to save the dataset

    saveExperimentsIn = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/ICPR_Experiments/DQL/Self/1000x50/" # Directory where the experiment will be saved

    # #Initial Run
    # metrics = ChefsHatExperimentHandler.runExperiment(numGames=numGames, playersAgents=playersAgents,
    #                                                   experimentDescriptor=experimentDescriptor, isLogging=isLogging,
    #                                                   isPlotting=isPlotting, plotFrequency=plotFrequency,
    #                                                   createDataset=createDataset, saveExperimentsIn=saveExperimentsIn,
    #                                                   loadModel=loadModel, rewardFunction=reward)

    bestAgent = 0
    description = experimentDescriptor
    epsilon = 1.0

    bestAgentsList = []
    secondBestList = []
    lastBestAgent = ""

    for i in range(numExperiments):

        agents = []
        agentsChoice = ""
        for agentNumber in range(3):
            probNumber = numpy.random.rand()

            if probNumber <= 0.33: #Pull from the BestAgentList
                if len(bestAgentsList) == 0:
                    agents.append("")
                else:
                    random.shuffle(bestAgentsList)
                    agents.append(bestAgentsList[0])
                agentsChoice = agentsChoice + "BestAgents-"

            elif probNumber > 0.33 and probNumber <= 0.66: #Pull from the secondBestList
                if len(secondBestList) == 0:
                    agents.append("")
                else:
                    random.shuffle(secondBestList)
                    agents.append(secondBestList[0])
                agentsChoice = agentsChoice + "SecondBestAgents-"
            else: #start a new agent from the scratch
                agents.append("")
                agentsChoice = agentsChoice + "Scratch-"
        agents.append(lastBestAgent)

        loadModel = agents
        # Train the best scored one
        agent1 = AgentDQL.AgentDQL([True, epsilon])  # training agent
        agent2 = AgentDQL.AgentDQL([True, epsilon])
        agent3 = AgentDQL.AgentDQL([True, epsilon])
        agent4 = AgentDQL.AgentDQL([True, epsilon])
        # epsilon = epsilon * 0.7
        # if epsilon < 0.1:
        #     epsilon = 0.1
        # if training specific agents
        playersAgents = [agent1, agent2, agent3, agent4]

        # loadModelAgent1 = loadModel[0]  # DQLModel #[actorModelA2C,criticModelA2c] #[actorModelDDPG,criticModelDDPG]
        #
        # loadModelAgent2 = loadModel[1]  # [actorModel,criticModel]
        #
        # loadModelAgent3 = loadModel[2]
        # loadModelAgent4 = loadModel[3]
        #
        # loadModel = [loadModelAgent1, loadModelAgent2, loadModelAgent3, loadModelAgent4]

        numGames = 1000
        plotFrequency = 1000  # plot the plots every X games
        print ("Choices: "+ str(agentsChoice))
        print("Best agent: " + str(bestAgent) + " - Loading:" + str(loadModel))

        # input("here")
        # experimentDescriptor = description + "_GameExperimentNumber_" + str(i) + "_Best_Agent_" + str(bestAgent)
        experimentDescriptor = description + "_GameExperimentNumber_" + str(i) + "_Training_Best_Agent_" + str(bestAgent)+ "Choice_"+str(agentsChoice)
        metrics = ChefsHatExperimentHandler.runExperiment(numGames=numGames, playersAgents=playersAgents,
                                                          experimentDescriptor=experimentDescriptor,
                                                          isLogging=isLogging,
                                                          isPlotting=isPlotting, plotFrequency=plotFrequency,
                                                          createDataset=createDataset,
                                                          saveExperimentsIn=saveExperimentsIn,
                                                          loadModel=loadModel, rewardFunction=reward)


        # Evaluate them without training them

        # print("Train metrics:" + str(metrics))
        # Get Trained Agents
        p1 = metrics[2]
        p2 = metrics[3]
        p3 = metrics[4]
        p4 = metrics[5]

        loadModelAgent1 = p1[4]
        loadModelAgent2 = p2[4]
        loadModelAgent3 = p3[4]
        loadModelAgent4 = p4[4]

        loadModel = [loadModelAgent1, loadModelAgent2, loadModelAgent3, loadModelAgent4]

        #Initialize evaluation agents
        agent1 = AgentDQL.AgentDQL([False, 0.1])
        agent2 = AgentDQL.AgentDQL([False, 0.1])
        agent3 = AgentDQL.AgentDQL([False, 0.1])
        agent4 = AgentDQL.AgentDQL([False, 0,1])
        playersAgents = [agent1, agent2, agent3, agent4]

        print ("Testing - loading: " + str(loadModel))
        # input("here")
        experimentDescriptor = description + "_GameExperimentNumber_" + str(i)+"_Test"

        numGames = 100
        plotFrequency = 100  # plot the plots every X games
        metrics = ChefsHatExperimentHandler.runExperiment(numGames=numGames, playersAgents=playersAgents,
                                                          experimentDescriptor=experimentDescriptor,
                                                          isLogging=isLogging,
                                                          isPlotting=isPlotting, plotFrequency=plotFrequency,
                                                          createDataset=createDataset,
                                                          saveExperimentsIn=saveExperimentsIn,
                                                          loadModel=loadModel, rewardFunction=reward)


        # Player1 - agent
        p1 = metrics[2]
        p2 = metrics[3]
        p3 = metrics[4]
        p4 = metrics[5]

        wins = (numpy.average(p1[2]), numpy.average(p2[2]), numpy.average(p3[2]), numpy.average(p4[2])) #Reward
        # wins = (numpy.array(p1[0].sum(), p2[0], p3[0], p4[0]) # Wins

        bestAgent = 0
        secondBestAgent = 0
        bestWin = -5000
        secondBestWin = -5000
        for a in range(4):
            if wins[a] >= bestWin:
                bestWin = wins[a]
                bestAgent = a
            if wins[a] >= secondBestWin and wins[a]< bestWin:
                secondBestWin = wins[a]
                secondBestAgent = a


        bestAgentsList.append(loadModel[bestAgent])
        lastBestAgent = loadModel[bestAgent]
        secondBestList.append(loadModel[secondBestAgent])

        # loadModel = [loadModel[bestAgent], loadModel[bestAgent], loadModel[bestAgent], loadModel[bestAgent]]


        print ("Best Agent: " + str(bestAgent))
        print("Rewards: " + str(wins))
        # input("Here")

    print ("Metrics:" + str(metrics))


config = tf.ConfigProto()
config.gpu_options.allow_growth = True

sess = tf.Session(config=config)
# from keras import backend as K
K.set_session(sess)

with tf.device('/gpu:0'):
    runModel()