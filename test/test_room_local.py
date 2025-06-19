import asyncio
import sys
import os
root_dir = os.path.abspath('.')
sys.path.insert(0, os.path.join(root_dir, 'src'))
sys.path.insert(0, root_dir)
from agents.random_agent import RandomAgent
from rooms.room import Room

def test_local_room(tmp_path):
    room = Room(
        run_remote_room=False,
        room_name="test_local",
        max_matches=1,
        output_folder=str(tmp_path)
    )
    agents = [RandomAgent(name=f"P{i}", log_directory=room.room_dir) for i in range(4)]
    for a in agents:
        room.connect_player(a)
    asyncio.run(room.run())
    assert hasattr(room, "final_scores")
