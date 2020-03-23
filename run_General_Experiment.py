from ExperimentHandler import ChefsHatExperimentHandler

from Agents import AgentRandom, AgentDQL, AgentA2C, AgentDDPG

from Rewards import RewardOnlyWinning, RewardIROSPaper
import tensorflow as tf
from keras import backend as K

import os

os.environ["CUDA_VISIBLE_DEVICES"] = "0"


def runModel():
    # Parameters of the agents
    agent1 = AgentDQL.AgentDQL([True, 1.0])  # training agent
    agent2 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)
    agent3 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)
    agent4 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)

    playersAgents = [agent1, agent2, agent3, agent4]  # if training specific agents

    reward = RewardOnlyWinning.RewardOnlyWinning()

    numGames = 1000  # amount of training games
    experimentDescriptor = "TrainingAgent"

    loadModelAgent1 = ""
    loadModelAgent2 = ""
    loadModelAgent3 = ""
    loadModelAgent4 = ""

    loadModel = [loadModelAgent1, loadModelAgent2, loadModelAgent3,
                 loadModelAgent4]  # indicate where the saved model is

    # #Parameters for controling the experiment

    isLogging = False  # Logg the experiment

    isPlotting = True  # plot the experiment

    plotFrequency = 1000  # plot the plots every X games

    createDataset = False  # weather to save the dataset

    saveExperimentsIn = "saveExperiment/"  # Directory where the experiment will be saved

    # Run simulation
    metrics = ChefsHatExperimentHandler.runExperiment(numGames=numGames, playersAgents=playersAgents,
                                                      experimentDescriptor=experimentDescriptor, isLogging=isLogging,
                                                      isPlotting=isPlotting, plotFrequency=plotFrequency,
                                                      createDataset=createDataset, saveExperimentsIn=saveExperimentsIn,
                                                      loadModel=loadModel, rewardFunction=reward)

    print("Metrics:" + str(metrics))


config = tf.ConfigProto()
config.gpu_options.allow_growth = True

sess = tf.Session(config=config)
K.set_session(sess)

with tf.device('/gpu:0'):
    runModel()


