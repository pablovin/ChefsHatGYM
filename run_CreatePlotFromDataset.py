from KEF import PlotManager
from KEF.PlotManager import plots


dataSetLocation = "*.pkl location" # dataset folder

plotSaveDirectory = "savingFolder" # Folder where the plots will be generated

game= 1 #Game to render the plots for specific games

plotsToGenerate = [plots["Experiment_SelfProbabilitySuccess"], plots["Experiment_Winners"], plots["Experiment_FinishingPosition"], plots["OneGame_DiscardBehavior"]]

PlotManager.generateSingleGamePlotsFromDataset(plotsToGenerate=plotsToGenerate,gameNumber=game, dataSetLocation=dataSetLocation, saveDirectory=plotSaveDirectory)
PlotManager.generateExperimentPlotsFromDataset(plotsToGenerate=plotsToGenerate,dataset=dataSetLocation,saveDirectory=plotSaveDirectory)

