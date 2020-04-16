from KEF import RenderManager
from KEF import PlotManager
from KEF.PlotManager import plots


dataSetLocation = "*.pkl location" # dataset folder

videoSaveFolder = "savingFolder" # Folder where the videos will be saved

resourceFolder ="folder" # directory of the images folder

fps = 25
gameToRender = [0, 1, 2] #List of games to be generated

render = RenderManager.RenderManager(videoSaveFolder, resourcesFolder=resourceFolder, fps=fps)

render.renderGameStatus(dataSet=dataSetLocation, gamesToRender=gameToRender, createVideo=True)