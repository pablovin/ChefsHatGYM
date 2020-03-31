import gym
import random
import numpy
from KEF import DataSetManager

class ChefsHatEnv(gym.Env):
  metadata = {'render.modes': ['human']}


  rewardFunction = ""

  def __init__(self):
    pass


  def nextPlayer(self):

      # check if the game is over, and if not move to the next round
      gameFinished = self.hasGameFinished()

      if not gameFinished:
          # move to the next round
          # self.rounds = self.rounds +1

          # self.allWrongActions[self.currentPlayer].append(self.currentWrongActions)
          # self.currentWrongActions = 0


          # if len(self.currentActionRewards) > 0:
          #     avgActionReward = numpy.average(self.currentActionRewards)
          #     self.allRewards[self.currentPlayer].append(avgActionReward)

          self.currentActionRewards = []

          self.currentPlayer = self.currentPlayer + 1

          if self.currentPlayer == self.numberPlayers:
              self.currentPlayer = 0


  def step(self, action):

    # player = player -1
    validAction = True
    actionTaken = ""
    reward = 0

    actionTag = ""
    actionComplete = ""

    possibleActions = self.getPossibleActions(self.currentPlayer)


    if self.isActionAllowed(self.currentPlayer, action):  # if the player can make the action, do it.
        # reward = 1.0  # Experiment 1
        validAction = True

        if numpy.argmax(action) == len(possibleActions) - 1:

            #if only the pass action is available
            if numpy.sum(possibleActions) == 1:
                reward = self.rewardFunction.getRewardOnlyPass()
            else: # you took the pass action even tho there were other actions available
                # reward = 0
                reward = self.rewardFunction.getRewardPass()
                # validAction = False

            actionTaken = DataSetManager.actionPass
            actionTag = DataSetManager.actionPass
            actionComplete = (DataSetManager.actionPass, [0])
            # reward = -0.1  # Experiment 2
        else:
            # reward = 1  # Experiment 1
            #reward = 0.1 # Experiment 2

            cardsDiscarded = self.discardCards(self.currentPlayer, action)

            unique, counts = numpy.unique(self.playersHand[self.currentPlayer], return_counts=True)
            currentPlayerHand = dict(zip(unique, counts))
            if 0 in self.playersHand[self.currentPlayer]:
                cardsInHand = len(self.playersHand[self.currentPlayer]) - currentPlayerHand[0]
            else:
                cardsInHand = len(self.playersHand[self.currentPlayer])


            # reward = (1 - cardsInHand*100 / len(self.playersHand[self.currentPlayer]) * 0.01) *0.7 #experiment 2
            # reward = -0.01  # experiment 3
            reward = self.rewardFunction.getRewardDiscard((cardsInHand, len(self.playersHand[self.currentPlayer])))


            actionTaken = DataSetManager.actionDiscard, cardsDiscarded
            actionTag = DataSetManager.actionDiscard
            actionComplete = (DataSetManager.actionDiscard, cardsDiscarded)

            # if len(cardsDiscarded) == 0:
            #     print ("here")

            self.lastToPass = self.currentPlayer   # if player did not pass nor finish, he was the last one to play

        # print("-- Action: Discard - ", cardsDiscarded)
    else:  # if the player cannot make the action, penalize it and repeat it until it can do it
        # reward = 0
        reward = self.rewardFunction.getRewardInvalidAction()  # experiment 3
        validAction = False
        actionTaken = "Invalid"
        self.currentWrongActions[self.currentPlayer] += 1
        # self.currentWrongActions += 1

    if self.hasPlayerFinished(self.currentPlayer): # If all the cards of the player hands are gone, he wins the round, maximum reward
        # if actionTaken == "Pass" and numpy.array(self.playersHand[
        #                                              self.currentPlayer]).sum() == 0:
            # print ("Finished:", player)
            # print("Score:", self.score)
            if not self.currentPlayer in self.score:
                self.score.append(self.currentPlayer)

            index = self.score.index(self.currentPlayer)
            reward = self.rewardFunction.getRewardFinish((index,self.rounds))
            # if index == 0:
            #     reward = 1 # experiment 3
            # else:
            #     # reward += 0
            #     reward = -0.01  # experiment 3
            # reward += 0  # Experiment 1
            # reward +=  (0.9 - index * 0.3) * 0.3 #Experiment 2
            # reward = 1
            # reward = -0.01  # experiment 3
            actionTaken = DataSetManager.actionFinish
            actionTag = DataSetManager.actionFinish
            # actionComplete = (DataSetManager.actionFinish, [0])
            # print ("Score", self.score)
            # input("here")

    #Update the player last action
    self.lastActionPlayers[self.currentPlayer] = actionTaken

    self.currentActionRewards.append(reward)


    self.currentGameRewards[self.currentPlayer].append(reward)


    if validAction:
        self.currentGameRewards[self.currentPlayer].append(reward)
        self.playerActionsTimeLine[self.currentPlayer].append(actionTag)
        self.playerActionsComplete[self.currentPlayer].append(actionComplete)


    # print ("Given reward:" + str(reward))
    return self.getCurrentPlayerState(), reward, validAction

      # reward, validAction, actionTaken, possibleActions



  def reset(self):
    # Create a deck
    self.cards = []
    for i in range(self.maxCardNumber + 1):
      for a in range(i):
        self.cards.append(self.maxCardNumber - a)

    #add joker dards
    self.cards.append(self.maxCardNumber+1) # add a joker card
    self.cards.append(self.maxCardNumber + 1) # add a joker card

    # if the score exists, update the winners and the all score and update the roles
    if len(self.score) > 1:
        self.currentRoles = []
        self.currentRoles.append(self.score[0]) # Chef
        self.currentRoles.append(self.score[1])  # sous-Chef
        self.currentRoles.append(self.score[2])  # waiter
        self.currentRoles.append(self.score[3])  # dishwasher

        self.allScores.append(self.score)
        self.winners.append(self.score[0])

        self.lastActionPlayers = []

        # update the game round and the reward counts and wrong actions count
        self.allRounds.append(self.rounds)

        for i in range(self.numberPlayers):
            self.allRewards[i].append(self.currentGameRewards[i])
            self.allWrongActions[i].append(self.currentWrongActions[i])
            self.playerActionsCompleteAllGames[i].append(self.playerActionsComplete[i])

        #update the startGame/win game values

        counter = 0
        for s in self.score:
            if self.playerStartedGame == s:
                self.startGameFinishingPosition[counter] +=1
            counter = counter+1


        # if self.playerStartedGame == self.score[0]:
        #     self.startGameWinGames += 1


    #reset current wrong actions and reward

    self.currentGameRewards = []
    self.currentWrongActions = []

    self.playerActionsTimeLine = []

    self.playerActionsComplete = []

    # set the score
    self.score = []

    # Current round of the game set to 0
    self.rounds = 0


    # shuffle the decks
    random.shuffle(self.cards)

    # create players hand and last actions and rewards

    self.playersHand = []
    for i in range(self.numberPlayers):
      self.playersHand.append([])
      self.lastActionPlayers.append("")
      self.currentGameRewards.append([])
      self.currentWrongActions.append(0)
      self.playerActionsTimeLine.append([])  # players actions timeline
      self.playerActionsComplete.append([]) # players actions complete


    self.numberOfCardsPerPlayer = int(len(self.cards) / len(self.playersHand))

    #number of actions

    # self.numberOfActions = (self.maxCardNumber*self.maxCardNumber*3)+2
    self.numberOfActions = 200
    # initialize the board
    self.restartBoard()

    # deal the cards
    self.dealCards()

    # If this is not the first game, then change the roles
    self.currentSpecialAction = ""
    self.currentPlayerDeclaredSpecialAction = ""
    if len(self.allScores) > 0:
        specialAction, foodFight = self.declareSpecialAction()
        if not foodFight or not specialAction:
            self.changeRoles(foodFight)



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



  def render(self, mode='human', close=False):
    print ("render")


  def isEndRound(self):

    pizzaReady = False
    allPLayerFinished = 0
    # print ("Number of Players:", self.numberPlayers)
    # print ("Number of Players:", self.numberPlayers)
    for i in range(self.numberPlayers):

      # print ("player "+str(i)+" action:" + str(self.lastActionPlayers[i]))
      if self.lastActionPlayers[i] == DataSetManager.actionPass:
        allPLayerFinished = allPLayerFinished + 0
      elif self.lastActionPlayers[i] == DataSetManager.actionFinish:
        allPLayerFinished = allPLayerFinished + 0
      else:
        allPLayerFinished = allPLayerFinished + 1

    if allPLayerFinished == 0:
      self.restartBoard()
      pizzaReady = True

      self.currentPlayer = self.lastToPass

    return pizzaReady

  def nextRound(self):
      self.rounds = self.rounds+1

  def hasGameFinished(self):

      for i in range(len(self.playersHand)):
          # print ("PLayer:" + str(i) + " : ", str(numpy.array(self.playersHand[i]).sum()))
          if numpy.array(self.playersHand[i]).sum() > 0:
              return False

      return True

  #the number of possible actions is: self.maxCardNumber * self.maxCardNumber * 3 + 2
  # where the *3 refers to the options: discard a card, card+1 joker, card + 2 jokers
  # the 2 refers to: discard only one joker, and pass action
  def getPossibleActions(self, player):

      if self.playerStartedGame == self.currentPlayer and self.rounds == 0:
          firstAction = True

      else:
          firstAction = False


      highLevelActions = []
      #print ("Player:", player)
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

      #
      # print("Possible actions:", possibleActions)

      cardDescription = ""
      for cardNumber in range (self.maxCardNumber):
          possibleAction = 0
          # print ("Card Number:", cardNumber+1)
          # # print("cardNumber:", cardNumber + 1)
          # #
          # print("- Player:", player)
          # print("- Hand:", currentPlayerHand)
          # print("- Current board:", currentBoard)
          # print("- Highest card on board:", highestCardOnBoard)
          # print("-Card lower than the ones in the board:", cardNumber + 1 < highestCardOnBoard)
          # print("-Card present in the player hand:", cardNumber + 1 in self.playersHand[player])

          # if this card is present in the hand and it is lower than the cards in the board
          for cardQuantity in range(cardNumber+1):


              # if cardQuantity == 0:
              #       print (len(possibleActions))
              if (cardNumber + 1 < highestCardOnBoard ) and cardNumber + 1 in self.playersHand[player]:

              #verify if the quantity of the card in the hand is allowed to be put down

                  # if the amount of cards in board and in the hand are the same or more than cardNumber quantity
                  # print("-- Card quantity:", cardQuantity+1)
                  # print("-- Amount of cards in hand:", currentPlayerHand[cardNumber + 1])
                  # print("-- Amount of cards in board:", currentBoard[highestCardOnBoard])
                  # print("-- Can I discard this qunatity:", currentPlayerHand[cardNumber + 1] >= cardQuantity+1)
                  # print("-- Is it the same or more than in the board:", currentBoard[
                  #     highestCardOnBoard] <= cardQuantity + 1)

                  if currentPlayerHand[cardNumber + 1] >= cardQuantity + 1 and (currentBoard[
                      highestCardOnBoard] + jokerQuantityBoard) <= cardQuantity + 1: # taking into consideration the amount of jokers in the board

                      if firstAction:  # if this is the first move
                         # print("--- First Action:")

                         if cardNumber+1 ==self.maxCardNumber: # if this is the highest card
                             # print("----- First Action Added!")
                             possibleActions.append(1)
                         else:
                             possibleActions.append(0)
                             # highLevelActions.append("C" + str(cardNumber + 1) + ";Q" + str(cardQuantity + 1) + ";J0")
                      else:
                          # print("----- Added here!")
                          possibleActions.append(1)
                          # highLevelActions.append("C" + str(cardNumber+1) + ";Q" + str(cardQuantity+1) + ";J0")
                  else:

                          possibleActions.append(0)
                          # highLevelActions.append("C" + str(cardNumber+1) + ";Q" + str(cardQuantity+1) + ";J0")

              else:
                  possibleActions.append(0)
                  # highLevelActions.append("C" + str(cardNumber+1) + ";Q" + str(cardQuantity+1) + ";J0")

              highLevelActions.append("C" + str(cardNumber + 1) + ";Q" + str(cardQuantity + 1) + ";J0")
              highLevelActions.append("C" + str(cardNumber + 1) + ";Q" + str(cardQuantity + 1) + ";J1")
              highLevelActions.append("C" + str(cardNumber + 1) + ";Q" + str(cardQuantity + 1) + ";J2")
              # if cardNumber



              # add the joker possibilities
              if self.maxCardNumber + 1 in self.playersHand[player]:  # there is a joker in the hand
                  jokerQuantity = currentPlayerHand[self.maxCardNumber + 1]

                  if (cardNumber + 1 < highestCardOnBoard) and cardNumber + 1 in self.playersHand[player]: # if I have the card in hand and it is lower than the one in the field

                     # for one joker
                     if currentPlayerHand[cardNumber + 1] >= cardQuantity and (currentBoard[
                      highestCardOnBoard] + jokerQuantityBoard) <= cardQuantity + 1: # verify if the amount of cards in the hand + a joker is more than the card quantity and if the cards in the board + possible jokers is more than the card quantity
                         if firstAction:  # if this is the first move
                             if cardNumber + 1 == self.maxCardNumber:  # if this is the highest card
                                 possibleActions.append(1) # I can discard one joker

                             else:
                                 possibleActions.append(0)  # I cannot discard one joker


                         else:
                             possibleActions.append(1) # I can discard one joker

                     else:
                         possibleActions.append(0) # I cannot discard one joker



                     if jokerQuantity == 2:
                        #for two joker
                        if currentPlayerHand[cardNumber + 1] >= cardQuantity -1 and (currentBoard[
                      highestCardOnBoard] + jokerQuantityBoard) <= cardQuantity + 1: # if the amount of cards in board and in the hand are the same or more than cardNumber quantity

                            if firstAction:  # if this is the first move
                                if cardNumber + 1 == self.maxCardNumber:  # if this is the highest card
                                    possibleActions.append(1)  # I can discard two jokers

                                else:
                                    possibleActions.append(0)  # I can discard two jokers

                            else:
                              possibleActions.append(1) # I can discard two jokers

                        else:
                            possibleActions.append(0) # I cannot discard two jokers


                     else:
                        possibleActions.append(0) # I cannot discard two jokers

                  # elif highestCardOnBoard == self.maxCardNumber: # if I do not have the card in the hand
                  #       possibleActions.append(1)
                  #       possibleActions.append(0)

                  else:  # there is no joker in the hand
                      possibleActions.append(0) # I cannot discard one joker

                      possibleActions.append(0) # I cannot discard two joker




              else:
                  possibleActions.append(0)  # I cannot discard one joker

                  possibleActions.append(0)  # I cannot discard two joker



      # print ("Possible actions:", possibleActions)
      # input("here")

      #Joker actions
      # verify how many jokers the player has at hand
      highLevelActions.append("C0;Q0;J1")
      if self.maxCardNumber+1 in self.playersHand[player]: # there is a joker in the hand
          if firstAction:
              possibleActions.append(0)
          else:
              if highestCardOnBoard == self.maxCardNumber+2:
                  possibleActions.append(1) # I can discard the joker

              else:
                  possibleActions.append(0)  # I cannot discard the joker

      else:
          possibleActions.append(0) #I can not discard one joker

      possibleActions.append(1) #the pass action, which is always a valid action
      highLevelActions.append("pass")


      self.highLevelActions = highLevelActions
      return possibleActions

  def isActionAllowed(self, player, action):
      possibleActions =self.getPossibleActions(player)# check possible actions

      actionToTake = numpy.argmax(action)
      #
      # print ("Action to take:", actionToTake)
      # print("Possible actions:", len(possibleActions))


      if possibleActions[actionToTake] == 1: # if this specific action is part of the game
          return True
      else:
          return False

  def discardCards(self, player, action):

      action = numpy.argmax(action)
      self.restartBoard()
      cardsToDiscard = []

      #find the cards to discard
      discardIndex = 0
      for cardNumber in range (self.maxCardNumber):
          for cardQuantity in range (cardNumber+1):

              if discardIndex == action:
                  for i in range(cardQuantity+1): # the card quantity starts always with 1
                      cardsToDiscard.append(cardNumber+1) # the card number starts always with 1

              #discard card + 1 Joker
              discardIndex = discardIndex + 1
              if discardIndex == action:
                  for i in range(cardQuantity+1): # the card quantity starts always with 1
                      cardsToDiscard.append(cardNumber+1) # the card number starts always with 1
                  cardsToDiscard.append(self.maxCardNumber+1)

              #discard card +2 Jokers
              discardIndex = discardIndex + 1
              if discardIndex == action:
                  for i in range(cardQuantity+1): # the card quantity starts always with 1
                      cardsToDiscard.append(cardNumber+1) # the card number starts always with 1
                  cardsToDiscard.append(self.maxCardNumber+1)
                  cardsToDiscard.append(self.maxCardNumber + 1)


              discardIndex = discardIndex + 1

      #discard only the joker
      if action == self.numberOfActions-2:
          cardsToDiscard.append(self.maxCardNumber + 1)


      originalCardDiscarded = cardsToDiscard.copy()
      # remove them from the players hand and add them to the board
      boardPosition = 0
      for cardIndex in range(len(self.playersHand[player])):

          # print ("Cards to discard:", len(cardsToDiscard))
          for i in cardsToDiscard:
              # print("Card to discard:", i)
              # print("card in player hand:", self.playersHand[player][cardIndex] )
              if self.playersHand[player][cardIndex] == i:
                  # print ("removing...")

                  self.playersHand[player][cardIndex] = 0
                  # self.playersHand[player].remove(i)
                  cardsToDiscard.remove(i)
                  self.board[boardPosition] = i
                  boardPosition = boardPosition+1

      # print("cardsToDiscard:", originalCardDiscarded)
      # print("self.playersHand[player]:", self.playersHand[player])
      # print("boardPosition:", self.board)
      # input("here")

      self.playersHand[player] = sorted(self.playersHand[player])
      return originalCardDiscarded


  def startNewGame(self, maxCardNumber=4, numberPlayers=2, numGames=0, rewardFunction=""):


    #start all variables

    self.rewardFunction = rewardFunction

    # variables for the entire experiment
    self.score = []  # the last score
    self.board = []  # the current board

    self.maxCardNumber = 0  # The highest value of a card in the deck

    self.numberPlayers = 0  # number of players playing the game

    self.numberOfCardsPerPlayer = 0  # number of cards each player has at hand in the begining of the game

    self.numberOfActions = 0

    # variables per game played
    self.cards = []  # the deck

    self.playersHand = []  # the current cards each player has at hand

    self.currentPlayer = 0

    self.currentGame = []

    self.gameFinished = False

    self.exchangedCards = []  # cards exchanged on the role change

    self.firstActionPlayed = 0

    self.playerStartedGame = 0  # who started the game

    self.currentRoles = []

    self.currentSpecialAction = []

    self.currentPlayerDeclaredSpecialAction = []

    self.rounds = 0

    self.lastToPass = 0

    self.lastActionPlayers = []

    self.playerActionsTimeLine = []

    self.playerActionsComplete = []

    self.playerActionsCompleteAllGames = []

    # Variables to log some statistics per all games
    self.allScores = []
    self.allRewards = []
    self.allWrongActions = []
    self.allRounds = []
    self.winners = []
    self.playerActionsCompleteAllGames = []

    self.startGameFinishingPosition = []

    self.currentGameRewards = []
    self.currentWrongActions = []

    # Auxiliatory variables
    self.takenActions = []  # store a set of actions that were taken by a certain agent
    self.currentActionRewards = []

    self.highLevelActions = []

    # update the max number of cards
    self.maxCardNumber = maxCardNumber

    # update number of players
    self.numberPlayers = numberPlayers

    self.startGameWinGames = 0

    self.allRewards = []
    for i in range(self.numberPlayers):
        self.allRewards.append([])
        self.allWrongActions.append([])
        self.startGameFinishingPosition.append(0)
        self.playerActionsCompleteAllGames.append([])

  def declareSpecialAction(self):

      specialAction =""
      for i in range(len(self.playersHand)):
          if self.maxCardNumber + 1 in self.playersHand[i]:
            # jokers =  self.playersHand[score[3]])
            unique, counts = numpy.unique(self.playersHand[i], return_counts=True)
            currentPlayerHand = dict(zip(unique, counts))

            jokerQuantity = currentPlayerHand[self.maxCardNumber + 1]
            if jokerQuantity ==2:
                if self.allScores[-1][0] or self.allScores[-1][1] or self.allScores[-1][2]:
                    specialAction = "Dinner served!"
                    # self.exchangedCards = [i, specialAction]
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

                    self.exchangedCards = [i, specialAction]
                    return True, True

      self.currentSpecialAction = ""
      self.currentPlayerDeclaredSpecialAction = ""
      return (False, False)


  def changeRoles(self, foodFight=False):

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

    self.numberOfCardsPerPlayer = int(len(self.cards) / len(self.playersHand))

    # For each player, distribute the amount of cards
    for playerNumber in range(len(self.playersHand)):
      self.playersHand[playerNumber] = sorted(self.cards[
                                              playerNumber * self.numberOfCardsPerPlayer:playerNumber * self.numberOfCardsPerPlayer + self.numberOfCardsPerPlayer])

  def restartBoard(self):
        # clean the board
        self.board = []
        for i in range(self.maxCardNumber):
            self.board.append(0)

        # start the game with the highest card
        self.board[0] = self.maxCardNumber + 2
        # input ("Board:" + str(self.board))

  def hasPlayerFinished(self, player):

    if numpy.array(self.playersHand[player]).sum() > 0:
      return False
    else:
      return True

  def getCurrentPlayerState(self):

    stateVector = []
    for a in self.playersHand[self.currentPlayer]:
      stateVector.append(a)
    for a in self.board:
      stateVector.append(a)

    return numpy.array(stateVector) / self.maxCardNumber  # preprocess the state input

  def writeLog(self, message):
      self.logger.write(message)