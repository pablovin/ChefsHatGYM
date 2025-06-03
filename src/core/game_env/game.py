# core/game.py

import datetime
from ..utils.cards import deal_cards
from ..utils.rules import find_starting_player
from .match import Match
from ..utils.player import Player
from ..dataset.dataset_manager import DataSetManager
import random


class Game:
    def __init__(
        self,
        player_names,
        max_matches=3,
        max_rounds=None,
        max_score=None,
        logger=None,
        save_dataset=True,
        dataset_directory="dataset",
    ):
        self.players = [Player(name, index=i) for i, name in enumerate(player_names)]
        self.max_matches = max_matches
        self.max_rounds = max_rounds
        self.max_score = max_score
        self.current_match_count = 0
        self.current_match = None
        self.skip_card_exchange = False
        self.finishing_order_last_game = []

        self.scores = {name: 0 for name in player_names}
        self.roles = {name: None for name in player_names}

        self.finished = False
        self.logger = logger

        self.now = datetime.datetime.now()

        self.dataset = DataSetManager(
            dataSetDirectory=dataset_directory if save_dataset else None
        )

    def start(self):

        self.dataset.startNewGame([p.name for p in self.players])

        # self._start_next_match()

    def deal_cards(self):
        hands = deal_cards(len(self.players))
        role_exchange = " AND CARD EXCHANGE" if self.current_match_count > 0 else ""
        header = "\n" + "#" * 40 + f" DEALING CARDS " + role_exchange + "#" * 40
        self.logger.engine_log(header)

        self.logger.engine_log("- Cards dealt:")
        for player, hand in zip(self.players, hands):
            player.cards = sorted(hand)
            self.logger.engine_log(
                f"  - {player.name} hand: {player.cards} ({len(hand)} cards)"
            )
        cards = [p.cards.copy() for p in self.players]

        self.dataset.dealAction(self.current_match_count, cards)

    def create_new_match(self):

        self.starting_player_index = find_starting_player(self.players)
        self.current_match_count += 1

        self.dataset.startNewMatch(
            self.current_match_count, self.scores.copy(), self.roles.copy()
        )

        match = Match(
            players=self.players,
            match_number=self.current_match_count,
            max_matches=self.max_matches,
            current_scores=self.scores,
            starting_player_name=self.players[self.starting_player_index].name,
            max_rounds=self.max_rounds,
            logger=self.logger,
            dataset=self.dataset,
        )

        self.current_match = match

    def start_match(self):
        self.current_match.start_match()

    def step(self, action=None):

        if self.finished:
            return None

        result = self.current_match.step(action)

        if result["match_over"]:
            match_score = self.update_scores(self.current_match.finishing_order)
            self.logger.engine_log(f"Match score: {match_score}")
            self.logger.engine_log(f"Updated score: {self.scores}")

            self.finishing_order_last_game = self.current_match.finishing_order.copy()

            self.dataset.end_match(
                self.current_match_count,
                result["this_round_number"],
                match_score,
                self.scores,
                self.roles,
            )

            if self.current_match_count + 1 > self.max_matches:
                self.finished = True
                self.logger.engine_log(
                    f"Game finished! Max matches ({self.max_matches} matches) reached!"
                )
                self.logger.engine_log(
                    f"Total Game time: {(datetime.datetime.now()-self.now).total_seconds()} seconds!"
                )

                self.dataset.end_experiment(
                    self.current_match_count,
                    result["this_round_number"],
                    self.roles,
                    self.scores.copy(),
                    self.scores.copy(),
                )
            elif self.max_score and any(
                s >= self.max_score for s in self.scores.values()
            ):
                self.finished = True
                self.logger.engine_log(
                    f"Game finished! Max score of {self.max_score} points reached!"
                )
                self.logger.engine_log(
                    f"Total matches played: {self.current_match_count }!"
                )
                self.logger.engine_log(
                    f"Total Game time: {(datetime.datetime.now()-self.now).total_seconds()} seconds!"
                )

            # else:
            # Assign roles for next match
            # self.assign_roles(self.last_finishing_order)
            # self.logger.engine_log(f"Role assigned! New roles: {self.roles}")
            # self.start_match()

        return result

    def update_scores(self, finishing_order):

        score_map = {0: 3, 1: 2, 2: 1}
        match_scores = {}
        for position, player in enumerate(finishing_order):
            self.scores[player] += score_map.get(position, 0)
            match_scores[player] = score_map.get(position, 0)
        return match_scores

    def assign_roles(self):
        roles = ["chef", "souschef", "waiter", "dishwasher"]
        for idx, player_name in enumerate(self.finishing_order_last_game):
            self.roles[player_name] = roles[idx]

        self.logger.engine_log(f"Role assigned! New roles: {self.roles}")

    def get_roles(self):
        return self.roles.copy()

    def get_exchange_requests(self):
        # Who must pick which cards and how many
        # Only chef and souschef choose, rest are automatic
        who = {}
        for name, role in self.roles.items():
            if role == "chef":
                who[name] = {"give_to": self.get_player_by_role("dishwasher"), "n": 2}
            if role == "souschef":
                who[name] = {"give_to": self.get_player_by_role("waiter"), "n": 1}

        self.logger.engine_log(f"Current Roles: {self.roles} ")
        self.logger.engine_log(f"Requesting card exchange: {who} ")

        return who

    def get_player_by_role(self, role):
        for name, r in self.roles.items():
            if r == role:
                return name
        return None

    def process_card_exchange(self, choices):
        # choices: {agent_name: [cards]}
        # This function does all validation, fallback, and modifies player hands
        # Return: dict {player_name: new_hand}
        hands = {p.name: p.cards for p in self.players}
        hands_before = {p.name: p.cards.copy() for p in self.players}

        # hands_before = hands.copy()

        # Chef
        chef_name = self.get_player_by_role("chef")
        dishwasher_name = self.get_player_by_role("dishwasher")
        chef_cards = choices.get(chef_name, [])
        if not self.valid_exchange_selection(chef_cards, hands[chef_name], 2):
            chef_cards = random.sample(hands[chef_name], 2)
        for c in chef_cards:
            hands[chef_name].remove(c)
            hands[dishwasher_name].append(c)

        # Dishwasher: two lowest to chef
        dishwasher_give = sorted(hands[dishwasher_name])[:2]
        for c in dishwasher_give:
            hands[dishwasher_name].remove(c)
            hands[chef_name].append(c)

        # Souschef
        souschef_name = self.get_player_by_role("souschef")
        waiter_name = self.get_player_by_role("waiter")
        souschef_cards = choices.get(souschef_name, [])
        if not self.valid_exchange_selection(souschef_cards, hands[souschef_name], 1):
            souschef_cards = [random.choice(hands[souschef_name])]
        for c in souschef_cards:
            hands[souschef_name].remove(c)
            hands[waiter_name].append(c)

        # Waiter: lowest to souschef
        waiter_give = min(hands[waiter_name])
        hands[waiter_name].remove(waiter_give)
        hands[souschef_name].append(waiter_give)

        # Sort hands
        for name in hands:
            hands[name].sort()
        # Update all actual Player objects
        for p in self.players:
            p.cards = hands[p.name]

        self.dataset.do_card_exchange(
            match_number=self.current_match_count,
            action_description=[
                "",
                "",
                dishwasher_give,
                waiter_give,
                souschef_cards,
                chef_cards,
            ],
            player_hands=[p.cards.copy() for p in self.players],
        )

        self.logger.engine_log(
            f" -  Chef [{chef_name}] is giving the cards: {chef_cards} and receiving: {dishwasher_give}."
        )
        self.logger.engine_log(f" ---- Hand before: {hands_before[chef_name]}")
        self.logger.engine_log(f" ---- Hand After: {hands[chef_name]}")

        self.logger.engine_log(
            f" - SousChef [{souschef_name}] is giving the cards: {souschef_cards} and receiving: {waiter_give}."
        )
        self.logger.engine_log(f" ---- Hand before: {hands_before[souschef_name]}")
        self.logger.engine_log(f" ---- Hand After: {hands[souschef_name]}")

        self.logger.engine_log(
            f" - Waiter [{waiter_name}] is giving the cards: {waiter_give} and receiving: {souschef_cards}."
        )
        self.logger.engine_log(f" ---- Hand before: {hands_before[waiter_name]}")
        self.logger.engine_log(f" ---- Hand After: {hands[waiter_name]}")

        self.logger.engine_log(
            f" - Dishwasher [{dishwasher_name}] is giving the cards: {dishwasher_give} and receiving: {chef_cards}."
        )
        self.logger.engine_log(f" ---- Hand before: {hands_before[dishwasher_name]}")
        self.logger.engine_log(f" ---- Hand After: {hands[dishwasher_name]}")

        self.logger.engine_log("- New updated hands:")
        for player, hand in zip(self.players, hands):
            self.logger.engine_log(
                f"  - {player.name} hand: {player.cards} ({len(player.cards)} cards)"
            )

        return {name: hands[name] for name in hands}

    def valid_exchange_selection(self, selected, hand, n):
        return (
            isinstance(selected, list)
            and len(selected) == n
            and all(card in hand for card in selected)
        )

    def get_joker_special_options(self):
        """
        Returns dict: {player_name: {"role": role, "option": str}}
        for each player holding two jokers (card 12).
        "option" is either "food_fight" (if dishwasher) or "dinner_served".
        """
        eligible = {}
        for p in self.players:
            if p.cards.count(12) >= 2:
                role = self.roles[p.name]
                if role == "dishwasher":
                    eligible[p.name] = {"role": role, "option": "food_fight"}
                else:
                    eligible[p.name] = {"role": role, "option": "dinner_served"}

        if len(eligible) > 0:
            self.logger.engine_log(f"Players eligible for special actions: {eligible}")
        return eligible

    def apply_joker_special(self, player_name, action):
        """
        Performs the chosen special action by player_name.
        - If 'food_fight', invert roles.
        - If 'dinner_served', skip card exchange for this match.
        """
        if action == "food_fight":
            # invert roles
            inverted = {}
            for k, v in self.roles.items():
                if v == "chef":
                    inverted[k] = "dishwasher"
                elif v == "dishwasher":
                    inverted[k] = "chef"
                elif v == "waiter":
                    inverted[k] = "souschef"
                elif v == "souschef":
                    inverted[k] = "waiter"
            self.roles = inverted
            if self.logger:
                self.logger.engine_log(
                    f"FOOD FIGHT! Roles inverted by {player_name}: {self.roles}"
                )
            return "food_fight"
        elif action == "dinner_served":
            # flag to skip card exchange
            self.skip_card_exchange = True
            if self.logger:
                self.logger.engine_log(
                    f"THE DINNER IS SERVED! Declared by {player_name}. No card exchange this round."
                )
            return "dinner_served"
        return None
