import keras
import numpy

from collections import deque
from keras.layers import Input, Dense, Flatten
from keras.models import Model
from keras.optimizers import Adam
from keras.callbacks import ModelCheckpoint

from keras.models import load_model

from keras import backend as K

import tensorflow as tf
import datetime

import random

class AgentDQL:


    name="DQL"
    actor = None
    numMaxCards = 0
    numCardsPerPlayer = 0
    trainingEpoches = 0
    decayFactor = 0.99
    eps = 0.25
    actionsTaken = []

    outputSize = 0
    def __init__(self, numMaxCards = 4, numCardsPerPlayer=0, trainingEpoches=10, loadModel =""):

        self.numMaxCards = numMaxCards
        self.numCardsPerPlayer = numCardsPerPlayer
        self.trainingEpoches = trainingEpoches
        self.outputSize = (self.numMaxCards * self.numMaxCards + 1) # all the possible ways to play cards plus the pass action
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95  # discount rate
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.batchSize = 128

        if loadModel=="":
            self.buildModel()
        else:
            self.loadModel(loadModel)


    def buildModel(self):

          self.buildSimpleModel()


    def buildPole(self, inputSize, outputSize):

        inputLayer = Input(shape=(inputSize,),
                           name="State")  # 5 cards in the player's hand + maximum 4 cards in current board

        dense_1 = Dense(24, activation="relu", name="ActorCritic_hidden1")(inputLayer)
        dense_2_actor = Dense(24, activation="relu", name="Actor_hidden2")(dense_1)
        outputActor = Dense(outputSize, activation="softmax")(
            dense_2_actor)  # Cards at the player hand plus the pass action

        self.actor = Model(inputs=[inputLayer], outputs=[outputActor])

        self.actor .compile(loss='mse', optimizer=Adam(lr=self.learning_rate), metrics=['mse'])


    def buildSimpleModel(self):

        inputSize = self.numCardsPerPlayer + self.numMaxCards

        inputLayer = Input(shape=(inputSize,),
                           name="State")  # 5 cards in the player's hand + maximum 4 cards in current board

        dense_1 = Dense(24, activation="relu", name="ActorCritic_hidden1")(inputLayer)
        dense_2_actor = Dense(24, activation="relu", name="Actor_hidden2")(dense_1)
        outputActor = Dense(self.outputSize, activation="softmax")(
            dense_2_actor)  # Cards at the player hand plus the pass action

        self.actor = Model(inputs=[inputLayer], outputs=[outputActor])

        self.actor .compile(loss='mse', optimizer=Adam(lr=self.learning_rate), metrics=['mse'])

        # self.actor .compile(loss=self._huber_loss, optimizer=Adam(lr=self.learning_rate), metrics=['mse'])


    def memorize(self, state, action, reward, next_state, done, savedNetwork, game):
        action = numpy.argmax(action)
        state = numpy.expand_dims(numpy.array(state), 0)
        next_state = numpy.expand_dims(numpy.array(next_state), 0)
        self.memory.append((state, action, reward, next_state, done))

        if len(self.memory) > self.batchSize:
            self.trainSimpleModel(self.batchSize, savedNetwork, game)

    def memorize2(self, state, action, reward, next_state, done):
        action = numpy.argmax(action)
        state = numpy.expand_dims(numpy.array(state), 0)
        next_state = numpy.expand_dims(numpy.array(next_state), 0)
        self.memory.append((state, action, reward, next_state, done))


    actionsTaken = []
    def getRandomAction(self, action):

        actionIndex = numpy.argmax(action)  # number of cards in the player hand plus pass

        while actionIndex in self.actionsTaken:
            actionIndex = actionIndex + 1
            if actionIndex >= len(action):
                actionIndex = 0

        action = numpy.zeros(self.outputSize)
        action[actionIndex] = 1
        self.actionsTaken.append(actionIndex)

        return action

    actions = 0
    def getAction(self, stateVector):

        # numberRandom =  numpy.random.random()
        # if numberRandom < self.eps:
        #     aIndex = numpy.random.randint(0, self.outputSize)
        #     a = numpy.zeros(self.outputSize)
        #     a[aIndex] = 1
        # else:
        #     stateVector = numpy.expand_dims(numpy.array(stateVector),0)
        #     a = self.actor.predict(stateVector)[0]

        if numpy.random.rand() <= self.epsilon:
            aIndex = numpy.random.randint(0, self.outputSize)
            a = numpy.zeros(self.outputSize)
            a[aIndex] = 1
        else:
            stateVector = numpy.expand_dims(numpy.array(stateVector), 0)
            a = self.actor.predict(stateVector)[0]

        return a

    def resetActionsTaken(self):
        self.actionsTaken = []

    def loadModel(self, model):
        self.actor  = load_model(model)

    def cleanMemory(self):
        self.memory = deque(maxlen=2000)

    def _huber_loss(self, y_true, y_pred, clip_delta=1.0):
        error = y_true - y_pred
        cond = K.abs(error) <= clip_delta

        squared_loss = 0.5 * K.square(error)
        quadratic_loss = 0.5 * K.square(clip_delta) + clip_delta * (K.abs(error) - clip_delta)

        return K.mean(tf.where(cond, squared_loss, quadratic_loss))


    def trainSimpleModel(self, batch_size, savedNetwork, game):

        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = (reward + self.gamma *
                          numpy.amax(self.actor.predict(next_state)[0]))
            target_f = self.actor.predict(state)
            target_f[0][action] = target
            self.actor.fit(state, target_f, epochs=1, verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        if game%20:
            self.actor.save(savedNetwork + "/actor_iteration_" + str(game) + ".hd5")


    def trainSimpleModelPole(self, batch_size):

        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = (reward + self.gamma *
                          numpy.amax(self.actor.predict(next_state[0])[0]))
            target_f = self.actor.predict(state[0])
            target_f[0][action] = target
            self.actor.fit(state, target_f, epochs=1, verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
