from ChefsHatGym.gameRooms.chefs_hat_room_server import ChefsHatRoomServer
from ChefsHatGym.env import ChefsHatEnv


# Room parameters
room_name = "server_room1"
room_password = "password"
room_port = 10003
timeout_player_subscribers = 5  # In seconds
timeout_player_response = 5  # In seconds

verbose_console = True
verbose_log = True
game_verbose_console = False
game_verbose_log = True
save_dataset = True


# Game parameters
game_type = ChefsHatEnv.GAMETYPE["MATCHES"]
stop_criteria = 3
maxRounds = -1


# Create the room
room = ChefsHatRoomServer(
    room_name,
    room_pass=room_password,
    room_port=room_port,
    timeout_player_subscribers=timeout_player_subscribers,
    timeout_player_response=timeout_player_response,
    game_type=game_type,
    stop_criteria=stop_criteria,
    max_rounds=maxRounds,
    verbose_console=verbose_console,
    verbose_log=verbose_log,
    game_verbose_console=game_verbose_console,
    game_verbose_log=game_verbose_log,
    save_dataset=save_dataset,
)

room.start_room()
