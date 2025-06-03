class AgentCommInterface:
    def notify_all(self, method, *args):
        raise NotImplementedError()

    def notify_one(self, player_name, method, *args):
        raise NotImplementedError()

    def request_one(self, player_name, method, *args):
        raise NotImplementedError()
