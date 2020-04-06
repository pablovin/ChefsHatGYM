from ExperimentHandler import ChefsHatExperimentHandler

from Agents import AgentRandom, AgentDQL, AgentA2C, AgentDDPG

from Rewards import RewardOnlyWinning,  RewardIROSPaper
import tensorflow as tf
from keras import backend as K

from KEF.PlotManager import  plotVictoriesTotal

import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"


def runModel():
    #Parameters for the game
    agent1 = AgentA2C.AgentA2C([False, 1.0]) #training agent
    agent2 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)
    agent3 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)
    agent4 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)

     # if training specific agents
    playersAgents = [agent1, agent2, agent3, agent4]

    reward = RewardOnlyWinning.RewardOnlyWinning()

    numRuns = 1 #Amount of runs
    numGames = 100# amount of games per run
    experimentDescriptor = "Testing_NewPlot_Stack"


    A2CActor = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/ICPR_Experiments/A2C/Random/1000/Player_4_Cards_11_games_1000TrainingAgents_['A2C', 'DUMMY_RANDOM', 'DUMMY_RANDOM', 'DUMMY_RANDOM']_Reward_OnlyWinning_Training_2020-03-27_14:14:16.796731/Model/actor_iteration_999_Player_0.hd5"
    A2CCritic = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/ICPR_Experiments/A2C/Random/1000/Player_4_Cards_11_games_1000TrainingAgents_['A2C', 'DUMMY_RANDOM', 'DUMMY_RANDOM', 'DUMMY_RANDOM']_Reward_OnlyWinning_Training_2020-03-27_14:14:16.796731/Model/critic_iteration_999_Player_0.hd5"

    loadModelAgent1 = [A2CActor, A2CCritic]#""#[actorModelDDPG,criticModelDDPG]#DQLModel#""# #"" #""#""#DQLModel#""#[actorModelDDPG,criticModelDDPG] ##""#[actorModelA2C,criticModelA2C] #[actorModelA2C,criticModelA2C] #DQLModel #[actorModelA2C,criticModelA2c] #[actorModelDDPG,criticModelDDPG]

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

    isPlotting = False #plot the experiment

    plotFrequency = 1 #plot the plots every X games

    createDataset = True # weather to save the dataset

    saveExperimentsIn = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/ICPR_Experiments/A2C/Random/1000/AllQValues" # Directory where the experiment will be saved

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

         # print ("Metrics:" + str(metrics))

    plotVictoriesTotal(winsP1, winsP2, winsP3, winsP4,numGames, experimentDescriptor, saveExperimentsIn)


config = tf.ConfigProto()
config.gpu_options.allow_growth = True

sess = tf.Session(config=config)
# from keras import backend as K
K.set_session(sess)

with tf.device('/gpu:0'):
    runModel()