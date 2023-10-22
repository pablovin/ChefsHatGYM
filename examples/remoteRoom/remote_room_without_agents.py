from ChefsHatGym.gameRooms.chefs_hat_room_remote import ChefsHatRoomRemote
import time
from ChefsHatGym.env import ChefsHatEnv
import redis


# Clean all the rooms
r = redis.Redis()
r.flushall()

# Room parameters
room_name = "Testing_1_Remote"
timeout_player_subscribers = 200
timeout_player_response = 5
verbose = True

# Game parameters
game_type = ChefsHatEnv.GAMETYPE["POINTS"]
stop_criteria = 15
maxRounds = -1

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

# Start the game
room.start_new_game()
while not room.get_room_finished():
    time.sleep(1)
