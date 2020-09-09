from Agents import AgentRandom, AgentDQL, AgentA2C, AgentPPO
from Adaptive_Agents import AIRL

import numpy

AGENTTYPE = {"DQL":"DQL", "A2C":"A2C", "PPO":"PPO", "LilDJ":"LilDJ", "RANDOM":"RANDOM"}


def getAgent(agentType, agentName, loadTrainedModel=False,trainable=False):

    loadFrom = ""
    if agentType == AGENTTYPE["DQL"]:
        agent = AgentDQL.AgentDQL([trainable, 1.0, agentName])
        if loadTrainedModel:
            loadFrom =  "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/TrainedModels/DQL_vsRandom/actor_iteration_999_Player_0.hd5"

    elif agentType == AGENTTYPE["A2C"]:
        agent = AgentA2C.AgentA2C([trainable, 1.0, agentName])
        if loadTrainedModel:

            A2cActor = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/TrainedModels/A2C_vsRandom/actor_iteration_999_Player_0.hd5"
            A2cCritic = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/TrainedModels/A2C_vsRandom/critic_iteration_999_Player_0.hd5"

            loadFrom = [A2cActor, A2cCritic]

    elif agentType == AGENTTYPE["PPO"]:
        agent = AgentPPO.AgentPPO([trainable, 1.0, agentName])
        if loadTrainedModel:

            PPOActor = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/TrainedModels/PPO_vsRandom/actor_iteration_999_Player_0.hd5"
            PPOCritic = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/TrainedModels/PPO_vsRandom/critic_iteration_999_Player_0.hd5"

            loadFrom = [PPOActor, PPOCritic]

    elif agentType == AGENTTYPE["LilDJ"]:
        demonstrations = numpy.load(
            "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/HumanData/DJ/Demonstrations.npy",
            allow_pickle=True)

        agent = AIRL.AgentAIRL([trainable, 1.0, agentName, None, demonstrations])  # training agent
        if loadTrainedModel:

            AIRLModel = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/HumanData/DJ/DJAgent_Training/Player_4_Cards_11_games_1000TrainingAgents_['DQL_AIRL_DJ', 'DUMMY_RANDOM', 'DUMMY_RANDOM', 'DUMMY_RANDOM']_Reward_OnlyWinning_DJ_Agent_2020-05-03_18:52:16.529786/Model/actor_iteration_499_Player_0.hd5"
            AIRLReward = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/HumanData/DJ/DJAgent_Training/Player_4_Cards_11_games_1000TrainingAgents_['DQL_AIRL_DJ', 'DUMMY_RANDOM', 'DUMMY_RANDOM', 'DUMMY_RANDOM']_Reward_OnlyWinning_DJ_Agent_2020-05-03_18:52:16.529786/Model/reward_iteration_499_Player_0.hd5"

            loadFrom = [AIRLModel, AIRLReward]

    elif agentType == AGENTTYPE["RANDOM"]:

        agent = AgentRandom.AgentRandom(AgentRandom.DUMMY_RANDOM, agentName)

    return agent, loadFrom



