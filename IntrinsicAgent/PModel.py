import numpy
import copy

from collections import deque
from keras.layers import Input, Dense, Flatten, Concatenate, Lambda, Multiply
import keras.backend as K

from keras.models import Model
from keras.optimizers import Adam

from keras.models import load_model

from Agents import MemoryBuffer

import random

class PModel():

    name=""
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

    training = False

    lastModel = ""

    losses = []

    def __init__(self):
        self.numMaxCards = 11
        self.numCardsPerPlayer = 17
        self.outputSize = 200  # all the possible ways to play cards plus the pass action

        self.hiddenLayers = 1
        self.hiddenUnits = 256
        self.batchSize = 128
        self.tau = 0.52  # target network update rate

        self.gamma = 1  # discount rate for PModel
        self.loss = "mse"

        QSize = 20000
        self.memory = MemoryBuffer.MemoryBuffer(QSize, False)

        # self.learning_rate = 0.01
        self.learning_rate = 0.001

        self.losses = []

        self.buildModel()


    def buildModel(self):

          self.buildPModel()

          self.online_network.compile(loss=self.loss, optimizer=Adam(lr=self.learning_rate), metrics=["mse"])

          self.targetNetwork.compile(loss=self.loss, optimizer=Adam(lr=self.learning_rate), metrics=["mse"])

          # self.successNetwork.compile(loss=self.loss, optimizer=Adam(lr=self.learning_rate), metrics=["mse"])

    def buildPModel(self):

        """ Build Deep Q-Network
               """
        def model():
            inputSize = self.numCardsPerPlayer + self.numMaxCards
            inputLayer = Input(shape=(28,),
                               name="State")  # 5 cards in the player's hand + maximum 4 cards in current board

            # dense = Dense(self.hiddenLayers, activation="relu", name="dense_0")(inputLayer)
            for i in range(self.hiddenLayers + 1):

                if i == 0:
                    previous = inputLayer
                else:
                  previous = dense

                dense = Dense(self.hiddenUnits * (i + 1), name="Dense" + str(i), activation="relu")(previous)


            possibleActions = Input(shape=(self.outputSize,),
                       name="PossibleAction")

            dense = Dense(self.outputSize, activation='softmax')(dense)
            output = Multiply()([possibleActions, dense])

            # probOutput =  Dense(self.outputSize, activation='softmax')(dense)

            return Model([inputLayer, possibleActions], output)

        self.online_network = model()
        self.targetNetwork =  model()


    def loadQValueReader(self):
        softmaxLayer = self.online_network.get_layer(index=-2)
        self.QValueReader = Model(self.online_network.inputs, softmaxLayer.output)


    def getProbability(self, params):

        stateVector, possibleActionsOriginal = params
        stateVector = numpy.expand_dims(numpy.array(stateVector), 0)
        possibleActions2 = copy.copy(possibleActionsOriginal)
        possibleActionsVector = numpy.expand_dims(numpy.array(possibleActions2), 0)

        a = self.online_network.predict([stateVector, possibleActionsVector])[0]

        return a

    def loadModel(self, model):
        self.online_network  = load_model(model)
        self.targetNetwork = load_model(model)


    def updateTargetNetwork(self):

        W = self.online_network.get_weights()
        tgt_W = self.targetNetwork.get_weights()
        for i in range(len(W)):
            tgt_W[i] = self.tau * W[i] + (1 - self.tau) * tgt_W[i]
        self.targetNetwork.set_weights(tgt_W)

        #
        # self.online_network.set_weights(self.online_network.get_weights())


    def updateModel(self, savedNetwork, game, thisPlayer):

        """ Train Q-network on batch sampled from the buffer
                """
        # Sample experience from memory buffer (optionally with PER)
        s, a, r, d, new_s, possibleActions, newPossibleActions, idx = self.memory.sample_batch(self.batchSize)

        # Apply Bellman Equation on batch samples to train our DDQN
        q = self.online_network.predict([s, possibleActions])
        next_q = self.online_network.predict([new_s, newPossibleActions])
        q_targ = self.targetNetwork.predict([new_s, newPossibleActions])

        # self.successNetwork.compile(loss=self.loss, optimizer=Adam(lr=self.learning_rate), metrics=["mse"])

        for i in range(s.shape[0]):
            old_q = q[i, a[i]]
            if d[i]:
                q[i, a[i]] = r[i]
            else:
                next_best_action = numpy.argmax(next_q[i, :])
                q[i, a[i]] = r[i] + self.gamma * q_targ[i, next_best_action]

        # Train on batch
        history = self.online_network.fit([s,possibleActions] , q, verbose=False)
        self.losses.append(history.history['loss'])

        if (game + 1) % 1000 == 0:
            self.online_network.save(savedNetwork + "/PModel_iteration_" + str(game) + "_Player_"+str(thisPlayer)+".hd5")
            self.lastModel = savedNetwork + "/PModel_iteration_" + str(game) + "_Player_"+str(thisPlayer)+".hd5"


        print (" - PLoss:" + str(history.history['loss']))


    def memorize(self, state, action, reward, next_state, done, possibleActions, newPossibleActions):

        td_error = 0
        self.memory.memorize(state, action, reward, done, next_state, possibleActions, newPossibleActions, td_error)


    def train(self, params=[]):

        state, action, reward, next_state, done, savedNetwork, game, possibleActions, newPossibleActions, thisPlayer, score = params

        action = numpy.argmax(action)

        self.memorize(state, action, reward, next_state, done, possibleActions, newPossibleActions)

        # if self.memory.size() > self.batchSize:
        if self.memory.size() > self.batchSize and done:
            self.updateModel(savedNetwork, game, thisPlayer)
            self.updateTargetNetwork()






