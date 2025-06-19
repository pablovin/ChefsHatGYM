from rooms.agent_communication import AgentCommInterface


class LocalComm(AgentCommInterface):

    def __init__(self, room, logger):
        self.room = room
        self.logger = logger

    async def notify_all(self, method, agents, *args):

        self.logger.room_log(f"Notify ALL -> method={method} | args={args}")

        for agent in agents:
            getattr(agent, method)(*args)

    async def notify_one(self, agent, method, *args):
        self.logger.room_log(
            f"Notify ONE -> {agent.name} | method={method} | args={args}"
        )
        getattr(agent, method)(*args)

    async def request_one(self, agent, method, *args):
        self.logger.room_log(
            f"Request ONE -> {agent.name} | method={method} | args={args}"
        )
        response = getattr(agent, method)(*args)
        self.logger.room_log(f" -- Response from {agent.name}: {response}")
        return response
