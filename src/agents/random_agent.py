import random
from .base_agent import BaseAgent


class RandomAgent(BaseAgent):
    def __init__(self, name, log_directory=""):
        super().__init__(name, log_directory)
        self.all_actions = []
        self.hand = []

    def update_game_start(self, payload):
        self.all_actions = list(payload["actions"].values())
        pass

    def update_game_over(self, payload):
        pass

    def update_new_hand(self, payload):
        self.hand = payload["hand"]
        pass

    def update_new_roles(self, payload):
        pass

    def update_food_fight(self, payload):
        pass

    def update_dinner_served(self, payload):
        pass

    def update_start_match(self, payload):
        self.hand = payload["hand"]
        pass

    def update_match_over(self, payload):
        pass

    def update_player_action(self, payload):
        pass

    def update_pizza_declared(self, payload):
        pass

    # ==== Synchronous stubs (for user to override) Requests ====

    def request_cards_to_exchange(self, info):
        # Return a list of n card(s) to give away (e.g. lowest, random, or agent-strategy)
        return sorted(info["hand"])[-info["n"] :]

    def request_special_action(self, info):
        return True

    def request_action(self, info):

        valid_actions = info["possible_actions"]
        non_pass_actions = [a for a in valid_actions if a != "pass"]
        chosen_action = random.choice(
            non_pass_actions if non_pass_actions else valid_actions
        )
        return self.all_actions.index(chosen_action)
