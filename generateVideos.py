from KEF import RenderManager

dataSetLocation = "Examples/Example_Random_Agents.csv"
fps = 25

render = RenderManager.RenderManager("Examples/", fps=fps)
render.renderGameStatus(dataSetLocation, createVideo=True)