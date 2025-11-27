from .base_agent import BaseAgent
import numpy as np


class LargerValue(BaseAgent):
    def __init__(self, name="GreedyHighDiscard", *args, **kwargs):
        super().__init__(name, *args, **kwargs)

    def update_game_start(self, info):
        self.all_actions = list(info["actions"].values())
        self.log(f"Received ordered list of Actions: {self.all_actions}")

    def update_game_over(self, payload):
        pass

    def update_new_hand(self, payload):
        pass

    def update_new_roles(self, payload):
        pass

    def update_food_fight(self, payload):
        pass

    def update_dinner_served(self, payload):
        pass

    def update_hand_after_exchange(self, payload):
        pass

    def update_start_match(self, payload):
        pass

    def update_player_action(self, payload):
        pass

    def update_pizza_declared(self, payload):
        pass

    def request_cards_to_exchange(self, payload):
        return sorted(payload["hand"])[-payload["n"] :]

    def request_special_action(self, payload):
        return True

    def request_action(self, payload):

        possible_actions_values = list(payload["possible_actions"])
        # If only one option, return its index in self.all_actions
        if len(possible_actions_values) == 1:
            self.log(
                f"Possible Actions: {possible_actions_values} - Action: {self.all_actions.index(possible_actions_values[0])}"
            )
            return self.all_actions.index(possible_actions_values[0])

        # Remove "pass" from the list if present (but remember its index)
        filtered = [a for a in possible_actions_values if a.lower() != "pass"]

        # If there are any non-pass options, pick the last one (highest index in self.all_actions)

        if filtered:
            # This will always pick the one that discards the most and highest-value cards!
            self.log(
                f"Possible Actions: {possible_actions_values} - Action: {self.all_actions.index(filtered[-1])}"
            )
            return self.all_actions.index(filtered[-1])
        else:
            # Only "pass" is available
            self.log(
                f"Possible Actions: {possible_actions_values} - Action: {self.all_actions.index("pass")}"
            )
            return self.all_actions.index("pass")
