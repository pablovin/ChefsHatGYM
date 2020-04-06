from ExperimentHandler import ChefsHatExperimentHandler

from Agents import  AgentRandom, AgentDQL, AgentA2C, AgentPPO

from Rewards import RewardOnlyWinning
import tensorflow as tf
from keras import backend as K
import numpy
from KEF.PlotManager import  plotVictoriesTotal

import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"


def runModel():
    #Parameters for the game
    agent1 = AgentPPO.AgentPPO([False, 1.0]) #training agent
    agent2 = AgentPPO.AgentPPO([False, 1.0])
    agent3 = AgentPPO.AgentPPO([False, 1.0])
    agent4 = AgentPPO.AgentPPO([False, 1.0])

     # if training specific agents
    playersAgents = [agent1, agent2, agent3, agent4]

    reward = RewardOnlyWinning.RewardOnlyWinning()

    numRuns = 10 #Amount of runs
    numGames = 100# amount of games per run

    experimentDescriptor = "Testing"

    A2cActor_1 = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/ICPR_Experiments/PPO/Self/1000/Player_4_Cards_11_games_1000TrainingAgents_['A2C', 'A2C', 'A2C', 'A2C']_Reward_OnlyWinning_Training_GameExperimentNumber_0_Training_Best_Agent_0Choice_ Scratch -  Scratch -  Second Best Agents - _2020-03-26_21:19:46.766347/Model/actor_iteration_999_Player_1.hd5"
    A2cCritic_1 = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/ICPR_Experiments/PPO/Self/1000/Player_4_Cards_11_games_1000TrainingAgents_['A2C', 'A2C', 'A2C', 'A2C']_Reward_OnlyWinning_Training_GameExperimentNumber_0_Training_Best_Agent_0Choice_ Scratch -  Scratch -  Second Best Agents - _2020-03-26_21:19:46.766347/Model/critic_iteration_999_Player_1.hd5"

    A2cActor_4 = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/ICPR_Experiments/PPO/Self/1000/Player_4_Cards_11_games_1000TrainingAgents_['A2C', 'A2C', 'A2C', 'A2C']_Reward_OnlyWinning_Training_GameExperimentNumber_4_Training_Best_Agent_0Choice_ Second Best Agents -  Best Agents -  Best Agents - _2020-03-26_21:42:00.824614/Model/actor_iteration_999_Player_3.hd5"
    A2cCritic_4 = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/ICPR_Experiments/PPO/Self/1000/Player_4_Cards_11_games_1000TrainingAgents_['A2C', 'A2C', 'A2C', 'A2C']_Reward_OnlyWinning_Training_GameExperimentNumber_4_Training_Best_Agent_0Choice_ Second Best Agents -  Best Agents -  Best Agents - _2020-03-26_21:42:00.824614/Model/critic_iteration_999_Player_3.hd5"

    A2cActor_9 = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/ICPR_Experiments/PPO/Self/1000/Player_4_Cards_11_games_1000TrainingAgents_['A2C', 'A2C', 'A2C', 'A2C']_Reward_OnlyWinning_Training_GameExperimentNumber_9_Training_Best_Agent_3Choice_ Scratch -  Scratch -  Scratch - _2020-03-26_22:27:02.430568/Model/actor_iteration_999_Player_3.hd5"
    A2cCritic_9 = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/ICPR_Experiments/PPO/Self/1000/Player_4_Cards_11_games_1000TrainingAgents_['A2C', 'A2C', 'A2C', 'A2C']_Reward_OnlyWinning_Training_GameExperimentNumber_9_Training_Best_Agent_3Choice_ Scratch -  Scratch -  Scratch - _2020-03-26_22:27:02.430568/Model/critic_iteration_999_Player_3.hd5"

    A2cActor_r = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/ICPR_Experiments/PPO/Random/1000/Player_4_Cards_11_games_1000TrainingAgents_['PPO', 'DUMMY_RANDOM', 'DUMMY_RANDOM', 'DUMMY_RANDOM']_Reward_OnlyWinning_Training_gamma_0.95_2020-03-27_14:45:07.604865/Model/actor_iteration_999_Player_0.hd5"
    A2cCritic_r = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/ICPR_Experiments/PPO/Random/1000/Player_4_Cards_11_games_1000TrainingAgents_['PPO', 'DUMMY_RANDOM', 'DUMMY_RANDOM', 'DUMMY_RANDOM']_Reward_OnlyWinning_Training_gamma_0.95_2020-03-27_14:45:07.604865/Model/critic_iteration_999_Player_0.hd5"


    loadModelAgent1 =[A2cActor_1, A2cCritic_1] #""#""#""  #DQLModel #[actorModelA2C,criticModelA2c] #[actorModelDDPG,criticModelDDPG]

    loadModelAgent2 =[A2cActor_4, A2cCritic_4]#""#""# ""#[actorModel,criticModel]

    loadModelAgent3 =[A2cActor_9, A2cCritic_9]#""#""# ""
    loadModelAgent4 =[A2cActor_r, A2cCritic_r]#""#DQLModelr#""#""# ""

    #
    # loadModel = [loadModelAgent1,loadModelAgent2, loadModelAgent3, loadModelAgent4] #indicate where the saved model is
    loadModel = [loadModelAgent1, loadModelAgent2, loadModelAgent3,
                 loadModelAgent4]  # indicate where the saved model is
    #
    # loadModel = "" #indicate where the saved model is

    # #Parameters for controling the experiment
    isLogging = False  # Logg the experiment

    isPlotting = True  # plot the experiment

    plotFrequency = 1000  # plot the plots every X games

    createDataset = True  # weather to save the dataset

    saveExperimentsIn = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/ICPR_Experiments/PPO/Self/1000/"  # Directory where the experiment will be saved

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