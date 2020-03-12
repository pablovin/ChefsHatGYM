import numpy
from Agents.AgentType  import DUMMY_RANDOM, DUMMY_DISCARDONECARD
import copy

class AgentRandom:

    numMaxCards = 0
    outputSize = 0
    actionsTaken = []
    name="DUMMY"
    behavior = "RANDOM"

    #agentsType


    def __init__(self, behavior, numMaxCards = 4, numActions=200):

        self.numMaxCards = numMaxCards
        self.outputSize = numActions # all the possible ways to play cards plus the pass action

        self.behavior = behavior

    def getAction(self, possibleActions):

        if self.behavior == DUMMY_RANDOM:
            possibleActions = possibleActions

        if self.behavior == DUMMY_DISCARDONECARD:

            originalPossibleAction = copy.copy(possibleActions)
            positionsWithOneCard = [0, 3, 9, 18, 30, 45, 63, 84, 108, 135, 165]
            for i in range(len(possibleActions)):

                if not i in positionsWithOneCard:
                    possibleActions[i] = 0

            if originalPossibleAction[198] == 1: #check if joker was an option
                possibleActions[198] = 1


        possibleActions[199] = 0 #pass action always will be selected if nothing else is possible

        trials = 0
        aIndex = numpy.random.randint(0, self.outputSize)
        while not possibleActions[aIndex] == 1:
            aIndex = aIndex + 1

            if aIndex >= len(possibleActions):
                aIndex = 0

            trials = trials+1
            if trials == len(possibleActions)-1:
                aIndex = 199
                break

        a = numpy.zeros(self.outputSize)
        a[aIndex] = 1

        return a

