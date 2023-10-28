from ChefsHatGym.agents.agent_random import AgentRandon
from ChefsHatGym.gameRooms.chefs_hat_room_local import ChefsHatRoomLocal
from ChefsHatGym.KEF import LogManager
from ChefsHatGym.env import ChefsHatEnv
import csv
import numpy
import random
import math
import copy
import gc
import os


class ChefsHatRoomTournament():

    def __init__(
        self,
        oponents,
        tournament_name: str,
        game_type: str = ChefsHatEnv.GAMETYPE["MATCHES"],
        stop_criteria: int = 10,
        max_rounds: int = -1,
        verbose: bool = True,
        save_dataset: bool = True,
        save_game_log: bool = True,
        log_directory: str = None,
        timeout_player_response: int = 5,
    ) -> None:
        """Initialize the room

        Args:
           
            opponents (list[ChefsHatAgent]): The list of opponents that will take part on the tournament.
             tournament_name (str): name of the tournament, no special character is allowed.
            game_type (str, optional): game type, defined as ChefsHatEnv.GAMETYPE. Defaults to ChefsHatEnv.GAMETYPE["MATCHES"].
            stop_criteria (int, optional): stop criteria for the game. Defaults to 10.
            max_rounds (int, optional): maximum rounds of the game, if -1 the game will play until it ends. Defaults to -1.
            verbose (bool, optional): room verbose. Defaults to True.
            save_dataset (bool, optional): save the game dataset .pkl. Defaults to True.
            save_game_log (bool, optional): save the game log. Defaults to True.
            log_directory (str, optional): directory to save the log. Defaults to None.
            timeout_player_response (int, optional): timeout for the player responses. Defaults to 5.
        
        """

        self.tournament_name = tournament_name
        self.opponents = oponents
        self.savingDirectory = log_directory
        self.verbose= verbose
        self.gameType = game_type
        self.gameStopCriteria = stop_criteria
        self.max_rounds = max_rounds
        self.save_dataset = save_dataset
        self.save_game_log = save_game_log



        """Complement the group of agents to be a number pow 2"""
        self.competitors = self.complementGroups()

        self.createFolderss()

    def createFolderss(self):
        """Create the folders that will be acessible by the agents
        """
        for agent in self.competitors:
                if not "RandomGYM_" in agent.name:
                    thisAgentFolder = os.path.join (self.savingDirectory, "Agents", agent.name) 
                    if not os.path.exists(thisAgentFolder):
                        os.makedirs(thisAgentFolder)
                        agent.saveModelIn = thisAgentFolder



    def createGroups(self):
        """Create the groups that will play the game.
         For each coop and compcoop agent, the agent will be paired with a "TeamMate_agent.name" random agent.

        :return: groups - list
        :rtype: list
        """
        random.shuffle(self.competitors)
        

        pairs = []

        [pairs.append([self.competitors[i], self.competitors[i + 1]]) for i in list(range(len(self.competitors)))[::2]]
        random.shuffle(pairs)

        groups = []
        for p in list(range(len(pairs)))[::2]:
            random.shuffle(pairs[p])
            newGroup = [pairs[p][0], pairs[p][1], pairs[p + 1][0], pairs[p + 1][1]]
            groups.append(newGroup)

        random.shuffle(groups)
        return groups


    def runTournament(self):

        """Run an entire tournament.
         Create all the brackets, control the game and tournament phases and creates all the metrics for comp and coop measures.
        """

        """Tournament parameters"""
        saveTournamentDirectory = self.savingDirectory  # Where all the logs will be saved

        groups = self.createGroups()

        brackets = [groups[0:int(len(groups) / 2)], groups[int(len(groups) / 2):]]

        phases = int(math.log(len(brackets[0]),2))+1

        logger = LogManager.Logger(os.path.join (saveTournamentDirectory, "Log.txt"), verbose=True)

        logger.newLogSession("Tournament starting!")
        logger.write("Total players:" + str(len(self.competitors)))
        logger.write("Total groups:" + str(len(groups)))
        for bIndex, b in enumerate(brackets):
            logger.write("Bracket "+str(bIndex)+":")
            for gIndex, g in enumerate(b):
                names = [a.name for a in b[gIndex]]
                logger.write(" -Group "+str(gIndex)+":"+str(names))

        logger.write("Phases per Bracket:" + str(phases))

        bWinners = []

        finalPosition = []
       
        thirds = []
        fourths = []

        for b in range(len(brackets)):
            logger.newLogSession("Starting Games from Bracket:" + str(b+1))
            thisPhaseGroup = brackets[b]
            for p in range(phases):
                logger.newLogSession("Starting Phase:" + str(p+1))
                names = [a.name for g in thisPhaseGroup for a in g]
                logger.write("- Participants:" + str(names))
                newPhaseGroups = []
                thirds.append([])
                fourths.append([])

                for game in range(len(thisPhaseGroup)):
                    names = [a.name for a in thisPhaseGroup[game]]
                    logger.write("- Game:" + str(game) + " - "+str(names))
                    first, second, third, fourth = self.playGame(thisPhaseGroup[game], b+1, p+1, game,saveTournamentDirectory, logger)
                    logger.write("-- First:" + str(first[0].name) + " - Second:" + str(second[0].name))

                    newPhaseGroups.append(first[0])
                    newPhaseGroups.append(second[0])

                    """Competitive Ranking"""

                    thirds[p].append([copy.copy(third[0].name), copy.copy(third[1])])
                    fourths[p].append([copy.copy(fourth[0].name), copy.copy(fourth[1])])

                    gc.collect()

                if p == phases-1:
                    bWinners.append(newPhaseGroups[0])
                    bWinners.append(newPhaseGroups[1])
                else:
                   thisPhaseGroup = [newPhaseGroups[g:g + 4] for g in list(range(len(newPhaseGroups)))[::4]]




        """After the end of the game sort the competitive rank fourths and thirds per phase and add them the bottom of the final Position"""
        for phaseIndex in range(phases):
            fourthsThisPhase = sorted(fourths[phaseIndex], key=lambda tup: tup[1])
            [finalPosition.append([f[0], f[1], (phaseIndex + 1)]) for f in fourthsThisPhase]

            thirdsThisPhase = sorted(thirds[phaseIndex], key=lambda tup: tup[1])
            [finalPosition.append([f[0], f[1], (phaseIndex + 1)]) for f in thirdsThisPhase]


        logger.newLogSession("Final match!")

        names = [a.name for a in bWinners if len(bWinners) > 0]
        logger.write("- Participants:" + str(names))
        first, second, third, fourth = self.playGame(bWinners, 3, 1, 1, saveTournamentDirectory, logger)

        """After the end of the last phase add the competitive agents to the competitive rank"""
        for agent in [fourth, third, second, first]:
            finalPosition.append([copy.copy(agent[0].name), copy.copy(agent[1]), copy.copy(phases+1)])

        logger.write("-- Final position:")
        logger.write("-- 1)" + str(first[0].name))
        logger.write("-- 2)" + str(second[0].name))
        logger.write("-- 3)" + str(third[0].name))
        logger.write("-- 4)" + str(fourth[0].name))

        """Writing comp rank"""
        with open(os.path.join (self.savingDirectory, "FinalResultsComp.csv"), mode='w') as csvFile:
            csvWriter = csv.writer(csvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            csvWriter.writerow(["Position", 'Player Name', 'Final Game Performance Score', 'Games Played'])
            for pIndex, player in enumerate(reversed(finalPosition)):
                csvWriter.writerow([(pIndex+1), player[0], player[1], player[2]])


    """Complement the opponents with random agents until we have enough to create two brackets"""
    def complementGroups(self):

        """Complement the number of agents so the game will have a number of 2^n players.
        The new players will be all random players and will have a RandomGYM_ name pattern.


               :param comp: The list of comp agents
               :type comp: list, mandatory

               :param coop: The list of coop agents
               :type coop: list, mandatory

               :param compCoop: The list of compCoop agents
               :type compCoop: list, mandatory


               :return: List of updated agents
               :rtype: list
         """

        totalAgents = len(self.opponents)

        difference = float(math.log(totalAgents,2))
        # print("Difference:" + str(difference))
        group = []
        [group.append(a) for a in self.opponents]

        if difference.is_integer():
            if totalAgents < 8:
                for n in range(int(8-totalAgents)):
                    group.append( AgentRandon(name=f"RandomGYM_{n}"))

            return group
        else:
            intDiff = math.modf(difference)[1]

            newAdditions = int(math.pow(2,intDiff+1) - totalAgents)

            for n in range(newAdditions):
                 group.append( AgentRandon(name=f"RandomGYM_{n}"))

        print (f"Competitors: {group}")
        return group


    """Playing a Game"""
    def playGame(self, group, bracket, round, gameNumber, saveDirectory, logger):

        """Play a single game and return the players in finishing order together with their score.

        The new players will be all random players and will have a RandomGYM_ name pattern.


               :param group: The list of players
               :type group: list, mandatory

               :param bracket: The bracket number
               :type bracket: int, mandatory

               :param round: The round number
               :type round: int, mandatory

               :param gameNumber: The number of this game within the tournament context
               :type gameNumber: int, mandatory

               :param saveDirectory: where this game will be saved
               :type gameNumber: str, mandatory

               :param logger: The logger
               :type logger: KEF.LogManager


               :return: [winner,performanceScoreWinner], [second, performanceScoreSecond], [third,performanceScoreThird], [fourth,performanceScoreFourth]
               :rtype: list
         """

        """Experiment parameters"""
        saveDirectory = os.path.join (saveDirectory, f"Bracket{bracket}", f"Phase_{round}", f"Game_{gameNumber}")
        verbose = False
        saveLog = True
        saveDataset = True

        """Setup the room"""

        room = ChefsHatRoomLocal(
            f"Bracket{bracket}_Phase_{round}_Game_{gameNumber}",
            timeout_player_response=5,
            game_type=self.gameType,
            stop_criteria=self.gameStopCriteria,
            max_rounds=self.max_rounds,
            verbose=verbose,
        )

        for a in group:
            room.add_player(a)

        info = room.start_new_game(game_verbose=True)    

       
        sortedScore = copy.copy(info["performanceScore"])
        sortedScore.sort()

        winnerIndex = info["performanceScore"].index(sortedScore[-1])
        performanceScoreWinner = info["performanceScore"][winnerIndex]

        sortedScore.pop(-1)

        secondIndex = info["performanceScore"].index(sortedScore[-1])
        performanceScoreSecond = info["performanceScore"][secondIndex]

        sortedScore.pop(-1)

        thirdIndex = info["performanceScore"].index(sortedScore[-1])
        performanceScoreThird = info["performanceScore"][thirdIndex]

        sortedScore.pop(-1)

        fourthIndex = info["performanceScore"].index(sortedScore[-1])
        performanceScoreFourth = info["performanceScore"][fourthIndex]

        winner = group[winnerIndex]
        second = group[secondIndex]
        third = group[thirdIndex]
        fourth = group[fourthIndex]

        if self.verbose:
            logger.write("-- Performance:" + str(info["performanceScore"]))
            logger.write("-- Points:" + str(info["score"]))

        return [winner,performanceScoreWinner], [second, performanceScoreSecond], [third,performanceScoreThird], [fourth,performanceScoreFourth]






