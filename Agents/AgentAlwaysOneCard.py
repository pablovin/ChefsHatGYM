import keras
import numpy

from keras.layers import Input, Dense, Flatten
from keras.models import Model
from keras.optimizers import Adam
from keras.callbacks import ModelCheckpoint

from keras import backend as K

import tensorflow as tf
import datetime


class AgentAlwaysOneCard:

    numMaxCards = 0
    outputSize = 0
    actionsTaken = []
    name="OneCardOnly"

    def __init__(self, numMaxCards = 4, numActions=365):

        self.numMaxCards = numMaxCards
        self.outputSize = numActions # all the possible ways to play cards plus the pass action

    def getPossibleActions(self, playerHand, firstAction, board):

        # print ("Player:", player)
        possibleActions = []

        unique, counts = numpy.unique(board, return_counts=True)
        currentBoard = dict(zip(unique, counts))

        unique, counts = numpy.unique(playerHand, return_counts=True)
        currentPlayerHand = dict(zip(unique, counts))

        highestCardOnBoard = 0
        for boardItem in currentBoard:
            if not boardItem == self.numMaxCards + 1:
                highestCardOnBoard = boardItem

        jokerQuantityBoard = 0

        if self.numMaxCards + 1 in board:
            jokerQuantityBoard = currentBoard[self.numMaxCards + 1]

        #
        # print("Possible actions:", possibleActions)

        for cardNumber in range(self.numMaxCards):
            possibleAction = 0
            # print ("Card Number:", cardNumber+1)
            # # print("cardNumber:", cardNumber + 1)
            # #
            # print("- Player:", player)
            # print("- Hand:", currentPlayerHand)
            # print("- Current board:", currentBoard)
            # print("- Highest card on board:", highestCardOnBoard)
            # print("-Card lower than the ones in the board:", cardNumber + 1 < highestCardOnBoard)
            # print("-Card present in the player hand:", cardNumber + 1 in playerHand)

            # if this card is present in the hand and it is lower than the cards in the board
            for cardQuantity in range(self.numMaxCards):

                if (cardNumber + 1 < highestCardOnBoard) and cardNumber + 1 in playerHand:

                    # verify if the quantity of the card in the hand is allowed to be put down

                    # if the amount of cards in board and in the hand are the same or more than cardNumber quantity
                    # print("-- Card quantity:", cardQuantity+1)
                    # print("-- Amount of cards in hand:", currentPlayerHand[cardNumber + 1])
                    # print("-- Amount of cards in board:", currentBoard[highestCardOnBoard])
                    # print("-- Can I discard this qunatity:", currentPlayerHand[cardNumber + 1] >= cardQuantity+1)
                    # print("-- Is it the same or more than in the board:", currentBoard[
                    #     highestCardOnBoard] <= cardQuantity + 1)

                    if currentPlayerHand[cardNumber + 1] >= cardQuantity + 1 and (currentBoard[
                                                                                      highestCardOnBoard] + jokerQuantityBoard) <= cardQuantity + 1:  # taking into consideration the amount of jokers in the board

                        if firstAction:  # if this is the first move
                            # print("--- First Action:")

                            if cardNumber + 1 == self.numMaxCards:  # if this is the highest card
                                # print("----- First Action Added!")

                                if cardQuantity == 1:
                                    possibleActions.append(1)
                                else:
                                    possibleActions.append(0)
                            else:
                                possibleActions.append(0)
                        else:
                            # print("----- Added here!")

                            if cardQuantity == 1:
                                possibleActions.append(1)
                            else:
                                possibleActions.append(0)

                    else:

                        possibleActions.append(0)

                else:
                    possibleActions.append(0)

                # add the joker possibilities
                if self.numMaxCards + 1 in playerHand:  # there is a joker in the hand
                    jokerQuantity = currentPlayerHand[self.numMaxCards + 1]

                    if (cardNumber + 1 < highestCardOnBoard) and cardNumber + 1 in playerHand:  # if I have the card in hand and it is lower than the one in the field

                        # for one joker
                        if currentPlayerHand[cardNumber + 1] >= cardQuantity and (currentBoard[
                                                                                      highestCardOnBoard] + jokerQuantityBoard) <= cardQuantity + 1:  # verify if the amount of cards in the hand + a joker is more than the card quantity and if the cards in the board + possible jokers is more than the card quantity
                            possibleActions.append(0)  # I can discard one joker
                        else:
                            possibleActions.append(0)  # I cannot discard one joker

                        if jokerQuantity == 2:
                            # for two joker
                            if currentPlayerHand[cardNumber + 1] >= cardQuantity - 1 and (currentBoard[
                                                                                              highestCardOnBoard] + jokerQuantityBoard) <= cardQuantity + 1:  # if the amount of cards in board and in the hand are the same or more than cardNumber quantity
                                possibleActions.append(0)  # I can discard two jokers
                            else:
                                possibleActions.append(0)  # I cannot discard two jokers

                        else:
                            possibleActions.append(0)  # I cannot discard two jokers
                    # elif highestCardOnBoard == self.numMaxCards: # if I do not have the card in the hand
                    #       possibleActions.append(1)
                    #       possibleActions.append(0)

                    else:  # there is no joker in the hand
                        possibleActions.append(0)  # I cannot discard one joker
                        possibleActions.append(0)  # I cannot discard two joker


                else:
                    possibleActions.append(0)  # I cannot discard one joker
                    possibleActions.append(0)  # I cannot discard two joker

                # possibleActions.append(possibleAction)

        # print ("Possible actions:", possibleActions)
        # input("here")

        # Joker actions
        # verify how many jokers the player has at hand
        if self.numMaxCards + 1 in playerHand:  # there is a joker in the hand
            if highestCardOnBoard == self.numMaxCards + 2:
                possibleActions.append(1)  # I can discard the joker
            else:
                possibleActions.append(0)  # I cannot discard the joker
        else:
            possibleActions.append(0)  # I can not discard one joker

        possibleActions.append(1)  # the pass action, which is always a valid action

        return possibleActions



    def getRandomAction(self, action):
        #
        # actionIndex = numpy.random.choice(self.outputSize, p=action) #number of cards in the player hand plus pass
        actionIndex = numpy.argmax(action)  # number of cards in the player hand plus pass

        while actionIndex in self.actionsTaken:
            actionIndex = actionIndex + 1
            if actionIndex >= len(action):
                actionIndex = 0

        action = numpy.zeros(self.outputSize)
        action[actionIndex] = 1
        self.actionsTaken.append(actionIndex)

        return action

    def resetActionsTaken(self):
        self.actionsTaken = []

    def getAction(self, playerHand, firstAction, board):

        a = numpy.zeros(self.outputSize)
        actions = self.getPossibleActions(playerHand, firstAction, board)

        for i in range(len(actions)):
            if actions[i]==1:
                a[i]= 1
                break

        # aIndex = numpy.random.randint(0, self.outputSize)
        # a = numpy.zeros(self.outputSize)
        # a[aIndex] = 1

        return a

