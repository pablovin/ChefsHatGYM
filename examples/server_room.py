from ChefsHatGym.gameRooms.chefs_hat_room_server import ChefsHatRoomServer
from ChefsHatGym.env import ChefsHatEnv

# Room parameters
room_name = "server_room1"
room_password = "password"
timeout_player_subscribers = 5
timeout_player_response = 5
verbose = True


# Game parameters
game_type = ChefsHatEnv.GAMETYPE["MATCHES"]
stop_criteria = 50
maxRounds = -1


# Create the room
room = ChefsHatRoomServer(
    room_name,
    room_pass=room_password,
    timeout_player_subscribers=timeout_player_subscribers,
    timeout_player_response=timeout_player_response,
    game_type=game_type,
    stop_criteria=stop_criteria,
    max_rounds=maxRounds,
    verbose=verbose,
    save_dataset=True,
    save_game_log=True,
)
