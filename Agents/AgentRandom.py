import numpy
import copy
from Agents import IAgent
import random

DUMMY_RANDOM = "DUMMY_RANDOM"
DUMMY_DISCARDONECARD = "DUMMY_DISCARDONECARD"

class AgentRandom(IAgent.IAgent):

    numMaxCards = 0
    outputSize = 0
    actionsTaken = []
    name = ""
    lastModel = ""

    currentCorrectAction = 0

    totalCorrectAction = []

    totalAction = []
    totalActionPerGame = 0

    losses = []
    QValues = []

    Probability = []

    SelectedActions = []

    def __init__(self, name):

        self.name = name

        self.totalCorrectAction.append(0)

    def startAgent(self, params):

        numMaxCards , cardsPlayer, numActions, loadModel, params  = params

        self.numMaxCards = numMaxCards
        self.outputSize = numActions # all the possible ways to play cards plus the pass action


    def getAction(self, params):

        state, possibleActions2 = params
        possibleActions = copy.copy(possibleActions2)

        if self.name == DUMMY_RANDOM:
            possibleActions = possibleActions

        if self.name == DUMMY_DISCARDONECARD:
            # print ("here")
            originalPossibleAction = copy.copy(possibleActions2)
            positionsWithOneCard = [0, 3, 9, 18, 30, 45, 63, 84, 108, 135, 165]
            for i in range(len(possibleActions)):

                if not i in positionsWithOneCard:
                    possibleActions[i] = 0

            if originalPossibleAction[198] == 1: #check if joker was an option
                possibleActions[198] = 1

            if originalPossibleAction[199] == 1:
                possibleActions[199] = 1


        itemindex = numpy.array(numpy.where(numpy.array(possibleActions) == 1))[0].tolist()
        random.shuffle(itemindex)
        aIndex = itemindex[0]
        a = numpy.zeros(self.outputSize)
        a[aIndex] = 1

        return a



        # aIndex = numpy.random.randint(0, self.outputSize)
        # if possibleActions[aIndex] == 0:
        # possibleActions[199] = 0 #pass action always will be selected if nothing else is possible
        #
        # trials = 0
        # aIndex = numpy.random.randint(0, self.outputSize)
        #
        #
        # while not possibleActions[aIndex] == 1:
        #     aIndex = aIndex + 1
        #
        #     if aIndex >= len(possibleActions):
        #         aIndex = 0
        #
        #     trials = trials+1
        #     if trials == len(possibleActions)-1:
        #         aIndex = 199
        #         break


    def loadModel(self, params):
        pass

    def buildModel(self):
        pass

    def train(self, params):
        pass

