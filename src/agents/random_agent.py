import random
from .base_agent import BaseAgent


class RandomAgent(BaseAgent):

    def __init__(
        self,
        name,
        log_directory="",
        verbose_log=True,
        run_remote=False,
        host="localhost",
        port=8765,
        room_name="room",
        room_password="password",
    ):
        super().__init__(
            name,
            log_directory,
            verbose_log,
            run_remote,
            host,
            port,
            room_name,
            room_password,
        )
        self.all_actions = []
        self.hand = []

    def update_game_start(self, payload):
        self.log(f"Game Start! Received payload {payload}")
        self.all_actions = list(payload["actions"].values())
        self.log(f"Received ordered list of Actions: {self.all_actions}")
        pass

    def update_game_over(self, payload):
        self.log(f"Game over! Received payload {payload}")
        pass

    def update_new_hand(self, payload):
        self.log(f"Update new hand!: {payload}")
        self.hand = payload["hand"]
        self.log(f"My Hand: {self.hand}")
        pass

    def update_new_roles(self, payload):
        self.log(f"Update New Roles! Received payload {payload}")
        pass

    def update_food_fight(self, payload):
        self.log(f"Update Food Fight! Received payload {payload}")
        pass

    def update_dinner_served(self, payload):
        self.log(f"Update dinner served! Received payload {payload}")
        pass

    def update_start_match(self, payload):
        self.hand = payload["hand"]
        self.log(f"Update start match! Received payload: {payload}")
        pass

    def update_match_over(self, payload):
        self.log(f"Update match over! Received payload: {payload}")
        pass

    def update_player_action(self, payload):
        self.log(f"Update player action! Received payload: {payload}")
        pass

    def update_pizza_declared(self, payload):
        self.log(f"Update pizza declared! Received payload: {payload}")
        pass

    # ==== Synchronous stubs (for user to override) Requests ====

    def request_cards_to_exchange(self, payload):
        # Return a list of n card(s) to give away (e.g. lowest, random, or agent-strategy)

        cards_chosen = sorted(payload["hand"])[-payload["n"] :]
        self.log(
            f"Request cards to exchange! Cards chosen: {cards_chosen} - Received payload: {payload}"
        )
        return cards_chosen

    def request_special_action(self, payload):
        self.log(
            f"Request special action! Response: True - Received payload: {payload}"
        )
        return True

    def request_action(self, payload):

        valid_actions = payload["possible_actions"]
        non_pass_actions = [a for a in valid_actions if a != "pass"]
        chosen_action = random.choice(
            non_pass_actions if non_pass_actions else valid_actions
        )
        action = self.all_actions.index(chosen_action)
        self.log(
            f"Request action! Action chosen: {action} - Received payload: {payload}"
        )

        return action
