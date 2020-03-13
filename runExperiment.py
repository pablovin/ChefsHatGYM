from ExperimentHandler import ChefsHatExperimentHandler

from Agents.AgentType import  DUMMY_RANDOM, DUMMY_DISCARDONECARD, DQL_v1, DQL_v2

#Parameters for the game
playersAgents = [DQL_v2, DUMMY_RANDOM, DUMMY_RANDOM, DUMMY_RANDOM]

numGames = 1000# amount of training games
experimentDescriptor = "Training_10x_NoPossibleActions_OnlyWinningReward"

# loadModel = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/Gym_Experiments/WINNINGDQL_Player_4_Cards_11_games_100TrainAgents_['DQL', 'RANDOM', 'RANDOM', 'RANDOM']_QLLearningAgent_2020-02-29_21:49:50.134777/Model/actor_iteration_27.hd5"

# loadModel = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/BaselineExperiments/DQL_V2/Player_4_Cards_11_games_50TrainAgents_['DQL_v2', 'DUMMY_RANDOM', 'DUMMY_RANDOM', 'DUMMY_RANDOM']_DQLV2_TargetNetwork_2020-03-03_11:32:23.968124/Model/actor_iteration_49.hd5"

loadModel = ""

# #Parameters for controling the experiment
isLogging = False #Logg the experiment

isPlotting = True #plot the experiment

plotFrequency = 100

createDataset = False # weather to save the dataset

saveExperimentsIn = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/Gym_Experiments" # where the experiment will be saved

metrics = ChefsHatExperimentHandler.runExperiment(numGames=numGames, playersAgents=playersAgents,experimentDescriptor=experimentDescriptor,isLogging=isLogging,isPlotting=isPlotting,plotFrequency = plotFrequency, createDataset=createDataset,saveExperimentsIn=saveExperimentsIn, loadModel=loadModel)

print ("Metrics:" + str(metrics))
