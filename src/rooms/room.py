import os
import random
import asyncio
from datetime import datetime

from core.game_env.game import Game
from core.logging.room_logger import RoomLogger
from core.logging.engine_logger import EngineLogger
from core.utils.rules import get_high_level_actions

from rooms.local_communicationn import LocalComm
from rooms.remote_communication import RemoteComm

# from fastapi import FastAPI, WebSocket, HTTPException
import websockets
import json


class Room:

    def __init__(
        self,
        run_remote_room=False,
        room_name="room",
        room_password="password",
        max_matches=3,
        max_rounds=None,
        max_score=None,
        output_folder="outputs",
        max_invalid_attemps_per_player=5,
        save_logs_room=True,
        save_logs_game=True,
        save_game_dataset=True,
        dataset_flush_interval=1000,
        room_host="0.0.0.0",
        room_port=99,
        agent_timeout=600,
    ):
        self.run_remote_room = run_remote_room
        self.room_name = room_name
        self.room_password = room_password

        self.max_invalid_attempts = max_invalid_attemps_per_player
        self.save_logs_room = save_logs_room
        self.save_logs_game = save_logs_game
        self.save_game_dataset = save_game_dataset
        self.dataset_flush_interval = dataset_flush_interval
        self.ws_host = room_host
        self.ws_port = room_port
        self.agent_timeout = agent_timeout

        self.max_matches = max_matches
        self.max_rounds = max_rounds
        self.max_score = max_score
        self.max_players = 4

        self.connected_players = {}
        self.invalid_counts = {}

        self._waiting_event = asyncio.Event()

        # Use microseconds in the timestamp to avoid collisions when multiple
        # rooms are created within the same second.
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        self.room_dir = os.path.join(output_folder, f"{room_name}_{self.timestamp }")
        os.makedirs(self.room_dir, exist_ok=True)

        self.action_lookup = {
            i: action for i, action in enumerate(get_high_level_actions())
        }

        # Logging
        self.room_logger = RoomLogger(
            room_name,
            self.timestamp,
            local=not run_remote_room,
            config={
                "max_matches": max_matches,
                "max_rounds": max_rounds,
                "max_score": max_score,
                "max_invalid_attempts_per_player": max_invalid_attemps_per_player,
            },
            save_logs=save_logs_room,
            output_folder=self.room_dir,
        )

        if not run_remote_room:
            self.comm = LocalComm(self, self.room_logger)
        else:
            self.comm = RemoteComm(self, self.room_logger, timeout=self.agent_timeout)
            self.websockets = {}  # websocket -> name
            self.name_to_websocket = {}

    async def wait_for_players(self):
        self.room_logger.room_log("Checking if all players are connected...")
        if not self.run_remote_room:
            # Local: you can either "connect" players directly in code,
            # or mimic a connect method for each agent to call.
            while len(self.connected_players) < self.max_players:
                await asyncio.sleep(0.1)
            return
        else:

            # Start the websocket server and wait until all players are connected
            async def handler(websocket, path=None):
                try:
                    join_msg = await websocket.recv()
                    try:
                        join_info = json.loads(join_msg)
                    except Exception:
                        await websocket.send(
                            json.dumps({"error": "Invalid join format"})
                        )
                        await websocket.close()
                        return

                    player_name = join_info.get("player_name")
                    password = join_info.get("password")
                    room_name = join_info.get("room_name")

                    if (
                        not player_name
                        or not password
                        or not room_name
                        or room_name != self.room_name
                        or password != self.room_password
                    ):
                        await websocket.send(
                            json.dumps({"error": "Invalid credentials"})
                        )
                        await websocket.close()
                        return

                    if player_name in self.connected_players:
                        await websocket.send(json.dumps({"error": "Name taken"}))
                        await websocket.close()
                        return

                    if len(self.connected_players) >= self.max_players:
                        await websocket.send(json.dumps({"error": "Room full"}))
                        await websocket.close()
                        return

                    self.room_logger.room_log(f"Remote player connected: {player_name}")
                    self.connected_players[player_name] = websocket
                    self.websockets[websocket] = player_name
                    self.name_to_websocket[player_name] = websocket
                    self.invalid_counts[player_name] = 0
                    if hasattr(self.comm, "register_websocket"):
                        self.comm.register_websocket(websocket)
                    await websocket.send(json.dumps({"status": "connected"}))

                    if len(self.connected_players) == self.max_players:
                        self._waiting_event.set()

                    # Keep connection alive until the game finishes.  The
                    # websocket library closes the connection once this handler
                    # returns, so wait here until the room signals that the game
                    # has started and later until the connection is closed by
                    # the agent or the server.
                    await self._waiting_event.wait()
                    await websocket.wait_closed()
                except Exception as e:
                    print("WebSocket handler error:", e)
                    await websocket.close()

            # Start server
            self.room_logger.room_log(
                f"Room server listening on ws://{self.ws_host}:{self.ws_port}/ (room={self.room_name})"
            )
            self._ws_server = await websockets.serve(
                handler, self.ws_host, self.ws_port
            )
            await self._waiting_event.wait()
            self.room_logger.room_log("All players connected. Ready to play.")

    async def close(self):
        if self.run_remote_room and hasattr(self, "_ws_server"):
            self._ws_server.close()
            await self._ws_server.wait_closed()

    async def handle_disconnect(self, player_name):
        if player_name not in self.connected_players:
            return
        self.room_logger.room_log(
            f"Player {player_name} disconnected. Replacing with RandomAgent"
        )
        self.engine_logger.engine_log(
            f"Player {player_name} disconnected. Replaced with RandomAgent"
        )
        ws = self.name_to_websocket.get(player_name)
        if ws:
            try:
                await ws.close()
            except Exception:
                pass
            self.websockets.pop(ws, None)
            if hasattr(self.comm, "unregister_websocket"):
                self.comm.unregister_websocket(ws)
            self.name_to_websocket.pop(player_name, None)
        from agents.random_agent import RandomAgent

        agent = RandomAgent(name=player_name, log_directory=self.room_dir)
        self.connected_players[player_name] = agent

    # Local player connection
    def connect_player(self, agent):

        if self.run_remote_room:
            raise RuntimeError("Use remote connection for remote rooms.")

        if agent.name in self.connected_players:
            self.room_logger.room_log(f"ERROR - Player {agent.name} already in use!!")

            raise ValueError(f"Player {agent.name} already connected!")

        if len(self.connected_players) >= self.max_players:
            self.room_logger.room_log(
                f"ERROR - Player {agent.name} tried to connect, but the room is full!"
            )
            raise Exception("Room is full")
        self.connected_players[agent.name] = agent
        self.invalid_counts[agent.name] = 0

        self.room_logger.room_log(
            f"Player {len(self.connected_players)} connected: {agent.name}"
        )

        if len(self.connected_players) == self.max_players:
            self.room_logger.room_log(f"All players connected!")
            self._waiting_event.set()

    async def run(self):
        await self.wait_for_players()

        self.engine_logger = EngineLogger(
            self.room_name,
            self.timestamp,
            player_names=list(self.connected_players.keys()),
            config={
                "max_matches": self.max_matches,
                "max_rounds": self.max_rounds,
                "max_score": self.max_score,
                "max_invalid_attempts_per_player": self.max_invalid_attempts,
            },
            save_logs=self.save_logs_game,
            output_folder=self.room_dir,
        )

        self.game = Game(
            player_names=list(self.connected_players.keys()),
            max_matches=self.max_matches,
            max_rounds=self.max_rounds,
            max_score=self.max_score,
            logger=self.engine_logger,
            save_dataset=self.save_game_dataset,
            dataset_directory=self.room_dir,
            dataset_flush_interval=self.dataset_flush_interval,
        )
        await self.game_loop()

    def get_player_hand(self, name):

        for agent in self.game.players:
            if agent.name == name:
                return agent.cards.copy()

    def _index_by_name(self, name):
        for i, agent in enumerate(self.game.players):
            if agent.name == name:
                return i
        return -1

    async def game_loop(self):

        self.game.start()
        self.room_logger.room_log("\n=== GAME STARTED ===")
        self.room_logger.room_log(
            f"Game setup: Players={len(self.connected_players)}, Max Matches={self.game.max_matches}, Max Rounds={self.game.max_rounds}, Max Score={self.game.max_score}"
        )

        await self.comm.notify_all(
            "update_game_start",
            self.connected_players.values(),
            {
                "opponents": list(self.connected_players.keys()),
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
            for agent, hand in zip(self.connected_players.values(), hands):
                await self.comm.notify_one(
                    agent,
                    "update_new_hand",
                    {"hand": hand},
                )

            # If this is the second or more match
            if self.game.current_match_count > 0:
                self.game.assign_roles()
                await self.comm.notify_all(
                    "update_new_roles",
                    self.connected_players.values(),
                    self.game.get_roles(),
                )

                # Check for special actions
                special_opts = self.game.get_joker_special_options()
                food_fight_action = False

                for player_name, info in special_opts.items():
                    # Ask only this player if they want to use the special action.
                    wants = await self.comm.request_one(
                        self.connected_players[player_name],
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
                            await self.comm.notify_all(
                                "update_food_fight",
                                self.connected_players.values(),
                                {"by": player_name, "new_roles": self.game.get_roles()},
                            )
                            food_fight_action = True
                        else:
                            await self.comm.notify_all(
                                "update_dinner_served",
                                self.connected_players.values(),
                                {"by": player_name},
                            )
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
                            cards = await self.comm.request_one(
                                self.connected_players[agent_name],
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
                        await self.comm.notify_one(
                            self.connected_players[player_name],
                            "update_hand_after_exchange",
                            {"hand": new_hand},
                        )
                    current_match = self.game.current_match_count

            self.game.create_new_match()

            self.room_logger.room_log(
                f"\n--- MATCH {self.game.current_match_count} STARTED ---"
            )
            for agent, hand in zip(self.connected_players.values(), hands):
                await self.comm.notify_one(
                    agent,
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
                            print(
                                f"Possible actions: {observation['possible_actions']}"
                            )
                            action = random.choice(observation["possible_actions"])
                            print(f"RANDOM!")
                            # print(f"Random action: {random_action}")
                            # # print(f"All actions: {self.action_lookup}")

                            # action_index = next(
                            #     (
                            #         key
                            #         for key, value in self.action_lookup.items()
                            #         if value == random_action
                            #     ),
                            #     self.action_lookup[199],
                            # )
                            # print(f"Random action: {action}")
                            # # action = self.action_lookup.
                        else:
                            action_index = await self.comm.request_one(
                                self.connected_players[player_name],
                                "request_action",
                                observation,
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
                        "next_player": result_after_action["next_player"],
                    }

                    for agent in self.connected_players.values():
                        name = (
                            agent.name
                            if not self.run_remote_room
                            else self.websockets.get(agent, "unknown")
                        )
                        if name == player_name:
                            action_info["observation_before"] = result_before_action[
                                "observation"
                            ]
                            action_info["observation_after"] = result_after_action[
                                "observation"
                            ]

                        await self.comm.notify_one(
                            agent,
                            "update_player_action",
                            action_info,
                        )

                    if result_after_action.get("round_over"):
                        await self.comm.notify_all(
                            "update_pizza_declared",
                            self.connected_players.values(),
                            {
                                "player": result_after_action["pizza_declarer"],
                                "round": result_after_action["this_round_number"],
                                "next_player": result_after_action["next_player"],
                            },
                        )

                if result_after_action.get("match_over"):
                    self.room_logger.room_log("\n--- MATCH ENDED ---")
                    await self.comm.notify_all(
                        "update_match_over",
                        self.connected_players.values(),
                        {
                            "scores": self.game.scores.copy(),
                            "finishing_order": self.game.finishing_order_last_game,
                        },
                    )
                    match_over = True

            # --------------------------------------------------

        self.room_logger.room_log("\n=== GAME ENDED ===")
        await self.comm.notify_all(
            "update_game_over",
            self.connected_players.values(),
            {"final_scores": self.game.scores},
        )
        self.room_logger.room_log(f"Final scores: {self.game.scores}")

        self.final_scores = self.game.scores

        if self.run_remote_room:
            for ws in list(self.websockets.keys()):
                try:
                    await ws.close()
                except Exception:
                    pass
                if hasattr(self.comm, "unregister_websocket"):
                    self.comm.unregister_websocket(ws)
                self.websockets.pop(ws, None)
            self.name_to_websocket.clear()
            await self.close()
