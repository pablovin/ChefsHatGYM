from .round import Round
from ..utils.rules import assign_roles
from ..utils.cards import deal_cards
from ..utils.rules import find_starting_player


class Match:

    def __init__(
        self,
        players,
        match_number,
        max_matches,
        current_scores,
        starting_player_name,
        max_rounds=None,
        logger=None,
        dataset=None,
    ):
        self.players = players
        self.match_number = match_number
        self.max_rounds = max_rounds

        self.rounds_played = 0
        self.current_round = None

        self.match_over = False
        self.finishing_order = []

        self.starting_player_name = starting_player_name

        self.logger = logger

        self.dataset = dataset

        header = "\n" + "#" * 40 + f" MATCH {self.match_number} START " + "#" * 40
        self.logger.engine_log(header)

        total_matches = f"/{max_matches}" if max_matches else ""

        self.logger.engine_log(f"- Match Number: {self.match_number}{total_matches}")
        scores_summary = ", ".join(f"{s}:{current_scores[s]}" for s in current_scores)
        self.logger.engine_log(f"- Current Game Scores: {{{scores_summary}}}")

        # if match_number > 1:
        #     assign_roles(self.players)
        #     self.logger and self.logger.info("Roles assigned:")
        #     for p in self.players:
        #         self.logger and self.logger.info(
        #             f"- {p.name} [index {p.index}]: {p.current_role}"
        #         )

        # self._deal_cards()

        # self.starting_player_index = find_starting_player(self.players)
        # self.starting_player_index = find_starting_player(self.players)

        # self._start_round(self.players[starting_player_index].name)

    def _deal_cards(self):
        hands = deal_cards(len(self.players))

        self.logger.engine_log("- Cards dealt:")
        for player, hand in zip(self.players, hands):
            player.cards = sorted(hand)
            self.logger.engine_log(
                f"  - {player.name} hand: {player.cards} ({len(hand)} cards)"
            )
        cards = [p.cards.copy() for p in self.players]

        self.dataset.dealAction(self.match_number, cards)

    def start_match(
        self,
    ):
        self._start_round(self.starting_player_name)

    def _start_round(self, name_initial_player):

        self.rounds_played += 1
        is_first_round = self.rounds_played == 1

        playing_agents = [
            player for player in self.players if not player.name in self.finishing_order
        ]

        # print(f"original list: {[p.name for p in self.players]}")
        # print(f"playing agents list: {[p.name for p in playing_agents]}")
        # print(f"Name of the player that should start the match: {name_initial_player}")

        original_player_index = None
        for i, player in enumerate(self.players):
            if name_initial_player == player.name:
                original_player_index = i
                break

        # If player name wasn't found (possible if next_player is None),
        # fall back to the first available playing agent
        if original_player_index is None:
            for i, player in enumerate(self.players):
                if player in playing_agents:
                    original_player_index = i
                    break

        # print(f"Position of this player in the original list: {original_player_index}")
        # If this item does exist in the playing_agents, get the next original item that exist in the players agent
        if not self.players[original_player_index] in playing_agents:
            # print(
            #     f"{self.players[original_player_index].name} is not on the playing list!"
            # )

            while not self.players[original_player_index] in playing_agents:
                original_player_index += 1
                if original_player_index >= len(playing_agents):
                    original_player_index = 0

            # print(
            #     f"Next player that will be on the playing list: {original_player_index}[{self.players[original_player_index].name}]"
            # )

        # grab the correct new index for this player
        starting_player_index = 0
        for i, player in enumerate(playing_agents):
            if self.players[original_player_index].name == player.name:
                starting_player_index = i
                break

                # print(
                #     f"Correct index of this player in the playing list: {starting_player_index}"
                # )

        self.round = Round(
            players=playing_agents,
            start_player_index=starting_player_index,
            is_first_round=is_first_round,
            rounds_played=self.rounds_played,
            match_number=self.match_number,
            max_rounds=self.max_rounds,
            logger=self.logger,
            dataset=self.dataset,
        )

        # self.rounds_played += 1

    def step(self, action):
        result = self.round.step(action)

        result["this_match_number"] = self.match_number
        result["match_over"] = False

        if result.get("round_over"):

            [
                self.finishing_order.append(player)
                for player in self.round.finishing_players
            ]

            self.dataset.declare_pizza(
                self.match_number, self.current_round, result["pizza_declarer"]
            )

            if len(self.finishing_order) >= 3:
                self.match_over = True
                self.logger.engine_log(
                    "Match over! All players finished or only one player remains."
                )
                self.logger.engine_log(f"Finishing position: {self.finishing_order}")
                self.logger.engine_log(f"Total rounds played: {self.rounds_played}")
                result["match_over"] = True

            elif self.max_rounds and self.rounds_played >= self.max_rounds:
                self.match_over = True
                self.logger.engine_log(" Match over! Max rounds reached.")
                self.logger.engine_log(f"Finishing position: {self.finishing_order}")
                self.logger.engine_log(f"Total rounds played: {self.rounds_played}")

                result["match_over"] = True
            else:

                self._start_round(result["next_player"])

            if result["match_over"]:
                for player in self.players:
                    if not player.name in self.finishing_order:
                        self.finishing_order.append(player.name)
        return result
