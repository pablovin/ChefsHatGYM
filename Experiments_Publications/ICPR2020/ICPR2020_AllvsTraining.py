from ExperimentHandler import ChefsHatExperimentHandler

from Agents import  AgentRandom, AgentDQL, AgentA2C, AgentPPO

from Rewards import RewardOnlyWinning
import tensorflow as tf
from keras import backend as K
import numpy

import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"


def runModel():
    #Parameters for the game
    agent1 = AgentDQL.AgentDQL([True, 1.0]) #training agent
    agent2 = AgentA2C.AgentA2C([True, 1.0])
    agent3 = AgentPPO.AgentPPO([True, 1.0])
    agent4 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)

     # if training specific agents
    playersAgents = [agent1, agent2, agent3, agent4]

    reward = RewardOnlyWinning.RewardOnlyWinning()

    numGames = 1000# amount of training games

    experimentDescriptor = "Training"

    DQLModel = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/ICPR_Experiments/DQL/Self/1000/Player_4_Cards_11_games_1000TrainingAgents_['DQL', 'DQL', 'DQL', 'DQL']_Reward_OnlyWinning_Training_GameExperimentNumber_0_Training_Best_Agent_0_2020-03-26_17:26:18.198600/Model/actor_iteration_999_Player_2.hd5"

    A2cActor = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/ICPR_Experiments/A2C/Self/1000/Player_4_Cards_11_games_1000TrainingAgents_['A2C', 'A2C', 'A2C', 'A2C']_Reward_OnlyWinning_Training_GameExperimentNumber_0_Training_Best_Agent_0Choice_ Scratch -  Second Best -  Best - _2020-03-26_19:11:39.863435/Model/actor_iteration_999_Player_0.hd5"
    A2cCritic = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/ICPR_Experiments/A2C/Self/1000/Player_4_Cards_11_games_1000TrainingAgents_['A2C', 'A2C', 'A2C', 'A2C']_Reward_OnlyWinning_Training_GameExperimentNumber_0_Training_Best_Agent_0Choice_ Scratch -  Second Best -  Best - _2020-03-26_19:11:39.863435/Model/critic_iteration_999_Player_0.hd5"

    PPOActor = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/ICPR_Experiments/PPO/Self/1000/Player_4_Cards_11_games_1000TrainingAgents_['A2C', 'A2C', 'A2C', 'A2C']_Reward_OnlyWinning_Training_GameExperimentNumber_9_Training_Best_Agent_3Choice_ Scratch -  Scratch -  Scratch - _2020-03-26_22:27:02.430568/Model/actor_iteration_999_Player_3.hd5"
    PPOCritic = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/ICPR_Experiments/PPO/Self/1000/Player_4_Cards_11_games_1000TrainingAgents_['A2C', 'A2C', 'A2C', 'A2C']_Reward_OnlyWinning_Training_GameExperimentNumber_9_Training_Best_Agent_3Choice_ Scratch -  Scratch -  Scratch - _2020-03-26_22:27:02.430568/Model/critic_iteration_999_Player_3.hd5"


    loadModelAgent1 =DQLModel #""#""#""  #DQLModel #[actorModelA2C,criticModelA2c] #[actorModelDDPG,criticModelDDPG]

    loadModelAgent2 =[A2cActor, A2cCritic]#""#""# ""#[actorModel,criticModel]

    loadModelAgent3 =[PPOActor, PPOCritic]#""#""# ""
    loadModelAgent4 =""#""#DQLModelr#""#""# ""

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

    saveExperimentsIn = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/ICPR_Experiments/All/QValuePlot"  # Directory where the experiment will be saved

    metrics = ChefsHatExperimentHandler.runExperiment(numGames=numGames, playersAgents=playersAgents,
                                                      experimentDescriptor=experimentDescriptor, isLogging=isLogging,
                                                      isPlotting=isPlotting, plotFrequency=plotFrequency,
                                                      createDataset=createDataset, saveExperimentsIn=saveExperimentsIn,
                                                      loadModel=loadModel, rewardFunction=reward)

    print("Metrics:" + str(metrics))


config = tf.ConfigProto()
config.gpu_options.allow_growth = True

sess = tf.Session(config=config)
# from keras import backend as K
K.set_session(sess)

with tf.device('/cpu:0'):
    runModel()