# test/test_run.py
from agents.random_agent import RandomAgent
from rooms.room import Room
import asyncio


# Initiate room
room = Room(
    run_remote_room=False,
    room_name="Room_local_Test",
    max_matches=10,
    output_folder="game_logs",
    save_game_dataset=True,
    save_logs_game=True,
    save_logs_room=True,
)


# Add Players

agents = [RandomAgent(name=f"Random{i}", log_directory=room.room_dir) for i in range(4)]

for agent in agents:
    room.connect_player(agent)

# Strart room
asyncio.run(room.run())
