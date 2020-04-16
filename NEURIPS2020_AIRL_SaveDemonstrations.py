from ExperimentHandler import ChefsHatExperimentHandler

from Agents import AgentRandom,AgentDQL

from Rewards import RewardOnlyWinning
import tensorflow as tf
from keras import backend as K

from IntrinsicAgent.Intrinsic import Intrinsic, CONFIDENCE_PHENOMENOLOGICAL, CONFIDENCE_PMODEL
from KEF.PlotManager import plots

import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

def runModel():


    """

    Collect Demonstrations from an expert

    """
    # Intrinsic plugins
    intrinsicWithMoodDQL = Intrinsic(selfConfidenceType=CONFIDENCE_PHENOMENOLOGICAL, isUsingSelfMood=True)

    # Plots
    plotsToGenerate = []

    # Parameters for the game
    agent1 = AgentDQL.AgentDQL([False, 1.0, "Expert"])  # training agent
    agent2 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)  # training agent
    agent3 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)
    agent4 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)

     # if training specific agents
    playersAgents = [agent1, agent2, agent3, agent4]

    reward = RewardOnlyWinning.RewardOnlyWinning()

    numGames = 1000# amount of training games
    experimentDescriptor = "ExpertCollection"


    DQLModel = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/TrainedModels/DQL_vsRandom/actor_iteration_999_Player_0.hd5"

    loadModelAgent1 = DQLModel# "" # ""#[actorModelDDPG,criticModelDDPG]#DQLModel#""# #"" #""#""#DQLModel#""#[actorModelDDPG,criticModelDDPG] ##""#[actorModelA2C,criticModelA2C] #[actorModelA2C,criticModelA2C] #DQLModel #[actorModelA2C,criticModelA2c] #[actorModelDDPG,criticModelDDPG]

    loadModelAgent2 = ""#""#DQLModel #"" #DQLModel

    loadModelAgent3 = ""# "" #[actorModelDDPG,criticModelDDPG]
    loadModelAgent4 = ""

    loadModel = [loadModelAgent1,loadModelAgent2, loadModelAgent3, loadModelAgent4] #indicate where the saved model is

    # #Parameters for controling the experiment
    isLogging = False #Logg the experiment

    isPlotting = False #plot the experiment

    plotFrequency = 1000 #plot the plots every X games

    createDataset = False # weather to save the dataset

    saveExperimentsIn = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/NEURIPS2020/AIRL/ExpertObs" # Directory where the experiment will be saved

    metrics = ChefsHatExperimentHandler.runExperiment(numGames=numGames, playersAgents=playersAgents,experimentDescriptor=experimentDescriptor,isLogging=isLogging,isPlotting=isPlotting,plotFrequency = plotFrequency, createDataset=createDataset,saveExperimentsIn=saveExperimentsIn, loadModel=loadModel, rewardFunction=reward, plots=plotsToGenerate)


    demonstrations = agent1.memory.sample_batch(agent1.memory.count)

    import numpy

    numpy.save(saveExperimentsIn+"/"+"Demonstrations_"+str(experimentDescriptor)+".npy", demonstrations)

config = tf.ConfigProto()
config.gpu_options.allow_growth = True

sess = tf.Session(config=config)
# from keras import backend as K
K.set_session(sess)

with tf.device('/gpu:0'):
    runModel()