import asyncio
from rooms.room import Room

async def main():
    room = Room(run_remote_room=True, room_name="example_room", room_password="secret", room_port=8765)
    await room.run()

if __name__ == "__main__":
    asyncio.run(main())
