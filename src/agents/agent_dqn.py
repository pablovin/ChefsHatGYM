import os
import numpy as np
from tensorflow.keras import Model
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.optimizers import Adam

from .base_agent import BaseAgent


class AgentDQN(BaseAgent):
    """Deep Q-Learning agent for Chef's Hat."""

    def __init__(
        self,
        name: str,
        training: bool = False,
        log_directory: str = "",
        verbose_console: bool = False,
    ):
        super().__init__(name, log_directory, verbose_console)
        self.training = training
        self.gamma = 0.95
        self.epsilon = 1.0 if training else 0.0
        self.epsilon_min = 0.1
        self.epsilon_decay = 0.995
        self.lr = 1e-3
        self.all_actions = []
        self.memory = []
        self._build_model()

    def _build_model(self):
        inp = Input(shape=(28,))
        x = Dense(64, activation="relu")(inp)
        x = Dense(64, activation="relu")(x)
        out = Dense(200, activation="linear")(x)
        self.model = Model(inp, out)
        self.model.compile(optimizer=Adam(self.lr), loss="mse")

    # ------------------------------------------------------------------
    # Game update callbacks
    # ------------------------------------------------------------------
    def update_game_start(self, info):
        self.all_actions = list(info["actions"].values())
        self.log(f"Received ordered list of Actions: {self.all_actions}")

    def update_game_over(self, payload):
        self.log(f"Game over! Received payload {payload}")

    def update_new_hand(self, payload):
        self.hand = payload["hand"]
        self.log(f"My Hand: {self.hand}")

    def update_new_roles(self, payload):
        pass

    def update_food_fight(self, payload):
        pass

    def update_dinner_served(self, payload):
        pass

    def update_hand_after_exchange(self, payload):
        pass

    def update_start_match(self, payload):
        self.hand = payload["hand"]
        self.log(f"Update start match! Received payload: {payload}")

    def update_match_over(self, payload):
        if not self.training:
            return
        reward = self._calculate_reward(payload.get("finishing_order", []))
        if self.memory:
            self.memory[-1]["reward"] = reward
            self.memory[-1]["done"] = True
            self._train_from_memory()
            self.memory = []
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        self.log(
            f"Match over. Finishing order: {payload.get('finishing_order')} - Reward: {reward}"
        )

    def update_player_action(self, payload):
        if payload.get("player") != self.name or not self.training:
            return
        prev_ob = payload.get("observation_before")
        next_ob = payload.get("observation_after")
        if not prev_ob or not next_ob:
            return
        state = np.concatenate(
            [np.array(prev_ob["hand"]) / 13, np.array(prev_ob["board"]) / 13]
        )
        next_state = np.concatenate(
            [np.array(next_ob["hand"]) / 13, np.array(next_ob["board"]) / 13]
        )
        mask_state = np.isin(self.all_actions, prev_ob["possible_actions"]).astype(int)
        mask_next = np.isin(self.all_actions, next_ob["possible_actions"]).astype(int)
        self.memory.append(
            {
                "state": state,
                "action": payload["action_index"],
                "mask": mask_state,
                "next_state": next_state,
                "next_mask": mask_next,
                "reward": 0.0,
                "done": False,
            }
        )

    def update_pizza_declared(self, payload):
        pass

    # ------------------------------------------------------------------
    # Requests
    # ------------------------------------------------------------------
    def request_cards_to_exchange(self, payload):
        return sorted(payload["hand"])[-payload["n"] :]

    def request_special_action(self, payload):
        return True

    def request_action(self, observations):
        hand = np.array(observations["hand"]) / 13
        board = np.array(observations["board"]) / 13
        possible_actions = np.array(observations["possible_actions"])
        state = np.concatenate([hand, board])
        mask = np.isin(self.all_actions, list(possible_actions)).astype(int)

        if np.random.rand() < self.epsilon:
            valid_indices = np.where(mask == 1)[0]
            action_index = int(np.random.choice(valid_indices))
        else:
            q_values = self.model.predict(state[None], verbose=0)[0]
            q_values[mask == 0] = -np.inf
            action_index = int(np.argmax(q_values))
        return action_index

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------
    def _calculate_reward(self, order):
        if not order or self.name not in order:
            return 0.0
        pos = order.index(self.name)
        rewards = {0: 1.0, 1: 0.5, 2: 0.1, 3: -1.0}
        return rewards.get(pos, -1.0)

    def _train_from_memory(self):
        batch = self.memory
        states = np.array([m["state"] for m in batch])
        next_states = np.array([m["next_state"] for m in batch])
        actions = np.array([m["action"] for m in batch])
        next_masks = np.array([m["next_mask"] for m in batch])
        rewards = np.array([m["reward"] for m in batch])
        dones = np.array([m["done"] for m in batch])

        q_values = self.model.predict(states, verbose=0)
        q_next = self.model.predict(next_states, verbose=0)
        q_next[next_masks == 0] = -np.inf
        max_next = np.max(q_next, axis=1)

        for i in range(len(batch)):
            target = rewards[i]
            if not dones[i]:
                target += self.gamma * max_next[i]
            q_values[i, actions[i]] = target

        self.model.fit(states, q_values, epochs=1, verbose=0)

