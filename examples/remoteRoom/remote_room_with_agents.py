from ChefsHatGym.gameRooms.chefs_hat_room_remote import ChefsHatRoomRemote
import time
from ChefsHatGym.env import ChefsHatEnv
import redis
from ChefsHatGym.agents.remote.random_agent_remote import AgentRandonRemote


# Room parameters
room_name = "Testing_1"

# Create the players
p1 = AgentRandonRemote(name="01")
p2 = AgentRandonRemote(name="02")
p3 = AgentRandonRemote(name="03")
p4 = AgentRandonRemote(name="04")


# Clean all the rooms
r = redis.Redis()
r.flushall()

# Room parameters
room_name = "Testing_1_Remote"
timeout_player_subscribers = 200
timeout_player_response = 5
verbose = False

# Game parameters
game_type = ChefsHatEnv.GAMETYPE["MATCHES"]
stop_criteria = 3
maxRounds = 10

# Start the room
room = ChefsHatRoomRemote(
    room_name,
    timeout_player_subscribers=timeout_player_subscribers,
    timeout_player_response=timeout_player_response,
    game_type=game_type,
    stop_criteria=stop_criteria,
    max_rounds=maxRounds,
    verbose=verbose,
)

# Give enought time for the room to setup
time.sleep(1)


# Join agents
for p in [p1, p2, p3, p4]:
    p.joinGame(room_name, verbose=False)

# Start the game
room.start_new_game(game_verbose=True)
while not room.get_room_finished():
    time.sleep(1)
