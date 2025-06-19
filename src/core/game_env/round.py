from ..utils.rules import (
    execute_action,
    parse_action_string,
    get_possible_actions,
    is_action_allowed,
    next_player,
    complement_array,
)
import time
from typing import Any, Dict, List, Optional

from ..dataset.dataset_manager import DataSetManager
from ..logging.engine_logger import EngineLogger


class Round:

    def __init__(
        self,
        players: List[Any],
        start_player_index: int,
        is_first_round: bool,
        rounds_played: int,
        max_rounds: Optional[int],
        match_number: int,
        logger: Optional[EngineLogger] = None,
        dataset: Optional[DataSetManager] = None,
    ) -> None:
        """Create a round instance.

        Parameters
        ----------
        players : list
            List of :class:`Player` instances in the match.
        start_player_index : int
            Index of the player that starts this round.
        is_first_round : bool
            Whether this is the first round of the match.
        rounds_played : int
            Number of rounds already played in this match.
        max_rounds : int | None
            Maximum number of rounds allowed in the match.
        match_number : int
            Match identifier used for logging.
        logger : EngineLogger | None
            Logger instance for debug information.
        dataset : DataSetManager | None
            Dataset manager used to store gameplay information.
        """
        self.players = players
        self.current_player_index = start_player_index
        self.board = [13]
        self.match_number = match_number

        self.finishing_players = []
        self.passing_players = []

        self.last_discarder = None

        self.logger = logger
        self.dataset = dataset

        self.this_round_number = rounds_played
        self.is_first_round = is_first_round
        self.is_first_turn = True

        # self.players_last_action = {}

        # print(f"Players: {self.players}")
        # for player in self.players:
        #     self.players_last_action[player.name] = None

        header = "\n" + "=" * 40 + f" ROUND START " + "=" * 40
        self.logger.engine_log(header)

        total_rounds = f"/{max_rounds}" if max_rounds else ""

        self.logger.engine_log(f"- Round: {self.this_round_number}{total_rounds}")

        self.logger.engine_log("Players in the round:")
        for p in self.players:
            self.logger.engine_log(f" {p.name} - {len(p.cards)} cards - {p.cards}")

        ordered_players = (
            self.players[start_player_index:] + self.players[:start_player_index]
        )
        playing_order = [p.name for p in ordered_players]
        self.logger.engine_log(f"Playing order: {playing_order}")

    def step(self, action: Optional[str] = None) -> Dict[str, Any]:
        """Execute ``action`` for the current player.

        Parameters
        ----------
        action : str | None
            Action string to be parsed and executed. When ``None`` a payload
            requesting the player's action is returned.

        Returns
        -------
        dict
            Information about the current state. The payload always contains the
            keys ``player`` and ``this_round_number``. When requesting an action
            the ``observation`` describes the player's hand, board and possible
            actions. If a round ends, ``round_over`` is ``True`` and
            ``pizza_declarer`` indicates who ended the round.
        """
        # print(f"self.current_player_index: {self.current_player_index}")
        current_player = self.players[self.current_player_index]

        # if current_player.finished:
        #     self.current_index = next_player(self.players, self.current_index)
        #     return self.step(action)

        possible_actions = get_possible_actions(
            current_player.cards,
            self.board,
            is_first_round=self.is_first_round,
            is_first_turn=self.is_first_turn,
        )

        # print(f"Is first turn: {is_first_turn}")

        # IF there is no action received, this means the round is requesting an action from the player
        if action is None:
            return {
                "request_action": True,
                "player": current_player.name,
                "this_round_number ": self.this_round_number,
                "observation": {
                    "hand": complement_array(current_player.cards, 17),
                    "board": complement_array(self.board.copy(), 11),
                    "possible_actions": possible_actions,
                },
            }

        parsed_action = parse_action_string(action)

        self.logger.engine_log(f" Player turn: [{current_player.name}]")
        self.logger.engine_log(f" --- Board: {self.board}")
        self.logger.engine_log(f" --- Player Hand: {current_player.cards}")
        self.logger.engine_log(f" --- First Round: [{self.is_first_round}]")
        self.logger.engine_log(f" --- First Turn: [{self.is_first_turn}]")
        self.logger.engine_log(f" --- Possible actions: {possible_actions}")
        self.logger.engine_log(f" --- Player action: >>> {action} <<<")

        if not is_action_allowed(parsed_action, possible_actions):
            return {
                "request_action": True,
                "player": current_player.name,
                "this_round_number": self.this_round_number,
                "valid_action": False,
                "round_over": False,
                "observation": {
                    "hand": complement_array(current_player.cards.copy(), 17),
                    "board": complement_array(self.board.copy(), 11),
                    "possible_actions": possible_actions,
                },
            }

        board_before = self.board.copy()
        execute_action(current_player, parsed_action, self.board)

        self.dataset.doDiscard(
            self.match_number,
            self.this_round_number,
            current_player.name,
            action,
            complement_array(current_player.cards, 17),
            complement_array(board_before, 11),
            complement_array(self.board, 11),
            possible_actions.copy(),
            bool(len(current_player.cards) == 0),
        )
        if self.is_first_turn:
            self.is_first_turn = False
        # self.players_last_action[current_player] = parsed_action

        self.logger.engine_log(f" --- Cards at hand after: {current_player.cards}")
        self.logger.engine_log(f" --- Board after: {self.board}")
        self.logger.engine_log(
            f" --- Player finished: {'Yes' if len(current_player.cards)==0 else 'No'}"
        )

        if action != "pass":
            self.last_discarder = current_player.name
        else:
            self.passing_players.append(current_player.name)

        # Verify if the player finished the game, after it did an action
        if len(current_player.cards) == 0:
            self.finishing_players.append(current_player.name)

        # Verify if all > (players -1) passed, then pizza.
        # Verify if all > players -1) finished the game, then round over

        possible_actions_after = get_possible_actions(
            current_player.cards,
            self.board,
            is_first_round=self.is_first_round,
            is_first_turn=self.is_first_turn,
        )

        if len(self.passing_players) > 0:
            self.logger.engine_log(
                f" - Players that have passed: [{self.passing_players}]"
            )
        if len(self.finishing_players) > 0:
            self.logger.engine_log(
                f" - Payers that have finished: [{self.finishing_players}]"
            )

        passed_or_finished = set(self.passing_players + self.finishing_players)
        # passed_or_finished = self.passing_players

        if (
            len(passed_or_finished) >= len(self.players)
            or len(self.passing_players) >= len(self.players) - 1
        ):
            # print(f"PIZZA MOTHAFOCKA!")
            # All players except one has passed or finished, and now we declare pizza!
            self.board = [13]
            self.logger.engine_log(
                f" - Pizza declared by {self.last_discarder}! Round {self.this_round_number} finished!"
            )

            next_player_name = self.last_discarder

            # print(f"Round: player that discarded last: {next_player_name}")

            if next_player_name in self.finishing_players and len(
                self.finishing_players
            ) < len(self.players):
                # print(f"Round: This player is in the finishing list!")
                current_index = next(
                    i
                    for i, player in enumerate(self.players)
                    if player.name == next_player_name
                )
                next_index = current_index + 1

                if next_index >= len(self.players):
                    next_index = 0

                # print(
                #     f"Round: Next index then: {next_index}[{self.players[next_index].name}]"
                # )
                # print(f"Round: Finishing list: {self.finishing_players}")

                while self.players[next_index].name in self.finishing_players:
                    next_index += 1
                    if next_index >= len(self.players):
                        next_index = 0
                #     print(
                #         f"Round: Updated the next index to: {next_index}[{self.players[next_index].name}]"
                #     )

                # print(
                #     f"Round: Next index that is not in the finishing list: {next_index}[{self.players[next_index].name}]"
                # )

                next_player_name = self.players[next_index].name

            return {
                "player": current_player.name,
                "this_round_number": self.this_round_number,
                "action_taken": action,
                "board": complement_array(self.board.copy(), 11),
                "round_over": True,
                "valid_action": True,
                "pizza_declarer": self.last_discarder,
                "observation": {
                    "hand": complement_array(current_player.cards.copy(), 17),
                    "board": complement_array(self.board.copy(), 11),
                    "possible_actions": possible_actions_after,
                },
                "next_player": next_player_name,
            }

        # next_player(players, current_index, passing_players, finished_players)

        self.current_player_index = next_player(
            self.players,
            self.current_player_index,
            self.passing_players,
            self.finishing_players,
        )

        self.logger.engine_log(
            f" - Next Player: [{self.current_player_index}] {self.players[self.current_player_index].name}"
        )

        # print(f"Something went wrong here: {self.current_player_index}")
        return {
            "player": current_player.name,
            "this_round_number": self.this_round_number,
            "action_taken": action,
            "board": complement_array(self.board.copy(), 11),
            "valid_action": True,
            "round_over": False,
            "observation": {
                "hand": complement_array(current_player.cards.copy(), 17),
                "board": complement_array(self.board.copy(), 11),
                "possible_actions": possible_actions_after,
            },
            "next_player": self.players[self.current_player_index].name,
        }
