from rooms.agent_communication import AgentCommInterface
import asyncio


class RemoteComm(AgentCommInterface):
    def __init__(
        self, room, logger
    ):  # Pass reference to UnifiedRoom for websockets, etc
        self.room = room
        self.logger = logger

    def notify_all(self, method, *args):
        # await in game loop, or run as task

        self.logger.room_log(f"Notify ALL -> method={method} | args={args}")

        return asyncio.create_task(
            self.room.broadcast({"type": method, "info": args[0] if args else {}})
        )

    def notify_one(self, player_name, method, *args):
        token = self.room.token_for_player_name[player_name]

        self.logger.room_log(
            f"Notify ONE -> {player_name} | method={method} | args={args}"
        )

        return asyncio.create_task(
            self.room.send_to_agent(
                token, {"type": method, "info": args[0] if args else {}}
            )
        )

    def request_one(self, player_name, method, *args):
        token = self.room.token_for_player_name[player_name]
        self.logger.room_log(
            f"Request ONE -> {player_name} | method={method} | args={args}"
        )
        response = asyncio.create_task(
            self.room.request_from_agent(
                token, method, args[0] if args else {}, timeout=60
            )
        )
        self.logger.room_log(f" -- Response from {player_name}: {response}")
        return response
