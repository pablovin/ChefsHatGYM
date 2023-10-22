from ChefsHatGym.agents.remote.random_agent_remote import AgentRandonRemote

# Room parameters
room_name = "Testing_1"

# Create the players
p1 = AgentRandonRemote(name="04")
p1.joinGame(room_name)
