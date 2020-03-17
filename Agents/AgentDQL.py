from Agents import IAgent
import numpy
import copy

from collections import deque
from keras.layers import Input, Dense, Flatten, Concatenate
from keras.models import Model
from keras.optimizers import Adam

from keras.models import load_model

import random

class AgentDQL(IAgent.IAgent):

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

    currentCorrectAction = 0

    totalCorrectAction = []

    totalAction = []
    totalActionPerGame = 0

    def __init__(self, params=[]):
        self.training = params[0]
        self.name = "DQL"
        pass


    def startAgent(self, params=[]):
        numMaxCards, numCardsPerPlayer, actionNumber, loadModel, agentParams = params

        self.numMaxCards = numMaxCards
        self.numCardsPerPlayer = numCardsPerPlayer
        self.outputSize = actionNumber  # all the possible ways to play cards plus the pass action

        if len(agentParams) > 1:

            self.hiddenLayers, self.hiddenUnits, QSize, self.batchSize, self.targetUpdateFrequency = agentParams

        else:

            #    space = hp.choice('a',
            #           [
            #               (hp.choice("layers", [1, 2, 3, 4]), hp.choice("hiddenUnits", [8, 32, 64, 256]),
            #                hp.choice("Qsize", [500, 1000 , 2500, 5000]),
            #                hp.choice("batchSize", [16, 64, 128, 256, 512]),
            #                hp.choice("TargetUpdateFunction", [16, 64, 128, 256, 512]),
            #               )
            #           ])

            #Best Hyperopt:{'Qsize': 1000, 'TargetUpdateFunction': 256, 'a': 0, 'batchSize': 256, 'hiddenUnits': 256, 'layers': 3}
            #(3, 256, 1000, 256, 256)
            self.hiddenLayers = 3
            self.hiddenUnits = 256
            self.batchSize = 256
            QSize = 1000
            self.targetUpdateFrequency = 256

            #My initial estimation
            # self.hiddenLayers = 1
            # self.hiddenUnits = 32
            # self.batchSize = 256
            # QSize = 1000
            # self.targetUpdateFrequency = 100

        self.gamma = 0.95  # discount rate
        self.outputActivation = "softmax"
        self.loss = "mse"

        # self.epsilon_min = 0.1
        # self.epsilon_decay = 0.995
        # self.epsilon = 1.0 # exploration rate



        self.memory = deque(maxlen=QSize)
        self.learning_rate = 0.001

        if loadModel == "":
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

        # dense = Dense(self.hiddenLayers, activation="relu", name="dense_0")(inputLayer)
        for i in range(self.hiddenLayers+1):
            if i == 0:
                previous = inputLayer
            else:
                previous = dense

            dense = Dense(self.hiddenUnits*(i+1), name="Dense"+str(i), activation="relu")(previous)

        outputActor = Dense(self.outputSize, activation=self.outputActivation)(
            dense)  # Cards at the player hand plus the pass action

        return  Model(inputs=[inputLayer], outputs=[outputActor])


    def getAction(self, params):

        # stateVector, possibleActionsOriginal = params
        # possibleActions = copy.copy(possibleActionsOriginal)
        #
        # # possibleActions[199] = 0
        # # trials = 0
        #
        # if numpy.random.rand() <= self.epsilon:
        #
        #     aIndex = numpy.random.randint(0, self.outputSize)
        #
        #     a = numpy.zeros(self.outputSize)
        #
        # else:
        #     # possibleActions = numpy.expand_dims(numpy.array(possibleActions), 0)
        #     stateVector = numpy.expand_dims(numpy.array(stateVector), 0)
        #     # a = self.online_network.predict([stateVector, possibleActions])[0]
        #     a = self.online_network.predict([stateVector])[0]
        #     aIndex = numpy.argmax(a)
        #
        # if possibleActions[aIndex] == 0:
        #     itemindex = numpy.where(numpy.array(possibleActions) == 1)
        #     numpy.random.shuffle(itemindex)
        #
        #     aIndex = itemindex[0]
        #     a[aIndex] = 1

        stateVector, possibleActionsOriginal = params
        stateVector = numpy.expand_dims(numpy.array(stateVector), 0)

        possibleActions = copy.copy(possibleActionsOriginal)

        prediction = self.online_network.predict([stateVector])[0]
        aIndex = numpy.argmax(prediction)
        a = prediction

        if possibleActions[aIndex] == 0:
            a = numpy.zeros(self.outputSize)
            aIndex = numpy.random.choice(numpy.arange(self.outputSize), 1, p=prediction)[0]
            a[aIndex] = 1

            if possibleActions[aIndex] == 0:
                itemindex = numpy.where(numpy.array(possibleActions) == 1)
                numpy.random.shuffle(itemindex)
                aIndex = itemindex[0]
                a = numpy.zeros(self.outputSize)
                a[aIndex] = 1
            else:
                # print ("Correct action!")
                self.currentCorrectAction = self.currentCorrectAction + 1
        else:
            self.currentCorrectAction = self.currentCorrectAction+1

        self.totalActionPerGame = self.totalActionPerGame+1
        return a



    def loadModel(self, model):
        self.online_network  = load_model(model)
        self.targetNetwork = load_model(model)


    def updateTargetNetwork(self):

        self.online_network.set_weights(self.online_network.get_weights())


    def updateModel(self, savedNetwork, game):

        minibatch = random.sample(self.memory, self.batchSize)
        ts = 0
        for state, action, reward, next_state, done, possibleActions in minibatch:
            ts = ts + 1
            # print ("--Training " + str(ts))
            target = reward
            if not done:
                # nextQValue = self.targetNetwork.predict([next_state, possibleActions])[0]
                nextQValue = self.targetNetwork.predict([next_state])[0]
                target = (reward + self.gamma * numpy.amax(nextQValue))

            # target_f = self.online_network.predict([state, possibleActions])
            target_f = self.online_network.predict([state])
            target_f[0][action] = target
            # self.online_network.fit([state,possibleActions], target_f, epochs=1, verbose=False)
            self.online_network.fit([state], target_f, epochs=1, verbose=False)
            # self.trainingStep += 1

            if ts % self.targetUpdateFrequency == 0:
                self.updateTargetNetwork()


        self.updateTargetNetwork() # to guarantee that it updates at least once per game

        # if self.epsilon > self.epsilon_min:
        #     self.epsilon *= self.epsilon_decay

        if (game + 1) % 100 == 0:
            self.online_network.save(savedNetwork + "/actor_iteration_" + str(game) + ".hd5")
            self.lastModel = savedNetwork + "/actor_iteration_" + str(game) + ".hd5"


    trainTime = 0
    def train(self, params=[]):

        state, action, reward, next_state, done, savedNetwork, game, possibleActions = params

        if done:
            self.totalCorrectAction.append(self.currentCorrectAction)
            self.totalAction.append(self.totalActionPerGame)

            self.currentCorrectAction = 0
            self.totalActionPerGame = 0

        if self.training:
            #memorize


            action = numpy.argmax(action)
            state = numpy.expand_dims(numpy.array(state), 0)
            next_state = numpy.expand_dims(numpy.array(next_state), 0)
            possibleActions = numpy.expand_dims(numpy.array(possibleActions), 0)

            self.memory.append((state, action, reward, next_state, done, possibleActions))

            if len(self.memory) > self.batchSize and done:
                self.trainTime = self.trainTime + 1
                self.updateModel(savedNetwork, game)



