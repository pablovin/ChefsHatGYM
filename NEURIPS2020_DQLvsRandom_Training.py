from ExperimentHandler import ChefsHatExperimentHandler

from Agents import AgentRandom, AgentDQL_Neurips

from Rewards import RewardOnlyWinning, RewardOnlyWinning_ZeroSum
import tensorflow as tf
from keras import backend as K

from IntrinsicAgent.Intrinsic import Intrinsic, CONFIDENCE_PHENOMENOLOGICAL, CONFIDENCE_PMODEL
from KEF.PlotManager import plots

import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

def runModel():

    # Intrinsic plugins
    intrinsicWithMoodDQL = Intrinsic(selfConfidenceType=CONFIDENCE_PHENOMENOLOGICAL, isUsingSelfMood=True)

    # Plots
    plotsToGenerate = [plots["Experiment_Winners"], plots["Experiment_Rounds"], plots["Experiment_Losses"], plots["Experiment_QValues"], plots["Experiment_MeanQValues"]]

    # Parameters for the game
    agent1 = AgentDQL_Neurips.AgentDQL([True, 1.0, "DQL"])  # training agent
    agent2 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)  # training agent
    agent3 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)  # training agent
    agent4 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)

     # if training specific agents
    playersAgents = [agent1, agent2, agent3, agent4]

    reward = RewardOnlyWinning_ZeroSum.RewardOnlyWinning_ZeroSum()

    numGames = 1000# amount of training games
    experimentDescriptor = "ZeroSum"


    DQLModel = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/ICPR_Experiments/DQL/Player_4_Cards_11_games_3000TrainingAgents_['DQL', 'DUMMY_RANDOM', 'DUMMY_RANDOM', 'DUMMY_RANDOM']_Reward_OnlyWinning_Training_2020-03-25_18:15:32.076987/Model/actor_iteration_2999_Player_0.hd5"

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

    plotFrequency = 1000 #plot the plots every X games

    createDataset = True # weather to save the dataset

    saveExperimentsIn = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/NEURIPS2020/DQL/Dueling/" # Directory where the experiment will be saved

    metrics = ChefsHatExperimentHandler.runExperiment(numGames=numGames, playersAgents=playersAgents,experimentDescriptor=experimentDescriptor,isLogging=isLogging,isPlotting=isPlotting,plotFrequency = plotFrequency, createDataset=createDataset,saveExperimentsIn=saveExperimentsIn, loadModel=loadModel, rewardFunction=reward, plots=plotsToGenerate)
    #
    # print ("Metrics:" + str(metrics))


config = tf.ConfigProto()
config.gpu_options.allow_growth = True

sess = tf.Session(config=config)
# from keras import backend as K
K.set_session(sess)

with tf.device('/gpu:0'):
    runModel()