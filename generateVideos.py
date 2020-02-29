from KEF import RenderManager

dataSetLocation = "Examples/Example_Random_Agent.csv"
fps = 25

render = RenderManager.RenderManager("Examples/", fps=fps)
render.renderGameStatus(dataSetLocation, createVideo=True)