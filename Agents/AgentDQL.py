from Agents import IAgent
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

class AgentDQL(IAgent.IAgent):

    name=""
    actor = None
    numMaxCards = 0
    numCardsPerPlayer = 0

    outputSize = 0

    training = False

    lastModel = ""

    currentCorrectAction = 0

    totalCorrectAction = []

    totalAction = []
    totalActionPerGame = 0

    losses = []

    SelectedActions = []

    intrinsic = None

    def __init__(self, params=[]):
        self.training = params[0]
        self.initialEpsilon = params[1]

        if len(params) > 2:
            agentName = "_"+params[2]
        else:
            agentName = ""

        if len(params) > 3:
            self.intrinsic = params[3]
        else:
            self.intrinsic = None

        self.name = "DQL"+agentName

        self.totalAction = []
        self.totalActionPerGame = 0

        self.currentCorrectAction = 0

        self.totalCorrectAction = []
        self.losses = []


    def startAgent(self, params=[]):
        numMaxCards, numCardsPerPlayer, actionNumber, loadModel, agentParams = params

        self.numMaxCards = numMaxCards
        self.numCardsPerPlayer = numCardsPerPlayer
        self.outputSize = actionNumber  # all the possible ways to play cards plus the pass action

        if len(agentParams) > 1:

            self.hiddenLayers, self.hiddenUnits, self.batchSize,  self.tau = agentParams

        else:

            self.hiddenLayers = 1
            self.hiddenUnits = 256
            self.batchSize = 128
            self.tau = 0.52  # target network update rate


        self.gamma = 0.95  # discount rate
        self.loss = "mse"

        self.epsilon_min = 0.1
        self.epsilon_decay = 0.990


        # self.tau = 0.1 #target network update rate

        if self.training:
            self.epsilon = self.initialEpsilon  # exploration rate while training
        else:
            self.epsilon = 0.0 #no exploration while testing

        # behavior parameters
        self.prioritized_experience_replay = False
        self.dueling = False

        QSize = 20000
        self.memory = MemoryBuffer.MemoryBuffer(QSize, self.prioritized_experience_replay)

        # self.learning_rate = 0.01
        self.learning_rate = 0.001

        if loadModel == "":
            self.buildModel()
        else:
            self.loadModel(loadModel)

        self.losses = []

        self.QValues = []

        self.SelectedActions = []

        self.MeanQValuesPerGame = []
        self.currentGameQValues = []


    def buildModel(self):

          self.buildSimpleModel()

          self.actor.compile(loss=self.loss, optimizer=Adam(lr=self.learning_rate), metrics=["mse"])

          self.targetNetwork.compile(loss=self.loss, optimizer=Adam(lr=self.learning_rate), metrics=["mse"])


    def buildSimpleModel(self):

        """ Build Deep Q-Network
               """

        def model():
            inputSize = self.numCardsPerPlayer + self.numMaxCards
            inputLayer = Input(shape=(inputSize,),
                               name="State")  # 5 cards in the player's hand + maximum 4 cards in current board

            # dense = Dense(self.hiddenLayers, activation="relu", name="dense_0")(inputLayer)
            for i in range(self.hiddenLayers + 1):

                if i == 0:
                    previous = inputLayer
                else:
                  previous = dense

                dense = Dense(self.hiddenUnits * (i + 1), name="Dense" + str(i), activation="relu")(previous)

            if (self.dueling):
                # Have the network estimate the Advantage function as an intermediate layer
                dense = Dense(self.outputSize + 1, activation='linear', name="duelingNetwork")(dense)
                dense = Lambda(lambda i: K.expand_dims(i[:, 0], -1) + i[:, 1:] - K.mean(i[:, 1:], keepdims=True),
                           output_shape=(self.outputSize,))(dense)


            possibleActions = Input(shape=(self.outputSize,),
                       name="PossibleAction")


            dense = Dense(self.outputSize, activation='softmax')(dense)
            output = Multiply()([possibleActions, dense])

            # probOutput =  Dense(self.outputSize, activation='softmax')(dense)

            return Model([inputLayer, possibleActions], output)

        self.actor = model()
        self.targetNetwork =  model()
        self.loadQValueReader()
        # self.successNetwork = Model([inputLayer, possibleActions], probOutput)


    def loadQValueReader(self):
        softmaxLayer = self.actor.get_layer(index=-2)
        self.QValueReader = Model(self.actor.inputs, softmaxLayer.output)


    def observeOponentAction(self, params):
        self.intrinsic.observeOponentAction(params, self.actor)

    def getAction(self, params):

        stateVector, possibleActionsOriginal = params
        stateVector = numpy.expand_dims(numpy.array(stateVector), 0)

        possibleActions2 = copy.copy(possibleActionsOriginal)

        if numpy.random.rand() <= self.epsilon:
            itemindex = numpy.array(numpy.where(numpy.array(possibleActions2) == 1))[0].tolist()
            random.shuffle(itemindex)
            aIndex = itemindex[0]
            a = numpy.zeros(self.outputSize)
            a[aIndex] = 1

        else:

            possibleActionsVector = numpy.expand_dims(numpy.array(possibleActions2), 0)
            a = self.actor.predict([stateVector, possibleActionsVector])[0]
            aIndex = numpy.argmax(a)

            #Update QValues
            self.QValues.append(a)
            self.currentGameQValues.append(numpy.sum(a))

            if possibleActionsOriginal[aIndex] == 1:
                self.currentCorrectAction = self.currentCorrectAction + 1

        self.totalActionPerGame = self.totalActionPerGame + 1
        return a

    def loadModel(self, model):
        self.actor  = load_model(model)
        self.targetNetwork = load_model(model)
        self.loadQValueReader()


    def updateTargetNetwork(self):

        W = self.actor.get_weights()
        tgt_W = self.targetNetwork.get_weights()
        for i in range(len(W)):
            tgt_W[i] = self.tau * W[i] + (1 - self.tau) * tgt_W[i]
        self.targetNetwork.set_weights(tgt_W)



    def updateModel(self, savedNetwork, game, thisPlayer):

        """ Train Q-network on batch sampled from the buffer
                """
        # Sample experience from memory buffer (optionally with PER)
        s, a, r, d, new_s, possibleActions, newPossibleActions, idx = self.memory.sample_batch(self.batchSize)

        # Apply Bellman Equation on batch samples to train our DDQN
        q = self.actor.predict([s, possibleActions])
        next_q = self.actor.predict([new_s, newPossibleActions])
        q_targ = self.targetNetwork.predict([new_s, newPossibleActions])

        # self.successNetwork.compile(loss=self.loss, optimizer=Adam(lr=self.learning_rate), metrics=["mse"])

        for i in range(s.shape[0]):
            old_q = q[i, a[i]]
            if d[i]:
                q[i, a[i]] = r[i]
            else:
                next_best_action = numpy.argmax(next_q[i, :])
                q[i, a[i]] = r[i] + self.gamma * q_targ[i, next_best_action]


            if (self.prioritized_experience_replay):
                # Update PER Sum Tree
                self.memory.update(idx[i], abs(old_q - q[i, a[i]]))


        # Train on batch
        history = self.actor.fit([s,possibleActions] , q, verbose=False)
        self.losses.append(history.history['loss'])

        if (game + 1) % 1000 == 0:
            self.actor.save(savedNetwork + "/actor_iteration_" + str(game) + "_Player_"+str(thisPlayer)+".hd5")
            self.lastModel = savedNetwork + "/actor_iteration_" + str(game) + "_Player_"+str(thisPlayer)+".hd5"


        print (" -- Epsilon:" + str(self.epsilon) + " - Loss:" + str(history.history['loss']))


    def memorize(self, state, action, reward, next_state, done, possibleActions, newPossibleActions):

        if (self.prioritized_experience_replay):
            state = numpy.expand_dims(numpy.array(state), 0)
            next_state = numpy.expand_dims(numpy.array(next_state), 0)
            q_val = self.actor.predict(state)
            q_val_t = self.targetNetwork.predict(next_state)
            next_best_action = numpy.argmax(q_val)
            new_val = reward + self.gamma * q_val_t[0, next_best_action]
            td_error = abs(new_val - q_val)[0]
        else:
            td_error = 0

        self.memory.memorize(state, action, reward, done, next_state, possibleActions, newPossibleActions, td_error)


    def train(self, params=[]):

        state, action, reward, next_state, done, savedNetwork, game, possibleActions, newPossibleActions, thisPlayer, score = params
        action = numpy.argmax(action)
        self.memorize(state, action, reward, next_state, done, possibleActions, newPossibleActions)


        if done:
            self.totalCorrectAction.append(self.currentCorrectAction)
            self.totalAction.append(self.totalActionPerGame)

            self.currentCorrectAction = 0
            self.totalActionPerGame = 0

            meanQValueThisGame = numpy.average(self.currentGameQValues)

            self.MeanQValuesPerGame.append(meanQValueThisGame)
            self.currentGameQValues = []

            # if not self.intrinsic == None:
            #     if len(score) >= 1:
            #         if thisPlayer in score:
            #             self.intrinsic.doEndOfGame(score, thisPlayer, params)


        if self.training:

            if not self.intrinsic == None:
                self.intrinsic.trainPModel(params)

            if self.memory.size() > self.batchSize and done:
                self.updateModel(savedNetwork, game, thisPlayer)
                self.updateTargetNetwork()

                # Update the decay
                if self.epsilon > self.epsilon_min:
                    self.epsilon *= self.epsilon_decay





