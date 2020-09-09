from KEF import RenderManager
from KEF import PlotManager
from KEF.PlotManager import plots
from MoodyFramework.Utils import GenerateMoodFromDataset
from MoodyFramework.Mood.Intrinsic import Intrinsic, CONFIDENCE_PHENOMENOLOGICAL

from Agents import AgentRandom, AgentDQL, AgentA2C, AgentPPO
import numpy

#Experiment control variables
dataSetLocation = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/Tournament/Adapting/DQLOnly/Bracket_1/Match_1/Player_4_Cards_11_games_-1TrainingAgents_['DQL_DQL_0', 'RANDOMRANDOM_1', 'DQL_DQL_2', 'RANDOMRANDOM_3']_Reward_OnlyWinning_TournamentExperiment_2020-06-30_17:52:46.220405/Datasets/Dataset.pkl" # dataset folder" #location of the dataset.PKL file
saveMoodPlot = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/Tournament/Plots/Adapting/Match1" #Location where the Mood Plots will be saved


plotsToGenerate = [plots["Experiment_Rounds"], plots["Experiment_Winners"],
                   plots["Experiment_Points"], plots["Experiment_ActionsBehavior"],
                   plots["Experiment_Reward"]]

# plot = PlotManager.generateIntrinsicPlotsFromDataset(plotsToGenerate=plotsToGenerate, IntrinsicDataset=moodDataset, gameNumber=2, saveDirectory=saveMoodPlot)
PlotManager.generateExperimentPlotsFromDataset(plotsToGenerate=plotsToGenerate,dataset=dataSetLocation,saveDirectory=saveMoodPlot)
# PlotManager.generateSingleGamePlotsFromDataset(plotsToGenerate, dataSetLocation, 1, saveDirectory = saveMoodPlot)
