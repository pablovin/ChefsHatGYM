from hyperopt import fmin, tpe, hp, STATUS_OK, Trials
import hyperopt

import pickle

import hyperopt.plotting

from ExperimentHandler import ChefsHatExperimentHandler


from Agents import  AgentRandom, AgentDQL, AgentA2C, AgentDDPG

from Rewards import RewardOnlyWinning
import tensorflow as tf
from keras import backend as K

import numpy
import time

import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"


def runModel():
    # Parameters for the game
    agent1 = AgentA2C.AgentA2C([True])  # training agent
    agent2 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)
    agent3 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)
    agent4 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)

    # if training specific agents
    playersAgents = [agent1, agent2, agent3, agent4]


    reward = RewardOnlyWinning.RewardOnlyWinning()

    numGames = 500# amount of training games
    experimentDescriptor = "Optmizing_A2C_Agent"

    saveTrialsDataset = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/BaselineExperiments/Optmizing/" +  experimentDescriptor

    actorModel = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/Gym_Experiments/Player_4_Cards_11_games_500TrainAgents_['A2C', 'DUMMY_RANDOM', 'DUMMY_RANDOM', 'DUMMY_RANDOM']_Reward_OnlyWinning_TrainingAgent_A2C_2020-03-16_15:54:06.142278/Model/actor_iteration_499.hd5"
    criticModel ="/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/Gym_Experiments/Player_4_Cards_11_games_500TrainAgents_['A2C', 'DUMMY_RANDOM', 'DUMMY_RANDOM', 'DUMMY_RANDOM']_Reward_OnlyWinning_TrainingAgent_A2C_2020-03-16_15:54:06.142278/Model/critic_iteration_499.hd5"
    DQLModel = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/Gym_Experiments/Player_4_Cards_11_games_500TrainAgents_['DQL', 'DUMMY_RANDOM', 'DUMMY_RANDOM', 'DUMMY_RANDOM']_Reward_OnlyWinning_TrainingAgent_DQL_2020-03-16_15:56:43.621816/Model/actor_iteration_499.hd5"

    loadModelAgent1 = ""

    loadModelAgent2 = "" #[actorModel,criticModel]

    loadModelAgent3 = ""
    loadModelAgent4 = ""

    #
    # loadModel = [loadModelAgent1,loadModelAgent2, loadModelAgent3, loadModelAgent4] #indicate where the saved model is
    loadModel = [loadModelAgent1,loadModelAgent2, loadModelAgent3, loadModelAgent4] #indicate where the saved model is
    #
    # loadModel = "" #indicate where the saved model is

    # #Parameters for controling the experiment
    numMaxEvals = 100 # number of evaluations for the optmization

    isLogging = False #Logg the experiment

    isPlotting = False #plot the experiment

    plotFrequency = 100 #plot the plots every X games

    createDataset = False # weather to save the dataset

    saveExperimentsIn = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/Gym_Experiments" # Directory where the experiment will be saved

    # self.hiddenLayers, self.hiddenUnits, QSize, self.batchSize, self.targetUpdateFrequency

    space = hp.choice('a',
                      [
                          (hp.choice("layers", [1, 2, 3, 4]), hp.choice("hiddenUnits", [8, 32, 64, 128, 256]),
                           hp.uniform("gamma", 0.01, 0.99),
                          )
                      ])

    def objective(args):
        agent1 = AgentA2C.AgentA2C([True])
        agent2 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)
        agent3 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)
        agent4 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)
        playersAgents = [agent1, agent2, agent3, agent4]

        loadModelAgent1 = ""

        loadModelAgent2 = ""  # [actorModel,criticModel]

        loadModelAgent3 = ""
        loadModelAgent4 = ""
        loadModel = [loadModelAgent1, loadModelAgent2, loadModelAgent3,
                     loadModelAgent4]

        numGames = 100

        #training trial
        metrics = ChefsHatExperimentHandler.runExperiment(numGames=numGames, playersAgents=playersAgents,
                                                          experimentDescriptor=experimentDescriptor,
                                                          isLogging=isLogging, isPlotting=isPlotting,
                                                          plotFrequency=plotFrequency, createDataset=createDataset,
                                                          saveExperimentsIn=saveExperimentsIn, loadModel=loadModel,
                                                          rewardFunction=reward, agentParams =[args])

        # Player1 - agent
        p1 = metrics[2]
        p1_model = p1[4]


        #testing trial
        agent1 = AgentA2C.AgentA2C([False])  # training agent
        playersAgents = [agent1, agent2, agent3, agent4]


        loadModelAgent1 = p1_model
        loadModel = [loadModelAgent1, loadModelAgent2, loadModelAgent3,
                     loadModelAgent4]
        numGames = 100  # amount of training games

        metrics = ChefsHatExperimentHandler.runExperiment(numGames=numGames, playersAgents=playersAgents,
                                                          experimentDescriptor=experimentDescriptor,
                                                          isLogging=isLogging, isPlotting=isPlotting,
                                                          plotFrequency=plotFrequency, createDataset=createDataset,
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
        averageReward = numpy.average(p1_rewards)
        averageRounds = rounds

        # return wins

        print("Args: ", args)
        return {
            'loss': wins,
            'status': STATUS_OK,
            # -- store other results like this
            'eval_time': time.time(),
            'other_stuff': {'reward': averageReward, "rounds": averageRounds, 'wrongMoves': p1_wrongActions},
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

with tf.device('/gpu:0'):
    runModel()
