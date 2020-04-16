from KEF import RenderManager
from KEF import PlotManager
from KEF.PlotManager import plots


dataSetLocation = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/DataSetGeneration/Player_4_Cards_11_games_30TrainingAgents_['DQL_DQL', 'PPO_PPO', 'A2C_A2C', 'DQL_AIRL']_Reward_OnlyWinning_Test10_2020-04-13_19:48:13.424718/Datasets/Dataset.pkl"

plotSaveDirectory = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/renderTest/plotTests"

fps = 25
gameToRender = 1

render = RenderManager.RenderManager("/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/renderTest/", resourcesFolder="/home/pablo/Documents/Workspace/ChefsHatGYM/images/", fps=fps)

plotsToGenerate = [plots["Experiment_Rounds"], plots["Experiment_FinishingPosition"], plots["Experiment_ActionsBehavior"],
                   plots["Experiment_Reward"], plots["Experiment_QValues"]]

plot = PlotManager.generateSingleGamePlotsFromDataset(plotsToGenerate, dataSetLocation, gameToRender, plotSaveDirectory)
plot = PlotManager.generateExperimentPlotsFromDataset(plotsToGenerate=plotsToGenerate, dataset=dataSetLocation, saveDirectory=plotSaveDirectory)
# render.renderGameStatus(dataSetLocation, gameToRender, createVideo=True)