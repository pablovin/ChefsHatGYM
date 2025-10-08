import os
import numpy as np
from collections import deque
import random
from tensorflow.keras import Input, Model
from tensorflow.keras.layers import Dense, Lambda, Add
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import MeanSquaredError
from tensorflow.keras.models import load_model as keras_load_model
import tensorflow as tf
from .base_agent import BaseAgent
from tensorflow.keras.losses import Huber


def dueling_lambda(a):
    return a - tf.reduce_mean(a, axis=1, keepdims=True)


class DQNAgent(BaseAgent):

    def __init__(
        self,
        name="",
        state_size=28,
        action_size=200,
        gamma=0.99,
        lr=1e-4,
        epsilon=1.0,
        epsilon_min=0.05,
        epsilon_decay=0.995,
        batch_size=512,
        memory_size=10000,
        log_directory: str = "",
        verbose_console: bool = False,
        train: bool = True,
        model_path: str = None,
        load_model: bool = False,
        run_remote=False,
        host="localhost",
        port=8765,
        room_name="room",
        room_password="password",
    ):
        super().__init__(
            name,
            log_directory,
            verbose_console,
            run_remote,
            host,
            port,
            room_name,
            room_password,
        )

        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=memory_size)
        self.gamma = gamma
        self.epsilon = epsilon if train else 0.0
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.batch_size = batch_size
        self.train = train
        self.model_path = model_path
        self.last_state = None
        self.last_action = None
        self.last_possible_actions = None
        self.match_experiences = []
        self.episode = []
        self.loss_history = []
        self.epsilon_history = []
        self.positions = []
        self.score_history = []
        self.all_actions = None
        self.verbose_console = verbose_console
        self.rewards = []

        model_path = os.path.join(log_directory, "model", "dql_model.h5")
        if model_path is not None and load_model and os.path.exists(model_path):
            print(f"Loading main model from {model_path}")
            self.model = keras_load_model(
                model_path, custom_objects={"dueling_lambda": dueling_lambda}
            )
            target_path = model_path.replace(".h5", ".target.h5")
            if os.path.exists(target_path):
                print(f"Loading target model from {target_path}")
                self.target_model = keras_load_model(
                    target_path, custom_objects={"dueling_lambda": dueling_lambda}
                )
            else:
                print("Target model file not found, copying policy weights.")
                self.target_model = self._build_model(lr)
                self.target_model.set_weights(self.model.get_weights())
        else:
            self.model = self._build_model(lr)
            self.target_model = self._build_model(lr)
            self.target_model.set_weights(self.model.get_weights())
        if not self.train:
            self.epsilon = 0.0

    def _build_model(self, lr):
        state_input = Input(shape=(self.state_size,), name="state_input")
        x = Dense(256, activation="relu")(state_input)
        x = Dense(128, activation="relu")(x)
        x = Dense(64, activation="relu")(x)
        value = Dense(1, activation="linear")(x)
        advantage = Dense(self.action_size, activation="linear")(x)
        advantage_mean = Lambda(dueling_lambda, output_shape=(self.action_size,))(
            advantage
        )
        q_values = Add()([value, advantage_mean])
        model = Model(inputs=state_input, outputs=q_values)
        model.compile(loss=Huber(), optimizer=Adam(learning_rate=lr))
        return model

    def remember(
        self,
        state,
        possible_actions,
        action,
        reward,
        next_state,
        next_possible_actions,
        done,
    ):
        if self.train:
            self.memory.append(
                (
                    state,
                    possible_actions,
                    action,
                    reward,
                    next_state,
                    next_possible_actions,
                    done,
                )
            )

    def act(self, state, possible_actions_mask, valid_actions):
        # Identify the index of the "pass" action
        pass_idx = None
        for i, action in enumerate(self.all_actions):
            if str(action).lower() == "pass":
                pass_idx = i
                break

        # Filter valid actions to avoid "pass" if possible
        non_pass_actions = [a for a in valid_actions if a != pass_idx]
        non_pass_mask = np.copy(possible_actions_mask)
        if pass_idx is not None:
            non_pass_mask[pass_idx] = 0

        # If only "pass" is available, fallback to it
        if len(non_pass_actions) == 0:
            action_indices = valid_actions  # Only pass remains
            action_mask = possible_actions_mask
        else:
            action_indices = non_pass_actions
            action_mask = non_pass_mask

        # Exploration: random action
        if self.train and np.random.rand() < self.epsilon:
            return int(np.random.choice(action_indices))

        # Exploitation: network prediction
        q_values = self.model.predict(state[np.newaxis, :], verbose=0)[0]
        masked_q_values = np.where(action_mask, q_values, -np.inf)
        if np.all(masked_q_values == -np.inf):
            return int(np.random.choice(action_indices))
        return int(np.argmax(masked_q_values))

    def soft_update_target_network(self, tau=0.01):
        model_weights = self.model.get_weights()
        target_weights = self.target_model.get_weights()
        new_weights = [
            tau * m + (1 - tau) * t for m, t in zip(model_weights, target_weights)
        ]
        self.target_model.set_weights(new_weights)

    def replay(self):
        if not self.train or len(self.memory) < self.batch_size:
            return

        minibatch = random.sample(self.memory, self.batch_size)
        states = np.array([x[0] for x in minibatch])
        possible_actions_batch = np.array([x[1] for x in minibatch])
        actions = np.array([x[2] for x in minibatch])
        rewards = np.array([x[3] for x in minibatch])
        next_states = np.array([x[4] for x in minibatch])
        next_possible_actions_batch = np.array([x[5] for x in minibatch])
        dones = np.array([x[6] for x in minibatch])

        # Get Q-values for next states using model and target_model
        next_q_values = self.model.predict(next_states, verbose=0)
        # Mask invalid actions in next state by setting to -inf
        next_q_values_masked = np.where(
            next_possible_actions_batch, next_q_values, -np.inf
        )
        next_best_actions = np.argmax(next_q_values_masked, axis=1)
        target_next = self.target_model.predict(next_states, verbose=0)

        # Prepare target
        target = self.model.predict(states, verbose=0)
        losses = []

        for i in range(self.batch_size):
            a = actions[i]
            old_val = target[i][a]
            if dones[i]:
                target[i][a] = rewards[i]
            else:
                # Only allow valid actions in target_next (double Q-learning)
                target[i][a] = (
                    rewards[i] + self.gamma * target_next[i][next_best_actions[i]]
                )
            losses.append(abs(old_val - target[i][a]))

        history = self.model.fit(states, target, epochs=1, verbose=0)
        avg_loss = (
            float(np.mean(losses))
            if losses
            else float(np.mean(history.history["loss"]))
        )
        self.loss_history.append(avg_loss)
        self.epsilon_history.append(self.epsilon)
        if self.epsilon > self.epsilon_min and self.train:
            self.epsilon *= self.epsilon_decay

        self.soft_update_target_network(tau=0.05)

    # Integration functions and reward shaping as before (unchanged)

    def update_game_start(self, info):

        self.score_history = []

        if "actions" in info:
            self.all_actions = list(info["actions"].values())
            if self.verbose_console:
                self.log(f"Received ordered list of Actions: {self.all_actions}")

    def update_game_over(self, payload):

        if self.train and self.model_path:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            self.model.save(self.model_path)
            self.target_model.save(self.model_path.replace(".h5", ".target.h5"))

    def update_new_hand(self, payload):
        self.episode = []
        self.last_state = None
        self.last_action = None
        self.last_possible_actions = None

    def request_cards_to_exchange(self, payload):
        return sorted(payload["hand"])[-payload["n"] :]

    def request_special_action(self, payload):
        return True

    def request_action(self, observations):
        hand = np.array(observations["hand"]).flatten() / 13
        board = np.array(observations["board"]).flatten() / 13
        possible_actions_values = list(observations["possible_actions"])

        obs = np.concatenate([hand, board])
        possible_actions_mask = np.zeros(self.action_size, dtype=np.float32)
        valid_action_indices = [
            self.all_actions.index(val) for val in possible_actions_values
        ]
        possible_actions_mask[valid_action_indices] = 1.0

        action_index = self.act(obs, possible_actions_mask, valid_action_indices)
        action_str = self.all_actions[action_index]

        # --- Reward Shaping (unchanged) ---
        shaped_reward = 0.0
        if action_str.lower() == "pass":
            shaped_reward -= 1.0

        shaped_reward -= 0.02

        if (
            self.last_state is not None
            and self.last_action is not None
            and self.train
            and self.last_possible_actions is not None
        ):
            self.episode.append(
                (
                    self.last_state,
                    self.last_possible_actions,
                    self.last_action,
                    shaped_reward,
                    obs,
                    possible_actions_mask,
                    False,
                )
            )
        self.last_state = obs
        self.last_action = action_index
        self.last_possible_actions = possible_actions_mask
        return action_index

    def update_match_over(self, payload):
        finishing_order = payload.get("finishing_order", [])
        scores = payload.get("scores", {})
        player_name = self.name

        # print(f"Scores: {payload['scores']} ")
        self.score_history.append(payload["scores"].copy())

        try:
            place = finishing_order.index(player_name) + 1
        except ValueError:
            place = len(finishing_order)

        reward, place = self._get_final_reward_and_place(payload)
        self.rewards.append(reward)
        self.positions.append(place)

        if (
            self.last_state is not None
            and self.last_action is not None
            and self.train
            and self.last_possible_actions is not None
        ):
            self.episode.append(
                (
                    self.last_state,
                    self.last_possible_actions,
                    self.last_action,
                    reward,
                    self.last_state,
                    self.last_possible_actions,
                    True,
                )
            )
        for exp in self.episode:
            self.remember(*exp)
        self.episode = []
        self.replay()

    def _get_final_reward_and_place(self, payload):
        player_name = self.name
        finishing_order = payload.get("finishing_order", [])
        scores = payload.get("scores", {})

        try:
            place = finishing_order.index(player_name) + 1
        except ValueError:
            place = len(finishing_order) if finishing_order else 4

        # reward = scores.get(player_name, 0)
        # print(f"Fiishing order: {finishing_order}")
        reward = 3 if place == 1 else -0.02
        # print(f"Finishing order: {place}")
        # print(f"Reward: {reward}")
        return reward, place

    # Plotting functions unchanged

    # ==== Plotting functions ====

    def plot_loss(self, path: str):
        import matplotlib.pyplot as plt

        if (
            not hasattr(self, "loss_history")
            or not hasattr(self, "epsilon_history")
            or len(self.loss_history) == 0
        ):
            print("[plot_loss] Warning: No loss or epsilon history to plot.")
            return

        steps = range(len(self.loss_history))
        fig, ax1 = plt.subplots()

        color_loss = "tab:blue"
        ax1.set_xlabel("Training Step")
        ax1.set_ylabel("Loss", color=color_loss)
        ax1.plot(steps, self.loss_history, color=color_loss, label="Loss")
        ax1.tick_params(axis="y", labelcolor=color_loss)

        ax2 = ax1.twinx()
        color_eps = "tab:red"
        ax2.set_ylabel("Epsilon", color=color_eps)
        ax2.plot(steps, self.epsilon_history, color=color_eps, label="Epsilon")
        ax2.tick_params(axis="y", labelcolor=color_eps)

        lines, labels = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines + lines2, labels + labels2, loc="upper right")

        plt.title("DQN Loss and Epsilon")
        fig.tight_layout()
        plt.savefig(path)
        plt.close(fig)

    def plot_positions(self, path: str):
        import matplotlib.pyplot as plt

        if not hasattr(self, "positions") or not self.positions:
            print("[plot_positions] Warning: No position data to plot.")
            return

        plt.figure()
        x = range(len(self.positions))
        y = self.positions
        plt.plot(x, y, label="Position", linestyle="-", marker="o", alpha=0.8)
        plt.xlabel("Match")
        plt.ylabel("Position (1=1st, 4=4th)")
        plt.title("Agent Position per Match")
        plt.gca().invert_yaxis()  # 1st place at the top
        plt.legend()
        plt.tight_layout()
        plt.savefig(path)
        plt.close()

    def plot_rewards(self, path: str, path_averaged: str, window: int = 10):
        import matplotlib.pyplot as plt

        if not hasattr(self, "rewards"):
            print("[plot_positions] Warning: No rewards data to plot.")
            return

        plt.figure()
        x = range(len(self.rewards))
        y = self.rewards
        plt.plot(x, y, label="Position", linestyle="-", marker="o", alpha=0.8)
        plt.xlabel("Match")
        plt.ylabel("Rewards per match")
        plt.title("Agent Reward per Match")
        plt.legend()
        plt.tight_layout()
        plt.savefig(path)
        plt.close()

        import matplotlib.pyplot as plt
        import numpy as np

        if not hasattr(self, "rewards"):
            print("[plot_rewards] Warning: No rewards data to plot.")
            return

        rewards = np.array(self.rewards)
        x = np.arange(len(rewards))

        # Compute rolling average
        if len(rewards) >= window:
            rewards_avg = np.convolve(rewards, np.ones(window) / window, mode="valid")
            x_avg = np.arange(window - 1, len(rewards))
        else:
            rewards_avg = rewards
            x_avg = x

        plt.cla()
        plt.figure()
        plt.plot(x, rewards, label="Reward (raw)", linestyle="-", marker="o", alpha=0.4)
        plt.plot(
            x_avg, rewards_avg, label=f"Reward (avg {window})", linewidth=2, alpha=0.9
        )

        plt.xlabel("Match")
        plt.ylabel("Rewards per match")
        plt.title("Agent Reward per Match")
        plt.legend()
        plt.tight_layout()
        plt.savefig(path_averaged)
        plt.close()

    def plot_score_progression(self, path: str):
        """
        Plots the score progression for each player over matches.
        - score_history: list of dicts, each dict is {player: score} for one match.
        """
        import matplotlib.pyplot as plt

        # Build cumulative score for each player
        players = sorted(list(self.score_history[0].keys()))
        scores_per_player = {p: [] for p in players}
        cumulative = {p: 0 for p in players}
        for match in self.score_history:
            for p in players:
                cumulative[p] = match[p]
                scores_per_player[p].append(cumulative[p])

        plt.figure(figsize=(8, 5))
        for p in players:
            plt.plot(scores_per_player[p], label=p)
        plt.xlabel("Match")
        plt.ylabel("Cumulative Score")
        plt.title("Score Progression per Player")
        plt.legend()
        plt.tight_layout()
        plt.savefig(path)
        plt.close()
