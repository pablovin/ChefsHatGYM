# Adapted from: https://github.com/LuEE-C/PPO-Keras/blob/master/Main.py
from agents.base_agent import BaseAgent
from ChefsHatGym.rewards.only_winning import RewardOnlyWinning

from keras.layers import Input, Dense, Multiply
from keras.models import Model
from keras.optimizers import Adam
import keras.backend as K
from keras.models import load_model


import random
import numpy
import copy
import os
import sys
import urllib.request
import keras
from typing import Literal
import tensorflow as tf

tf.experimental.numpy.experimental_enable_numpy_behavior()


def proximal_policy_optimization_loss():
    def loss(y_true, y_pred):
        LOSS_CLIPPING = 0.2  # Only implemented clipping for the surrogate loss, paper said it was best
        ENTROPY_LOSS = 5e-3
        y_tru_valid = y_true[:, 0:200]
        old_prediction = y_true[:, 200:400]
        advantage = y_true[:, 400][0]

        prob = K.sum(y_tru_valid * y_pred, axis=-1)
        old_prob = K.sum(y_tru_valid * old_prediction, axis=-1)
        r = prob / (old_prob + 1e-10)

        return -K.mean(
            K.minimum(
                r * advantage,
                K.clip(r, min_value=1 - LOSS_CLIPPING, max_value=1 + LOSS_CLIPPING)
                * advantage,
            )
            + ENTROPY_LOSS * -(prob * K.log(prob + 1e-10))
        )

    return loss


# Adapted from: https://github.com/germain-hug/Deep-RL-Keras

types = ["Scratch", "vsRandom", "vsEveryone", "vsSelf"]


class AgentPPO(BaseAgent):
    suffix = "PPO"
    actor = None
    training = False

    loadFrom = {
        "vsRandom": [
            "Trained/ppo_actor_vsRandom.hd5",
            "Trained/ppo_critic_vsRandom.hd5",
        ],
        "vsEveryone": [
            "Trained/ppo_actor_vsEveryone.hd5",
            "Trained/ppo_critic_vsEveryone.hd5",
        ],
        "vsSelf": ["Trained/ppo_actor_vsSelf.hd5", "Trained/ppo_critic_vsSelf.hd5"],
    }

    downloadFrom = {
        "vsRandom": [
            "https://github.com/pablovin/ChefsHatPlayersClub/raw/main/src/ChefsHatPlayersClub/agents/classic/Trained/ppo_actor_vsRandom.hd5",
            "https://github.com/pablovin/ChefsHatPlayersClub/raw/main/src/ChefsHatPlayersClub/agents/classic/Trained/ppo_critic_vsRandom.hd5",
        ],
        "vsEveryone": [
            "https://github.com/pablovin/ChefsHatPlayersClub/raw/main/src/ChefsHatPlayersClub/agents/classic/Trained/ppo_actor_vsEveryone.hd5",
            "https://github.com/pablovin/ChefsHatPlayersClub/raw/main/src/ChefsHatPlayersClub/agents/classic/Trained/ppo_critic_vsEveryone.hd5",
        ],
        "vsSelf": [
            "https://github.com/pablovin/ChefsHatPlayersClub/raw/main/src/ChefsHatPlayersClub/agents/classic/Trained/ppo_actor_vsSelf.hd5",
            "https://github.com/pablovin/ChefsHatPlayersClub/raw/main/src/ChefsHatPlayersClub/agents/classic/Trained/ppo_critic_vsSelf.hd5",
        ],
    }

    def __init__(
        self,
        name: str,
        continueTraining=False,
        agentType="Scratch",
        initialEpsilon=1.0,
        loadNetwork="",
        saveFolder="",
        verbose_console=False,
        verbose_log=False,
        log_directory="",
    ):

        super().__init__(
            self.suffix + "_" + agentType + "_" + name,
            # this_agent_folder=saveFolder,
            # verbose_console=verbose_console,
            # verbose_log=verbose_log,
            log_directory=log_directory,
        )

        if continueTraining:
            assert log_directory != "", "Log directory required for training."

        self.training = continueTraining
        self.initialEpsilon = initialEpsilon
        self.loadNetwork = loadNetwork
        self.save_model = os.path.join(self.this_log_folder, "savedModel")

        self.type = agentType
        self.reward = RewardOnlyWinning()

        self.startAgent()

        if not self.type == "Scratch":
            path = os.path.join(
                os.path.abspath(sys.modules[AgentPPO.__module__].__file__)[0:-6],
                "Trained",
            )
            print(f"Saving here: {path}")
            fileNameActor = os.path.join(
                os.path.abspath(sys.modules[AgentPPO.__module__].__file__)[0:-6],
                self.loadFrom[agentType][0],
            )
            fileNameCritic = os.path.join(
                os.path.abspath(sys.modules[AgentPPO.__module__].__file__)[0:-6],
                self.loadFrom[agentType][1],
            )
            os.makedirs(
                os.path.join(
                    os.path.abspath(sys.modules[AgentPPO.__module__].__file__)[0:-6],
                    "Trained",
                ),
                exist_ok=True,
            )

            if not os.path.exists(fileNameCritic):
                urllib.request.urlretrieve(
                    self.downloadFrom[agentType][0], fileNameActor
                )
                urllib.request.urlretrieve(
                    self.downloadFrom[agentType][1], fileNameCritic
                )

            self.loadModel([fileNameActor, fileNameCritic])

        if not loadNetwork == "":
            self.loadModel(loadNetwork)

        self.old_policies = []

    # PPO Functions
    def startAgent(self):
        self.hiddenLayers = 2
        self.hiddenUnits = 64
        self.gamma = 0.95  # discount rate

        # Game memory
        self.resetMemory()

        self.learning_rate = 1e-4

        if self.training:
            self.epsilon = self.initialEpsilon  # exploration rate while training
        else:
            self.epsilon = 0.0  # no exploration while testing

        self.epsilon_min = 0.1
        self.epsilon_decay = 0.990

        self.buildModel()

    def buildActorNetwork(self):
        inputSize = 28
        inp = Input((inputSize,), name="Actor_State")

        for i in range(self.hiddenLayers + 1):
            if i == 0:
                previous = inp
            else:
                previous = dense

            dense = Dense(
                self.hiddenUnits * (i + 1),
                name="Actor_Dense" + str(i),
                activation="relu",
            )(previous)

        outputActor = Dense(200, activation="softmax", name="actor_output")(dense)

        actionsOutput = Input(shape=(200,), name="PossibleActions")

        outputPossibleActor = Multiply()([actionsOutput, outputActor])

        self.actor = Model([inp, actionsOutput], outputPossibleActor)

        self.actor.compile(
            optimizer=Adam(learning_rate=self.learning_rate),
            loss=[proximal_policy_optimization_loss()],
        )

    def buildCriticNetwork(self):
        # Critic model
        inputSize = 28

        inp = Input((inputSize,), name="Critic_State")

        for i in range(self.hiddenLayers + 1):
            if i == 0:
                previous = inp
            else:
                previous = dense

            dense = Dense(
                self.hiddenUnits * (i + 1),
                name="Critic_Dense" + str(i),
                activation="relu",
            )(previous)

        outputCritic = Dense(1, activation="linear", name="critic_output")(dense)

        self.critic = Model([inp], outputCritic)

        self.critic.compile(Adam(self.learning_rate), "mse")

    def buildModel(self):
        self.buildCriticNetwork()
        self.buildActorNetwork()

    def discount(self, r):
        """Compute the gamma-discounted rewards over an episode"""
        discounted_r, cumul_r = numpy.zeros_like(r), 0
        for t in reversed(range(0, len(r))):
            cumul_r = r[t] + cumul_r * self.gamma
            discounted_r[t] = cumul_r
        return discounted_r

    def loadModel(self, model):
        def loss(y_true, y_pred):
            LOSS_CLIPPING = 0.2  # Only implemented clipping for the surrogate loss, paper said it was best
            ENTROPY_LOSS = 5e-3
            y_tru_valid = y_true[:, 0:200]
            old_prediction = y_true[:, 200:400]
            advantage = y_true[:, 400][0]

            prob = K.sum(y_tru_valid * y_pred, axis=-1)
            old_prob = K.sum(y_tru_valid * old_prediction, axis=-1)
            r = prob / (old_prob + 1e-10)

            return -K.mean(
                K.minimum(
                    r * advantage,
                    K.clip(r, min_value=1 - LOSS_CLIPPING, max_value=1 + LOSS_CLIPPING)
                    * advantage,
                )
                + ENTROPY_LOSS * -(prob * K.log(prob + 1e-10))
            )

        actorModel, criticModel = model
        self.actor = load_model(actorModel, custom_objects={"loss": loss})
        self.critic = load_model(criticModel, custom_objects={"loss": loss})

        self.log(f"--------")
        self.log(f"Loading actor from: {actorModel}")
        self.log(f"Loading critic from: {criticModel}")
        self.log(f"--------")

    def updateModel(self, last_reward):

        state = numpy.array(self.states)

        action = self.actions
        # reward = numpy.array(self.rewards)
        reward = numpy.full(len(state), last_reward)

        possibleActions = numpy.array(self.possibleActions)
        realEncoding = numpy.array(self.realEncoding)

        # Compute discounted rewards and Advantage (TD. Error)
        discounted_rewards = self.discount(reward)
        state_values = self.critic(numpy.array(state))
        advantages = discounted_rewards - numpy.reshape(state_values, len(state_values))

        criticLoss = self.critic.train_on_batch([state], [reward])

        actions = []
        for i in range(len(action)):
            advantage = numpy.zeros(numpy.array(action[i]).shape)
            advantage[0] = advantages[i]
            # print ("advantages:" + str(numpy.array(advantage).shape))
            # print ("actions:" + str(numpy.array(action[i]).shape))
            # print("realEncoding:" + str(numpy.array(realEncoding[i]).shape))
            concatenated = numpy.concatenate((action[i], realEncoding[i], advantage))
            actions.append(concatenated)
        actions = numpy.array(actions)

        actorLoss = self.actor.train_on_batch([state, possibleActions], [actions])

        # Update the decay
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        # self.log(f" -- Reward: {reward}")
        self.log(f" -- Discounted reward: {discounted_rewards}")
        self.log(
            f" -- Epsilon: {self.epsilon} - Actor Loss: {actorLoss} - Critic Loss: {criticLoss}"
        )
        self.actorLoss = actorLoss
        self.criticLoss = criticLoss

    def resetMemory(self):
        self.states = []
        self.actions = []
        self.rewards = []
        self.possibleActions = []
        self.realEncoding = []

    # Agent Chefs Hat Functions

    def request_cards_to_exchange(self, info):
        # print (F"HERE!")
        return sorted(info["hand"])[-info["n"] :]

    def request_special_action(self, info):
        return True

    def get_reward(self, info):
        # "Chef", "Souschef", "Dishwasher", "Waiter"
        roles = {"Chef": 0, "Souschef": 1, "Waiter": 2, "Dishwasher": 3}
        # this_player_index = info["Player_Names"].index(self.name)
        this_player_position = 3 - info["finishing_order"].index(self.name)

        # this_player_role = info["scores"][this_player_index]
        # this_player_position = roles[this_player_role]

        reward = self.reward.getReward(this_player_position, True)

        # self.log(f"Player names: {this_player_index} - this player name: {self.name}")

        # self.log(
        #     f"this_player: {this_player_index} - Match_Score this player: {info['Match_Score']} - finished players: {info['Finished_Players']}"
        # )
        self.log(f"Finishing position: {this_player_position} - Reward: {reward} ")
        # self.log(
        #     f"REWARD: This player position: {this_player_position} - this player finished: {this_player_finished} - {reward}"
        # )

        return reward

    def request_action(self, observations):
        # stateVector = numpy.concatenate((observations[0:11], observations[11:28]))
        # possibleActions = observations[28:]

        # stateVector = numpy.expand_dims(numpy.array(stateVector), 0)
        # possibleActions2 = copy.copy(possibleActions)

        hand = numpy.array(observations["hand"]) / 13
        board = numpy.array(observations["board"]) / 13
        possible_actions = numpy.array(observations["possible_actions"])

        stateVector = numpy.concatenate([board, hand]).astype(
            numpy.float32
        )

        possibleActions = numpy.isin(self.all_actions, list(possible_actions)).astype(
            int
        )
        possibleActions2 = possibleActions.copy()

        randNum = numpy.random.rand()

        if randNum <= self.epsilon:

            itemindex = numpy.array(numpy.where(numpy.array(possibleActions2) == 1))[
                0
            ].tolist()
            if len(itemindex) > 1:
                itemindex.pop()

            a_index = itemindex[-1:][0]
            # a = numpy.zeros(200)
            # a[a_index] = 1

            # print(f"randNum: {randNum} - epsilon: {self.epsilon}")
        else:
            sumBefore = numpy.sum(possibleActions)

            if numpy.sum(possibleActions2) > 1:
                possibleActions2[-1] = 0
            # print(
            #     f"Sum possible actions before: {sumBefore} after: {numpy.sum(possibleActions2)}"
            # )
            stateVector = numpy.expand_dims(numpy.array(stateVector), 0)
            possibleActionsVector = numpy.expand_dims(numpy.array(possibleActions2), 0)
            # self.log(f"-------------------")
            # self.log(f"State vector: {stateVector} ")
            # self.log(f"Possible Actions: {possible_actions} ")
            # self.log(f"possibleActionsVector vector: {possibleActionsVector} ")

            # print(f"State Vector shape: {stateVector.shape}")
            # print(f"possibleActionsVector shape: {possibleActionsVector.shape}")
            # print (f"sate vector: {stateVector} ")
            a = self.actor([stateVector, possibleActionsVector])[0]
            # self.log(f"Output: {a} ")
            # self.log(f"Output: {numpy.argmax(a)} ")

            a_index = numpy.argmax(a)

        # print(f"Action: {a_index} - {self.all_actions[a_index]} - {a}")
        # print (f"A INDEX: {a_index}")
        return a_index

    def update_match_over(self, info):
        if self.training:
            self.log(f"--------")
            self.log(f"Match Over! Updating the Model!")
            self.log(f"--------")
            last_reward = self.get_reward(info)
            self.updateModel(last_reward)
            self.log(f"--------")

            # save model

            self.log(f"--------")
            self.log(f"Saving model here: {self.save_model}")
            self.log(f"--------")

            os.makedirs(self.save_model, exist_ok=True)
            keras.models.save_model(
                self.actor,
                os.path.join(
                    self.save_model,
                    "actor_Player_" + str(self.name) + ".keras",
                ),
            )

            keras.models.save_model(
                self.critic,
                os.path.join(
                    self.save_model,
                    "critic_Player_" + str(self.name) + ".keras",
                ),
            )

            self.resetMemory()

    def update_player_action(self, info):

        if info["player"] == self.name and self.training:

            self.log(
                f"---- Saving training data in agent memory! Total actions saved: {len(self.states)} ----"
            )
            action_index = self.all_actions.index(info["action"])


            hand = numpy.array(info["observation_before"]["hand"]) / 13
            board = numpy.array(info["observation_before"]["board"]) / 13
            possible_actions = numpy.array(info["observation_before"]["possible_actions"])

            stateVector = numpy.concatenate([board, hand])

            possibleActions = numpy.isin(self.all_actions, list(possible_actions)).astype(
                int
            )

            observation_before = numpy.concatenate([board, hand, possibleActions])

            observation = numpy.array(observation_before)

            state = numpy.concatenate((observation[0:11], observation[11:28]))
            possibleActions = observation[28:]

            action = numpy.zeros(200)
            action[action_index] = 1

            self.states.append(state)
            self.actions.append(action)
            # self.rewards.append(reward)
            self.possibleActions.append(possibleActions)
            self.realEncoding.append(action)

    def update_game_start(self, info):
        self.all_actions = list(info["actions"].values())
        # print(f"self.all_actions: {self.all_actions}")
