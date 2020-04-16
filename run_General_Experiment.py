from ExperimentHandler import ChefsHatExperimentHandler

from Agents import AgentRandom, AgentDQL, AgentA2C, AgentPPO
from KEF.PlotManager import plots

from Rewards import RewardOnlyWinning
import tensorflow as tf
from keras import backend as K


import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

def runModel():

    #Plots
    plotsToGenerate = [plots["Experiment_Rounds"], plots["Experiment_FinishingPosition"], plots["Experiment_ActionsBehavior"],
                   plots["Experiment_Reward"], plots["Experiment_QValues"], plots["Experiment_Mood"], plots["Experiment_MoodNeurons"],
                   plots["Experiment_SelfProbabilitySuccess"]]
    plotsToGenerate = []

    #Parameters for the agents
    agent1 = AgentDQL.AgentDQL([False, 1.0, "DQL"]) #training agent
    agent2 = AgentPPO.AgentPPO([False, 1.0, "PPO"]) #training agent
    agent3 = AgentA2C.AgentA2C([False, 1.0, "A2C"])  # training agent
    agent4 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)  # training agent

    #Load agents from
    DQLModel = ""

    A2cActor = ""
    A2cCritic = ""

    PPOActor = ""
    PPOCritic = ""

    loadModelAgent1 = DQLModel
    loadModelAgent3 = [A2cActor, A2cCritic]
    loadModelAgent2 = [PPOActor,PPOCritic]
    loadModelAgent4 =""

    loadModel = [loadModelAgent1,loadModelAgent2, loadModelAgent3, loadModelAgent4]

    #List of agents
    playersAgents = [agent1, agent2, agent3, agent4]

    #Reward function
    reward = RewardOnlyWinning.RewardOnlyWinning()

    #Experimental parameters
    numGames = 1 # amount of games to be executed
    experimentDescriptor = "GeneralTraining" #Experiment name

    isLogging = False # create a .txt file with the experiment log

    isPlotting = True #Create plots of the experiment

    createDataset = True # Create a .pkl dataset of the experiemnt

    saveExperimentsIn = ""  # Directory where the experiment will be saved

    metrics = ChefsHatExperimentHandler.runExperiment(numGames=numGames, playersAgents=playersAgents,experimentDescriptor=experimentDescriptor,isLogging=isLogging,isPlotting=isPlotting, createDataset=createDataset,saveExperimentsIn=saveExperimentsIn, loadModel=loadModel, rewardFunction=reward, plots=plotsToGenerate)

config = tf.ConfigProto()
config.gpu_options.allow_growth = True

sess = tf.Session(config=config)
# from keras import backend as K
K.set_session(sess)

with tf.device('/cpu:0'):
    runModel()