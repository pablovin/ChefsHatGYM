from KEF import RenderManager

dataSetLocation = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/BaselineExperiments/DQL_V1/Player_4_Cards_11_games_50TrainAgents_['DQL_v1', 'DUMMY_DISCARDONECARD', 'DUMMY_DISCARDONECARD', 'DUMMY_DISCARDONECARD']_DQL_Retraining_WinningAgent_2020-03-02_18:21:17.925342/Datasets/Game_1.csv"

fps = 25

render = RenderManager.RenderManager("/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/testRender/", fps=fps)
render.createGameTimeLine(dataSetLocation)


# render.renderGameStatus(dataSetLocation, createVideo=True)