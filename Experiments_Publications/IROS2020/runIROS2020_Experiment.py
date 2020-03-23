from ExperimentHandler import ChefsHatExperimentHandler

from Agents import  AgentRandom, AgentDQL

from Rewards import  RewardIROSPaper
import tensorflow as tf
from keras import backend as K

import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"


def runModel():
    #Parameters for the game
    agent1 = AgentDQL.AgentDQL([True, 1.0]) #training agent
    agent2 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)
    agent3 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)
    agent4 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)

     # if training specific agents
    playersAgents = [agent1, agent2, agent3, agent4]

    reward = RewardIROSPaper.RewardIROSPaper()

    numGames = 250
    experimentDescriptor = "IROSExperiments"


    loadModelAgent1 = "" #If loading an existing agent, indicate here.
    loadModelAgent2 = "" #If loading an existing agent, indicate here.

    loadModelAgent3 = "" #If loading an existing agent, indicate here.
    loadModelAgent4 = "" #If loading an existing agent, indicate here.

    loadModel = [loadModelAgent1,loadModelAgent2, loadModelAgent3, loadModelAgent4] #indicate where the saved model is

    isLogging = True #Logg the experiment

    isPlotting = True #plot the experiment

    plotFrequency = 250 #plot the plots every X games

    createDataset = False # weather to save the dataset

    saveExperimentsIn = "SaveExperiment_IROS2020/" # Directory where the experiment will be saved

    metrics = ChefsHatExperimentHandler.runExperiment(numGames=numGames, playersAgents=playersAgents,experimentDescriptor=experimentDescriptor,isLogging=isLogging,isPlotting=isPlotting,plotFrequency = plotFrequency, createDataset=createDataset,saveExperimentsIn=saveExperimentsIn, loadModel=loadModel, rewardFunction=reward)

    print ("Metrics:" + str(metrics))


config = tf.ConfigProto()
config.gpu_options.allow_growth = True

sess = tf.Session(config=config)
# from keras import backend as K
K.set_session(sess)

with tf.device('/cpu:0'):
    runModel()