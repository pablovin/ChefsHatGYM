from ExperimentHandler import ChefsHatExperimentHandler

from Agents import  AgentRandom, AgentDQL

from Rewards import RewardOnlyWinning

#Parameters for the game
playersAgents = [AgentDQL.AgentDQL(), AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM), AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM), AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)]

reward = RewardOnlyWinning.RewardOnlyWinning()

numGames = 1000# amount of training games
experimentDescriptor = "TrainingAgent_10x_LinearOutput"

#loadModel = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/BaselineExperiments/DQL_V2/Player_4_Cards_11_games_1000TrainAgents_['DQL_v2', 'DUMMY_RANDOM', 'DUMMY_RANDOM', 'DUMMY_RANDOM']_Training_1000x_NoPossibleActions_OnlyWinningReward_2020-03-13_12:50:08.475705/Model/actor_iteration_977.hd5" #indicate where the saved model is

loadModel = "" #indicate where the saved model is

# #Parameters for controling the experiment
isLogging = False #Logg the experiment

isPlotting = True #plot the experiment

plotFrequency = 100 #plot the plots every X games

createDataset = False # weather to save the dataset

saveExperimentsIn = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/Gym_Experiments" # where the experiment will be saved

metrics = ChefsHatExperimentHandler.runExperiment(numGames=numGames, playersAgents=playersAgents,experimentDescriptor=experimentDescriptor,isLogging=isLogging,isPlotting=isPlotting,plotFrequency = plotFrequency, createDataset=createDataset,saveExperimentsIn=saveExperimentsIn, loadModel=loadModel, rewardFunction=reward)

print ("Metrics:" + str(metrics))
