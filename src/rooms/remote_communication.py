import asyncio
import json
import websockets
from rooms.agent_communication import AgentCommInterface

class RemoteComm(AgentCommInterface):
    def __init__(self, room, logger, timeout=10):
        self.room = room
        self.logger = logger
        self.timeout = timeout

    async def notify_all(self, method, agents, *args):
        payload = args[0] if args else {}
        self.logger.room_log(f"Notify ALL -> method={method} | args={args}")
        message = json.dumps({"type": method, "payload": payload})
        await asyncio.gather(*[a.send(message) for a in agents], return_exceptions=True)

    async def notify_one(self, agent, method, *args):
        payload = args[0] if args else {}
        name = self.room.websockets.get(agent, "unknown")
        self.logger.room_log(f"Notify ONE -> {name} | method={method} | args={args}")
        try:
            await agent.send(json.dumps({"type": method, "payload": payload}))
        except websockets.exceptions.ConnectionClosed:
            await self.room.handle_disconnect(name)

    async def request_one(self, agent, method, *args):
        payload = args[0] if args else {}
        name = self.room.websockets.get(agent, "unknown")
        self.logger.room_log(f"Request ONE -> {name} | method={method} | args={args}")
        try:
            await agent.send(json.dumps({"type": method, "payload": payload}))
            resp = await asyncio.wait_for(agent.recv(), timeout=self.timeout)
            data = json.loads(resp)
            self.logger.room_log(f" -- Response from {name}: {data}")
            return data.get("result")
        except (asyncio.TimeoutError, websockets.exceptions.ConnectionClosed):
            await self.room.handle_disconnect(name)
            agent_local = self.room.connected_players[name]
            return getattr(agent_local, method)(*args)
