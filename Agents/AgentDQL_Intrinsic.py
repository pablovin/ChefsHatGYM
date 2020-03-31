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

    losses = []
    Probability = []

    SelectedActions = []


    def __init__(self, params=[]):
        self.training = params[0]
        self.initialEpsilon = params[1]
        self.name = "DQL"

        self.totalAction = []
        self.totalActionPerGame = 0

        self.currentCorrectAction = 0

        self.totalCorrectAction = []
        losses = []


    def startAgent(self, params=[]):
        numMaxCards, numCardsPerPlayer, actionNumber, loadModel, agentParams = params

        self.numMaxCards = numMaxCards
        self.numCardsPerPlayer = numCardsPerPlayer
        self.outputSize = actionNumber  # all the possible ways to play cards plus the pass action

        if len(agentParams) > 1:

            self.hiddenLayers, self.hiddenUnits, self.batchSize,  self.tau = agentParams

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

            # BEst: (1, 256, 128, 0.5217984836612634)
            # Best: {'a': 0, 'batchSize': 2, 'hiddenUnits': 3, 'layers': 0, 'tau': 0.5217984836612634}
            # avg
            # best
            # error: 0.9378571428571428

            self.hiddenLayers = 1
            self.hiddenUnits = 256
            self.batchSize = 128
            self.tau = 0.52  # target network update rate



            # #My initial estimation
            # self.hiddenLayers = 1
            # self.hiddenUnits = 256
            # self.batchSize = 256
            # self.tau = 0.1  # target network update rate


            # QSize = 1000
            # self.targetUpdateFrequency = 100

        self.gamma = 0.95  # discount rate
        # self.gamma = 0.1  # epirobTesting
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

        self.learning_rate = 0.001

        if loadModel == "":
            self.buildModel()
        else:
            self.loadModel(loadModel)

        self.losses = []

        self.QValues = []

        self.Probability = []

        self.SelectedActions = []


    def buildModel(self):

          self.buildSimpleModel()

          self.online_network.compile(loss=self.loss, optimizer=Adam(lr=self.learning_rate), metrics=["mse"])

          self.targetNetwork.compile(loss=self.loss, optimizer=Adam(lr=self.learning_rate), metrics=["mse"])

          # self.successNetwork.compile(loss=self.loss, optimizer=Adam(lr=self.learning_rate), metrics=["mse"])

    def buildSimpleModel(self):

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



        self.online_network = model()
        self.targetNetwork =  model()
        self.loadQValueReader()
        # self.successNetwork = Model([inputLayer, possibleActions], probOutput)


    def calculateProbabilityOfSuccess(self, QValue):
        theta = 0.0
        maxreward = 1
        probability = (1-theta) * (1/2*numpy.log10(QValue/maxreward)+1)

        if probability <= 0:
            probability = 0
        if probability >= 1:
            probability =1

        return probability


    def loadQValueReader(self):
        softmaxLayer = self.online_network.get_layer(index=-2)
        self.QValueReader = Model(self.online_network.inputs, softmaxLayer.output)

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
            a = self.online_network.predict([stateVector, possibleActionsVector])[0]
            aIndex = numpy.argmax(a)
            #
            # self.online_network.summary()
            qvalues = self.QValueReader.predict([stateVector, possibleActionsVector])[0]

            # nonzeros = numpy.nonzero(qvalues)
            nonzeros = numpy.array(numpy.where(numpy.array(qvalues))>= 0.1)[0].tolist()
            nonzerosA = numpy.copy(a[nonzeros,])

            while len(nonzerosA) < 10:
                nonzerosA = numpy.append(nonzerosA, 0)

            def softmax(x):
                """Compute softmax values for each sets of scores in x."""
                e_x = numpy.exp(x - numpy.max(x))
                return e_x / e_x.sum(axis=0)  # only difference

            # aSort = numpy.sort(a)
            # aSortShort = aSort
            softMaxA = numpy.array(softmax(nonzerosA))
            argSoftMax = numpy.argmax(softMaxA)
            # print ("AIndex: "  + str(aIndex) + "("+str(a[aIndex]) + " - SoftmaxA: " + str(softMaxA[argSoftMax])+")")

            self.QValues.append(softMaxA)

            self.Probability.append(self.calculateProbabilityOfSuccess(qvalues[aIndex]))

            # self.SelectedActions.append(aIndex)

            # self.QValues.append(a)

            if possibleActionsOriginal[aIndex] == 1:
                self.currentCorrectAction = self.currentCorrectAction + 1


        self.totalActionPerGame = self.totalActionPerGame + 1
        return a

    def loadModel(self, model):
        self.online_network  = load_model(model)
        self.targetNetwork = load_model(model)
        self.loadQValueReader()


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

            if (self.prioritized_experience_replay):
                # Update PER Sum Tree
                self.memory.update(idx[i], abs(old_q - q[i, a[i]]))


        # Train on batch
        history = self.online_network.fit([s,possibleActions] , q, verbose=False)
        self.losses.append(history.history['loss'])

        #Update the decay
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        if (game + 1) % 1000 == 0:
            self.online_network.save(savedNetwork + "/actor_iteration_" + str(game) + "_Player_"+str(thisPlayer)+".hd5")
            self.lastModel = savedNetwork + "/actor_iteration_" + str(game) + "_Player_"+str(thisPlayer)+".hd5"


        print (" -- Epsilon:" + str(self.epsilon) + " - Loss:" + str(history.history['loss']))


    def memorize(self, state, action, reward, next_state, done, possibleActions, newPossibleActions):

        if (self.prioritized_experience_replay):
            state = numpy.expand_dims(numpy.array(state), 0)
            next_state = numpy.expand_dims(numpy.array(next_state), 0)
            q_val = self.online_network.predict(state)
            q_val_t = self.targetNetwork.predict(next_state)
            next_best_action = numpy.argmax(q_val)
            new_val = reward + self.gamma * q_val_t[0, next_best_action]
            td_error = abs(new_val - q_val)[0]
        else:
            td_error = 0

        self.memory.memorize(state, action, reward, done, next_state, possibleActions, newPossibleActions, td_error)


    def train(self, params=[]):

        state, action, reward, next_state, done, savedNetwork, game, possibleActions, newPossibleActions, thisPlayer = params

        if done:
            self.totalCorrectAction.append(self.currentCorrectAction)
            self.totalAction.append(self.totalActionPerGame)

            self.currentCorrectAction = 0
            self.totalActionPerGame = 0

        if self.training:
            #memorize
            action = numpy.argmax(action)
            # state = numpy.expand_dims(numpy.array(state), 0)
            # next_state = numpy.expand_dims(numpy.array(next_state), 0)
            # possibleActions = numpy.expand_dims(numpy.array(possibleActions), 0)

            self.memorize(state, action, reward, next_state, done, possibleActions, newPossibleActions)

            #
            # self.memory.append((state, action, reward, next_state, done, possibleActions))

            if self.memory.size() > self.batchSize and done:
                self.updateModel(savedNetwork, game, thisPlayer)
                self.updateTargetNetwork()




