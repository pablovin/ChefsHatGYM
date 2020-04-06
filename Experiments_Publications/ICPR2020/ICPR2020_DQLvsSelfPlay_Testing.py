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
    agent1 = AgentDQL.AgentDQL([False, 1.0]) #training agent
    agent2 = AgentDQL.AgentDQL([False, 1.0])
    agent3 = AgentDQL.AgentDQL([False, 1.0])
    agent4 = AgentDQL.AgentDQL([False, 1.0])

     # if training specific agents
    playersAgents = [agent1, agent2, agent3, agent4]

    reward = RewardOnlyWinning.RewardOnlyWinning()

    numRuns = 10 #Amount of runs
    numGames = 100# amount of games per run

    experimentDescriptor = "Testing_50x1000"

    # DQLModel1 = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/ICPR_Experiments/DQL/Self/Player_4_Cards_11_games_1000TrainingAgents_['DQL', 'DQL', 'DQL', 'DQL']_Reward_OnlyWinning_Training_GameExperimentNumber_1_Training_Best_Agent_2_2020-03-26_17:33:51.517296/Model/actor_iteration_999_Player_1.hd5"
    # DQLModel2 = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/ICPR_Experiments/DQL/Self/Player_4_Cards_11_games_1000TrainingAgents_['DQL', 'DQL', 'DQL', 'DQL']_Reward_OnlyWinning_Training_GameExperimentNumber_2_Training_Best_Agent_1_2020-03-26_17:42:24.306637/Model/actor_iteration_999_Player_1.hd5"
    # DQLModel3 = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/ICPR_Experiments/DQL/Self/Old/Player_4_Cards_11_games_1000TrainingAgents_['DQL', 'DQL', 'DQL', 'DQL']_Reward_OnlyWinning_Training_GameExperimentNumber_3_Training_Best_Agent_2_2020-03-26_00:13:55.479460/Model/actor_iteration_999_Player_1.hd5"
    # DQLModelr = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/ICPR_Experiments/DQL/Random/Player_4_Cards_11_games_3000TrainingAgents_['DQL', 'DUMMY_RANDOM', 'DUMMY_RANDOM', 'DUMMY_RANDOM']_Reward_OnlyWinning_Training_2020-03-25_18:15:32.076987/Model/actor_iteration_2999_Player_0.hd5"
    #
    #
    #
    # DQLModel0 = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/ICPR_Experiments/DQL/Self/1000/Player_4_Cards_11_games_1000TrainingAgents_['DQL', 'DQL', 'DQL', 'DQL']_Reward_OnlyWinning_Training_GameExperimentNumber_0_Training_Best_Agent_0_2020-03-26_17:26:18.198600/Model/actor_iteration_999_Player_2.hd5"
    # DQLModel4 = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/ICPR_Experiments/DQL/Self/1000/Player_4_Cards_11_games_1000TrainingAgents_['DQL', 'DQL', 'DQL', 'DQL']_Reward_OnlyWinning_Training_GameExperimentNumber_4_Training_Best_Agent_3_2020-03-26_18:03:32.220659/Model/actor_iteration_999_Player_2.hd5"
    # DQLModel9 = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/ICPR_Experiments/DQL/Self/Player_4_Cards_11_games_3000TrainingAgents_['DQL', 'DQL', 'DQL', 'DQL']_Reward_OnlyWinning_Training_GameExperimentNumber_0_Training_Best_Agent_0Choice_ Scratch -  Second Best Agents -  Second Best Agents - _2020-03-26_20:28:12.574082/Model/actor_iteration_2999_Player_0.hd5"
    # DQLModelr = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/ICPR_Experiments/DQL/Random/Player_4_Cards_11_games_3000TrainingAgents_['DQL', 'DUMMY_RANDOM', 'DUMMY_RANDOM', 'DUMMY_RANDOM']_Reward_OnlyWinning_Training_2020-03-25_18:15:32.076987/Model/actor_iteration_2999_Player_0.hd5"


    DQLModel0 = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/ICPR_Experiments/DQL/Self/1000x50/Player_4_Cards_11_games_1000TrainingAgents_['DQL', 'DQL', 'DQL', 'DQL']_Reward_OnlyWinning_Training_GameExperimentNumber_0_Training_Best_Agent_0Choice_SecondBestAgents-SecondBestAgents-Scratch-_2020-03-27_01:55:16.105188/Model/actor_iteration_999_Player_2.hd5"
    DQLModel4 = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/ICPR_Experiments/DQL/Self/1000x50/Player_4_Cards_11_games_1000TrainingAgents_['DQL', 'DQL', 'DQL', 'DQL']_Reward_OnlyWinning_Training_GameExperimentNumber_15_Training_Best_Agent_2Choice_SecondBestAgents-BestAgents-BestAgents-_2020-03-27_04:50:05.205901/Model/actor_iteration_999_Player_2.hd5"
    DQLModel9 = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/ICPR_Experiments/DQL/Self/1000x50/Player_4_Cards_11_games_1000TrainingAgents_['DQL', 'DQL', 'DQL', 'DQL']_Reward_OnlyWinning_Training_GameExperimentNumber_30_Training_Best_Agent_0Choice_BestAgents-BestAgents-BestAgents-_2020-03-27_12:18:40.723555/Model/actor_iteration_999_Player_2.hd5"
    DQLModelr = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/ICPR_Experiments/DQL/Random/1000/Player_4_Cards_11_games_1000TrainingAgents_['DQL', 'DUMMY_RANDOM', 'DUMMY_RANDOM', 'DUMMY_RANDOM']_Reward_OnlyWinning_Training_2020-03-27_14:26:46.054899/Model/actor_iteration_999_Player_0.hd5"

    loadModelAgent1 =DQLModel0 #""#""#""  #DQLModel #[actorModelA2C,criticModelA2c] #[actorModelDDPG,criticModelDDPG]

    loadModelAgent2 =DQLModel4#""#""# ""#[actorModel,criticModel]

    loadModelAgent3 =DQLModel9#""#""# ""
    loadModelAgent4 =DQLModelr#""#DQLModelr#""#""# ""

    #
    # loadModel = [loadModelAgent1,loadModelAgent2, loadModelAgent3, loadModelAgent4] #indicate where the saved model is
    loadModel = [loadModelAgent3, loadModelAgent4, loadModelAgent1,
                 loadModelAgent2]  # indicate where the saved model is
    #
    # loadModel = "" #indicate where the saved model is

    # #Parameters for controling the experiment
    isLogging = False  # Logg the experiment

    isPlotting = True  # plot the experiment

    plotFrequency = 1000  # plot the plots every X games

    createDataset = True  # weather to save the dataset

    saveExperimentsIn = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/ICPR_Experiments/DQL/Self/1000/"  # Directory where the experiment will be saved

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