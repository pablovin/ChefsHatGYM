from KEF import RenderManager

dataSetLocation = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/Gym_Experiments/Player_4_Cards_11_games_10TrainAgents_['QL', 'QL', 'QL', 'QL']_QLLearningAgent_2020-02-29_19:09:11.913605/Datasets/Game_8.csv"

fps = 25

render = RenderManager.RenderManager("/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/testRender/", fps=fps)
render.renderGameStatus(dataSetLocation, createVideo=True)