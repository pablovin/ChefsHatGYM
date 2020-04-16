from ExperimentHandler import ChefsHatExperimentHandler

from Agents import AgentRandom, AgentDQL_Neurips, AgentDQL
from IRLAgents import AIRL

from Rewards import RewardOnlyWinning
import tensorflow as tf
from keras import backend as K
import numpy

from IntrinsicAgent.Intrinsic import Intrinsic, CONFIDENCE_PHENOMENOLOGICAL, CONFIDENCE_PMODEL
from KEF.PlotManager import plots

import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

def runModel():


    """Collect Demonstrations"""


    demonstrations = numpy.load("/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/NEURIPS2020/AIRL/ExpertObs/Demonstrations_ExpertCollection.npy", allow_pickle=True)

    """ RUN games and try to learn from the expert """


    # Plots
    plotsToGenerate = [plots["Experiment_MeanQValues"], plots["Experiment_QValues"], plots["Experiment_Losses"], plots["Experiment_Rounds"], plots["Experiment_Winners"], plots["Experiment_FinishingPosition"], plots["Experiment_SelfReward"], plots["Experiment_Reward"]]

    # Parameters for the game
    agent1 = AIRL.AgentAIRL([True, 1.0, "AIRL",None,demonstrations])  # training agent
    # agent2 = AgentDQL.AgentDQL([False, 1.0, "DQL", None])  # training agent
    agent2 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)
    agent3 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)
    agent4 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)

     # if training specific agents
    playersAgents = [agent1, agent2, agent3, agent4]

    reward = RewardOnlyWinning.RewardOnlyWinning()

    numGames = 5000# amount of training games
    experimentDescriptor = "Train_NegativeReward_notInverted"


    DQLModel = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/TrainedModels/DQL_vsRandom/actor_iteration_999_Player_0.hd5"

    loadModelAgent1 = ""# "" # ""#[actorModelDDPG,criticModelDDPG]#DQLModel#""# #"" #""#""#DQLModel#""#[actorModelDDPG,criticModelDDPG] ##""#[actorModelA2C,criticModelA2C] #[actorModelA2C,criticModelA2C] #DQLModel #[actorModelA2C,criticModelA2c] #[actorModelDDPG,criticModelDDPG]

    loadModelAgent2 = DQLModel#""#""#DQLModel #"" #DQLModel

    loadModelAgent3 = ""# "" #[actorModelDDPG,criticModelDDPG]
    loadModelAgent4 = ""

    loadModel = [loadModelAgent1,loadModelAgent2, loadModelAgent3, loadModelAgent4] #indicate where the saved model is

    # #Parameters for controling the experiment
    isLogging = False #Logg the experiment

    isPlotting = True #plot the experiment

    plotFrequency = 5000 #plot the plots every X games

    createDataset = False # weather to save the dataset

    saveExperimentsIn = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/NEURIPS2020/AIRL/Training" # Directory where the experiment will be saved

    metrics = ChefsHatExperimentHandler.runExperiment(numGames=numGames, playersAgents=playersAgents,experimentDescriptor=experimentDescriptor,isLogging=isLogging,isPlotting=isPlotting,plotFrequency = plotFrequency, createDataset=createDataset,saveExperimentsIn=saveExperimentsIn, loadModel=loadModel, rewardFunction=reward, plots=plotsToGenerate)




config = tf.ConfigProto()
config.gpu_options.allow_growth = True

sess = tf.Session(config=config)
# from keras import backend as K
K.set_session(sess)

with tf.device('/gpu:0'):
    runModel()