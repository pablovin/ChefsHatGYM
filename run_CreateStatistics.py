from KEF import StatisticsManager
from KEF.StatisticsManager import statisticsGame, statisticsPreGame, statisticsAfterGame, statisticsIntegrated
import os

#Experiment control variables
datasetsGameLocation = "/home/pablo/Documents/Datasets/CHefsHatWeb/Study1_No_Image/Game_Data_All_200814" # Folder where all datasets are
savePlots = "/home/pablo/Documents/Datasets/CHefsHatWeb/Study1_No_Image/Plots_Data_All_200814" #Location where the Plots will be saved

preGameCSV = "/home/pablo/Documents/Datasets/CHefsHatWeb/Study1_No_Image/Survey_Pre_Game_Data_All_200814/CSV/PreGameCleaned.csv"

inGameCSV = "/home/pablo/Documents/Datasets/CHefsHatWeb/Study1_No_Image/Survey_In_Game_Data_All_200814/CSV/CollectorList.csv"

afterGameCSV = "/home/pablo/Documents/Datasets/CHefsHatWeb/Study1_No_Image/Survey_After_Game_Data_All_200814/CSV/afterGameCleaned.csv"


statisticsToGenerate = [statisticsGame["GameDuration"], statisticsGame["NumberGames"],
                        statisticsGame["NumberRounds"], statisticsGame["PlayerScore"],
                        statisticsGame["AgregatedScore"]]


statisticsToGeneratePreGame = [statisticsPreGame["Personality"], statisticsPreGame["Competitiveness"],
                               statisticsPreGame["Experience"]]

statisticsToGenerateAfterGame = [statisticsAfterGame["Personality"]]

statisticsToGenerateIntegrated = [statisticsIntegrated["Similarity"]]

datasets = []

for location in os.listdir(datasetsGameLocation):
    datasets.append(datasetsGameLocation+"/"+ location+"/Dataset.pkl")
    print ("Player:" + location)

StatisticsManager.calculateGameStatistics(statisticsToCalculate=statisticsToGenerate,datasets=datasets,saveDirectory=savePlots)

StatisticsManager.calculatePreGameStatistics(statisticsToCalculate=statisticsToGeneratePreGame,preGameCSV=preGameCSV,saveDirectory=savePlots)

StatisticsManager.calculateAfterGameStatistics(statisticsToCalculate=statisticsToGenerateAfterGame,afterGameCSV=afterGameCSV,saveDirectory=savePlots)

StatisticsManager.calculateIntegratedGameStatistics(statisticsToGenerateIntegrated, afterGameCSV, preGameCSV, savePlots)