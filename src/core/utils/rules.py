# # core/rules.py

import random
from itertools import groupby
import numpy as np


def execute_action(player, parsed_action, board):
    if parsed_action == "pass":
        # player.last_action = "pass"
        return

    value, qty, jokers = parsed_action
    action_cards = [value] * qty + [12] * jokers
    for card in action_cards:
        player.cards.remove(card)
    board.clear()
    board.extend(action_cards)
    # player.last_action = parsed_action


def parse_action_string(action):
    if action == "pass":
        return action
    parts = action.split(";")
    value = int(parts[0][1:])
    qty = int(parts[1][1:])
    jokers = int(parts[2][1:])
    return value, qty, jokers


def get_high_level_actions():
    """Generate all the possible actions in a human-friendly way

    :return: highLevelActions - List
        :rtype: list
    """
    highLevelActions = []

    for cardNumber in range(11):
        for cardQuantity in range(cardNumber + 1):
            highLevelActions.append(
                "C" + str(cardNumber + 1) + ";Q" + str(cardQuantity + 1) + ";J0"
            )
            highLevelActions.append(
                "C" + str(cardNumber + 1) + ";Q" + str(cardQuantity + 1) + ";J1"
            )
            highLevelActions.append(
                "C" + str(cardNumber + 1) + ";Q" + str(cardQuantity + 1) + ";J2"
            )

    highLevelActions.append("C0;Q0;J1")
    highLevelActions.append("pass")

    return highLevelActions


def get_possible_actions(hand, board, is_first_round, is_first_turn):

    groups = {k: len(list(g)) for k, g in groupby(sorted(hand)) if k != 12}
    jokers = hand.count(12)
    board_values = [card for card in board if card != 13]

    possible_actions = []

    if not board_values:
        for card, count in groups.items():
            for qty in range(1, count + 1):
                if is_first_turn and is_first_round and card != 11:
                    continue
                possible_actions.append(f"C{card};Q{qty};J0")
                if jokers >= 1:
                    possible_actions.append(f"C{card};Q{qty};J1")
                if jokers >= 2:
                    possible_actions.append(f"C{card};Q{qty};J2")
        if not (is_first_turn and is_first_round):
            if jokers == 1:
                possible_actions.append("C0;Q0;J1")
    else:
        top_card = board_values[0]
        required_qty = len(board)

        for card, count in groups.items():
            if card < top_card:
                for qty in range(required_qty, count + 1):
                    possible_actions.append(f"C{card};Q{qty};J0")
                    if jokers >= 1:
                        possible_actions.append(f"C{card};Q{qty};J1")
                    if jokers >= 2:
                        possible_actions.append(f"C{card};Q{qty};J2")

        # if jokers >= required_qty:
        #     possible_actions.append("C0;Q0;J1")
    
    if not (is_first_turn and is_first_round):
        possible_actions.append("pass")

    return possible_actions


def is_action_allowed(parsed_action, possible_actions):
    if parsed_action == "pass":
        return "pass" in possible_actions
    elif isinstance(parsed_action, tuple):
        val, qty, jokers = parsed_action
        return f"C{val};Q{qty};J{jokers}" in possible_actions
    return False


def next_player(players, current_index, passing_players, finished_players):
    next_index = current_index + 1
    if next_index >= len(players):
        next_index = 0

    while (players[next_index].name in passing_players) or (
        players[next_index].name in finished_players
    ):
        # print("---")
        # print(f"Passed players: {passing_players} ")
        # print(f"Finished players: {finished_players} ")
        # print(f"Next player: [{next_index}]{players[next_index].name} ")
        # print("---")
        next_index = next_index + 1
        if next_index >= len(players):
            next_index = 0

    return next_index


def assign_roles(players, finishing_position):
    players_sorted = sorted(
        [p for p in players if p.finished_position is not None],
        key=lambda p: p.finished_position,
    )
    if len(players_sorted) >= 4:
        players_sorted[0].current_role = "Chef"
        players_sorted[1].current_role = "Sous-Chef"
        players_sorted[2].current_role = "Waiter"
        players_sorted[3].current_role = "Dishwasher"


def find_starting_player(players):

    start_index = random.randint(0, len(players) - 1)
    for i in range(len(players)):
        candidate = players[(start_index + i) % len(players)]
        if 11 in candidate.cards:
            return (start_index + i) % len(players)
    return start_index


def complement_array(array, max_number):
    array_to_complement = array.copy()
    missing_numbers = np.zeros((max_number - len(array_to_complement)))
    array_to_complement = np.concatenate([array_to_complement, missing_numbers])
    return array_to_complement
