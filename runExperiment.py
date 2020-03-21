from ExperimentHandler import ChefsHatExperimentHandler

from Agents import  AgentRandom, AgentDQL, AgentA2C, AgentDDPG, AgentDQL_Trfl

from Rewards import RewardOnlyWinning, RewardOnlyWinning_PunishmentInvalid, RewardOnlyWinning_ShortRounds, RewardIROSPaper,RewardValidAction
import tensorflow as tf
from keras import backend as K

import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"


def runModel():
    #Parameters for the game
    agent1 = AgentA2C.AgentA2C([True, 1.0]) #training agent
    # agent1 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)
    agent2 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)
    agent3 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)
    agent4 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)

     # if training specific agents
    playersAgents = [agent1, agent2, agent3, agent4]

    reward = RewardOnlyWinning.RewardOnlyWinning()

    numGames = 300# amount of training games
    experimentDescriptor = "Test_DQLSelfPlay20"

    actorModelA2C = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/Gym_Experiments/Player_4_Cards_11_games_1000TrainAgents_['A2C', 'DUMMY_RANDOM', 'DUMMY_RANDOM', 'DUMMY_RANDOM']_Reward_OnlyWinning_A2CTraining_2020-03-17_20:01:40.860961/Model/actor_iteration_999_Player_0.hd5"
    criticModelA2C = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/Gym_Experiments/Player_4_Cards_11_games_1000TrainAgents_['A2C', 'DUMMY_RANDOM', 'DUMMY_RANDOM', 'DUMMY_RANDOM']_Reward_OnlyWinning_A2CTraining_2020-03-17_20:01:40.860961/Model/critic_iteration_999_Player_0.hd5"

    actorModelDDPG = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/Gym_Experiments/Player_4_Cards_11_games_1000TrainAgents_['DDPG', 'DUMMY_RANDOM', 'DUMMY_RANDOM', 'DUMMY_RANDOM']_Reward_OnlyWinning_Test_DQLSelfPlay20_2020-03-21_14:31:29.941388/Model/actor_iteration_999_Player_0.hd5"
    criticModelDDPG = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/Gym_Experiments/Player_4_Cards_11_games_1000TrainAgents_['DDPG', 'DUMMY_RANDOM', 'DUMMY_RANDOM', 'DUMMY_RANDOM']_Reward_OnlyWinning_Test_DQLSelfPlay20_2020-03-21_14:31:29.941388/Model/critic_iteration_999_Player_0.hd5"

    DQLModel = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/ICPR_Experiments/DQL/DQL_Vs_SelfPlay/Player_4_Cards_11_games_2000TrainAgents_['DQL', 'DQL', 'DQL', 'DQL']_Reward_OnlyWinning_Training_SelfPlay__GameExperimentNumber_17_Best_Agent_3_2020-03-21_10:19:50.794104/Model/actor_iteration_1799_Player_0.hd5"

    loadModelAgent1 = ""#[actorModelDDPG,criticModelDDPG]#DQLModel#""# #"" #""#""#DQLModel#""#[actorModelDDPG,criticModelDDPG] ##""#[actorModelA2C,criticModelA2C] #[actorModelA2C,criticModelA2C] #DQLModel #[actorModelA2C,criticModelA2c] #[actorModelDDPG,criticModelDDPG]

    loadModelAgent2 = ""#DQLModel #"" #DQLModel

    loadModelAgent3 = "" #[actorModelDDPG,criticModelDDPG]
    loadModelAgent4 = ""

    #
    # loadModel = [loadModelAgent1,loadModelAgent2, loadModelAgent3, loadModelAgent4] #indicate where the saved model is
    loadModel = [loadModelAgent1,loadModelAgent2, loadModelAgent3, loadModelAgent4] #indicate where the saved model is
    #
    # loadModel = "" #indicate where the saved model is

    # #Parameters for controling the experiment
    isLogging = False #Logg the experiment

    isPlotting = True #plot the experiment

    plotFrequency = 100 #plot the plots every X games

    createDataset = False # weather to save the dataset

    saveExperimentsIn = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/Gym_Experiments" # Directory where the experiment will be saved

    metrics = ChefsHatExperimentHandler.runExperiment(numGames=numGames, playersAgents=playersAgents,experimentDescriptor=experimentDescriptor,isLogging=isLogging,isPlotting=isPlotting,plotFrequency = plotFrequency, createDataset=createDataset,saveExperimentsIn=saveExperimentsIn, loadModel=loadModel, rewardFunction=reward)

    print ("Metrics:" + str(metrics))


config = tf.ConfigProto()
config.gpu_options.allow_growth = True

sess = tf.Session(config=config)
# from keras import backend as K
K.set_session(sess)

with tf.device('/gpu:0'):
    runModel()