from ExperimentHandler import ChefsHatExperimentHandler

from Agents import  AgentRandom, AgentDQL, AgentA2C, AgentDDPG

from Rewards import RewardOnlyWinning, RewardOnlyWinning_PunishmentInvalid
import tensorflow as tf
from keras import backend as K
import numpy

import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"


def runModel():
    #Parameters for the game
    agent1 = AgentDQL.AgentDQL([True]) #training agent
    agent2 = AgentDQL.AgentDQL([True])
    agent3 = AgentDQL.AgentDQL([True])
    agent4 = AgentDQL.AgentDQL([True])

     # if training specific agents
    playersAgents = [agent1, agent2, agent3, agent4]

    reward = RewardOnlyWinning.RewardOnlyWinning()

    numExperiments = 10 # number of experiments. At the end of each experiment, we copy the best player and make them play against each other.
    numGames = 200# amount of training games

    experimentDescriptor = "Training_SelfPlay_"

    actorModelA2C = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/BaselineExperiments/Optmizing/A2C, DQL, DDPG/Player_4_Cards_11_games_500TrainAgents_['A2C', 'DUMMY_RANDOM', 'DUMMY_RANDOM', 'DUMMY_RANDOM']_Reward_OnlyWinning_TrainingHyperoptAgent_2020-03-17_09:43:50.235338/Model/actor_iteration_499.hd5"
    criticModelA2c = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/BaselineExperiments/Optmizing/A2C, DQL, DDPG/Player_4_Cards_11_games_500TrainAgents_['A2C', 'DUMMY_RANDOM', 'DUMMY_RANDOM', 'DUMMY_RANDOM']_Reward_OnlyWinning_TrainingHyperoptAgent_2020-03-17_09:43:50.235338/Model/critic_iteration_499.hd5"

    actorModelDDPG = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/BaselineExperiments/Optmizing/A2C, DQL, DDPG/Player_4_Cards_11_games_500TrainAgents_['DDPG', 'DUMMY_RANDOM', 'DUMMY_RANDOM', 'DUMMY_RANDOM']_Reward_OnlyWinning_TrainingMyAgent_2020-03-17_10:48:23.512129/Model/actor_iteration_499.hd5"
    criticModelDDPG = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/BaselineExperiments/Optmizing/A2C, DQL, DDPG/Player_4_Cards_11_games_500TrainAgents_['DDPG', 'DUMMY_RANDOM', 'DUMMY_RANDOM', 'DUMMY_RANDOM']_Reward_OnlyWinning_TrainingMyAgent_2020-03-17_10:48:23.512129/Model/critic_iteration_499.hd5"

    DQLModel = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/Gym_Experiments_SelfPlay/DQL_100x10/MostlyChoosingRandomAgents/Player_4_Cards_11_games_100TrainAgents_['DQL', 'DQL', 'DQL', 'DQL']_Reward_OnlyWinning_Training_SelfPlay__GameExperimentNumber_3_Best_Agent_1_2020-03-18_15:41:31.786142/Model/actor_iteration_99_Player_3.hd5"


    loadModelAgent1 =""#""  #DQLModel #[actorModelA2C,criticModelA2c] #[actorModelDDPG,criticModelDDPG]

    loadModelAgent2 =""# ""#[actorModel,criticModel]

    loadModelAgent3 =""# ""
    loadModelAgent4 =""# ""

    #
    # loadModel = [loadModelAgent1,loadModelAgent2, loadModelAgent3, loadModelAgent4] #indicate where the saved model is
    loadModel = [loadModelAgent1,loadModelAgent2, loadModelAgent3, loadModelAgent4] #indicate where the saved model is
    #
    # loadModel = "" #indicate where the saved model is

    # #Parameters for controling the experiment
    isLogging = False #Logg the experiment

    isPlotting = True #plot the experiment

    plotFrequency = 50 #plot the plots every X games

    createDataset = False # weather to save the dataset

    saveExperimentsIn = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/Gym_Experiments_SelfPlay/DQL_100x10/" # Directory where the experiment will be saved

    # #Initial Run
    # metrics = ChefsHatExperimentHandler.runExperiment(numGames=numGames, playersAgents=playersAgents,
    #                                                   experimentDescriptor=experimentDescriptor, isLogging=isLogging,
    #                                                   isPlotting=isPlotting, plotFrequency=plotFrequency,
    #                                                   createDataset=createDataset, saveExperimentsIn=saveExperimentsIn,
    #                                                   loadModel=loadModel, rewardFunction=reward)

    bestAgent = 0
    description = experimentDescriptor
    for i in range(numExperiments):

        # Train the best scored one
        agent1 = AgentDQL.AgentDQL([True])  # training agent
        agent2 = AgentDQL.AgentDQL([True])
        agent3 = AgentDQL.AgentDQL([True])
        agent4 = AgentDQL.AgentDQL([True])

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

        numGames = 200
        print("Best agent: " + str(bestAgent) + " - Loading:" + str(loadModel))
        # input("here")
        experimentDescriptor = description + "_GameExperimentNumber_" + str(i) + "_Best_Agent_" + str(bestAgent)
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
        agent1 = AgentDQL.AgentDQL([False])
        agent2 = AgentDQL.AgentDQL([False])
        agent3 = AgentDQL.AgentDQL([False])
        agent4 = AgentDQL.AgentDQL([False])
        playersAgents = [agent1, agent2, agent3, agent4]

        print ("Testing - loading: " + str(loadModel))
        # input("here")
        experimentDescriptor = description + "_GameExperimentNumber_" + str(i)+"_Test"

        numGames = 100
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
        bestWin = -5000
        for a in range(4):
            if wins[a] > bestWin:
                bestWin = wins[a]
                bestAgent = a

        loadModel = [loadModel[bestAgent], loadModel[bestAgent], loadModel[bestAgent], loadModel[bestAgent]]


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