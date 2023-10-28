from ChefsHatGym.gameRooms.chefs_hat_tournament import ChefsHatRoomTournament
from ChefsHatGym.env import ChefsHatEnv
from ChefsHatGym.agents.agent_random import AgentRandon

# Tounament parameters
tournamentFolder = "tournament/"
tournament_name = "Tournament_1"
timeout_player_response = 5
verbose = True

# Game parameters
game_type = ChefsHatEnv.GAMETYPE["MATCHES"]
stop_criteria = 3
maxRounds = -1

p1 = AgentRandon(name="01")
p2 = AgentRandon(name="02")
p3 = AgentRandon(name="03")
p4 = AgentRandon(name="04")


# Start the tournament
tournament = ChefsHatRoomTournament(
        oponents = [p1,p2,p3,p4],
        tournament_name = tournament_name,
        game_type = game_type,
        stop_criteria= stop_criteria,
        max_rounds = maxRounds,
        verbose= verbose,
        save_dataset = True,
        save_game_log = True,
        log_directory = tournamentFolder
)


# Run the tournament
tournament.runTournament()
