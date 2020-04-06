from ExperimentHandler import ChefsHatExperimentHandler

from Agents import  AgentRandom, AgentDQL, AgentA2C, AgentDDPG

from Rewards import RewardOnlyWinning
import tensorflow as tf
from keras import backend as K
import numpy

from KEF.PlotManager import  plotVictoriesTotal

import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"


def runModel():
    #Parameters for the game
    agent1 = AgentA2C.AgentA2C([False, 1.0]) #training agent
    agent2 = AgentA2C.AgentA2C([False, 1.0])
    agent3 = AgentA2C.AgentA2C([False, 1.0])
    agent4 = AgentA2C.AgentA2C([False, 1.0])

     # if training specific agents
    playersAgents = [agent1, agent2, agent3, agent4]

    reward = RewardOnlyWinning.RewardOnlyWinning()

    numRuns = 10 #Amount of runs
    numGames = 100# amount of games per run

    experimentDescriptor = "Testing_NewPlot"

    A2cActor_1 = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/ICPR_Experiments/A2C/Self/1000/Player_4_Cards_11_games_1000TrainingAgents_['A2C', 'A2C', 'A2C', 'A2C']_Reward_OnlyWinning_Training_GameExperimentNumber_0_Training_Best_Agent_0Choice_ Scratch -  Second Best -  Best - _2020-03-26_19:11:39.863435/Model/actor_iteration_999_Player_0.hd5"
    A2cCritic_1 = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/ICPR_Experiments/A2C/Self/1000/Player_4_Cards_11_games_1000TrainingAgents_['A2C', 'A2C', 'A2C', 'A2C']_Reward_OnlyWinning_Training_GameExperimentNumber_0_Training_Best_Agent_0Choice_ Scratch -  Second Best -  Best - _2020-03-26_19:11:39.863435/Model/critic_iteration_999_Player_0.hd5"

    A2cActor_4 = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/ICPR_Experiments/A2C/Self/1000/Player_4_Cards_11_games_1000TrainingAgents_['A2C', 'A2C', 'A2C', 'A2C']_Reward_OnlyWinning_Training_GameExperimentNumber_4_Training_Best_Agent_1Choice_ Best -  Scratch -  Scratch - _2020-03-26_19:27:58.464895/Model/actor_iteration_999_Player_0.hd5"
    A2cCritic_4 = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/ICPR_Experiments/A2C/Self/1000/Player_4_Cards_11_games_1000TrainingAgents_['A2C', 'A2C', 'A2C', 'A2C']_Reward_OnlyWinning_Training_GameExperimentNumber_4_Training_Best_Agent_1Choice_ Best -  Scratch -  Scratch - _2020-03-26_19:27:58.464895/Model/critic_iteration_999_Player_0.hd5"

    A2cActor_9 = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/ICPR_Experiments/DQL/Self/1000/Player_4_Cards_11_games_1000TrainingAgents_['DQL', 'DQL', 'DQL', 'DQL']_Reward_OnlyWinning_Training_GameExperimentNumber_1_Training_Best_Agent_2_2020-03-26_17:33:51.517296/Model/actor_iteration_999_Player_1.hd5"
    A2cCritic_9 = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/ICPR_Experiments/DQL/Self/1000/Player_4_Cards_11_games_1000TrainingAgents_['DQL', 'DQL', 'DQL', 'DQL']_Reward_OnlyWinning_Training_GameExperimentNumber_2_Training_Best_Agent_1_2020-03-26_17:42:24.306637/Model/actor_iteration_999_Player_1.hd5"

    A2cActor_r = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/ICPR_Experiments/A2C/Random/1000/Player_4_Cards_11_games_1000TrainingAgents_['A2C', 'DUMMY_RANDOM', 'DUMMY_RANDOM', 'DUMMY_RANDOM']_Reward_OnlyWinning_Training_2020-03-27_14:14:16.796731/Model/actor_iteration_999_Player_0.hd5"
    A2cCritic_r = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/ICPR_Experiments/A2C/Random/1000/Player_4_Cards_11_games_1000TrainingAgents_['A2C', 'DUMMY_RANDOM', 'DUMMY_RANDOM', 'DUMMY_RANDOM']_Reward_OnlyWinning_Training_2020-03-27_14:14:16.796731/Model/critic_iteration_999_Player_0.hd5"


    loadModelAgent1 =[A2cActor_1, A2cCritic_1] #""#""#""  #DQLModel #[actorModelA2C,criticModelA2c] #[actorModelDDPG,criticModelDDPG]

    loadModelAgent2 =[A2cActor_4, A2cCritic_4]#""#""# ""#[actorModel,criticModel]

    loadModelAgent3 =[A2cActor_9, A2cCritic_9]#""#""# ""
    loadModelAgent4 =[A2cActor_r, A2cCritic_r]#""#DQLModelr#""#""# ""

    #
    loadModel = [loadModelAgent4,loadModelAgent3, loadModelAgent1, loadModelAgent2] #indicate where the saved model is
    # loadModel = [loadModelAgent3, loadModelAgent2, loadModelAgent1,
    #              loadModelAgent4]  # indicate where the saved model is
    #
    # loadModel = "" #indicate where the saved model is

    # #Parameters for controling the experiment
    isLogging = False  # Logg the experiment

    isPlotting = True  # plot the experiment

    plotFrequency = 1000  # plot the plots every X games

    createDataset = True  # weather to save the dataset

    saveExperimentsIn = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/ICPR_Experiments/A2C/Self/1000/"  # Directory where the experiment will be saved

    winsP1 = []
    winsP2 = []
    winsP3 = []
    winsP4 = []
    for i in range(numRuns):
         metrics = ChefsHatExperimentHandler.runExperiment(numGames=numGames, playersAgents=playersAgents,experimentDescriptor=experimentDescriptor,isLogging=isLogging,isPlotting=isPlotting,plotFrequency = plotFrequency, createDataset=createDataset,saveExperimentsIn=saveExperimentsIn, loadModel=loadModel, rewardFunction=reward)

         # Player1 - agent
         p1 = metrics[2]
         p2 = metrics[3]
         p3 = metrics[4]
         p4 = metrics[5]

         winsP1.append(p1[0])
         winsP2.append(p2[0])
         winsP3.append(p3[0])
         winsP4.append(p4[0])

         print ("Metrics:" + str(metrics))

    plotVictoriesTotal(winsP1, winsP2, winsP3, winsP4,numGames, experimentDescriptor, saveExperimentsIn)




config = tf.ConfigProto()
config.gpu_options.allow_growth = True

sess = tf.Session(config=config)
# from keras import backend as K
K.set_session(sess)

with tf.device('/cpu:0'):
    runModel()