from hyperopt import fmin, tpe, hp, STATUS_OK, Trials
import hyperopt

import pickle

import hyperopt.plotting

from ExperimentHandler import ChefsHatExperimentHandler


from Agents import  AgentRandom, AgentDQL

from Rewards import RewardOnlyWinning
import tensorflow as tf
from keras import backend as K

import numpy
import time

import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""


def runModel():
    # Parameters for the game
    agent1 = AgentDQL.AgentDQL([True, 1.0, "DQL"]) #training agent
    agent2 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)
    agent3 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)
    agent4 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)

    # Load agents from

    loadModels = ""

    loadModel = [loadModels, loadModels, loadModels, loadModels]

    # List of agents
    playersAgents = [agent1, agent2, agent3, agent4]

    # Reward function
    reward = RewardOnlyWinning.RewardOnlyWinning()

    # Experimental parameters

    numGames = 1000  # amount of games to be executed
    numMaxEvals = 100  # number of evaluations for the optmization
    experimentDescriptor = "Optmizing_DQL"  # Experiment name

    saveTrialsDataset = "folder" #Folder where the optmization trials will be saved
    saveTrialsDataset += experimentDescriptor

    isLogging = False  # create a .txt file with the experiment log

    isPlotting = False  # Create plots of the experiment

    createDataset = False  # Create a .pkl dataset of the experiemnt

    saveExperimentsIn = ""  # Directory where the experiment will be saved

    #Search space for the agent
    space = hp.choice('a',
                      [
                          (hp.choice("layers", [1, 2, 3, 4]), hp.choice("hiddenUnits", [8, 32, 64, 256]),
                           hp.choice("batchSize", [16, 64, 128, 256, 512]),
                           hp.uniform("tau", 0.01, 0.99)
                          )
                      ])

    def objective(args):
        agent1 = AgentDQL.AgentDQL([True, 1.0, "DQL"]) #training agent
        agent2 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)
        agent3 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)
        agent4 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)
        playersAgents = [agent1, agent2, agent3, agent4]

        loadModels = ""

        loadModel = [loadModels, loadModels, loadModels, loadModels]

        numGames = 100

        #training trial
        metrics = ChefsHatExperimentHandler.runExperiment(numGames=numGames, playersAgents=playersAgents,
                                                          experimentDescriptor=experimentDescriptor,
                                                          isLogging=isLogging, isPlotting=isPlotting,
                                                           createDataset=createDataset,
                                                          saveExperimentsIn=saveExperimentsIn, loadModel=loadModel,
                                                          rewardFunction=reward, agentParams =[args])

        # Player1 - agent
        p1 = metrics[2]
        p1_model = p1[4]


        #testing trial
        agent1 = AgentDQL.AgentDQL([False, 1.0, "DQL"])  # training agent
        playersAgents = [agent1, agent2, agent3, agent4]


        loadModelAgent1 = p1_model
        loadModel = [loadModelAgent1, loadModels, loadModels,
                     loadModels]
        numGames = 100  # amount of training games

        metrics = ChefsHatExperimentHandler.runExperiment(numGames=numGames, playersAgents=playersAgents,
                                                          experimentDescriptor=experimentDescriptor,
                                                          isLogging=isLogging, isPlotting=isPlotting,
                                                          createDataset=createDataset,
                                                          saveExperimentsIn=saveExperimentsIn, loadModel=loadModel,
                                                          rewardFunction=reward, agentParams =[args])

        rounds = metrics[0]
        startGameFinishingPosition = metrics[1]

        # Player1 - agent
        p1 = metrics[2]
        p1_wins = p1[0]
        p1_positions = p1[1]
        p1_rewards = p1[2]
        p1_wrongActions = p1[3]
        p1_model = p1[4]

        p2 = metrics[3]
        p3 = metrics[4]

        wins = numGames - p1_wins
        averageReward = 1 - numpy.average(p1_rewards)
        averageRounds = rounds

        # return wins
        print("Args: " + str(args) + "Reward:" + str(averageReward))
        return {
            'loss': averageReward,
            'status': STATUS_OK,
            # -- store other results like this
            'eval_time': time.time(),
            'other_stuff': {'wins': wins, "rounds": averageRounds, 'wrongMoves': p1_wrongActions},
        }

    trials = Trials()
    best = fmin(objective,
                space=space,
                algo=tpe.suggest,
                max_evals=numMaxEvals,
                trials=trials)

    print("Saving the trials dataset:", saveTrialsDataset)

    pickle.dump(trials, open(saveTrialsDataset, "wb"))

    print("Trials:", trials)
    print("BEst: ", hyperopt.space_eval(space, best))
    print("Best:" + str(best))

    hyperopt.plotting.main_plot_history(trials, title="WinsHistory")



config = tf.ConfigProto()
config.gpu_options.allow_growth = True

sess = tf.Session(config=config)
# from keras import backend as K
K.set_session(sess)

with tf.device('/cpu:0'):
    runModel()
