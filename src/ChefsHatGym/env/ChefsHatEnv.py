import gym
import random
import numpy
from ChefsHatGym.KEF import DataSetManager
from ChefsHatGym.KEF import ExperimentManager
import copy
from gym import spaces
import os

GAMETYPE = {"POINTS": "POINTS", "MATCHES": "MATCHES"}
ROLES = {0: "Dishwasher", 1: "Waiter", 2: "Souschef", 3: "Chef"}


class Player:
    name = ""
    cards = []

    acumulated_score = 0
    acumulated_performance_score = 0

    current_score = -1
    current_role = ""

    number_passes = 0
    number_discards = 0
    number_invalid_actions = 0
    number_pass_actions = 0

    last_action = ""
    finished = False
    finishing_position = -1

    def __init__(self, name, position) -> None:
        self.name = name
        self.position = position


class ChefsHatEnv(gym.Env):
    """ChefsHatEnv is the Chefs Hat game enviromnet class that allows to start and execute each step of the game.
    To instatiate the class, use gym.make('chefshat-v1').
    """

    gameFinished = False  #: Whether the game has been finished (True) or not (False).
    metadata = {"render.modes": ["human"]}

    def __init__(self):
        """Constructor method. Use gym.make instead of it."""

        # if integratedState:
        self.action_space = spaces.Discrete(int(200))
        self.observation_space = spaces.Box(
            low=numpy.float32(numpy.zeros(228)), high=numpy.float32(numpy.ones(228))
        )
        # pass

    def startExperiment(
        self,
        gameType=GAMETYPE["POINTS"],
        stopCriteria=3,
        maxRounds=-1,
        maxInvalidActions=5,
        playerNames=[],
        logDirectory="",
        verbose=0,
        saveLog=False,
        saveDataset=False,
    ):
        """This method stores parameters for a new exeperiment. An experiment is a set of games (see startNewGame method).

        :param rewardFunctions: A list of reward functions for each player, defaults to []
        :param gameType: The game type ("POINTS" or "MATCHES"), defaults to GAMETYPE["POINTS"]
        :type gameType: str, optional
        :param stopCriteria: Number of "MATCHES" or "POINTS" to stop the experiment, defaults to 3
        :type stopCriteria: int, optional
        :param maxRounds: Number maximum of rounds, before stoping the game. If -1, continue until all cards are finished, defaults to -1
        :type maxRounds: int, optional
        :param maxInvalidActions: How many invalid or continuous pass actions an Agent can do before a random action is assigned to it, defaults to 10
        :type maxInvalidActions: int, optional
        :param playerNames: A list of names for each player, defaults to []
        :type playerNames: list, mandatory
        :param logDirectory: The path for log directory, defaults to ""
        :type logDirectory: str, optional
        :param verbose: Verbose level (0 to 1), defaults to 0
        :type verbose: int, optional
        :param saveLog: Whether the log file will be generated (True) or not (False), defaults to False
        :type saveLog: bool, optional
        :param saveDataset: Whether the game dataset will be saved (True) or not (False), defaults to False
        :type saveDataset: bool, optional
        """

        # Start all game variables
        self.gameType = gameType
        self.stopCriteria = stopCriteria
        self.maxRounds = maxRounds if maxRounds > 0 else 999999
        self.players = []

        for count, name in enumerate(playerNames):
            self.players.append(Player(name, count))

        self.playerNames = playerNames
        self.saveDataset = saveDataset

        self.episodeNumber = 0

        self.logDirectory = logDirectory
        self.verbose = verbose
        self.saveLog = saveLog
        self.maxInvalidActions = maxInvalidActions

        self.playersInvalidActions = [0, 0, 0, 0]
        self.playersPassAction = [0, 0, 0, 0]

    def reset(self, seed=None, options=None):
        """This method increments episodeNumber, start a new game and return the first observation

        :return: The first observation array after the game has started. The observation is an int data-type ndarray.
        :rtype: ndarray
        """

        self.episodeNumber += 1
        self.startNewGame()
        return (numpy.array(self.getObservation()).astype(numpy.float32), {})

    def startNewGame(self):
        """Starts a new game using the parameters defined by the method startExperiment.
        You have to define the game type (per points or per game), and the stoping criteria (maximum points, maximum games).
        For logging purpose, set the saveLog, verbose and logDirectory in startExperiment method.
        """
        if not self.logDirectory == "":
            _path = os.path.split(self.logDirectory)
            self.experimentManager = ExperimentManager.ExperimentManager(
                _path[0],
                _path[1],
                verbose=self.verbose,
                saveLog=self.saveLog,
                save_dataset=self.saveDataset,
            )
            self.logger = self.experimentManager.logManager
            self.logger.newLogSession("Starting new Episode:" + str(self.episodeNumber))
            self.logger.write(
                "Players :" + str([player.name for player in self.players])
            )
            self.logger.write(
                "Stop Criteria :" + str(self.stopCriteria) + " " + str(self.gameType)
            )
            self.logger.write("Max Rounds :" + str(self.maxRounds))
        else:
            self.logger = None
            self.experimentManager = None
            self.saveDataset = False

        # Set Players Score and performance score
        # for player in self.players:
        #     player.score = -1
        # self.score = [0, 0, 0, 0]  # the score
        # self.performanceScore = [0, 0, 0, 0]  # the performance score

        self.board = []  # the current board
        self.maxCardNumber = 11  # The highest value of a card in the deck
        self.numberPlayers = 4  # number of players playing the game
        self.numberOfCardsPerPlayer = (
            0  # number of cards each player has at hand in the begining of the game
        )
        self.highLevelActions = self.getHighLevelActions()
        self.matches = 0
        self.gameFinished = False
        # self.finishingOrder = []  # Which payers already finished this match

        # Variables per Match
        self.cards = []  # the deck
        # self.playersHand = []  # the current cards each player has at hand
        self.currentPlayer = 0  # The current player playing the game
        self.playerStartedGame = 0  # who started the game
        # self.currentRoles = []  # Current roles of each player

        self.currentSpecialAction = []
        self.currentPlayerDeclaredSpecialAction = []

        self.rounds = 0
        self.lastToDiscard = 0

        self.experimentManager.dataSetManager.startNewGame(
            agent_names=self.playerNames,
        )

        # self.startNewmatch()  # Initiate all the match parameters

        self.start_match_handle_cards()
        self.start_match_define_order()

    def get_acumulated_performance_score(self):
        score = {}
        for player in self.players:
            score[player.name] = player.acumulated_performance_score

        return score

    def get_acumulated_score(self):
        score = {}
        for player in self.players:
            score[player.name] = player.acumulated_score

        return score

    def get_current_score(self):
        score = {}
        for player in self.players:
            score[player.name] = player.current_score

        return score

    def get_current_roles(self):
        role = {}
        for player in self.players:
            role[player.name] = player.current_role

        return role

    def player_finished(self, player_index):

        finishing_position = 0
        for p in self.players:
            if p.finished:
                finishing_position += 1

        self.players[player_index].finished = True
        self.players[player_index].finishing_position = finishing_position
        self.players[player_index].cards = numpy.zeros(self.numberOfCardsPerPlayer)

    def update_player_score_roles(self, player_index):

        points = self.calculateScore(self.players[player_index].finishing_position)

        self.players[player_index].acumulated_score += points
        self.players[player_index].current_score = points

        pScore = (points * 10) / self.rounds
        self.players[player_index].acumulated_performance_score = (
            self.players[player_index].acumulated_performance_score * (self.matches - 1)
            + pScore
        ) / self.matches

        self.players[player_index].current_role = ROLES[points]

        # if numpy.max(self.score) > 0:
        #     # Chef, sous-Chef, waiter and dishwasher
        #     self.currentRoles = [self.finishingOrder[i] for i in range(4)]

    def start_match_handle_cards(self):
        """Handle the cards to the players."""

        # Stop by round set to false
        self.stoppedByRound = False

        # Create a deck
        flat = lambda l: [item for sublist in l for item in sublist]
        self.cards = flat(
            [[v for _ in range(v)] for v in range(1, self.maxCardNumber + 1)]
        ) + [self.maxCardNumber + 1 for _ in range(2)]

        # self.lastActionPlayers = ["", "", "", ""]

        # shuffle the decks
        random.shuffle(self.cards)

        # # create players hand
        # self.playersHand = []
        # for p in self.players:
        #     self.playersHand.append([])

        self.numberOfCardsPerPlayer = int(len(self.cards) / len(self.players))

        # initialize the board
        self.restartBoard()

        # Update the Match number

        self.matches += 1

        self.experimentManager.dataSetManager.startNewMatch(
            match_number=self.matches,
            game_score=self.get_current_score(),
            current_roles=self.get_current_roles(),
        )

        # deal the cards
        self.dealCards()

        # Reset Players info
        for p in self.players:
            p.current_score = -1
            p.number_passes = 0
            p.number_discards = 0
            p.number_invalid_actions = 0
            p.number_pass_actions = 0

            p.last_action = ""
            p.finished = False
            p.finishing_position = -1

        if not self.experimentManager == None:
            self.logger.newLogSession("Match Number %f Starts!" % self.matches)
            self.logger.write("Deck: " + str(self.cards))
            for player in self.players:
                self.logger.write(f"Player {player.name} hand: {player.cards}")

    def start_match_define_order(self):
        """Define the starting order for each match"""
        # Establishes who starts the game randomly
        playerTurn = numpy.array(range(self.numberPlayers))
        random.shuffle(playerTurn)

        index = numpy.array(range(self.numberPlayers))
        random.shuffle(index)

        self.currentPlayer = playerTurn[index[0]]

        # verify if this player has a 12 in its hand, otherwise iterate to the next player

        while not (self.maxCardNumber + 1 in self.players[self.currentPlayer].cards):
            self.currentPlayer = self.currentPlayer + 1
            if self.currentPlayer >= self.numberPlayers:
                self.currentPlayer = 0

        # save the player who started the game
        self.playerStartedGame = self.currentPlayer

        # Reset the players finish order, finish position and last action
        for player in self.players:
            player.finished = False
            player.finishing_position = -1
            player.last_action = ""

        # self.finishingOrder = []  # Reset the players that finished this match

        # Current round of the game set to 0
        self.rounds = 1

        if not self.experimentManager == None:
            self.logger.newLogSession("Round:" + str(self.rounds))

    def doSpecialAction(self, player, action):
        """Allows an agent to perform a special action

        Args:
            player (_type_): _description_
            action (_type_): _description_
        """
        if not self.experimentManager == None:
            self.logger.write(
                "- Player :"
                + str(self.players[player].name)
                + " declared "
                + str(self.currentSpecialAction)
                + "!"
            )

        if (
            action == "It is food fight!"
        ):  # If it is food fight, update the roles of the game.
            for p in self.players:
                p.current_role = ROLES[3 - p.score]

            # newcurrentRoles = []
            # newcurrentRoles.append(self.currentRoles[3])  # Chef
            # newcurrentRoles.append(self.currentRoles[2])  # sous-Chef
            # newcurrentRoles.append(self.currentRoles[1])  # waiter
            # newcurrentRoles.append(self.currentRoles[0])  # dishwasher
            # self.currentRoles = []
            # self.currentRoles = newcurrentRoles

            self.logNewRoles()

        self.experimentManager.dataSetManager.do_special_action(
            match_number=self.matches,
            source=self.players[player].name,
            current_roles=self.get_current_roles(),
            action_description=action,
        )

    def get_chef_souschef_roles_cards(self):
        """returns the cards at hand of the chef and souschef.

        Returns:
            _type_: _description_
        """

        chef = 0
        sousChef = 0
        dishwasher = 0
        waiter = 0

        chefCards = []
        sousChefCards = []
        dishwasherCards = []
        waiterCards = []

        for count, p in enumerate(self.players):
            if p.current_role == ROLES[3]:
                chef = count
                chefCards = p.cards
            elif p.current_role == ROLES[2]:
                sousChef = count
                sousChefCards = p.cards
            elif p.current_role == ROLES[1]:
                waiter = count
                waiterCards = sorted(p.cards)[0]  # get the minimum waiter card
            else:
                dishwasher = count
                dishwasherCards = sorted(p.cards)[
                    0:2
                ]  # get the minimum dishwasher cards

        # # Chef, sous-Chef, waiter and dishwasher
        # score = self.currentRoles

        # dishwasherCards = sorted(self.playersHand[score[3]])[
        #     0:2
        # ]  # get the minimum dishwasher cards
        # waiterCard = sorted(self.playersHand[score[2]])[0]  # get the minimum waiterCard

        # print(f"Chef cards: {chefCards}")
        # print(f"Souschef card: {sousChefCards}")
        # print(f"Waiter card: {waiterCards}")
        # print(f"Dishwasher cards: {dishwasherCards}")

        return (
            dishwasher,
            dishwasherCards,
            waiter,
            waiterCards,
            sousChef,
            sousChefCards,
            chef,
            chefCards,
        )

    def exchange_cards(
        self,
        chefCards,
        souschefCard,
        waiterCard,
        dishwasherCards,
        specialAction,
        playerDeclared,
    ):
        """Allows a chef and souschef agent to select the cards to be exchanged.

        Args:
            souschefCard (_type_): _description_
            chefCards (_type_): _description_
            specialAction (_type_): _description_
            playerDeclared (_type_): _description_
        """

        # souschefCard = souschefCard[0]
        # waiterCard = waiterCard[0]

        # dishwasherCards = sorted(self.playersHand[score[3]])[
        #     0:2
        # ]  # get the minimum dishwasher cards
        # waiterCard = sorted(self.playersHand[score[2]])[0]  # get the minimum waiterCard

        for p in self.players:
            if p.current_role == ROLES[0]:
                # update the dishwasher cards
                for i in range(len(dishwasherCards)):
                    cardIndex = p.cards.index((dishwasherCards[i]))
                    p.cards[cardIndex] = chefCards[i]

            elif p.current_role == ROLES[1]:
                # update the waiter card
                cardIndex = p.cards.index((waiterCard))
                p.cards[cardIndex] = souschefCard

            elif p.current_role == ROLES[2]:
                # update the souschef cards
                cardIndex = p.cards.index((souschefCard))
                p.cards[cardIndex] = waiterCard
            else:

                # update the chef cards
                for i in range(len(chefCards)):
                    cardIndex = p.cards.index((chefCards[i]))
                    p.cards[cardIndex] = dishwasherCards[i]

        # # update the souschef cards
        # cardIndex = self.playersHand[score[1]].index((souschefCard))
        # self.playersHand[score[1]][cardIndex] = waiterCard

        # Logging new cards exchanged!

        self.logger.newLogSession("Changing cards!")
        self.logger.write("--- Dishwasher gave:" + str(dishwasherCards))
        self.logger.write("--- Waiter gave:" + str(waiterCard))
        self.logger.write("--- Souschef gave:" + str(souschefCard))
        self.logger.write("--- Chef gave:" + str(chefCards))

        self.experimentManager.dataSetManager.do_card_exchange(
            match_number=self.matches,
            action_description=[
                specialAction,
                playerDeclared,
                dishwasherCards,
                waiterCard,
                souschefCard,
                chefCards,
            ],
            player_hands=[p.cards for p in self.players],
        )

        self.start_match_define_order()

    def logNewRoles(self):
        """Add the new roles to log"""
        self.logger.newLogSession("Changind roles!")

        roles = self.get_current_roles()

        for role in roles:
            self.logger.write(f"- {role} : {roles[role]}")

    def getObservation(self):
        """Get a new observation. The observation is composed of the current board, the playersHand and the possible actions.

        :return: The observation is an int data-type ndarray.
                    The observation array has information about the board game, the current player's hand, and current player possible actions.
                    This array must have the shape of (228, ) as follows:
                    The first 11 elements represent the board game card placeholder (the pizza area).
                    The game cards are represented by an integer, where 0 (zero) means no card.
                    The following 17 elements (from index 11 to 27) represent the current player hand cards in the sequence.
                    By the end, the last 200 elements (from index 27 to 227) represent all possible actions in the game.
                    The allowed actions for the current player are filled with one, while invalid actions are filled with 0.
        :rtype: ndarray
        """
        board = numpy.array(self.board) / (self.maxCardNumber + 2)

        playersHand = numpy.array(self.players[self.currentPlayer].cards) / (
            self.maxCardNumber + 2
        )
        possibleActions = self.getPossibleActions(self.currentPlayer)

        return numpy.concatenate((board, playersHand, possibleActions)).astype(
            numpy.float32
        )

    def isGameOver(self):
        """isGameOver
        :return: Boolean flag if the game is over.
        :rtype: bool
        """
        gameFinished = False

        # input("here")
        # Verify if the game is over
        if self.gameType == GAMETYPE["POINTS"]:
            scores = self.get_acumulated_score()
            for score in scores:
                if scores[score] >= self.stopCriteria:
                    gameFinished = True
                    break
        elif self.gameType == GAMETYPE["MATCHES"]:
            if self.matches >= self.stopCriteria:
                gameFinished = True

        if not self.experimentManager == None and gameFinished:
            # print(f"Adding to the log!")
            self.logger.newLogSession(
                "Game Over! Final Score:"
                + str(self.get_acumulated_score())
                + " - Final Performance Score:"
                + str(self.get_acumulated_performance_score())
            )

        return gameFinished

    def nextPlayer(self):
        """nextPlayer
        advance to the next player
        """

        self.currentPlayer = self.currentPlayer + 1
        if self.currentPlayer == self.numberPlayers:
            self.currentPlayer = 0

        while (
            self.players[self.currentPlayer].finished
            or self.players[self.currentPlayer].last_action == "pass"
        ):

            self.currentPlayer = self.currentPlayer + 1
            if self.currentPlayer == self.numberPlayers:
                self.currentPlayer = 0

        # for i in range(len(self.lastActionPlayers)):
        #     if (
        #         (not self.lastActionPlayers[self.currentPlayer] == "")
        #         and self.lastActionPlayers[self.currentPlayer][0]
        #         == DataSetManager.actionPass
        #     ) or (
        #         (not self.lastActionPlayers[self.currentPlayer] == "")
        #         and self.lastActionPlayers[self.currentPlayer][0]
        #         == DataSetManager.actionFinish
        #     ):
        #         self.currentPlayer = self.currentPlayer + 1
        #         if self.currentPlayer == self.numberPlayers:
        #             self.currentPlayer = 0

    def calculateScore(self, finishingPosition):
        """calculateScore
        :param playerPosition: The finishing position of the player
        :type playerPosition: int, mandatory
        :return: Integer the score of the given player.
        :rtype: int
        """
        return 3 - finishingPosition

    def getRandomAction(self, possibleActions):
        """getRandomAction
            Return a random allowed action.

        :param possibleActions: The list of possible actions
        :type possibleActions: list, mandatory
        :return: List the random action.
        :rtype: list
        """
        itemindex = numpy.array(numpy.where(numpy.array(possibleActions) == 1))[
            0
        ].tolist()

        random.shuffle(itemindex)
        aIndex = itemindex[0]
        a = numpy.zeros(200)
        a[aIndex] = 1

        return a.tolist()

    def decode_possible_actions(self, possibleActions):

        nonzeroElements = numpy.nonzero(possibleActions)

        currentlyAllowedActions = list(
            numpy.copy(numpy.array(self.highLevelActions)[nonzeroElements,])[0]
        )

        return currentlyAllowedActions

    def step(self, action):
        """Execute an action in the game.

        :param action: The action array with 200 elements, where the choosen action is the index of the highest value
        :type action: ndarray
        :return: a tuple cointaining:
                observation - ndarray
                return of reward function - float
                True if the match is over, False if not - bool
                info - dict: {
                'actionIsRandom':(bool),
                'validAction': (bool),
                'matches': (bool),
                'rounds': (int),
                'score': (int),
                'performanceScore': (int),
                'thisPlayer': (int),
                'thisPlayerFinished': (bool),
                'isPizzaReady': (bool),
                'boardBefore': (ndarray),
                'boardAfter': (ndarray),
                'board': (ndarray),
                'possibleActions': (list),
                'action': (ndarray),
                'thisPlayerPosition': (int),
                'lastPlayerAction': (int),
                'lastActionPlayers': (ndarray),
                'lastActionTypes': (ndarray),
                'RemainingCardsPerPlayer': (ndarray),
                'players': (list),
                'currentRoles': (list),
                'currentPlayer': (int),
                }

        :rtype: tuple
        """
        validAction = False
        isMatchOver = False
        isPizzaReady = False
        actionIsRandom = False
        thisPlayerPosition = -1

        possibleActions = self.getPossibleActions(self.currentPlayer)

        # Calculate the decoded possible actions in a high-level
        nonzeroElements = numpy.nonzero(possibleActions)
        possibleActions_decoded = list(
            numpy.copy(numpy.array(self.highLevelActions)[nonzeroElements,])[0]
        )

        thisPlayer = copy.copy(self.currentPlayer)
        boardBefore = copy.copy(self.board)

        observationBefore = copy.copy(self.getObservation())

        if (
            self.players[thisPlayer].number_invalid_actions >= self.maxInvalidActions
            or self.players[thisPlayer].number_pass_actions >= self.maxInvalidActions
        ):
            action = self.getRandomAction(possibleActions)
            actionIsRandom = True

        if self.isActionAllowed(
            action, possibleActions
        ):  # if the player can make the action, do it.
            validAction = True
            self.players[thisPlayer].number_invalid_actions = 0

            cardsDiscarded = []
            if numpy.argmax(action) == len(possibleActions) - 1:  # Pass action
                actionComplete = self.highLevelActions[numpy.argmax(action)]
                self.players[thisPlayer].number_pass_actions += 1
                self.players[thisPlayer].last_action = actionComplete
            else:  # Discard action
                self.players[thisPlayer].number_pass_actions = 0
                cardsDiscarded = self.discardCards(self.currentPlayer, action)

                actionComplete = self.highLevelActions[numpy.argmax(action)]
                self.players[thisPlayer].last_action = actionComplete

                self.lastToDiscard = self.currentPlayer

            # Verify if the player has finished this match
            if self.hasPlayerFinished(self.currentPlayer):

                self.player_finished(self.currentPlayer)

                # # self.finishingOrder.append(self.currentPlayer)

                # # actionComplete = (DataSetManager.actionFinish, cardsDiscarded)

                # # Calculate and update the player score
                # # playerFinishingPosition = self.finishingOrder.index(self.currentPlayer)

                # points = self.calculateScore(playerFinishingPosition)

                # self.score[self.currentPlayer] += points

                # pScore = (points * 10) / self.rounds
                # # self.performanceScore[self.currentPlayer] += pScore
                # self.performanceScore[self.currentPlayer] = (
                #     self.performanceScore[self.currentPlayer] * (self.matches - 1)
                #     + pScore
                # ) / self.matches
                # thisPlayerPosition = playerFinishingPosition

            # Update the player last action
            # self.lastActionPlayers[self.currentPlayer] = actionComplete

            if not self.experimentManager == None:
                self.logger.write(
                    " -- Player "
                    + str(thisPlayer)
                    + " - "
                    + str(self.players[self.currentPlayer].name)
                )
                self.logger.write(
                    " --- Player Hand: " + str(self.players[self.currentPlayer].cards)
                )
                self.logger.write(" --- Board Before: " + str(boardBefore))
                self.logger.write(
                    " --- Action: " + str(self.highLevelActions[numpy.argmax(action)])
                )

                if self.players[self.currentPlayer].finished:
                    self.logger.write(" --- Player Finished!")

                self.logger.write(" --- Board After: " + str(self.board))

            boardAfter = self.getObservation()[0:11].tolist()

            self.experimentManager.dataSetManager.doDiscard(
                match_number=self.matches,
                round_number=self.rounds,
                source=self.players[thisPlayer].name,
                action_description=self.highLevelActions[numpy.argmax(action)],
                player_hands=self.players[thisPlayer].cards,
                board_before=[int(b * 13) for b in boardBefore],
                board_after=[int(b * 13) for b in boardAfter],
                possible_actions=possibleActions_decoded,
                player_finished=self.players[thisPlayer].finished,
            )

            # Identify if the pizza is ready
            isPizzaReady = False
            if self.makePizza():
                isPizzaReady = True

                self.experimentManager.dataSetManager.declare_pizza(
                    match_number=self.matches,
                    round_number=self.rounds - 1,
                    source=self.players[self.lastToDiscard].name,
                )

                self.currentPlayer = self.lastToDiscard
                if self.players[self.currentPlayer].finished:
                    self.nextPlayer()
            else:
                self.nextPlayer()

            # If finish the game by rounds, calculate the finishing order, and remove the cards from the hands of all players.
            points_position = [0, 0, 0, 0]

            if self.rounds > self.maxRounds:

                # Calculate the players position based on the amount of cards they have in their hand

                # amountOfCardsByPlayer = [
                #     numpy.count_nonzero(a.cards) for a in self.players
                # ]

                # print("---------------")
                # print(f"AMount of cards by player: {amountOfCardsByPlayer}")

                positions = {}
                for p in self.players:
                    positions[p.name] = numpy.count_nonzero(p.cards)

                sortedPositions = dict(sorted(positions.items(), key=lambda x: x[1]))

                print(f"Player position: {positions}")
                print(f"Player sorted position: {sortedPositions}")

                for player_name in sortedPositions.keys():
                    this_player = None
                    for count, p in enumerate(self.players):
                        if p.name == player_name:
                            this_player = count
                            break

                    self.player_finished(this_player)

                # # Put all player hands to 0
                # for p in self.players:
                #     p.cards = numpy.zeros(self.numberOfCardsPerPlayer)

                # for i in range(len(self.playersHand)):
                #     self.playersHand[i] = numpy.zeros(self.numberOfCardsPerPlayer)

                # Calculate the players score
                # points_position = [
                #     self.calculateScore(position) for position in self.finishingOrder
                # ]

                # print(f"Points Position: {points_position}")

                # for count, point in enumerate(points_position):
                #     self.score[count] += point

                #     pScore = (point * 10) / self.rounds

                #     self.performanceScore[count] = (
                #         self.performanceScore[count] * (self.matches - 1) + pScore
                #     ) / self.matches

            if self.isMatchover():
                isMatchOver = True

                "Update points and score per player"
                for count, p in enumerate(self.players):
                    self.update_player_score_roles(count)

                # # if the score exists, update roles
                # if numpy.max(self.score) > 0:
                #     # Chef, sous-Chef, waiter and dishwasher
                #     self.currentRoles = [self.finishingOrder[i] for i in range(4)]

                self.experimentManager.dataSetManager.saveFile()

                if isPizzaReady:
                    log_round = self.rounds - 1
                else:
                    log_round = self.rounds

                self.experimentManager.dataSetManager.end_match(
                    match_number=self.matches,
                    round_number=log_round,
                    match_score=self.get_current_score(),
                    game_score=self.get_acumulated_score(),
                    current_roles=self.get_current_roles(),
                )

                if not self.experimentManager == None:
                    self.logger.newLogSession(
                        "Match "
                        + str(self.matches)
                        + " over! Current Score:"
                        + str(self.get_current_score())
                    )

                if self.isGameOver():
                    self.gameFinished = True
                    self.experimentManager.dataSetManager.end_experiment(
                        match_number=self.matches,
                        round_number=log_round,
                        current_roles=self.get_current_roles(),
                        game_score=self.get_acumulated_score(),
                        game_performance=self.get_acumulated_performance_score(),
                    )
                else:
                    self.logNewRoles()
                    self.start_match_handle_cards()

            # if self.gameFinished:
            #     self.experimentManager.dataSetManager.saveFile()
        else:
            self.players[thisPlayer].number_invalid_actions += 1
            isMatchOver = False
            boardAfter = self.getObservation()[0:11].tolist()

        # Sanitizing the action
        arg_max_action = numpy.argmax(action)
        action[arg_max_action] = 1

        # this_row["Match"] = match_number
        # this_row["Round"] = round_number
        # this_row["Agent_Names"] = [agent_names]
        # this_row["Source"] = source
        # this_row["Action_Type"] = action_type
        # this_row["Action_Description"] = action_description
        # this_row["Player_Finished"] = player_finished
        # this_row["Player_Hands"] = [player_hands]
        # this_row["Board_Before"] = [board_before]
        # this_row["Board_After"] = [board_after]
        # this_row["Possible_Actions"] = [possible_actions]
        # this_row["Current_Roles"] = [current_roles]
        # this_row["Match_Score"] = [match_score]
        # this_row["Game_Score"] = [game_score]
        # this_row["Game_Performance_Score"] = [game_performance_score]

        info = {}
        # Game Settings Info
        info["Matches"] = int(self.matches)
        info["Rounds"] = int(self.rounds)
        info["Player_Names"] = [p.name for p in self.players]

        # This Player Info
        info["Author_Index"] = int(thisPlayer)
        info["Author_Possible_Actions"] = possibleActions_decoded

        # Action Info
        info["Action_Valid"] = bool(validAction)
        info["Action_Random"] = bool(actionIsRandom)
        info["Action_Index"] = int(numpy.argmax(action))
        info["Action_Decoded"] = self.highLevelActions[numpy.argmax(action)]

        # Gameplay Status
        info["Is_Pizza"] = bool(isPizzaReady)
        info["Pizza_Author"] = int(self.lastToDiscard) if isPizzaReady else -1
        info["Finished_Players"] = {p.name: bool(p.finished) for p in self.players}
        info["Cards_Per_Player"] = {
            p.name: numpy.count_nonzero(p.cards) for p in self.players
        }

        info["Next_Player"] = int(self.currentPlayer)

        # Board Info
        info["Board_Before"] = [int(a * 13) for a in observationBefore[0:11].tolist()]
        info["Board_After"] = [int(a * 13) for a in boardAfter]

        # Match Info
        info["Current_Roles"] = self.get_current_roles()
        info["Match_Score"] = self.get_current_score()
        info["Game_Score"] = self.get_acumulated_score()
        info["Game_Performance_Score"] = self.get_acumulated_performance_score()

        # info["actionIsRandom"] = actionIsRandom
        # info["validAction"] = validAction
        # info["matches"] = int(self.matches)
        # info["rounds"] = int(self.rounds)
        # info["score"] = self.score
        # info["performanceScore"] = self.performanceScore
        # info["thisPlayer"] = int(thisPlayer)
        # info["thisPlayerFinished"] = thisPlayer in self.finishingOrder
        # info["PlayersFinished"] = [
        #     p in self.finishingOrder for p in range(self.numberPlayers)
        # ]
        # info["isPizzaReady"] = isPizzaReady
        # info["boardBefore"] = observationBefore[0:11].tolist()
        # info["boardAfter"] = boardAfter
        # info["board"] = numpy.array(self.getObservation() * 13, dtype=int).tolist()[:11]
        # info["possibleActions"] = possibleActions
        # info["possibleActionsDecoded"] = currentlyAllowedActions
        # info["action"] = action
        # info["thisPlayerPosition"] = int(thisPlayerPosition)
        # info["lastActionPlayers"] = self.lastActionPlayers
        # info["lastActionTypes"] = [
        #     "" if a == "" else a[0] for a in self.lastActionPlayers
        # ]
        # info["RemainingCardsPerPlayer"] = [
        #     len(list(filter(lambda a: a > 0, self.playersHand[i])))
        #     for i in range(self.numberPlayers)
        # ]
        # info["players"] = self.playerNames
        # info["currentRoles"] = self.currentRoles
        # info["currentPlayer"] = int(self.currentPlayer)

        reward = 0
        return (
            numpy.array(self.getObservation()).astype(numpy.float32),
            reward,
            isMatchOver,
            False,
            info,
        )

    def render(self, mode="human", close=False):
        pass

    def close(self):
        pass

    def makePizza(self):
        """Make a pizza. Update the game to the next round and collect all cards from the board

        :return: pizzaReady - bool
        :rtype: bool
        """
        playersInGame = []
        for count, player in enumerate(self.players):
            if not player.finished:
                playersInGame.append(count)

        print(f"------------")
        print(f"Checking Pizza")

        # for i in range(len(self.lastActionPlayers)):
        #     if not (i in self.finishingOrder):
        #         playersInGame.append(i)

        # print ("self.lastActionPlayers:" + str(self.lastActionPlayers))
        # print ("FInishing Order:" + str(self.finishingOrder))
        number_passes = 0
        numberOfActions = 0

        for i in playersInGame:
            print(
                f"Player: {self.players[i].name } - last action: {self.players[i].last_action }"
            )
            if self.players[i].last_action == self.highLevelActions[-1]:
                number_passes += 1

            if self.players[i].last_action != "":
                numberOfActions += 1

        # print("Players in game:" + str(playersInGame))
        # print("Number of Actions:" + str(numberOfActions))
        # print("Number passes:" + str(number_passes))

        pizzaReady = False
        if (number_passes >= len(playersInGame) - 1) and (
            numberOfActions == len(playersInGame)
        ):
            self.restartBoard()
            pizzaReady = True

            if not self.experimentManager == None:
                self.logger.newLogSession(
                    f"{self.players[self.lastToDiscard].name} Made a Pizza!!!"
                )

            self.nextRound()

        print(f"-------------")

        return pizzaReady

    def nextRound(self):
        """move the game to the next round"""
        self.rounds = self.rounds + 1

        newLastActionPlayers = ["", "", "", ""]

        for player in self.players:
            if not player.finished:
                player.last_action = ""

        # for actionIndex, action in enumerate(self.lastActionPlayers):
        #     if (not action == "") and action[0] == DataSetManager.actionFinish:
        #         newLastActionPlayers[actionIndex] = action

        # print ("Previous actions:" + str(self.lastActionPlayers))
        # print ("Next actions:" + str(newLastActionPlayers))
        # self.lastActionPlayers = newLastActionPlayers

        if not self.experimentManager == None:
            self.logger.newLogSession("Round:" + str(self.rounds))

    def isMatchover(self):
        """Verify if this match is over
        look at the players hand, if 3 of them have 0 cards, match over.
        if match over,  add plyers to the finishing order


        :return: isMatchOver - bool
            :rtype: bool
        """
        isMatchOver = True

        players_finished = 0

        for p in self.players:
            if p.finished:
                players_finished += 1

        # for i in range(len(self.playersHand)):
        #     if numpy.array(self.playersHand[i]).sum() == 0:
        #         players_finished += 1

        if players_finished < 3:
            isMatchOver = False
        else:
            # Finish the last player
            for count, p in enumerate(self.players):
                if not p.finished:
                    self.player_finished(count)

        # for i in range(len(self.playersHand)):
        #     if not i in self.finishingOrder:
        #         self.finishingOrder.append(i)
        #         break

        return isMatchOver

    def getHighLevelActions(self):
        """Generate all the possible actions in a human-friendly way

        :return: highLevelActions - List
            :rtype: list
        """
        highLevelActions = []

        for cardNumber in range(self.maxCardNumber):
            for cardQuantity in range(cardNumber + 1):
                highLevelActions.append(
                    "C" + str(cardNumber + 1) + ";Q" + str(cardQuantity + 1) + ";J0"
                )
                highLevelActions.append(
                    "C" + str(cardNumber + 1) + ";Q" + str(cardQuantity + 1) + ";J1"
                )
                highLevelActions.append(
                    "C" + str(cardNumber + 1) + ";Q" + str(cardQuantity + 1) + ";J2"
                )

        highLevelActions.append("C0;Q0;J1")
        highLevelActions.append("pass")

        return highLevelActions

    # the number of possible actions is: self.maxCardNumber * self.maxCardNumber * 3 + 2
    # where the *3 refers to the options: discard a card, card+1 joker, card + 2 jokers
    # the 2 refers to: discard only one joker, and pass action
    def getPossibleActions(self, player):
        """Given a player, return the actions this player is allowed to make

            :param player: the player index
            :type player: int

        :return: getPossibleActions - (ndarray)
            :rtype: (ndarray)
        """

        this_player_played = self.players[player].last_action == ""
        firstAction = (
            self.playerStartedGame == self.currentPlayer
            and self.rounds == 1
            and this_player_played
        )

        # print(
        #     f"First action = {firstAction} - Player started game ({self.playerStartedGame}) == currentPlayer ({self.currentPlayer}) and self.rounds({self.rounds}) == 1"
        # )

        # print ("Player:", player)
        possibleActions = []

        unique, counts = numpy.unique(self.board, return_counts=True)
        currentBoard = dict(zip(unique, counts))

        unique, counts = numpy.unique(self.players[player].cards, return_counts=True)
        currentPlayerHand = dict(zip(unique, counts))

        highestCardOnBoard = 0
        for boardItem in currentBoard:
            if not boardItem == self.maxCardNumber + 1:
                highestCardOnBoard = boardItem

        jokerQuantityBoard = 0

        if self.maxCardNumber + 1 in self.board:
            jokerQuantityBoard = currentBoard[self.maxCardNumber + 1]

        if self.maxCardNumber + 1 in currentPlayerHand.keys():
            jokerQuantity = currentPlayerHand[self.maxCardNumber + 1]
        else:
            jokerQuantity = 0

        cardDescription = ""
        for cardNumber in range(self.maxCardNumber):
            for cardQuantity in range(cardNumber + 1):
                isThisCombinationAllowed = 0
                isthisCombinationOneJokerAllowed = 0
                isthisCombinationtwoJokersAllowed = 0

                # print("Card:" + str(cardNumber + 1) + " Quantity:" + str(cardQuantity + 1))

                """If this card number is in my hands and the amount of cards in my hands is this amount"""
                if (cardNumber + 1) in self.players[player].cards and currentPlayerHand[
                    cardNumber + 1
                ] >= cardQuantity + 1:
                    # print("-- this combination exists in my hand!")

                    """Check combination without the joker"""
                    """Check if this combination of card and quantity can be discarded given teh cards on the board"""
                    """Check if this cardnumber is smaller than the cards on the board"""
                    """ and check if the cardquantity is equal of higher than the number of cards on the board (represented by the highest card on the board ) + number of jokers on the board"""
                    if (cardNumber + 1 < highestCardOnBoard) and (
                        cardQuantity + 1
                        >= currentBoard[highestCardOnBoard] + jokerQuantityBoard
                    ):
                        """Check if this is the first move"""
                        """If it is the first move, onle 11s are allowed"""
                        if firstAction:
                            if cardNumber + 1 == self.maxCardNumber:
                                isThisCombinationAllowed = 1
                                # print("--- this combination can be put down on the board because it is first action!")
                        else:
                            """If it is not first move, anything on this combination is allowed!"""
                            # print("--- this combination can be put down on the board because and it is not first action!")
                            isThisCombinationAllowed = 1

                    """Check combination with the joker"""

                    if jokerQuantity > 0:
                        """Check for 1 joker at hand"""
                        """Check if this combination of card and quantity + joker can be discarded given the cards on the board"""
                        """Check if this cardnumber is smaller than the cards on the board"""
                        """ and check if the cardquantity + 1 joker is equal or higher than the number of cards on the board (represented by the highest card on the board ) + number of jokers on the board"""
                        if (cardNumber + 1 < highestCardOnBoard) and (
                            (cardQuantity + 1 + 1)
                            >= currentBoard[highestCardOnBoard] + jokerQuantityBoard
                        ):
                            """Check if this is the first move"""
                            """If it is the first move, onle 11s are allowed"""
                            if firstAction:
                                if cardNumber + 1 == self.maxCardNumber:
                                    # print(
                                    #     "--- this combination can be put down on the board because and it is first action and joker!")
                                    isthisCombinationOneJokerAllowed = 1
                            else:
                                """If it is not first move, anything on this combination is allowed!"""
                                # print(
                                #     "--- this combination can be put down on the board because and it is not first action and joker!")
                                isthisCombinationOneJokerAllowed = 1

                        if jokerQuantity > 1:
                            """Check for 2 jokers at hand"""
                            """Check if this combination of card and quantity + joker can be discarded given the cards on the board"""
                            """Check if this cardnumber is smaller than the cards on the board"""
                            """ and check if the cardquantity + 2 joker is equal or higher than the number of cards on the board (represented by the highest card on the board ) + number of jokers on the board"""
                            if (cardNumber + 1 < highestCardOnBoard) and (
                                (cardQuantity + 1 + 2)
                                >= currentBoard[highestCardOnBoard] + jokerQuantityBoard
                            ):
                                """Check if this is the first move"""
                                """If it is the first move, onle 11s are allowed"""
                                if firstAction:
                                    if cardNumber + 1 == self.maxCardNumber:
                                        # print(
                                        #     "--- this combination can be put down on the board because and it is first action and 2 jokers!")
                                        isthisCombinationtwoJokersAllowed = 1

                                else:
                                    """If it is not first move, anything on this combination is allowed!"""
                                    # print(
                                    #     "--- this combination can be put down on the board because and it is not first action and 2 jokers!")
                                    isthisCombinationtwoJokersAllowed = 2

                possibleActions.append(isThisCombinationAllowed)
                possibleActions.append(isthisCombinationOneJokerAllowed)
                possibleActions.append(isthisCombinationtwoJokersAllowed)

        canDiscardOnlyJoker = 0

        if (
            self.maxCardNumber + 1 in self.players[player].cards
        ):  # there is a joker in the hand
            if not firstAction:
                if highestCardOnBoard == self.maxCardNumber + 2:
                    canDiscardOnlyJoker = 1

        possibleActions.append(canDiscardOnlyJoker)

        if firstAction:
            possibleActions.append(
                0
            )  # the pass action, which is anot a valid action on the first action
        else:
            possibleActions.append(1)  # the pass action, which is always a valid action

        # print(
        #     f"First Action: {firstAction} - This PLayer played: {this_player_played} - POssible Actions: {possibleActions}"
        # )
        return possibleActions

    def isActionAllowed(self, action, possibleActions):
        """Given a player, the action and possible actions, verify if this action is allowed

        :param action: the action
        :type player: list

        :param possibleActions: the possible actions for this player
        :type player: (ndarray)

        :return: if the action is allowed or not - bool
        :rtype: bool
        """
        actionToTake = numpy.argmax(action)

        if (
            possibleActions[actionToTake] == 1
        ):  # if this specific action is part of the game
            return True
        else:
            return False

    def discardCards(self, player, action):
        """Discard a set of cards from a player's hand

        :param player: the player index
        :type player: int

        :param action: the action
        :type player: list

        :return: the discarded cards - list
        :rtype: list
        """
        cardsToDiscard = []
        actionIndex = numpy.argmax(action)
        takenAction = self.highLevelActions[actionIndex].split(";")
        cardValue = int(takenAction[0][1:])
        cardQuantity = int(takenAction[1][1:])
        jokerQuantity = int(takenAction[2][1:])

        for q in range(cardQuantity):
            cardsToDiscard.append(cardValue)
        for j in range(jokerQuantity):
            cardsToDiscard.append(12)

        self.restartBoard()

        originalCardDiscarded = cardsToDiscard.copy()
        # remove them from the players hand and add them to the board
        boardPosition = 0
        for cardIndex in range(len(self.players[player].cards)):
            for i in cardsToDiscard:
                if self.players[player].cards[cardIndex] == i:
                    self.players[player].cards[cardIndex] = 0

                    cardsToDiscard.remove(i)
                    self.board[boardPosition] = i
                    boardPosition = boardPosition + 1

        self.players[player].cards = sorted(self.players[player].cards)
        return originalCardDiscarded

    def list_players_with_special_actions(self):
        """list players that are allowed to do a special actions

        Returns:
            _type_: list()
        """
        players_special_action = []
        for count, player in enumerate(self.players):
            if (
                self.maxCardNumber + 1 in player.cards
            ):  # Check if this specific player has jokers in his hand
                unique, counts = numpy.unique(player.cards, return_counts=True)
                currentPlayerHand = dict(zip(unique, counts))

                jokerQuantity = currentPlayerHand[self.maxCardNumber + 1]

                # If the player has 2 jokers, check which position it has finished
                if jokerQuantity == 2:
                    current_role = player.current_role

                    if current_role == ROLES[0]:  # If it is the dishwasher
                        specialAction = "Dinner served!"
                    else:
                        specialAction = "It is food fight!"

                    # Return the player and the type of special action they can do
                    players_special_action.append([count, specialAction])

        # for i in range(len(self.playersHand)):
        #     if (
        #         self.maxCardNumber + 1 in self.playersHand[i]
        #     ):  # Check if this specific player has jokers in his hand
        #         unique, counts = numpy.unique(self.playersHand[i], return_counts=True)
        #         currentPlayerHand = dict(zip(unique, counts))

        #         jokerQuantity = currentPlayerHand[self.maxCardNumber + 1]
        #         # If the player has 2 jokers, check which position it has finished
        #         if jokerQuantity == 2:
        #             playerIndex = self.finishingOrder.index(i)

        #             if playerIndex < 3:
        #                 specialAction = "Dinner served!"
        #             else:
        #                 specialAction = "It is food fight!"

        #             # Return the player and the type of special action they can do
        #             players_special_action.append([i, specialAction])

        return players_special_action

    def declareSpecialAction(self):
        """Declare a special action (food fight/dinner is served)

        :return: if it is a special action
        :rtype: bool

        :return: if it is a food fight
        :rtype: bool
        """

        specialAction = ""
        for i in range(len(self.playersHand)):
            if self.maxCardNumber + 1 in self.playersHand[i]:
                # jokers =  self.playersHand[score[3]])
                unique, counts = numpy.unique(self.playersHand[i], return_counts=True)
                currentPlayerHand = dict(zip(unique, counts))

                jokerQuantity = currentPlayerHand[self.maxCardNumber + 1]
                if jokerQuantity == 2:
                    playerIndex = self.finishingOrder.index(i)

                    if playerIndex < 3:
                        specialAction = "Dinner served!"
                        self.currentSpecialAction = "DinnerServed"
                        self.currentPlayerDeclaredSpecialAction = i
                        return True, False
                    else:
                        specialAction = "It is food fight!"
                        self.currentSpecialAction = "FoodFight"
                        self.currentPlayerDeclaredSpecialAction = i

                        newcurrentRoles = []
                        newcurrentRoles.append(self.currentRoles[3])  # Chef
                        newcurrentRoles.append(self.currentRoles[2])  # sous-Chef
                        newcurrentRoles.append(self.currentRoles[1])  # waiter
                        newcurrentRoles.append(self.currentRoles[0])  # dishwasher
                        self.currentRoles = []
                        self.currentRoles = newcurrentRoles

                        self.exchangedCards = [i, specialAction, 0, 0]
                        return True, True

        self.currentSpecialAction = ""
        self.currentPlayerDeclaredSpecialAction = ""
        return (False, False)

    def changeRoles(self):
        """Change the player's roles, following a new game start"""

        score = self.currentRoles
        dishwasherCards = sorted(self.playersHand[score[3]])[
            0:2
        ]  # get the minimum dishwasher cards
        waiterCard = sorted(self.playersHand[score[2]])[0]  # get the minimum waiterCard
        souschefCard = sorted(self.playersHand[score[1]])[-1]
        chefCards = sorted(self.playersHand[score[0]])[-3:-1]

        # update the dishwasher cards
        for i in range(len(dishwasherCards)):
            cardIndex = self.playersHand[score[3]].index((dishwasherCards[i]))
            self.playersHand[score[3]][cardIndex] = chefCards[i]

        # update the chef cards
        for i in range(len(chefCards)):
            cardIndex = self.playersHand[score[0]].index((chefCards[i]))
            self.playersHand[score[0]][cardIndex] = dishwasherCards[i]

        # update the waiter cards
        cardIndex = self.playersHand[score[2]].index((waiterCard))
        self.playersHand[score[2]][cardIndex] = souschefCard

        # update the souschef cards
        cardIndex = self.playersHand[score[1]].index((souschefCard))
        self.playersHand[score[1]][cardIndex] = waiterCard

        self.exchangedCards = dishwasherCards, waiterCard, souschefCard, chefCards

        self.logNewRoles()

    def dealCards(self):
        """Deal the cards at the begining of a match"""
        # self.numberOfCardsPerPlayer = int(len(self.cards) / len(self.playersHand))

        for count, player in enumerate(self.players):
            player.cards = sorted(
                self.cards[
                    count
                    * self.numberOfCardsPerPlayer : count
                    * self.numberOfCardsPerPlayer
                    + self.numberOfCardsPerPlayer
                ]
            )

        # For each player, distribute the amount of cards
        # for playerNumber in range(len(self.playersHand)):
        #     self.playersHand[playerNumber] = sorted(
        #         self.cards[
        #             playerNumber
        #             * self.numberOfCardsPerPlayer : playerNumber
        #             * self.numberOfCardsPerPlayer
        #             + self.numberOfCardsPerPlayer
        #         ]
        #     )

        # match_number: int = 0,
        # round_number: int = 0,
        # agent_names: list = np.nan,
        # source: str = "SYSTEM",
        # action_type: str = np.nan,
        # action_description: str = np.nan,
        # player_hands: list = np.nan,
        # board_before: list = np.nan,
        # board_after: list = np.nan,
        # possible_actions: list = np.nan,
        # current_roles: list = np.nan,
        # match_score: list = np.nan,
        # game_score: list = np.nan,
        # game_performance_score: list = np.nan,

        self.experimentManager.dataSetManager.dealAction(
            match_number=self.matches,
            player_hands=[players.cards for players in self.players],
        )

    def restartBoard(self):
        """restart the board"""
        # clean the board
        self.board = []
        for i in range(self.maxCardNumber):
            self.board.append(0)

        # start the game with the highest card
        self.board[0] = self.maxCardNumber + 2
        # input ("Board:" + str(self.board))

    def hasPlayerFinished(self, player):
        """Identify it this specific player has finished the match

        :param player: the player index
        :type player: int


        :return: if the player has finished the match
        :rtype: bool
        """

        return numpy.array(self.players[player].cards).sum() <= 0
