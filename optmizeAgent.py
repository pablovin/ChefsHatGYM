from ExperimentHandler import ChefsHatExperimentHandler
import time
import numpy

from Agents.AgentList import  DUMMY_RANDOM, DUMMY_DISCARDONECARD, DQL_v1, DQL_v2

from hyperopt import fmin, tpe, hp, STATUS_OK, Trials
import hyperopt

import pickle

import hyperopt.plotting

#Parameters for the game
playersAgents = [DQL_v2, DUMMY_RANDOM, DUMMY_RANDOM, DUMMY_RANDOM]

numGames = 30# amount of training games
numMaxEvals = 100
experimentDescriptor = "ModelOptmization_agents_"+str(playersAgents)+"_Games_"+str(numGames)+"_Evals_"+str(numMaxEvals)

# loadModel = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/Gym_Experiments/WINNINGDQL_Player_4_Cards_11_games_100TrainAgents_['DQL', 'RANDOM', 'RANDOM', 'RANDOM']_QLLearningAgent_2020-02-29_21:49:50.134777/Model/actor_iteration_27.hd5"

loadModel = ""

isLogging = False #Logg the experiment

# #Parameters for controling the experiment
createDataset = False # weather to save the dataset
saveExperimentsIn = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/Gym_Experiments" # where the experiment will be saved

saveTrialsDataset = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/BaselineExperiments/Optmizing/" + str(experimentDescriptor)+".p"

optmizeFunction =""



# space =  [{
# 'memroySize', hp.choice("memorySize", [5, 50, 100, 500, 1000, 2000])
# }]

space = hp.choice('a',
    [
        (hp.choice("layers", [0, 2, 4]), hp.choice("hiddenUnits", [8, 32, 64, 256]), hp.choice("outputActivation", ["tanh", "linear", "softmax"]), hp.choice("loss", ["mse", "categorical_crossentropy", "huber_loss"]))
    ])

# space = hp.choice('a',
#     [
#         (hp.loguniform("gamma", 0, 1), hp.loguniform("epsilon_min", 0, 0.5), hp.loguniform("epsilon_decay", 0.5, 0.9999), hp.choice("batchSize", [8, 32, 64, 100]), hp.randint('targetUpdateFrequency', 3, 100), hp.choice("layers", [1, 2, 4]), hp.choice("hiddenUnits", [8, 32, 64, 256, 512]), hp.choice["outputActivation", ["tanh", "linear", "softmax"], hp.choice("loss", ["mse", "categorical_crossentropy", "huber_loss"])])
#     ])


# space =  [{
# 'memroySize', hp.choice("memorySize", [5, 50, 100, 500, 1000, 2000]),
# 'gamma', hp.loguniform("gamma", 0, 1),
# 'epsilon_min', hp.loguniform("epsilon_min", 0, 0.5),
# 'epsilon_decay', hp.loguniform("epsilon_decay", 0.5, 0.9999),
# 'batchSize', hp.choice("batchSize", [8, 32, 64, 128, 256, 512, 1024]),
# 'targetUpdateFrequency', hp.randint('targetUpdateFrequency', 5, 25)
# }]



def objective(args):
    metrics = ChefsHatExperimentHandler.runExperiment(numGames=numGames, playersAgents=playersAgents,
                                                      experimentDescriptor=experimentDescriptor, isLogging=isLogging,
                                                      createDataset=createDataset, saveExperimentsIn=saveExperimentsIn, agentParams=[args])
    rounds = metrics[0]
    startGameFinishingPosition = metrics[1]

    #Player1 - agent
    p1 = metrics[2]
    p1_wins = p1[0]
    p1_positions = p1[1]
    p1_rewards = p1[2]
    p1_wrongActions = p1[3]

    p2 = metrics[3]
    p3 = metrics[4]

    wins = numGames - p1_wins
    averageReward = numpy.average(p1_rewards)
    averageRounds = rounds

    # return wins

    print ("Args: ", args)
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

print ("Saving the trials dataset:", saveTrialsDataset)

pickle.dump(trials, open(saveTrialsDataset, "wb"))

print ("Trials:", trials)
print ("BEst: ", hyperopt.space_eval(space, best))
print ("Best:" + str(best))

hyperopt.plotting.main_plot_history(trials, title="WinsHistory")