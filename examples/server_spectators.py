from ChefsHatGym.agents.spectator_logger import SpectatorLogger

room_pass = "password"
room_url = "localhost"
room_port = 10003

# Create the players
s1 = SpectatorLogger(name="01", verbose_console=True, verbose_log=True)
s2 = SpectatorLogger(name="02", verbose_console=True, verbose_log=True)

# Join spectators
s1.joinGame(room_pass=room_pass, room_url=room_url, room_port=room_port)
s2.joinGame(room_pass=room_pass, room_url=room_url, room_port=room_port)
