import keras
import numpy

from collections import deque
from keras.layers import Input, Dense, Flatten, Concatenate
from keras.models import Model
from keras.optimizers import Adam
from keras.callbacks import ModelCheckpoint

from keras.models import load_model

from keras import backend as K

import tensorflow as tf
import datetime

import random

from Agents.AgentType import DQL_v2

class AgentDQLV2:


    name=DQL_v2
    actor = None
    numMaxCards = 0
    numCardsPerPlayer = 0
    trainingEpoches = 0
    decayFactor = 0.99
    eps = 0.25
    actionsTaken = []

    trainingStep = 0
    targetUpdateFrequency = 50

    outputSize = 0
    def __init__(self, numMaxCards = 4, numCardsPerPlayer=0,  actionNumber = 200, loadModel ="", agentParams=[]):

        self.numMaxCards = numMaxCards
        self.numCardsPerPlayer = numCardsPerPlayer
        self.outputSize = actionNumber # all the possible ways to play cards plus the pass action


        if len(agentParams) > 1:

            # var1, var2 = agentParams
            #  self.gamma,self.epsilon_min,self.epsilon_decay,self.batchSize, self.targetUpdateFrequency   = agentParams

             self.hiddenLayers, self.hiddenUnits, self.outputActivation, self.loss = agentParams

            # [
            #     ('memroySize', hp.choice("memorySize", [5, 50, 100, 500, 1000, 2000])),
            #     ('gamma', hp.loguniform("gamma", 0, 1)),
            #     ('epsilon_min', hp.loguniform("epsilon_min", 0, 0.5)),
            #     ('epsilon_decay', hp.loguniform("epsilon_decay", 0.5, 0.9999)),
            #     ('batchSize', hp.choice("batchSize", [8, 32, 64, 128, 256, 512, 1024])),
            #     ('targetUpdateFrequency', hp.quniform('targetUpdateFrequency', 5, 25))
            # ])
        else:

             self.hiddenLayers = 1
             self.hiddenUnits = 32
             self.outputActivation = "tanh"
             self.loss ="mse"

        self.gamma = 0.95  # discount rate

        self.epsilon_min = 0.1
        self.epsilon_decay = 0.995

        self.batchSize = 256
        self.targetUpdateFrequency = 50

        self.memory = deque(maxlen= 1000)
        self.learning_rate = 0.001
        self.epsilon = 1.0  # exploration rate
        if loadModel=="":
            self.buildModel()
        else:
            self.loadModel(loadModel)


    def buildModel(self):

          self.online_network =self.buildSimpleModel()
          self.targetNetwork = self.buildSimpleModel()

          self.online_network.compile(loss=self.loss, optimizer=Adam(lr=self.learning_rate), metrics=["mse"])

          self.targetNetwork.compile(loss=self.loss, optimizer=Adam(lr=self.learning_rate), metrics=["mse"])

    def buildSimpleModel(self):

        inputSize = self.numCardsPerPlayer + self.numMaxCards

        inputLayer = Input(shape=(inputSize,),
                           name="State")  # 5 cards in the player's hand + maximum 4 cards in current board

        dense = Dense(128, activation="relu", name="dense_0")(inputLayer)
        for i in range(self.hiddenLayers):
            dense = Dense(self.hiddenUnits*(i+1), activation="relu")(dense)

        # possibleActionsLayer = Input(shape=(self.outputSize,), name="PossibleActions")
        #
        # concatLayer = Concatenate()([dense, possibleActionsLayer])
        #
        # outputActor = Dense(self.outputSize, activation=self.outputActivation)(
        #     concatLayer)  # Cards at the player hand plus the pass action
        #
        # return  Model(inputs=[inputLayer, possibleActionsLayer], outputs=[outputActor])




        outputActor = Dense(self.outputSize, activation=self.outputActivation)(
            dense)  # Cards at the player hand plus the pass action

        return  Model(inputs=[inputLayer], outputs=[outputActor])


        # self.actor .compile(loss='mse', optimizer=Adam(lr=self.learning_rate), metrics=['mse'])

        # self.actor .compile(loss=self._huber_loss, optimizer=Adam(lr=self.learning_rate), metrics=['mse'])


    def memorize(self, state, action, reward, next_state, done, savedNetwork, game, possibleActions):
        action = numpy.argmax(action)
        state = numpy.expand_dims(numpy.array(state), 0)
        next_state = numpy.expand_dims(numpy.array(next_state), 0)
        possibleActions =  numpy.expand_dims(numpy.array(possibleActions), 0)

        self.memory.append((state, action, reward, next_state, done, possibleActions))

        # if len(self.memory) > self.batchSize and game % 100==0:
        if len(self.memory) > self.batchSize:
            self.train(self.batchSize, savedNetwork, game)


    actions = 0
    def getAction(self, stateVector, possibleActions):

        if numpy.random.rand() <= self.epsilon:

            possibleActions[199] = 0
            trials = 0
            aIndex = numpy.random.randint(0, self.outputSize)
            while not possibleActions[aIndex] == 1:
                aIndex = aIndex + 1

                if aIndex >= len(possibleActions):
                    aIndex = 0

                trials = trials + 1
                if trials == len(possibleActions) - 1:
                    aIndex = 199
                    break
            a = numpy.zeros(self.outputSize)
            a[aIndex] = 1

        else:
            possibleActions = numpy.expand_dims(numpy.array(possibleActions), 0)
            stateVector = numpy.expand_dims(numpy.array(stateVector), 0)
            # a = self.online_network.predict([stateVector, possibleActions])[0]
            a = self.online_network.predict([stateVector])[0]

        return a

    def resetActionsTaken(self):
        self.actionsTaken = []

    def loadModel(self, model):
        self.online_network  = load_model(model)
        self.targetNetwork = load_model(model)


    def cleanMemory(self):
        self.memory = deque(maxlen=2000)

    def updateTargetNetwork(self):

        self.online_network.set_weights(self.online_network.get_weights())

    def train(self, batch_size, savedNetwork, game):

        # print ("Training agent...")

        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done, possibleActions in minibatch:
            target = reward
            if not done:
                # nextQValue = self.targetNetwork.predict([next_state, possibleActions])[0]
                nextQValue = self.targetNetwork.predict([next_state])[0]
                target = (reward + self.gamma *numpy.amax(nextQValue))


            # target_f = self.online_network.predict([state, possibleActions])
            target_f = self.online_network.predict([state])
            target_f[0][action] = target
            # self.online_network.fit([state,possibleActions], target_f, epochs=1, verbose=False)
            self.online_network.fit([state], target_f, epochs=1, verbose=False)
            self.trainingStep += 1


        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        if self.trainingStep % self.targetUpdateFrequency == 0:
            self.updateTargetNetwork()

        if game%20:
            self.online_network.save(savedNetwork + "/actor_iteration_" + str(game) + ".hd5")
