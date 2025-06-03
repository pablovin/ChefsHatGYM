# communication_protocol.py

"""
Central protocol definitions for all messages exchanged between ServerRoom and agents.
Every message type is documented, with direction, expected payload, and optional response.
"""

COMMUNICATION_PROTOCOL = {
    # Game lifecycle
    "update_game_start": {
        "direction": "server_to_agent",
        "doc": "Tells agent the game will start. No payload.",
        "payload": {
            "opponents": "List[string] name of the agents on the game",
            "actions": "List[string] list of all possible actions in the format C0Q0J0",
            "max_rounds": "int number of maximum rounds for this game",
            "max_matches": "int number of maximum matches for this game",
            "max_points": "int number of maximum points for this game",
        },
        "response": None,
    },
    "update_game_over": {
        "direction": "server_to_agent",
        "doc": "Game finished. Payload contains final scores or summary.",
        "payload": {"info": "dict, summary/final scores"},
        "response": None,
    },
    # Cards Handling, Role updates
    "update_new_hand": {
        "direction": "server_to_agent",
        "doc": "Notifies agent of their new hand after dealing.",
        "payload": {"hand": "List[int] (cards in hand)"},
        "response": None,
    },
    "update_new_roles": {
        "direction": "server_to_agent",
        "doc": "Notifies agent of current role assignments.",
        "payload": {"roles": "dict {player_name: role}"},
        "response": None,
    },
    "request_cards_to_exchange": {
        "direction": "server_to_agent",
        "doc": "Asks agent to choose cards for exchange phase.",
        "payload": {"hand": "List[int]", "n": "int (number of cards to choose)"},
        "response": {
            "type": "request_cards_to_exchange_reply",
            "fields": {"result": "List[int]"},
        },
    },
    "request_special_action": {
        "direction": "server_to_agent",
        "doc": "Asks if agent wants to activate a special action.",
        "payload": {
            "option": "'food_fight' or 'dinner_served'",
            "hand": "List[int] current cards in the players hand",
            "role": "str current role of the player",
        },
        "response": {
            "type": "request_special_action_reply",
            "fields": {"result": "bool"},
        },
    },
    "update_food_fight": {
        "direction": "server_to_agent",
        "doc": "Notifies all agents that 'food fight' was declared and roles inverted.",
        "payload": {"by": "str (player who declared)", "new_roles": "dict"},
        "response": None,
    },
    "update_dinner_served": {
        "direction": "server_to_agent",
        "doc": "Notifies all agents that 'dinner served' was declared.",
        "payload": {"by": "str"},
        "response": None,
    },
    "update_hand_after_exchange": {
        "direction": "server_to_agent",
        "doc": "Notifies agent of their hand after card exchange.",
        "payload": {"hand": "List[int]"},
        "response": None,
    },
    # Match lifecycle
    "update_start_match": {
        "direction": "server_to_agent",
        "doc": "New match starts. ",
        "payload": {
            "hand": "List[int] of this player",
            "starting_player": "str the name of the player starting the game",
        },
        "response": None,
    },
    "update_match_over": {
        "direction": "server_to_agent",
        "doc": "A match is finished. Payload contains scores, roles, etc.",
        "payload": {"scores": "dict", "roles": "dict"},
        "response": None,
    },
    # Round lifecycle
    "request_action": {
        "direction": "server_to_agent",
        "doc": "Requests agent's action for this turn.",
        "payload": {"observation": "dict, game state info"},
        "response": {
            "type": "request_action_reply",
            "fields": {"result": "int index of the action choosenm by the agent"},
        },
    },
    "update_player_action": {
        "direction": "server_to_agent",
        "doc": "Notifies agent of any action taken by any player.",
        "payload": {
            "player": "str player name",
            "action": "str the action",
            "valid": "bool was it a valid action",
            "random": "bool was it a random action",
            "action_index": "index of the action",
            "board_before": "board before the action",
            "board_after": "board after the action",
            "cards_left": "list[int] - amount of cards left in each player`s hands",
            "observation_before": "list[int] observation before the action. Only sent to the player that did the action.",
            "observation_before": "list[int] observation before the action. Only sent to the player that did the action.",
        },
        "response": None,
    },
    "update_pizza_declared": {
        "direction": "server_to_agent",
        "doc": "Notifies all agents that someone declared 'pizza' (round finish).",
        "payload": {"player": "str", "round": "int", "next_player": "str"},
        "response": None,
    },
    # Role Exchange phases
    # Joker/special actions
    # Misc (waiting, etc.)
    "waiting": {
        "direction": "server_to_agent",
        "doc": "Server tells how many players are connected.",
        "payload": {"n": "int (players connected)"},
        "response": None,
    },
}


# Optionally: helper to auto-document or check message type validity.
def describe_protocol():
    for k, v in COMMUNICATION_PROTOCOL.items():
        print(
            f"{k}: {v['doc']}\n  Payload: {v['payload']}\n  Response: {v['response']}\n"
        )
