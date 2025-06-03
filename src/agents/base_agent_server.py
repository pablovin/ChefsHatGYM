# base_agent.py

import asyncio
import websockets
import json
import logging
from server.communication_protocol import COMMUNICATION_PROTOCOL


class BaseAgent:
    def __init__(self, name):
        self.name = name
        self.ws = None
        self.logger = logging.getLogger(f"Agent-{self.name}")

    async def connect(self, ws_url, token):
        uri = f"{ws_url}?token={token}"
        self.ws = await websockets.connect(uri)
        # Handshake: send player name
        await self.ws.send(json.dumps({"name": self.name}))
        self.logger.info(f"Connected as {self.name}")

    async def run(self, ws_url, token):
        await self.connect(ws_url, token)
        while True:
            msg = await self.ws.recv()
            data = json.loads(msg)
            msg_type = data.get("type")
            payload = data.get("payload", {})
            req_id = data.get("req_id", None)
            handler_name = f"on_{msg_type}"
            handler = getattr(self, handler_name, None)
            if handler:
                result = await handler(payload)
                # If protocol expects a reply:
                proto = COMMUNICATION_PROTOCOL.get(msg_type)
                if proto and proto["response"] and req_id is not None:
                    reply_type = proto["response"]["type"]
                    await self.ws.send(
                        json.dumps(
                            {"type": reply_type, "req_id": req_id, "result": result}
                        )
                    )
            else:
                print(f"WARNING: No handler for {msg_type}")

    # === Handler Methods ===
    # Each can be sync or async; if sync, it is wrapped to async automatically below

    async def on_update_game_start(self, payload):
        await self.update_start_game(payload)

    async def on_update_game_over(self, payload):
        await self.update_game_over(payload)

    async def on_update_new_hand(self, payload):
        await self.update_new_hand(payload)

    async def on_update_new_roles(self, payload):
        await self.update_new_roles(payload)

    async def on_update_food_fight(self, payload):
        await self.update_food_fight(payload)

    async def on_update_dinner_served(self, payload):
        await self.update_dinner_served(payload)

    async def on_update_start_match(self, payload):
        await self.update_start_match(payload)

    async def on_update_match_over(self, payload):
        await self.update_match_over(payload)

    async def on_update_player_action(self, payload):
        await self.update_player_action(payload)

    async def on_update_pizza_declared(self, payload):
        await self.update_pizza_declared(payload)

    # ==== Request/response methods (must return a value) ====
    async def on_request_action(self, payload):
        return await self.request_action(payload)

    async def on_request_cards_to_exchange(self, payload):
        return await self.choose_cards_to_give(payload)

    async def on_request_special_action(self, payload):
        return await self.request_special_action(payload)

    # ==== Synchronous stubs (for user to override) Updates ====
    async def update_game_start(self, payload):
        pass

    async def update_game_over(self, payload):
        pass

    async def update_new_hand(self, payload):
        pass

    async def update_new_roles(self, payload):
        pass

    async def update_food_fight(self, payload):
        pass

    async def update_dinner_served(self, payload):
        pass

    async def update_start_match(self, payload):
        pass

    async def update_match_over(self, payload):
        pass

    async def update_player_action(self, payload):
        pass

    async def update_pizza_declared(self, payload):
        pass

    # ==== Synchronous stubs (for user to override) Requests ====

    async def choose_cards_to_give(self, info):
        pass

    async def request_special_action(self, info):
        pass

    async def request_action(self, info):
        pass

    # === Utilities ===

    # Wrap sync methods to async for subclassing flexibility
    def __getattribute__(self, name):
        attr = object.__getattribute__(self, name)
        protocol_types = set(COMMUNICATION_PROTOCOL.keys())
        handler_prefix = "on_"

        # Only auto-wrap message handler methods
        if name.startswith(handler_prefix):
            if not asyncio.iscoroutinefunction(attr):

                async def async_wrap(*args, **kwargs):
                    return attr(*args, **kwargs)

                return async_wrap
        return attr
