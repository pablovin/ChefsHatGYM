import gym
import random
import numpy
from ChefsHatGym.KEF import DataSetManager
from ChefsHatGym.KEF import ExperimentManager
import copy
from gym import spaces

GAMETYPE = {"POINTS": "POINTS",
            "MATCHES": "MATCHES"}


class ChefsHatEnv(gym.Env):
    """ChefsHatEnv is the Chefs Hat game enviromnet class that allows to start and execute each step of the game.
    To instatiate the class, use gym.make('chefshat-v0').
    """
    
    gameFinished = False #: Whether the game has been finished (True) or not (False).
    metadata = {'render.modes': ['human']}


    def __init__(self):
        """Constructor method. Use gym.make instead of it.
        """
        pass


    def startExperiment(self, rewardFunctions=[], gameType=GAMETYPE["POINTS"], stopCriteria=3, maxInvalidActions=10, playerNames=[], logDirectory="", verbose=0, saveLog=False, saveDataset=False):
        """This method stores parameters for a new exeperiment. An experiment is a set of games (see startNewGame method).

        :param rewardFunctions: A list of reward functions for each player, defaults to []
        :type rewardFunctions: list, mandatory
        :param gameType: The game type ("POINTS" or "MATCHES"), defaults to GAMETYPE["POINTS"]
        :type gameType: str, optional
        :param stopCriteria: Number of "MATCHES" or "POINTS" to stop the experiment, defaults to 3
        :type stopCriteria: int, optional
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
        self.rewardFunctions = rewardFunctions
        self.gameType = gameType
        self.stopCriteria = stopCriteria
        self.playerNames = playerNames
        self.saveDataset = saveDataset

        self.episodeNumber = 0

        self.logDirectory = logDirectory
        self.verbose = verbose
        self.saveLog = saveLog
        self.maxInvalidActions = maxInvalidActions

        self.playersInvalidActions = [0, 0, 0, 0]
        self.playersPassAction = [0, 0, 0, 0]

        # if integratedState:
        self.action_space = spaces.Discrete(200)
        self.observation_space = spaces.Box(low=numpy.zeros(228), high=numpy.ones(228))

    def reset(self):
        """This method increments episodeNumber, start a new game and return the first observation
                
                :return: The first observation array after the game has started. The observation is an int data-type ndarray.
                :rtype: ndarray
        """

        self.episodeNumber += 1
        self.startNewGame()
        return self.getObservation()


    def startNewGame(self):
        """Starts a new game using the parameters defined by the method startExperiment.
            You have to define the game type (per points or per game), and the stoping criteria (maximum points, maximum games).
            For logging purpose, set the saveLog, verbose and logDirectory in startExperiment method.
        """

        if not self.logDirectory=="":
            experimentName = "E_"+str(self.episodeNumber)+"_P_" + str(self.playerNames) +  "_GT_" + str(self.gameType) + "_SC" + str(self.stopCriteria)
            self.experimentManager = ExperimentManager.ExperimentManager(self.logDirectory,
                                                                        experimentName,
                                                                        verbose=self.verbose, saveLog=self.saveLog)
            self.logger = self.experimentManager.logManager
            self.logger.newLogSession("Starting new Episode:" + str(self.episodeNumber))
            self.logger.write("Players :" + str(self.playerNames))
            self.logger.write("Stop Criteria :" + str(self.stopCriteria))
        else:
            self.logger = None
            self.experimentManager = None
            self.saveDataset = False

        self.score = [0,0,0,0]  # the score
        self.performanceScore = [0,0,0,0]  # the performance score

        self.board = []  # the current board

        self.maxCardNumber = 11  # The highest value of a card in the deck

        self.numberPlayers = 4  # number of players playing the game

        self.numberOfCardsPerPlayer = 0  # number of cards each player has at hand in the begining of the game

        self.highLevelActions = self.getHighLevelActions()

        self.matches = 0

        self.gameFinished = False

        self.finishingOrder =  [] #Which payers already finished this match

        # Variables per Match
        self.cards = []  # the deck

        self.playersHand = []  # the current cards each player has at hand

        self.currentPlayer = 0 #The current player playing the game

        self.playerStartedGame = 0  # who started the game

        self.currentRoles = [] # Current roles of each player

        self.currentSpecialAction = []

        self.currentPlayerDeclaredSpecialAction = []

        self.rounds = 0

        self.lastToDiscard = 0

        if self.saveDataset:
            self.experimentManager.dataSetManager.startNewGame()



        self.startNewmatch()  # Initiate all the match parameters


    def startNewmatch(self):
        """Start a new match
        """
        # Create a deck
        self.cards = []
        for i in range(self.maxCardNumber + 1):
            for a in range(i):
                self.cards.append(self.maxCardNumber - a)

        # add joker cards
        self.cards.append(self.maxCardNumber+1) # add a joker card
        self.cards.append(self.maxCardNumber + 1) # add a joker card

        # if the score exists, update roles
        if numpy.max(self.score) > 0:
            self.currentRoles = []
            self.currentRoles.append(self.finishingOrder[0]) # Chef
            self.currentRoles.append(self.finishingOrder[1])  # sous-Chef
            self.currentRoles.append(self.finishingOrder[2])  # waiter
            self.currentRoles.append(self.finishingOrder[3])  # dishwasher

        self.lastActionPlayers = ["", "", "", ""]

        # shuffle the decks
        random.shuffle(self.cards)

        # create players hand
        self.playersHand = []
        for i in range(self.numberPlayers):
            self.playersHand.append([])

        self.numberOfCardsPerPlayer = int(len(self.cards) / len(self.playersHand))

        # initialize the board
        self.restartBoard()

        # Update the Match number

        self.matches = self.matches + 1

        # deal the cards
        self.dealCards()

        if self.saveDataset:
            self.experimentManager.dataSetManager.startNewMatch(self.matches, str(self.playerNames))

        if not self.experimentManager == None:
            self.logger.newLogSession("Match Number %f Starts!" % self.matches)
            self.logger.write("Deck: " + str(self.cards))
            for i in range(len(self.playerNames)):
                self.logger.write("Player " + str(i) + ":" + str(self.playersHand[i]))

        # If this is not the first game, then change the roles
        self.currentSpecialAction = ""
        self.currentPlayerDeclaredSpecialAction = ""
        if self.matches >= 2:
            specialAction, foodFight = self.declareSpecialAction()

            dishwasherCards, waiterCard, souschefCard, chefCards = [], [], [], []
            if not foodFight or not specialAction:
                self.changeRoles()

                if not self.experimentManager == None:
                    self.logger.newLogSession("Changind roles!")
                    self.logger.write("- Waiter: Player " + str(self.currentRoles[3] + 1))
                    self.logger.write("- Dishwasher Player:" + str(self.currentRoles[2] + 1))
                    self.logger.write("- Souschef Player:" + str(self.currentRoles[1] + 1))
                    self.logger.write("- Chef Player:" + str(self.currentRoles[0] + 1))

            else:

                if not self.experimentManager == None:
                    self.logger.write("- Player :" + str(self.currentPlayerDeclaredSpecialAction) + " declared " + str(
                        self.currentSpecialAction) + "!")

                    if self.currentSpecialAction == "" or self.currentSpecialAction == "FoodFight" :
                        dishwasherCards, waiterCard, souschefCard, chefCards = self.exchangedCards
                        self.logger.newLogSession("Changing cards!")
                        self.logger.write("--- Dishwasher gave:" + str(dishwasherCards))
                        self.logger.write("--- Waiter gave:" + str(waiterCard))
                        self.logger.write("--- Souschef gave:" + str(souschefCard))
                        self.logger.write("--- Chef gave:" + str(chefCards))

            if self.saveDataset:
                self.experimentManager.dataSetManager.exchangeRolesAction(self.playersHand, self.currentRoles, (self.currentSpecialAction, self.currentPlayerDeclaredSpecialAction, dishwasherCards, waiterCard, souschefCard, chefCards), self.matches)

        # Establishes who starts the game randomly
        playerTurn = numpy.array(range(self.numberPlayers))
        random.shuffle(playerTurn)

        index = numpy.array(range(self.numberPlayers))
        random.shuffle(index)

        self.currentPlayer = playerTurn[index[0]]

        # verify if this player has a 11 in its hand, otherwise iterate to the next player

        while not (self.maxCardNumber in self.playersHand[self.currentPlayer]):
            self.currentPlayer = self.currentPlayer + 1
            if self.currentPlayer >= self.numberPlayers:
                self.currentPlayer = 0

        # save the player who started the game
        self.playerStartedGame = self.currentPlayer

        self.finishingOrder = [] #Reset the players that finished this match

        # Current round of the game set to 0
        self.rounds = 1

        if not self.experimentManager == None:
            self.logger.newLogSession("Round:" + str(self.rounds))


    def getObservation(self):
        """Get a new observation. The observation is composed of the current board, the playersHand and the possible actions.
            
            :return: The observation is an int data-type ndarray.
                        The observation array has information about the board game, the current player's hand, and current player possible actions.
                        This array must have the shape of (228, ) as follows:
                        The first 11 elements represent the board game card placeholder (the pizza area).
                        The game cards are represented by an integer, where 0 (zero) means no card.
                        The following 17 elements (from index 11 to 27) represent the current player hand cards in the sequence.
                        By the end, the last 200 elements (from index 28 to 227) represent all possible actions in the game.
                        The allowed actions for the current player are filled with one, while invalid actions are filled with 0.
            :rtype: ndarray
        """
        board = numpy.array(self.board) / (self.maxCardNumber + 2)
        playersHand = numpy.array(self.playersHand[self.currentPlayer]) / (self.maxCardNumber + 2)
        possibleActions = self.getPossibleActions(self.currentPlayer)

        return numpy.concatenate((board,playersHand, possibleActions))


    def isGameOver(self):
        """isGameOver
            :return: Boolean flag if the game is over.
            :rtype: bool
        """
        gameFinished = False

        # input("here")
        # Verify if the game is over
        if self.gameType  == GAMETYPE["POINTS"]:
            if self.score[numpy.argmax(self.score)] >= self.stopCriteria:
                gameFinished = True
        elif self.gameType == GAMETYPE["MATCHES"]:
            if self.matches >= self.stopCriteria:
                gameFinished = True


        if self.experimentManager == None:
                self.logger.newLogSession("Game Over! Final Score:" + str(self.score) + " - Final Performance Score:" + str(self.performanceScore))

        return gameFinished

    def nextPlayer(self):
        """nextPlayer
            advance to the next player
        """
        self.currentPlayer = self.currentPlayer + 1
        if self.currentPlayer == self.numberPlayers:
            self.currentPlayer = 0

        for i in range(len(self.lastActionPlayers)):
            if ((not self.lastActionPlayers[self.currentPlayer] == "") and self.lastActionPlayers[self.currentPlayer][0] == DataSetManager.actionPass) or ((not self.lastActionPlayers[self.currentPlayer] == "") and self.lastActionPlayers[self.currentPlayer][0] == DataSetManager.actionFinish):
                self.currentPlayer = self.currentPlayer + 1
                if self.currentPlayer == self.numberPlayers:
                    self.currentPlayer = 0


    def calculateScore(self, playerPosition):
        """calculateScore
            :param playerPosition: The finishing position of the player
            :type playerPosition: int, mandatory
            :return: Integer the score of the given player.
            :rtype: int
        """
        return 3 - playerPosition

    def getRandomAction(self, possibleActions):
        """getRandomAction
                Return a random allowed action.

            :param possibleActions: The list of possible actions
            :type possibleActions: list, mandatory
            :return: List the random action.
            :rtype: list
        """
        itemindex = numpy.array(numpy.where(numpy.array(possibleActions) == 1))[0].tolist()

        random.shuffle(itemindex)
        aIndex = itemindex[0]
        a = numpy.zeros(200)
        a[aIndex] = 1

        return a

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
                'possibleActions': (list),
                'action': (ndarray),
                'thisPlayerPosition': (int),
                'thisPlayerPosition': (ndarray),
                'players': (list),
                }

        :rtype: tuple
        """

        validAction = False
        isMatchOver = False
        isPizzaReady = False
        thisPlayerPosition = -1
        actionIsRandom = False

        possibleActions = self.getPossibleActions(self.currentPlayer)
        thisPlayer = copy.copy(self.currentPlayer)
        boardBefore = copy.copy(self.board)

        observationBefore = copy.copy(self.getObservation())

        stateBefore = copy.copy(self.getObservation())

        if self.playersInvalidActions[thisPlayer] >= self.maxInvalidActions or self.playersPassAction[thisPlayer] >= self.maxInvalidActions:

            action = self.getRandomAction(possibleActions)
            actionIsRandom = True

        if self.isActionAllowed(thisPlayer, action, possibleActions):  # if the player can make the action, do it.

            validAction = True

            self.playersInvalidActions[thisPlayer] = 0

            if numpy.argmax(action) == len(possibleActions) - 1: # Pass action
                actionComplete = (DataSetManager.actionPass, [0])
                self.playersPassAction[thisPlayer] +=1

            else: # Discard action
                self.playersPassAction[thisPlayer] = 0
                cardsDiscarded = self.discardCards(self.currentPlayer, action)
                actionComplete = (DataSetManager.actionDiscard, cardsDiscarded)
                self.lastToDiscard = self.currentPlayer

            # Verify if the player has finished this match
            if self.hasPlayerFinished(self.currentPlayer):
                if not self.currentPlayer in self.finishingOrder:
                    self.finishingOrder.append(self.currentPlayer)
                    actionComplete = (DataSetManager.actionFinish, cardsDiscarded)

                    # Calculate and update the player score
                    playerFinishingPosition = self.finishingOrder.index(self.currentPlayer)
                    points = self.calculateScore(playerFinishingPosition)


                    self.score[self.currentPlayer] += points


                    pScore =  (points*10) / self.rounds
                    # self.performanceScore[self.currentPlayer] += pScore
                    self.performanceScore[self.currentPlayer] = (self.performanceScore[self.currentPlayer] * (self.matches-1) + pScore)/ self.matches
                    thisPlayerPosition = playerFinishingPosition

            # Update the player last action
            self.lastActionPlayers[self.currentPlayer] = actionComplete


            if not self.experimentManager == None:
                self.logger.write(" -- Player " +str(thisPlayer)+" - "+ str(self.playerNames[self.currentPlayer]))
                self.logger.write(" --- Player Hand: " + str(self.playersHand[self.currentPlayer]))
                self.logger.write(" --- Board Before: " + str(boardBefore))
                self.logger.write(" --- Action: " + str(actionComplete))
                self.logger.write(" --- Board After: " + str(self.board))

            if self.saveDataset:
                self.experimentManager.dataSetManager.doActionAction(self.matches, thisPlayer, self.rounds,
                                                                    actionComplete, self.board,
                                                                    0, 0,
                                                                    self.playersHand, self.currentRoles,
                                                                    self.score, self.lastActionPlayers,
                                                                    action, 0, 0, validAction)
            # Verify if it is end of match

            if self.makePizza():
                isPizzaReady = True
                self.currentPlayer = self.lastToDiscard
                if self.currentPlayer in self.finishingOrder:
                    self.nextPlayer()


            else:
                self.nextPlayer()

            if self.isMatchover():
                isMatchOver = True
                if self.isGameOver():
                    self.gameFinished = True
                else:
                    self.startNewmatch()

            if self.gameFinished:
                self.experimentManager.dataSetManager.saveFile()
        else:
            self.playersInvalidActions[thisPlayer]+=1
            isMatchOver = False

        info = {}
        info["actionIsRandom"] = actionIsRandom
        info["validAction"] = validAction
        info["matches"] = self.matches
        info["rounds"] = self.rounds
        info["score"] = self.score
        info["performanceScore"] = self.performanceScore
        info["thisPlayer"] = thisPlayer
        info["thisPlayerFinished"] = thisPlayer in self.finishingOrder
        info["isPizzaReady"] = isPizzaReady

        info["boardBefore"] = observationBefore[0:11]
        info["boardAfter"] = self.getObservation()[0:11]
        info["possibleActions"] = possibleActions
        info["action"] = action

        info["thisPlayerPosition"] = thisPlayerPosition

        info["lastActionPlayers"] = self.lastActionPlayers
        info["players"] = self.playerNames

        stateAfter = copy.copy(self.getObservation())
        reward = self.rewardFunctions[thisPlayer](info,stateBefore, stateAfter )

        return self.getObservation(), reward, isMatchOver, info
            # observation, reward, isMatchOver, {}



    def render(self, mode='human', close=False):
        pass

    def close(self):
        pass

    def makePizza(self):
        """Make a pizza. Update the game to the next round and collect all cards from the board

        :return: pizzaReady - bool
        :rtype: bool
        """
        playersInGame = []
        for i in range(len(self.lastActionPlayers)):
            if not (i in self.finishingOrder):
                playersInGame.append(i)

        # print ("self.lastActionPlayers:" + str(self.lastActionPlayers))
        # print ("FInishing Order:" + str(self.finishingOrder))
        numberFinished = 0
        numberOfActions = 0

        for i in playersInGame:
            if (not self.lastActionPlayers[i] == "") and (self.lastActionPlayers[i][0] == DataSetManager.actionPass):
                numberFinished += 1

            if (not self.lastActionPlayers[i] == ""):
                numberOfActions+=1


        # print ("Players in game:" + str(playersInGame))
        # print ("Number of Actions:" + str(numberOfActions))
        # print("Number Finished:" + str(numberFinished))

        pizzaReady = False
        if ((numberFinished >= len(playersInGame) -1 ) and (numberOfActions == len(playersInGame)   )):
            self.restartBoard()
            pizzaReady = True

            if not self.experimentManager == None:
                self.logger.newLogSession("Pizza ready!!!")

            if self.saveDataset:
                #     # print ("Pizza!")
                self.experimentManager.dataSetManager.doActionPizzaReady(self.rounds,
                                                                    self.board, self.playersHand, self.currentRoles,
                                                                    self.score, self.lastActionPlayers, self.matches)

            self.nextRound()

        return pizzaReady

    def nextRound(self):
        """move the game to the next round


        """
        self.rounds = self.rounds+1

        newLastActionPlayers = ["", "", "", ""]
        for actionIndex, action in enumerate(self.lastActionPlayers):
            if (not action =="") and action[0] == DataSetManager.actionFinish:
                newLastActionPlayers[actionIndex] =action

        # print ("Previous actions:" + str(self.lastActionPlayers))
        # print ("Next actions:" + str(newLastActionPlayers))
        self.lastActionPlayers = newLastActionPlayers

        if not self.experimentManager == None:
            self.logger.newLogSession("Round:" + str(self.rounds))


    def isMatchover(self):
        """Verify if this match is over

        :return: isMatchOver - bool
            :rtype: bool
        """
        isMatchOver = True
        for i in range(len(self.playersHand)):
            if numpy.array(self.playersHand[i]).sum() > 0:
                isMatchOver = False
                break


        if isMatchOver:
            if not self.experimentManager == None:
                self.logger.newLogSession("Match "+str(self.matches) +" over! Current Score:"+str(self.score))

        return isMatchOver


    def getHighLevelActions(self):
        """Generate all the possible actions in a human-friendly way

        :return: highLevelActions - List
            :rtype: list
        """
        highLevelActions = []

        for cardNumber in range(self.maxCardNumber):
            for cardQuantity in range(cardNumber + 1):
                highLevelActions.append("C" + str(cardNumber + 1) + ";Q" + str(cardQuantity + 1) + ";J0")
                highLevelActions.append("C" + str(cardNumber + 1) + ";Q" + str(cardQuantity + 1) + ";J1")
                highLevelActions.append("C" + str(cardNumber + 1) + ";Q" + str(cardQuantity + 1) + ";J2")

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
        if self.playerStartedGame == self.currentPlayer and self.rounds == 1:
            firstAction = True

        else:
            firstAction = False

        # print ("Player:", player)
        possibleActions = []

        unique, counts = numpy.unique(self.board, return_counts=True)
        currentBoard = dict(zip(unique, counts))

        unique, counts = numpy.unique(self.playersHand[player], return_counts=True)
        currentPlayerHand = dict(zip(unique, counts))

        highestCardOnBoard = 0
        for boardItem in currentBoard:
            if not boardItem == self.maxCardNumber+1:
                highestCardOnBoard = boardItem

        jokerQuantityBoard = 0

        if self.maxCardNumber + 1 in self.board:
            jokerQuantityBoard = currentBoard[self.maxCardNumber + 1]


        if self.maxCardNumber + 1 in currentPlayerHand.keys():
            jokerQuantity = currentPlayerHand[self.maxCardNumber + 1]
        else:
            jokerQuantity = 0

        cardDescription = ""
        for cardNumber in range (self.maxCardNumber):
            for cardQuantity in range(cardNumber+1):

                isThisCombinationAllowed = 0
                isthisCombinationOneJokerAllowed = 0
                isthisCombinationtwoJokersAllowed = 0

                # print("Card:" + str(cardNumber + 1) + " Quantity:" + str(cardQuantity + 1))

                """If this card number is in my hands and the amount of cards in my hands is this amount"""
                if (cardNumber + 1) in self.playersHand[player] and currentPlayerHand[cardNumber + 1] >= cardQuantity + 1:
                    # print("-- this combination exists in my hand!")

                    """Check combination without the joker"""
                    """Check if this combination of card and quantity can be discarded given teh cards on the board"""
                    """Check if this cardnumber is smaller than the cards on the board"""
                    """ and check if the cardquantity is equal of higher than the number of cards on the board (represented by the highest card on the board ) + number of jokers on the board"""
                    if (cardNumber + 1 < highestCardOnBoard) and (
                            cardQuantity + 1 >= currentBoard[highestCardOnBoard] + jokerQuantityBoard):

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
                                (cardQuantity + 1 + 1) >= currentBoard[highestCardOnBoard] + jokerQuantityBoard):
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
                                    (cardQuantity + 1 + 2) >= currentBoard[highestCardOnBoard] + jokerQuantityBoard):
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

        if self.maxCardNumber+1 in self.playersHand[player]: # there is a joker in the hand
            if not firstAction:
                if highestCardOnBoard == self.maxCardNumber+2:
                    canDiscardOnlyJoker = 1

        possibleActions.append(canDiscardOnlyJoker)

        possibleActions.append(1) #the pass action, which is always a valid action

        return possibleActions

    def isActionAllowed(self, player, action, possibleActions):
        """Given a player, the action and possible actions, verify if this action is allowed

            :param player: the player index
            :type player: int

            :param action: the action
            :type player: list

            :param possibleActions: the possible actions for this player
            :type player: (ndarray)

            :return: if the action is allowed or not - bool
            :rtype: bool
        """
        actionToTake = numpy.argmax(action)

        if possibleActions[actionToTake] == 1: # if this specific action is part of the game
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
        for cardIndex in range(len(self.playersHand[player])):
            for i in cardsToDiscard:

                if self.playersHand[player][cardIndex] == i:


                    self.playersHand[player][cardIndex] = 0

                    cardsToDiscard.remove(i)
                    self.board[boardPosition] = i
                    boardPosition = boardPosition + 1


        self.playersHand[player] = sorted(self.playersHand[player])
        return originalCardDiscarded


    def declareSpecialAction(self):
        """Declare a special action (food fight/dinner is served)


            :return: if it is a special action
            :rtype: bool

            :return: if it is a food fight
            :rtype: bool
        """

        specialAction =""
        for i in range(len(self.playersHand)):
            if self.maxCardNumber + 1 in self.playersHand[i]:
                # jokers =  self.playersHand[score[3]])
                unique, counts = numpy.unique(self.playersHand[i], return_counts=True)
                currentPlayerHand = dict(zip(unique, counts))

                jokerQuantity = currentPlayerHand[self.maxCardNumber + 1]
                if jokerQuantity ==2:
                    playerIndex = self.finishingOrder.index(i)

                    if playerIndex < 3 :
                        specialAction = "Dinner served!"
                        self.currentSpecialAction = "DinnerServed"
                        self.currentPlayerDeclaredSpecialAction = i
                        return True, False
                    else:
                        specialAction = "It is food fight!"
                        self.currentSpecialAction = "FoodFight"
                        self.currentPlayerDeclaredSpecialAction = i

                        newcurrentRoles = []
                        newcurrentRoles.append(self.currentRoles[3]) # Chef
                        newcurrentRoles.append(self.currentRoles[2]) # sous-Chef
                        newcurrentRoles.append(self.currentRoles[1]) # waiter
                        newcurrentRoles.append(self.currentRoles[0]) # dishwasher
                        self.currentRoles = []
                        self.currentRoles = newcurrentRoles

                        self.exchangedCards = [i, specialAction, 0, 0]
                        return True, True

        self.currentSpecialAction = ""
        self.currentPlayerDeclaredSpecialAction = ""
        return (False, False)


    def changeRoles(self):
        """Change the player's roles, following a new game start

        """

        score = self.currentRoles

        dishwasherCards = sorted(self.playersHand[score[3]])[0:2]  # get the minimum dishwasher cards

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


    def dealCards(self):
        """Deal the cards at the begining of a match

        """

        self.numberOfCardsPerPlayer = int(len(self.cards) / len(self.playersHand))

        # For each player, distribute the amount of cards
        for playerNumber in range(len(self.playersHand)):
            self.playersHand[playerNumber] = sorted(self.cards[
                                                    playerNumber * self.numberOfCardsPerPlayer:playerNumber * self.numberOfCardsPerPlayer + self.numberOfCardsPerPlayer])

        if self.saveDataset:
            self.experimentManager.dataSetManager.dealAction(self.playersHand, self.matches)

    def restartBoard(self):
        """restart the board
        """
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
        if numpy.array(self.playersHand[player]).sum() > 0:
            return False
        else:
            return True
