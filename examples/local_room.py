from ChefsHatGym.gameRooms.chefs_hat_room_local import ChefsHatRoomLocal
from ChefsHatGym.env import ChefsHatEnv
from ChefsHatGym.agents.agent_random import AgentRandon

# Room parameters
room_name = "Testing_1"

# Room parameters
room_name = "Testing_1_Local"
timeout_player_response = 5

verbose = True

# Game parameters
game_type = ChefsHatEnv.GAMETYPE["POINTS"]
stop_criteria = 15
maxRounds = -1

# Start the room
room = ChefsHatRoomLocal(
    room_name,
    timeout_player_response=timeout_player_response,
    game_type=game_type,
    stop_criteria=stop_criteria,
    max_rounds=maxRounds,
    verbose=verbose,
)

# Create the players
p1 = AgentRandon(name="01")
p2 = AgentRandon(name="02")
p3 = AgentRandon(name="03")
p4 = AgentRandon(name="04")

# Adding players to the room
for p in [p1, p2, p3, p4]:
    room.add_player(p)


# Start the game
info = room.start_new_game(game_verbose=True)

print(f"Performance score: {info['performanceScore']}")
print(f"Scores: {info['score']}")
