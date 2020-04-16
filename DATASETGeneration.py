from ExperimentHandler import ChefsHatExperimentHandler

from Agents import AgentRandom, AgentDQL, AgentA2C, AgentPPO

from Rewards import RewardOnlyWinning,  RewardIROSPaper
import tensorflow as tf
from keras import backend as K
from IRLAgents import AIRL

import numpy
from IntrinsicAgent.Intrinsic import Intrinsic, CONFIDENCE_PHENOMENOLOGICAL, CONFIDENCE_PMODEL

from KEF.PlotManager import plots
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

def runModel():

    #Intrinsic PModel
    pModelDQL = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/EPIROB_Experiments/DQL/Pmodel/Player_4_Cards_11_games_1000TrainingAgents_['DQL_I', 'DUMMY_RANDOM', 'DUMMY_RANDOM', 'DUMMY_RANDOM']_Reward_OnlyWinning_Training_PModel_2020-04-02_15:38:21.102815/Model/PModel_iteration_999_Player_0.hd5"

    #Intrinsic plugins
    intrinsicWithMoodDQL = Intrinsic(selfConfidenceType=CONFIDENCE_PHENOMENOLOGICAL, isUsingSelfMood=True,isUsingOponentMood=True)
    intrinsicWithMoodA2C = Intrinsic(selfConfidenceType=CONFIDENCE_PHENOMENOLOGICAL, isUsingSelfMood=True,isUsingOponentMood=True)
    intrinsicWithMoodPPO = Intrinsic(selfConfidenceType=CONFIDENCE_PHENOMENOLOGICAL, isUsingSelfMood=True,isUsingOponentMood=True)
    intrinsicWithMoodPPO2 = Intrinsic(selfConfidenceType=CONFIDENCE_PHENOMENOLOGICAL, isUsingSelfMood=True,isUsingOponentMood=True)

    demonstrations = numpy.load(
        "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/NEURIPS2020/AIRL/ExpertObs/Demonstrations_ExpertCollection.npy",
        allow_pickle=True)

    # intrinsicWithMoodDQLPmodel = Intrinsic(selfConfidenceType=CONFIDENCE_PMODEL, isUsingSelfMood=True, loadPModel=pModelDQL)
    # intrinsicWithMoodDQLPmodel2 = Intrinsic(selfConfidenceType=CONFIDENCE_PMODEL, isUsingSelfMood=True, loadPModel=pModelDQL)
    # intrinsicWithMoodPPO = Intrinsic(selfConfidenceType=CONFIDENCE_PHENOMENOLOGICAL, isUsingSelfMood=True)

    #Plots
    # plotsToGenerate = [plots["Experiment_Rounds"], plots["Experiment_FinishingPosition"], plots["Experiment_ActionsBehavior"],
    #                plots["Experiment_Reward"], plots["Experiment_QValues"], plots["Experiment_Mood"], plots["Experiment_MoodNeurons"],
    #                plots["Experiment_SelfProbabilitySuccess"]]
    plotsToGenerate = []

    #Parameters for the game
    agent1 = AgentDQL.AgentDQL([False, 1.0, "DQL", intrinsicWithMoodDQL]) #training agent
    agent2 = AgentPPO.AgentPPO([False, 1.0, "PPO", intrinsicWithMoodA2C]) #training agent
    # agent3= AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)  # training agent
    # agent3 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)  # training agent
    # agent4 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)  # training agent
    agent3 = AgentA2C.AgentA2C([False, 1.0, "A2C", intrinsicWithMoodPPO])  # training agent
    agent4 = AIRL.AgentAIRL([False, 1.0, "AIRL", intrinsicWithMoodPPO2, demonstrations])  # training agent
    # agent4 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)  # training agent
    # agent2 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)
    # agent3 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)
    # agent4 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)
    # agent2 = AgentA2C.AgentA2C([False, 1.0, "I", intrinsicWithMoodA2C]) #training agent
    # agent3 = AgentPPO.AgentPPO([False, 1.0, "I", intrinsicWithMoodPPO]) #training agent
    # agent4 = AgentDQL.AgentDQL([False, 1.0, "I", intrinsicWithMoodDQL])  # training agent
    # agent4 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)

     # if training specific agents
    playersAgents = [agent1, agent2, agent3, agent4]

    reward = RewardOnlyWinning.RewardOnlyWinning()

    numGames = 5# amount of training games
    experimentDescriptor = "Test10"

    DQLModel = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/TrainedModels/DQL_vsEveryone/actor_iteration_999_Player_0.hd5"

    A2cActor = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/TrainedModels/A2C_vsEveryone/actor_iteration_999_Player_1.hd5"
    A2cCritic = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/TrainedModels/A2C_vsEveryone/critic_iteration_999_Player_1.hd5"

    PPOActor = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/TrainedModels/PPO_vsEveryone/actor_iteration_999_Player_2.hd5"
    PPOCritic = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/TrainedModels/PPO_vsEveryone/critic_iteration_999_Player_2.hd5"

    AIRLModel = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/NEURIPS2020/AIRL/Training/Player_4_Cards_11_games_5000TrainingAgents_['DQL_AIRL', 'DUMMY_RANDOM', 'DUMMY_RANDOM', 'DUMMY_RANDOM']_Reward_OnlyWinning_Train_NegativeReward_notInverted_2020-04-05_16:31:22.781799/Model/actor_iteration_4999_Player_0.hd5"
    AIRLReward = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/NEURIPS2020/AIRL/Training/Player_4_Cards_11_games_5000TrainingAgents_['DQL_AIRL', 'DUMMY_RANDOM', 'DUMMY_RANDOM', 'DUMMY_RANDOM']_Reward_OnlyWinning_Train_NegativeReward_notInverted_2020-04-05_16:31:22.781799/Model/reward_iteration_4999_Player_0.hd5"

    loadModelAgent1 = DQLModel#[DQLEgreedy, DQLEgreedyPModel]# ""#[DQLSoftmax, DQLSoftmaxPmodel]# [DQLModelGamma095,DQLModelGamma095P]  #""#[actorModelDDPG,criticModelDDPG]#DQLModel#""# #"" #""#""#DQLModel#""#[actorModelDDPG,criticModelDDPG] ##""#[actorModelA2C,criticModelA2C] #[actorModelA2C,criticModelA2C] #DQLModel #[actorModelA2C,criticModelA2c] #[actorModelDDPG,criticModelDDPG]

    loadModelAgent3 = [A2cActor, A2cCritic]# #""#[DQLModel9,DQLModel9]#""#""##[DQLModel2,DQLModel2]# ""#DQLModel #"" #DQLModel

    loadModelAgent2 = [PPOActor,PPOCritic]# ""#DQLModel3#[DQLModel3,DQLModel3] #[actorModelDDPG,criticModelDDPG]
    loadModelAgent4 =[AIRLModel, AIRLReward]# DQLModel4# ""

    #
    # loadModel = [loadModelAgent1,loadModelAgent2, loadModelAgent3, loadModelAgent4] #indicate where the saved model is
    loadModel = [loadModelAgent1,loadModelAgent2, loadModelAgent3, loadModelAgent4] #indicate where the saved model is
    #
    # loadModel = "" #indicate where the saved model is

    # #Parameters for controling the experiment
    isLogging = False #Logg the experiment

    isPlotting = True #plot the experiment

    plotFrequency = 1 #plot the plots every X games

    createDataset = True # weather to save the dataset

    saveExperimentsIn = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/DataSetGeneration/"  # Directory where the experiment will be saved

    metrics = ChefsHatExperimentHandler.runExperiment(numGames=numGames, playersAgents=playersAgents,experimentDescriptor=experimentDescriptor,isLogging=isLogging,isPlotting=isPlotting,plotFrequency = plotFrequency, createDataset=createDataset,saveExperimentsIn=saveExperimentsIn, loadModel=loadModel, rewardFunction=reward, plots=plotsToGenerate)
    #
    # print ("Metrics:" + str(metrics))


config = tf.ConfigProto()
config.gpu_options.allow_growth = True

sess = tf.Session(config=config)
# from keras import backend as K
K.set_session(sess)

with tf.device('/cpu:0'):
    runModel()