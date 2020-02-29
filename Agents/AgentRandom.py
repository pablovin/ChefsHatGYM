import keras
import numpy

from keras.layers import Input, Dense, Flatten
from keras.models import Model
from keras.optimizers import Adam
from keras.callbacks import ModelCheckpoint

from keras import backend as K

import tensorflow as tf
import datetime


class AgentRandom:

    numMaxCards = 0
    outputSize = 0
    actionsTaken = []
    name="RANDOM"

    def __init__(self, numMaxCards = 4, numActions=365):

        self.numMaxCards = numMaxCards
        self.outputSize = numActions # all the possible ways to play cards plus the pass action


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

    def getAction(self, state):

        aIndex = numpy.random.randint(0, self.outputSize)
        a = numpy.zeros(self.outputSize)
        a[aIndex] = 1

        return a

