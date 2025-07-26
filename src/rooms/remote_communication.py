import asyncio
import json
from typing import Any

import numpy as np
import websockets
from rooms.agent_communication import AgentCommInterface


def _to_serializable(obj: Any) -> Any:
    """Recursively convert numpy types to JSON serializable types."""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, np.generic):
        return obj.item()
    if isinstance(obj, dict):
        return {k: _to_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_serializable(v) for v in obj]
    return obj


class RemoteComm(AgentCommInterface):
    def __init__(self, room, logger, timeout=10):
        self.room = room
        self.logger = logger
        self.timeout = timeout
        self._send_locks = {}

    def register_websocket(self, ws):
        if ws not in self._send_locks:
            self._send_locks[ws] = asyncio.Lock()

    def unregister_websocket(self, ws):
        self._send_locks.pop(ws, None)

    async def _safe_send(self, ws, message):
        lock = self._send_locks.setdefault(ws, asyncio.Lock())
        async with lock:
            await ws.send(message)

    async def notify_all(self, method, agents, *args):
        payload = _to_serializable(args[0]) if args else {}
        self.logger.room_log(f"Notify ALL -> method={method} | args={args}")
        message = json.dumps({"type": method, "payload": json.dumps(payload)})
        await asyncio.gather(
            *[self._safe_send(a, message) for a in agents],
            return_exceptions=True,
        )

    async def notify_one(self, agent, method, *args):
        payload = _to_serializable(args[0]) if args else {}
        name = self.room.websockets.get(agent, "unknown")
        self.logger.room_log(f"Notify ONE -> {name} | method={method} | args={args}")
        try:
            await self._safe_send(
                agent, json.dumps({"type": method, "payload": json.dumps(payload)})
            )
        except websockets.exceptions.ConnectionClosed:
            await self.room.handle_disconnect(name)

    async def request_one(self, agent, method, *args):
        payload = _to_serializable(args[0]) if args else {}
        name = self.room.websockets.get(agent, "unknown")
        self.logger.room_log(f"Request ONE -> {name} | method={method} | args={args}")
        try:
            async with self._send_locks.setdefault(agent, asyncio.Lock()):
                await agent.send(
                    json.dumps({"type": method, "payload": json.dumps(payload)})
                )
                resp = await asyncio.wait_for(agent.recv(), timeout=self.timeout)
            data = json.loads(resp)
            self.logger.room_log(f" -- Response from {name}: {data}")
            return data.get("result")
        except (asyncio.TimeoutError, websockets.exceptions.ConnectionClosed):
            await self.room.handle_disconnect(name)
            agent_local = self.room.connected_players[name]
            return getattr(agent_local, method)(*args)
