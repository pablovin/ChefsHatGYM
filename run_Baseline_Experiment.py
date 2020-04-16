from ExperimentHandler import ChefsHatExperimentHandler

from Agents import AgentRandom, AgentDQL, AgentA2C, AgentPPO
from KEF.PlotManager import plots

from Rewards import RewardOnlyWinning
import tensorflow as tf
from keras import backend as K
import numpy
import pandas as pd

from IRLAgents import AIRL


import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

def runModel():

    #Plots
    plotsToGenerate = []

    demonstrations = numpy.load("/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/NEURIPS2020/AIRL/ExpertObs/Demonstrations_ExpertCollection.npy", allow_pickle=True)

    #Parameters for the agents
    agentDQL = AgentDQL.AgentDQL([False, 1.0, "DQL"]) #training agent
    agentA2C = AgentA2C.AgentA2C([False, 1.0, "A2C"])  # training agent
    agentPPO = AgentPPO.AgentPPO([False, 1.0, "PPO"])  # training agent
    agentAIRL = AIRL.AgentAIRL([False, 1.0, "AIRL", None, demonstrations])  # training agent

    possibleAgent1 = [agentDQL,agentA2C, agentPPO, agentAIRL ]


    agent2 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)  # training agent
    agent3 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)  # training agent
    agent4 = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM)  # training agent

    #Load agents from
    DQLModel = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/TrainedModels/DQL_vsRandom/actor_iteration_999_Player_0.hd5"

    A2cActor = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/TrainedModels/A2C_vsEveryone/actor_iteration_999_Player_1.hd5"
    A2cCritic = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/TrainedModels/A2C_vsEveryone/critic_iteration_999_Player_1.hd5"

    PPOActor = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/TrainedModels/PPO_vsEveryone/actor_iteration_999_Player_2.hd5"
    PPOCritic = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/TrainedModels/PPO_vsEveryone/critic_iteration_999_Player_2.hd5"

    AIRLModel = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/NEURIPS2020/AIRL/Training/Player_4_Cards_11_games_5000TrainingAgents_['DQL_AIRL', 'DUMMY_RANDOM', 'DUMMY_RANDOM', 'DUMMY_RANDOM']_Reward_OnlyWinning_Train_NegativeReward_notInverted_2020-04-05_16:31:22.781799/Model/actor_iteration_4999_Player_0.hd5"
    AIRLReward = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/NEURIPS2020/AIRL/Training/Player_4_Cards_11_games_5000TrainingAgents_['DQL_AIRL', 'DUMMY_RANDOM', 'DUMMY_RANDOM', 'DUMMY_RANDOM']_Reward_OnlyWinning_Train_NegativeReward_notInverted_2020-04-05_16:31:22.781799/Model/reward_iteration_4999_Player_0.hd5"

    possibleLoadModel1 = [DQLModel, [A2cActor, A2cCritic], [PPOActor,PPOCritic], [AIRLModel,AIRLReward]]
    loadModelEmpty = ""

    #Reward function
    reward = RewardOnlyWinning.RewardOnlyWinning()

    #Experimental parameters
    numberOfTrials = 50
    maximumScore = 15 # maximumScore to be reached
    experimentDescriptor = "BaselineExperimentsVsRandom" #Experiment name

    isLogging = False # create a .txt file with the experiment log

    isPlotting = False #Create plots of the experiment

    createDataset = False # Create a .pkl dataset of the experiemnt

    saveExperimentsIn = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/BaselineNumberGames"  # Directory where the experiment will be saved

    #Metrics to be saved
    avgTotalGames = []

    avgWonGames = []
    avgPoints = []
    avgWonRounds = []

    for a in range(4):
        avgPoints.append([])
        avgWonGames.append([])
        avgWonRounds.append([])


    columns = ["ExperimentName", "AvgTotalNumberGames", "stdNumberGames",
               "Player0_AvgPoints", "Player0_stdAvgPoints",
               "Player0_AvgWonGames", "Player0_stdAvgWonGames",
               "Player0_AvgWonRounds","Player0_stdWonRounds",
               "Player1_AvgPoints", "Player1_stdAvgPoints",
               "Player1_AvgWonGames", "Player1_stdAvgWonGames",
               "Player1_AvgWonRounds", "Player1_stdWonRounds",
               "Player2_AvgPoints", "Player2_stdAvgPoints",
               "Player2_AvgWonGames", "Player2_stdAvgWonGames",
               "Player2_AvgWonRounds", "Player2_stdWonRounds",
               "Player3_AvgPoints", "Player3_stdAvgPoints",
               "Player3_AvgWonGames", "Player3_stdAvgWonGames",
               "Player3_AvgWonRounds", "Player3_stdWonRounds",
                     ]

    totalDataFame = pd.DataFrame(columns = columns)


    for agent in range(4):

        loadModel = [possibleLoadModel1[agent], loadModelEmpty, loadModelEmpty, loadModelEmpty]

        # List of agents and Models to Load
        playersAgents = [possibleAgent1[agent], agent2, agent3, agent4]
        print ("Evaluating agent:" + str(playersAgents[0].name))
        for a in range(numberOfTrials):

            metrics = ChefsHatExperimentHandler.runExperiment(maximumScore=maximumScore, playersAgents=playersAgents,experimentDescriptor=experimentDescriptor,isLogging=isLogging,isPlotting=isPlotting, createDataset=createDataset,saveExperimentsIn=saveExperimentsIn, loadModel=loadModel, rewardFunction=reward, plots=plotsToGenerate)
            games = metrics[-1]
            score = metrics[-2]
            winner = numpy.argmax(score)

            for i in range(len(playersAgents)):
                playerMetric = metrics[2+i]
                rounds = playerMetric[5]
                avgPoints[i].append(score[i])
                if winner == i:
                    avgWonGames[i].append(games)
                    avgWonRounds[i].append(numpy.mean(rounds))

            print("Trial:" + str(a) + "- Games" + str(games) + " - Winner: " + str(winner))
            avgTotalGames.append(games)

        currentDataFrame = []
        currentDataFrame.append(playersAgents[0].name) #Trained Agent Name
        currentDataFrame.append(numpy.mean(avgTotalGames)) # AvgTotalNumberGames
        currentDataFrame.append(numpy.std(avgTotalGames))# AvgSTDTotalNumberGames


        for i in range(len(playersAgents)):
            points = avgPoints[i]
            wongamesNumber = avgWonGames[i]
            wonRounds = avgWonRounds[i]

            currentDataFrame.append(numpy.mean(points)) # Player X AvgPoints
            currentDataFrame.append(numpy.std(points))  # Player X StdPoints

            currentDataFrame.append(numpy.mean(wongamesNumber)) # Player X AvgWonGames
            currentDataFrame.append(numpy.std(wongamesNumber))  # Player X StdWonGames

            currentDataFrame.append(numpy.mean(wonRounds)) # Player X AvgRounds
            currentDataFrame.append(numpy.std(wonRounds))  # Player X StdRounds
            # print ("Player - " + str(i))
            # print (" -- Average points:" + str(numpy.mean(points)) + "("+str(numpy.std(points))+")")
            # print(" -- Average Num Games  When Win:" + str(numpy.mean(wongamesNumber)) + "(" + str(numpy.std(wongamesNumber)) + ")")
            # print(" -- Average Num Rounds  When Win:" + str(numpy.mean(roundsWin)) + "(" + str(
            #     numpy.std(roundsWin)) + ")")


        totalDataFame.loc[-1] = currentDataFrame
        totalDataFame.index = totalDataFame.index + 1

        totalDataFame.to_pickle(saveExperimentsIn+"/"+experimentDescriptor)
        totalDataFame.to_csv(saveExperimentsIn+"/"+experimentDescriptor + ".csv", index=False, header=True)

        # print ("Avg. Num Games: " + str(numpy.mean(avgTotalGames))+"("+str(numpy.std(avgTotalGames))+")")
        #





config = tf.ConfigProto()
config.gpu_options.allow_growth = True

sess = tf.Session(config=config)
# from keras import backend as K
K.set_session(sess)

with tf.device('/cpu:0'):
    runModel()