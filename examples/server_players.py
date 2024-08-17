from ChefsHatGym.agents.agent_random import AgentRandon

room_pass = "password"
room_url = "localhost"
room_port = 10003


# Create the players
p1 = AgentRandon(name="01", verbose=True)
p2 = AgentRandon(name="02", verbose=True)
p3 = AgentRandon(name="03", verbose=True)
p4 = AgentRandon(name="04", verbose=True)

# Join agents

p1.joinGame(room_pass=room_pass, room_url=room_url, room_port=room_port)
p2.joinGame(room_pass=room_pass, room_url=room_url, room_port=room_port)
p3.joinGame(room_pass=room_pass, room_url=room_url, room_port=room_port)
p4.joinGame(room_pass=room_pass, room_url=room_url, room_port=room_port)
