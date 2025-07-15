# core/room.py
from core.game_env.game import Game
import random
import os
from datetime import datetime
from core.utils.rules import get_high_level_actions
from core.logging.room_logger import RoomLogger
from core.logging.engine_logger import EngineLogger


class Room:

    def __init__(
        self,
        player_agents,
        max_matches=3,
        max_rounds=None,
        max_score=None,
        output_folder="outputs",
        room_name="room",
        max_invalid_attemps_per_player=5,
        save_logs_room=True,
        save_logs_game=True,
        save_game_dataset=True,
    ):

        self.player_agents = {agent.name: agent for agent in player_agents}
        self.max_invalid_attempts = max_invalid_attemps_per_player
        self.invalid_counts = {agent.name: 0 for agent in player_agents}

        # Include microseconds so directories are always unique
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        self.room_dir = os.path.join(output_folder, f"{room_name}_{timestamp}")
        os.makedirs(self.room_dir, exist_ok=True)

        self.room_logger = RoomLogger(
            room_name,
            timestamp,
            player_names=[agent.name for agent in player_agents],
            config={
                "max_matches": max_matches,
                "max_rounds": max_rounds,
                "max_score": max_score,
                "max_invalid_attempts_per_player": max_invalid_attemps_per_player,
            },
            save_logs=save_logs_room,
            output_folder=self.room_dir,
        )

        self.engine_logger = EngineLogger(
            room_name,
            timestamp,
            player_names=[agent.name for agent in player_agents],
            config={
                "max_matches": max_matches,
                "max_rounds": max_rounds,
                "max_score": max_score,
                "max_invalid_attempts_per_player": max_invalid_attemps_per_player,
            },
            save_logs=save_logs_game,
            output_folder=self.room_dir,
        )

        self.game = Game(
            player_names=list(self.player_agents.keys()),
            max_matches=max_matches,
            max_rounds=max_rounds,
            max_score=max_score,
            logger=self.engine_logger,
            save_dataset=save_game_dataset,
            dataset_directory=self.room_dir,
        )

        self.action_lookup = {
            i: action for i, action in enumerate(get_high_level_actions())
        }
        self.match_initialized = False

    def notify_all(self, method, *args):
        for name, agent in self.player_agents.items():
            self.room_logger.room_log(
                f"Notify ALL -> {name} | method={method} | args={args}"
            )
            getattr(agent, method)(*args)

    def notify_one(self, player_name, method, *args):
        self.room_logger.room_log(
            f"Notify ONE -> {player_name} | method={method} | args={args}"
        )
        getattr(self.player_agents[player_name], method)(*args)

    def request_one(self, player_name, method, *args):
        self.room_logger.room_log(
            f"Request ONE -> {player_name} | method={method} | args={args}"
        )
        result = getattr(self.player_agents[player_name], method)(*args)
        self.room_logger.room_log(f"Response from {player_name}: {result}")
        return result

    def _index_by_name(self, name):
        for i, agent in enumerate(self.player_agents):
            if self.player_agents[agent].name == name:
                return i
        return -1

    # NEW: helper to get a player's hand for agent request (relays to Game)
    def get_player_hand(self, player_name):
        player_index = self._index_by_name(player_name)
        return self.game.players[player_index].cards

    def run(self):
        self.game.start()
        self.room_logger.room_log("\n=== GAME STARTED ===")
        self.room_logger.room_log(
            f"Game setup: Players={len(self.player_agents)}, Max Matches={self.game.max_matches}, Max Rounds={self.game.max_rounds}, Max Score={self.game.max_score}"
        )

        self.notify_all(
            "update_game_start",
            {
                "opponents": [self.player_agents[a].name for a in self.player_agents],
                "actions": self.action_lookup,
                "max_rounds": self.game.max_rounds,
                "max_matches": self.game.max_matches,
                "max_points": self.game.max_score,
            },
        )

        while not self.game.finished:
            self.game.deal_cards()
            self.room_logger.room_log(f"\n--- CARDS HANDED TO PLAYERS ---")
            hands = [player.cards for player in self.game.players].copy()
            for agent, hand in zip(self.player_agents, hands):
                self.notify_one(
                    self.player_agents[agent].name,
                    "update_new_hand",
                    {"hand": hand},
                )

            # If this is the second or more match
            if self.game.current_match_count > 0:
                self.game.assign_roles()
                self.notify_all("update_new_roles", self.game.get_roles())

                # Check for special actions
                special_opts = self.game.get_joker_special_options()
                dinner_serve_action = False
                food_fight_action = False

                for player_name, info in special_opts.items():
                    # Ask only this player if they want to use the special action.
                    wants = self.request_one(
                        player_name,
                        "request_special_action",
                        {
                            "option": info["option"],
                            "hand": self.get_player_hand(player_name),
                            "role": info["role"],
                        },
                    )

                    if wants:  # Agent returns True or truthy to activate.
                        self.game.apply_joker_special(player_name, info["option"])
                        # Inform all agents about what happened
                        if info["option"] == "food_fight":
                            self.notify_all(
                                "update_food_fight",
                                {"by": player_name, "new_roles": self.game.get_roles()},
                            )
                            food_fight_action = True
                        else:
                            self.notify_all("update_dinner_served", {"by": player_name})
                            dinner_serve_action = True
                        special_done = True
                        break  # Only one special action per match!

                # IF the special action about food fight is not declared, do the cards exchange
                if not food_fight_action:
                    # === CARD EXCHANGE PHASE (NEW) ===
                    exchange_requests = (
                        self.game.get_exchange_requests()
                    )  # Game tells who needs to choose cards
                    agent_choices = {}
                    self.room_logger.room_log(
                        f"Requesting card exchange: {exchange_requests}"
                    )
                    for agent_name, req in exchange_requests.items():
                        attempts = 0
                        while True:
                            cards = self.request_one(
                                agent_name,
                                "request_cards_to_exchange",
                                {
                                    "hand": self.get_player_hand(agent_name),
                                    "n": req["n"],
                                },
                            )

                            if self.game.valid_exchange_selection(
                                cards, self.get_player_hand(agent_name), req["n"]
                            ):
                                agent_choices[agent_name] = cards
                                break
                            attempts += 1
                            if attempts >= self.max_invalid_attempts:
                                agent_choices[agent_name] = (
                                    []
                                )  # Game will randomize as fallback
                                break

                    # Apply exchange (Game validates and executes)
                    hands_after = self.game.process_card_exchange(agent_choices)

                    # Notify each player of their updated hand privately
                    for player_name, new_hand in hands_after.items():
                        self.notify_one(
                            player_name,
                            "update_hand_after_exchange",
                            {"hand": new_hand},
                        )
                    current_match = self.game.current_match_count

            self.game.create_new_match()

            self.room_logger.room_log(
                f"\n--- MATCH {self.game.current_match_count} STARTED ---"
            )
            for agent, hand in zip(self.player_agents, hands):
                self.notify_one(
                    self.player_agents[agent].name,
                    "update_start_match",
                    {
                        "hand": hand,
                        "starter_index": self.game.starting_player_index,
                    },
                )

            self.game.start_match()

            match_over = False

            while not match_over:
                result_before_action = self.game.step()
                result_after_action = {}

                if result_before_action and result_before_action.get("request_action"):
                    player_name = result_before_action["player"]
                    observation = result_before_action["observation"]

                    valid_action = False
                    while not valid_action:
                        if self.invalid_counts[player_name] > self.max_invalid_attempts:
                            action_index = random.choice(
                                observation["possible_actions"]
                            )
                            action = self.action_lookup[action_index]
                        else:
                            action_index = self.request_one(
                                player_name, "request_action", observation
                            )
                            action = self.action_lookup.get(action_index)

                        result_after_action = self.game.step(action)
                        valid_action = result_after_action["valid_action"]

                        if not valid_action:
                            self.invalid_counts[player_name] += 1

                    self.invalid_counts[player_name] = 0

                    board_before = observation["board"]
                    board_after = result_after_action["observation"]["board"]
                    action_info = {
                        "player": player_name,
                        "action": action,
                        "valid": result_after_action["valid_action"],
                        "random": self.invalid_counts[player_name]
                        >= self.max_invalid_attempts,
                        "action_index": action_index,
                        "board_before": board_before,
                        "board_after": board_after,
                        "cards_left": len(
                            self.game.players[self._index_by_name(player_name)].cards
                        ),
                    }

                    for agent in self.player_agents:
                        if self.player_agents[agent].name == player_name:
                            action_info["observation_before"] = result_before_action[
                                "observation"
                            ]
                            action_info["observation_after"] = result_after_action[
                                "observation"
                            ]

                        self.notify_one(
                            self.player_agents[agent].name,
                            "update_player_action",
                            action_info,
                        )

                    if result_after_action.get("round_over"):
                        self.notify_all(
                            "update_pizza_declared",
                            {
                                "player": player_name,
                                "round": result_after_action["this_round_number"],
                                "next_player": result_after_action["next_player"],
                            },
                        )

                if result_after_action.get("match_over"):
                    self.room_logger.room_log("\n--- MATCH ENDED ---")
                    self.notify_all(
                        "update_match_over",
                        {
                            "scores": self.game.scores,
                            "roles": self.game.get_roles(),
                        },
                    )
                    match_over = True

            # --------------------------------------------------

        self.room_logger.room_log("\n=== GAME ENDED ===")
        self.notify_all("game_over", {"final_scores": self.game.scores})
        self.room_logger.room_log(f"Final scores: {self.game.scores}")
