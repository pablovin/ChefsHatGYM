from KEF import RenderManager
from KEF import PlotManager
from KEF.PlotManager import plots
from IntrinsicAgent import GenerateMoodFromDataset
from IntrinsicAgent.Intrinsic import Intrinsic, CONFIDENCE_PHENOMENOLOGICAL

from Agents import AgentRandom, AgentDQL, AgentA2C, AgentPPO
from IRLAgents import AIRL
import numpy

#Experiment control variables
dataSetLocation = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/DataSetGeneration/Player_4_Cards_11_games_10TrainingAgents_['DQL_DQL', 'PPO_PPO', 'A2C_A2C', 'DQL_AIRL']_Reward_OnlyWinning_Test10_2020-04-14_18:41:11.199791/Datasets/Dataset.pkl"

saveMoodDataset = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/renderTest/MoodDataset"
saveMoodPlot = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/renderTest/MoodDataset"

gameToGenerateMood = 0

#Agents

demonstrations = numpy.load(
    "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/NEURIPS2020/AIRL/ExpertObs/Demonstrations_ExpertCollection.npy",
    allow_pickle=True)

agent1 = AgentDQL.AgentDQL([False, 1.0, "DQL"]) #training agent
agent2 = AgentPPO.AgentPPO([False, 1.0, "PPO"]) #training agent
agent3 = AgentA2C.AgentA2C([False, 1.0, "A2C"])  # training agent
agent4 = AIRL.AgentAIRL([False, 1.0, "AIRL", None, demonstrations])  # training agent

agents = [agent1,agent2,agent3,agent4]

DQLModel = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/TrainedModels/DQL_vsEveryone/actor_iteration_999_Player_0.hd5"

A2cActor = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/TrainedModels/A2C_vsEveryone/actor_iteration_999_Player_1.hd5"
A2cCritic = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/TrainedModels/A2C_vsEveryone/critic_iteration_999_Player_1.hd5"

PPOActor = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/TrainedModels/PPO_vsEveryone/actor_iteration_999_Player_2.hd5"
PPOCritic = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/TrainedModels/PPO_vsEveryone/critic_iteration_999_Player_2.hd5"

AIRLModel = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/NEURIPS2020/AIRL/Training/Player_4_Cards_11_games_5000TrainingAgents_['DQL_AIRL', 'DUMMY_RANDOM', 'DUMMY_RANDOM', 'DUMMY_RANDOM']_Reward_OnlyWinning_Train_NegativeReward_notInverted_2020-04-05_16:31:22.781799/Model/actor_iteration_4999_Player_0.hd5"
AIRLReward = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/NEURIPS2020/AIRL/Training/Player_4_Cards_11_games_5000TrainingAgents_['DQL_AIRL', 'DUMMY_RANDOM', 'DUMMY_RANDOM', 'DUMMY_RANDOM']_Reward_OnlyWinning_Train_NegativeReward_notInverted_2020-04-05_16:31:22.781799/Model/reward_iteration_4999_Player_0.hd5"

loadModelAgent1 = DQLModel
loadModelAgent2 = [PPOActor, PPOCritic]
loadModelAgent3 = [A2cActor,
                   A2cCritic]
loadModelAgent4 = [AIRLModel, AIRLReward]

loadModel = [loadModelAgent1,loadModelAgent2, loadModelAgent3, loadModelAgent4]

#Mood Controlers
intrinsicWithMoodAgent1 = Intrinsic(selfConfidenceType=CONFIDENCE_PHENOMENOLOGICAL, isUsingSelfMood=True,isUsingOponentMood=True)
intrinsicWithMoodAgent2 = Intrinsic(selfConfidenceType=CONFIDENCE_PHENOMENOLOGICAL, isUsingSelfMood=True,isUsingOponentMood=True)
intrinsicWithMoodAgent3 = Intrinsic(selfConfidenceType=CONFIDENCE_PHENOMENOLOGICAL, isUsingSelfMood=True,isUsingOponentMood=True)
intrinsicWithMoodAgent4 = Intrinsic(selfConfidenceType=CONFIDENCE_PHENOMENOLOGICAL, isUsingSelfMood=True,isUsingOponentMood=True)

# intrinsicMoods = [intrinsicWithMoodAgent1, intrinsicWithMoodAgent2,intrinsicWithMoodAgent3, intrinsicWithMoodAgent4]

intrinsicMoods = [intrinsicWithMoodAgent1, intrinsicWithMoodAgent2, intrinsicWithMoodAgent3, intrinsicWithMoodAgent4]

#
# # Generate MoodDataset
# GenerateMoodFromDataset.generateMoodFromDataset(intrinsicModels=intrinsicMoods, dataset=dataSetLocation, agents=agents, loadModels=loadModel,saveDirectory = saveMoodDataset)

# Generate Plots
moodDataset = saveMoodDataset + "/IntrinsicDataset.pkl"
plotsToGenerate = [plots["Experiment_Mood"], plots["Experiment_MoodNeurons"],
                   plots["Experiment_SelfProbabilitySuccess"], plots["Experiment_Winners"], plots["Experiment_FinishingPosition"]]

plot = PlotManager.generateIntrinsicPlotsFromDataset(plotsToGenerate=plotsToGenerate, IntrinsicDataset=moodDataset, gameNumber=2, saveDirectory=saveMoodPlot)
PlotManager.generateExperimentPlotsFromDataset(plotsToGenerate=plotsToGenerate,dataset=dataSetLocation,saveDirectory=saveMoodPlot)