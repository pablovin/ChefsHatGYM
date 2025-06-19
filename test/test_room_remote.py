import asyncio
import sys
import os

root_dir = os.path.abspath('.')
sys.path.insert(0, os.path.join(root_dir, 'src'))
sys.path.insert(0, root_dir)

from agents.random_agent import RandomAgent
from rooms.room import Room

async def run_room_server(tmp_path):
    room = Room(
        run_remote_room=True,
        room_name="test_remote",
        room_password="secret",
        room_port=8765,
        output_folder=str(tmp_path)
    )
    agents = [RandomAgent(name=f"P{i}", log_directory=room.room_dir) for i in range(4)]
    for a in agents:
        a.run_remote = True
        a.remote_host = "localhost"
        a.remote_port = room.ws_port
        a.remote_room_name = room.room_name
        a.remote_room_password = room.room_password
    agent_tasks = [asyncio.create_task(a.remote_loop()) for a in agents]
    await room.run()
    await asyncio.gather(*agent_tasks, return_exceptions=True)
    assert hasattr(room, "final_scores")


def test_remote_room(tmp_path):
    asyncio.run(run_room_server(tmp_path))

