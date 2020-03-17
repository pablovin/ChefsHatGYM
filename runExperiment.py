from ExperimentHandler import ChefsHatExperimentHandler

from Agents import  AgentRandom, AgentDQL, AgentA2C, AgentDDPG

from Rewards import RewardOnlyWinning, RewardOnlyWinning_PunishmentInvalid
import tensorflow as tf
from keras import backend as K

import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"


def runModel():
    #Parameters for the game
    agent1 = AgentDDPG.AgentDDPG([True]) #training agent
    agent2 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)
    agent3 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)
    agent4 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)

     # if training specific agents
    playersAgents = [agent1, agent2, agent3, agent4]

    reward = RewardOnlyWinning.RewardOnlyWinning()

    numGames = 100# amount of training games
    experimentDescriptor = "Training_Penalty_Agent"

    actorModelA2C = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/BaselineExperiments/Optmizing/A2C/Player_4_Cards_11_games_500TrainAgents_['A2C', 'DUMMY_RANDOM', 'DUMMY_RANDOM', 'DUMMY_RANDOM']_Reward_OnlyWinning_TrainingHyperoptAgent_2020-03-17_09:43:50.235338/Model/actor_iteration_499.hd5"
    criticModelA2c ="/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/BaselineExperiments/Optmizing/A2C/Player_4_Cards_11_games_500TrainAgents_['A2C', 'DUMMY_RANDOM', 'DUMMY_RANDOM', 'DUMMY_RANDOM']_Reward_OnlyWinning_TrainingHyperoptAgent_2020-03-17_09:43:50.235338/Model/critic_iteration_499.hd5"

    actorModelDDPG = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/BaselineExperiments/Optmizing/A2C, DQL, DDPG/Player_4_Cards_11_games_500TrainAgents_['DDPG', 'DUMMY_RANDOM', 'DUMMY_RANDOM', 'DUMMY_RANDOM']_Reward_OnlyWinning_TrainingMyAgent_2020-03-17_10:48:23.512129/Model/actor_iteration_499.hd5"
    criticModelDDPG = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/BaselineExperiments/Optmizing/A2C, DQL, DDPG/Player_4_Cards_11_games_500TrainAgents_['DDPG', 'DUMMY_RANDOM', 'DUMMY_RANDOM', 'DUMMY_RANDOM']_Reward_OnlyWinning_TrainingMyAgent_2020-03-17_10:48:23.512129/Model/critic_iteration_499.hd5"

    DQLModel = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/BaselineExperiments/Optmizing/A2C, DQL, DDPG/Player_4_Cards_11_games_500TrainAgents_['DQL', 'DUMMY_RANDOM', 'DUMMY_RANDOM', 'DUMMY_RANDOM']_Reward_OnlyWinning_TrainingHyperoptAgent_2020-03-17_10:07:02.985994/Model/actor_iteration_499.hd5"

    loadModelAgent1 = "" #DQLModel #[actorModelA2C,criticModelA2c] #[actorModelDDPG,criticModelDDPG]

    loadModelAgent2 = "" #[actorModel,criticModel]

    loadModelAgent3 = ""
    loadModelAgent4 = ""

    #
    # loadModel = [loadModelAgent1,loadModelAgent2, loadModelAgent3, loadModelAgent4] #indicate where the saved model is
    loadModel = [loadModelAgent1,loadModelAgent2, loadModelAgent3, loadModelAgent4] #indicate where the saved model is
    #
    # loadModel = "" #indicate where the saved model is

    # #Parameters for controling the experiment
    isLogging = False #Logg the experiment

    isPlotting = True #plot the experiment

    plotFrequency = 10 #plot the plots every X games

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