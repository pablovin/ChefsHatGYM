# core/cards.py

import random


def shuffle_cards():

    cards = [val for val in range(1, 12) for _ in range(val)] + [
        12,
        12,
    ]

    random.shuffle(cards)
    return cards


def deal_cards(num_players):
    shuffled_cards = shuffle_cards()
    cards_per_player = len(shuffled_cards) // num_players
    return [
        shuffled_cards[i * cards_per_player : (i + 1) * cards_per_player]
        for i in range(num_players)
    ]
