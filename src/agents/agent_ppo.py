# PPO Agent for ChefsHat (Corrected Version)
# NOTE: Assumes environment observation space and action space sizes remain the same

from agents.base_agent import BaseAgent
from ChefsHatGym.rewards.only_winning import RewardOnlyWinning

from keras.layers import Input, Dense, Multiply
from keras.models import Model
from keras.optimizers import Adam
import keras.backend as K
from keras.models import load_model

import numpy as np
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
        LOSS_CLIPPING = 0.2
        ENTROPY_LOSS = 5e-3
        y_true_action = y_true[:, 0:200]
        y_old_pred = y_true[:, 200:400]
        advantage = y_true[:, 400]

        prob = K.sum(y_true_action * y_pred, axis=-1)
        old_prob = K.sum(y_true_action * y_old_pred, axis=-1)
        r = prob / (old_prob + 1e-10)

        entropy = -K.sum(y_pred * K.log(y_pred + 1e-10), axis=-1)

        return -K.mean(
            K.minimum(
                r * advantage,
                K.clip(r, 1 - LOSS_CLIPPING, 1 + LOSS_CLIPPING) * advantage,
            )
            + ENTROPY_LOSS * entropy
        )

    return loss


class AgentPPO(BaseAgent):
    suffix = "PPO"

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
            agentType + "_" + name,
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
        self.save_model = os.path.join(self.log_directory, "savedModel")

        self.type = agentType
        self.reward = RewardOnlyWinning()

        self.startAgent()

        if not self.type == "Scratch":
            fileNameActor = os.path.join(
                os.path.abspath(sys.modules[AgentPPO.__module__].__file__)[0:-6],
                self.loadFrom[agentType][0],
            )
            fileNameCritic = os.path.join(
                os.path.abspath(sys.modules[AgentPPO.__module__].__file__)[0:-6],
                self.loadFrom[agentType][1],
            )
            if not os.path.exists(
                os.path.join(
                    os.path.abspath(sys.modules[AgentPPO.__module__].__file__)[0:-6],
                    "Trained",
                )
            ):
                os.mkdir(
                    os.path.join(
                        os.path.abspath(sys.modules[AgentPPO.__module__].__file__)[
                            0:-6
                        ],
                        "Trained",
                    )
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

    def loadModel(self, model):
        def loss(y_true, y_pred):
            LOSS_CLIPPING = 0.2
            ENTROPY_LOSS = 5e-3
            y_true_action = y_true[:, 0:200]
            y_old_pred = y_true[:, 200:400]
            advantage = y_true[:, 400]

            prob = K.sum(y_true_action * y_pred, axis=-1)
            old_prob = K.sum(y_true_action * y_old_pred, axis=-1)
            r = prob / (old_prob + 1e-10)

            entropy = -K.sum(y_pred * K.log(y_pred + 1e-10), axis=-1)

            return -K.mean(
                K.minimum(
                    r * advantage,
                    K.clip(r, 1 - LOSS_CLIPPING, 1 + LOSS_CLIPPING) * advantage,
                )
                + ENTROPY_LOSS * entropy
            )

        actorModel, criticModel = model
        self.actor = load_model(actorModel, custom_objects={"loss": loss})
        self.critic = load_model(criticModel, custom_objects={"loss": loss})

        self.log(f"--------")
        self.log(f"Loading actor from: {actorModel}")
        self.log(f"Loading critic from: {criticModel}")
        self.log(f"--------")

    def startAgent(self):
        self.hiddenLayers = 2
        self.hiddenUnits = 64
        self.gamma = 0.95
        self.resetMemory()

        self.learning_rate = 1e-4
        self.epsilon = self.initialEpsilon if self.training else 0.0
        self.epsilon_min = 0.1
        self.epsilon_decay = 0.990

        self.buildModel()

    def buildActorNetwork(self):
        inp = Input((28,), name="Actor_State")
        x = inp
        for i in range(self.hiddenLayers + 1):
            x = Dense(
                self.hiddenUnits * (i + 1), activation="relu", name=f"Actor_Dense_{i}"
            )(x)
        out_raw = Dense(200, activation="softmax", name="actor_output")(x)
        action_mask = Input((200,), name="Action_Mask")
        out_masked = Multiply()([out_raw, action_mask])
        self.actor = Model([inp, action_mask], out_masked)
        self.actor.compile(
            optimizer=Adam(self.learning_rate), loss=proximal_policy_optimization_loss()
        )

    def buildCriticNetwork(self):
        inp = Input((28,), name="Critic_State")
        x = inp
        for i in range(self.hiddenLayers + 1):
            x = Dense(
                self.hiddenUnits * (i + 1), activation="relu", name=f"Critic_Dense_{i}"
            )(x)
        out = Dense(1, activation="linear", name="critic_output")(x)
        self.critic = Model(inp, out)
        self.critic.compile(optimizer=Adam(self.learning_rate), loss="mse")

    def buildModel(self):
        self.buildCriticNetwork()
        self.buildActorNetwork()

    def discount(self, r):
        discounted = np.zeros_like(r)
        running_add = 0
        for t in reversed(range(len(r))):
            running_add = r[t] + self.gamma * running_add
            discounted[t] = running_add
        return discounted

    def request_action(self, observations):
        # print(f"Received observation: {observations}")
        # print(f"All actions: {self.all_actions}")

        hand = np.array(observations["hand"]) / 13
        board = np.array(observations["board"]) / 13
        possible_actions = np.array(observations["possible_actions"])

        state = np.concatenate([hand, board])
        action_mask = np.isin(self.all_actions, list(possible_actions)).astype(int)

        # state = np.concatenate((observations[0:11], observations[11:28]))
        # action_mask = observations[28:]

        state_input = np.expand_dims(state, 0)
        mask_input = np.expand_dims(action_mask, 0)

        # print(f"State shape: {state_input.shape}")
        # print(f"Mask shape: {mask_input.shape}")

        if np.random.rand() < self.epsilon:
            valid_indices = np.where(action_mask == 1)[0]
            action_index = np.random.choice(valid_indices)
        else:
            probs = self.actor.predict([state_input, mask_input], verbose=0)[0]
            action_index = np.argmax(probs)
            # probs = probs / np.sum(probs)
            # action_index = np.random.choice(np.arange(len(probs)), p=probs)

        action_onehot = np.zeros(200)
        action_onehot[action_index] = 1

        if self.training:
            self.states.append(state)
            self.actions.append(action_onehot)
            self.possibleActions.append(action_mask)
            old_policy = self.actor.predict([state_input, mask_input], verbose=0)[0]
            self.old_policies.append(old_policy)

        # print(f"Possible Actions: {mask_input}")
        # print(f"Possible Actions: {mask_input}")

        print(f"Returning: {action_index} - {self.all_actions[action_index]}")
        return action_index

    def update_my_action(self, info):
        pass  # Nothing needed here anymore

    def get_reward(self, info):
        # "Chef", "Souschef", "Dishwasher", "Waiter"
        roles = {"Chef": 0, "Souschef": 1, "Waiter": 2, "Dishwasher": 3}
        this_player_index = info["Player_Names"].index(self.name)
        this_player_role = info["Current_Roles"][this_player_index]
        this_player_position = roles[this_player_role]

        reward = self.reward.getReward(this_player_position, True)

        # self.log(f"Player names: {this_player_index} - this player name: {self.name}")

        # self.log(
        #     f"this_player: {this_player_index} - Match_Score this player: {info['Match_Score']} - finished players: {info['Finished_Players']}"
        # )
        self.log(f"Finishing position: {this_player_role} - Reward: {reward} ")
        # self.log(
        #     f"REWARD: This player position: {this_player_position} - this player finished: {this_player_finished} - {reward}"
        # )

        return reward

    def update_end_match(self, info):
        if not self.training:
            return

        reward = self.get_reward(info)
        self.rewards = [reward] * len(self.states)  # fixed length

        states = np.array(self.states)
        actions = np.array(self.actions)
        masks = np.array(self.possibleActions)
        old_policies = np.array(self.old_policies)

        discounted = self.discount(self.rewards)
        values = self.critic.predict(states, verbose=0).flatten()

        assert len(discounted) == len(
            values
        ), f"Length mismatch: discounted={len(discounted)} vs values={len(values)}"

        advantages = discounted - values
        y_train = np.hstack([actions, old_policies, advantages.reshape(-1, 1)])

        critic_loss = self.critic.train_on_batch(states, discounted)
        actor_loss = self.actor.train_on_batch([states, masks], y_train)

        self.actorLoss = actor_loss
        self.criticLoss = critic_loss

        self.log(
            f" -- Match: {info['Matches']} - Epsilon: {self.epsilon:.4f} - Actor Loss: {actor_loss:.4f} - Critic Loss: {critic_loss:.4f}"
        )

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        os.makedirs(self.save_model, exist_ok=True)
        keras.models.save_model(
            self.actor, os.path.join(self.save_model, f"actor_Player_{self.name}.keras")
        )
        keras.models.save_model(
            self.critic,
            os.path.join(self.save_model, f"critic_Player_{self.name}.keras"),
        )

        self.resetMemory()

    def resetMemory(self):
        self.states = []
        self.actions = []
        self.rewards = []
        self.possibleActions = []
        self.old_policies = []

    # Agent Chefs Hat Functions

    def get_exhanged_cards(self, cards, amount):
        selectedCards = sorted(cards[-amount:])
        return selectedCards

    def do_special_action(self, info, specialAction):
        return True

    def update_game_start(self, info):
        self.all_actions = list(info["actions"].values())
        print(f"self.all_actions: {self.all_actions}")
