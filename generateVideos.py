from KEF import RenderManager

dataSetLocation = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/Gym_Experiments/Player_4_Cards_11_games_2TrainAgents_['RANDOM', 'RANDOM', 'RANDOM', 'RANDOM']_Joker_Trial_QL_2020-02-29_16:30:17.444821/Datasets/Game_1.csv"

fps = 25

render = RenderManager.RenderManager("/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/testRender/", fps=fps)
render.renderGameStatus(dataSetLocation, createVideo=True)