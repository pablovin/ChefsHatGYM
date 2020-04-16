from Agents import IAgent
import numpy
import copy

from collections import deque
from keras.layers import Input, Dense, Flatten, Concatenate, Lambda, Multiply, LeakyReLU, BatchNormalization
import keras.backend as K

from keras.models import Model
from keras.optimizers import Adam

from keras.models import load_model

from Agents import MemoryBuffer

import random

class AgentAIRL(IAgent.IAgent):

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

    SelectedActions = []

    intrinsic = None

    demonstrations = None

    selfReward = []
    currentReward = []
    meanReward = []

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

        if len(params) > 4:
            self.demonstrations = params[4]
        else:
            self.demonstrations = None

        self.name = "DQL"+agentName

        self.totalAction = []
        self.totalActionPerGame = 0

        self.currentCorrectAction = 0

        self.totalCorrectAction = []
        losses = []
        self.selfReward = []
        self.currentReward = []
        self.meanReward = []



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
          self.compileModels()

    def compileModels(self):
          self.actor.compile(loss=self.loss, optimizer=Adam(lr=self.learning_rate), metrics=["mse"])

          self.targetNetwork.compile(loss=self.loss, optimizer=Adam(lr=self.learning_rate), metrics=["mse"])

          self.rewardNetwork.compile(loss="binary_crossentropy", optimizer=Adam(lr=self.learning_rate), metrics=["mse"])


          # self.getOptmizer()
          # self.rewardNetworkcompile(loss='binary_crossentropy',
          #         optimizer=Adam(lr=self.learning_rate),
          #         metrics=['accuracy'])

          space = Input(shape=(28,))
          possibleAction = Input(shape=(200,))
          inputSelfReward = Input(shape=(228,))

          self.actor.trainable = False
          action = self.actor([space, possibleAction])

          concat = Concatenate()([space,action])

          self.combined = Model([space,possibleAction], self.rewardNetwork(concat))
          self.combinedDemonstrator = Model([inputSelfReward], self.rewardNetwork(inputSelfReward))


          self.combined.compile(loss='binary_crossentropy', optimizer=Adam(lr=self.learning_rate))
          self.combinedDemonstrator.compile(loss='binary_crossentropy', optimizer=Adam(lr=self.learning_rate))
          #
          # self.successNetwork.compile(loss=self.loss, optimizer=Adam(lr=self.learning_rate), metrics=["mse"])

    def buildSimpleModel(self):

        """ Build Deep Q-Network
               """

        def modelQValue():
            inputSize = self.numCardsPerPlayer + self.numMaxCards
            inputLayer = Input(shape=(28,),
                               name="State")  # 5 cards in the player's hand + maximum 4 cards in current board

            # dense = Dense(self.hiddenLayers, activation="relu", name="dense_0")(inputLayer)
            for i in range(self.hiddenLayers + 1):

                if i == 0:
                    previous = inputLayer
                else:
                  previous = dense

                dense = Dense(self.hiddenUnits * (i + 1), name="Dense" + str(i))(previous)
                dense = LeakyReLU()(dense)

            if (self.dueling):
                # Have the network estimate the Advantage function as an intermediate layer
                dense = Dense(self.outputSize + 1,  name="duelingNetwork")(dense)
                dense = LeakyReLU()(dense)
                dense = Lambda(lambda i: K.expand_dims(i[:, 0], -1) + i[:, 1:] - K.mean(i[:, 1:], keepdims=True),
                           output_shape=(self.outputSize,))(dense)



            possibleActions = Input(shape=(self.outputSize,),
                       name="PossibleAction")


            dense = Dense(self.outputSize, activation='softmax')(dense)
            output = Multiply()([possibleActions, dense])

            # probOutput =  Dense(self.outputSize, activation='softmax')(dense)

            return Model([inputLayer, possibleActions], output)

        def modelReward():
            inputSize = self.numCardsPerPlayer + self.numMaxCards
            inputLayer = Input(shape=(228,),
                               name="RewardInput")  # 5 cards in the player's hand + maximum 4 cards in current board

            dense = Dense(256, name="Dense" + str(0))(inputLayer)
            dense = LeakyReLU()(dense)
            # dense = Dense(256, name="Dense" + str(1), activation="relu")(dense)


            dense = Dense(1, activation='tanh')(dense)

            # probOutput =  Dense(self.outputSize, activation='softmax')(dense)

            return Model([inputLayer], dense)

        self.actor = modelQValue()
        self.targetNetwork =  modelQValue()
        self.rewardNetwork = modelReward()

        self.loadQValueReader()

    def getOptmizer(self):

        adamOptmizer = Adam(lr=self.learning_rate)

        state = K.placeholder(shape=(None, 28))
        nextState = K.placeholder(shape=(None, 28))
        actionProb =  K.placeholder(shape=(None, 200))

        state_d = K.placeholder(shape=(None, 28))
        nextState_d = K.placeholder(shape=(None, 28))
        actionProb_d =  K.placeholder(shape=(None, 200))

        gamma =  K.variable(self.gamma)

        stateValues = K.function([self.actor.input], self.actor.output)
        rewardValue = K.function([self.rewardNetwork.input], self.rewardNetwork.output)

        reward = rewardValue(state)
        stateValue = stateValues(state)
        nextStateValue = stateValue(nextState)

        reward_d = rewardValue(state_d)
        stateValue_d = stateValues(state_d)
        nextStateValue_d = stateValue(nextState_d)

        logits = reward + gamma * nextStateValue - stateValue - actionProb
        logits_d = reward_d+gamma*nextStateValue_d - stateValue_d - actionProb_d

        loss = K.mean(K.softplus(-(logits))) + K.mean(K.softplus((logits_d)))

        updatesOnline = adamOptmizer.get_updates(self.actor.trainable_weights, [], loss)
        updatesReward = adamOptmizer.get_updates(self.rewardNetwork.trainable_weights, [], loss)

        self.updateOnline = K.function([state, nextState, actionProb, state_d,nextState_d,actionProb_d], loss, updates=updatesOnline)
        self.updateReward = K.function([state, nextState, actionProb, state_d, nextState_d, actionProb_d], loss,
                                       updates=updatesReward)



    def loadQValueReader(self):
        softmaxLayer = self.actor.get_layer(index=-2)
        self.QValueReader = Model(self.actor.inputs, softmaxLayer.output)



    def observeOponentAction(self, params):
        self.intrinsic.observeOponentAction(params, self.actor)

    def getAction(self, params):

        state, possibleActionsOriginal = params
        stateVector = numpy.expand_dims(numpy.array(state), 0)

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


            # if not self.intrinsic == None:
            #     self.intrinsic.doSelfAction(a, params)

            #Update QValues
            self.QValues.append(a)
            self.currentGameQValues.append(numpy.sum(a))

            if possibleActionsOriginal[aIndex] == 1:
                self.currentCorrectAction = self.currentCorrectAction + 1

        rewardShape = numpy.concatenate([state,a])
        rewardShape = numpy.expand_dims(numpy.array(rewardShape), 0)
        reward = self.rewardNetwork.predict([rewardShape])[0][0]
        self.currentReward.append(reward)
        self.selfReward.append(reward)

        self.totalActionPerGame = self.totalActionPerGame + 1
        return a

    def loadModel(self, model):

        onlineModel,rewardModel = model
        self.rewardNetwork = load_model(rewardModel)
        self.actor  = load_model(onlineModel)
        self.targetNetwork = load_model(onlineModel)
        self.loadQValueReader()
        self.compileModels()


    def updateTargetNetwork(self):

        W = self.actor.get_weights()
        tgt_W = self.targetNetwork.get_weights()
        for i in range(len(W)):
            tgt_W[i] = self.tau * W[i] + (1 - self.tau) * tgt_W[i]
        self.targetNetwork.set_weights(tgt_W)

        #
        # self.actor.set_weights(self.actor.get_weights())


    def updateModel(self, savedNetwork, game, thisPlayer):

        """ Train Q-network on batch sampled from the buffer
                """
        # Sample experience from memory buffer (optionally with PER)
        s, a, r, d, new_s, possibleActions, newPossibleActions, idx = self.memory.sample_batch(self.batchSize)


        batchIndex = numpy.array(range(len(self.demonstrations[0])))
        random.shuffle(batchIndex)
        batchIndex = batchIndex[0:self.batchSize]

        d_s = self.demonstrations[0][batchIndex]
        d_a = self.demonstrations[1][batchIndex]
        d_r = self.demonstrations[2][batchIndex]
        d_d = self.demonstrations[3][batchIndex]
        d_new_s = self.demonstrations[4][batchIndex]
        d_possibleActions = self.demonstrations[5][batchIndex]
        d_newPossibleActions = self.demonstrations[6][batchIndex]
        # d_idx = self.demonstrations[7][batchIndex]

        # d_s, d_a, d_r, d_d, d_new_s, d_possibleActions, d_newPossibleActions, d_idx = self.demonstrations[0:7,batchIndex]
        #
        # lossOnline = self.updateOnline([s, new_s, a, d_s,d_new_s,d_a])
        # lossReward = self.updateReward([s, new_s, a, d_s,d_new_s,d_a])
        #
        # self.losses.append([numpy.mean(lossOnline), numpy.mean(lossReward)])
        #
        # if (game + 1) % 1000 == 0:
        #     self.actor.save(savedNetwork + "/actor_iteration_" + str(game) + "_Player_"+str(thisPlayer)+".hd5")
        #     self.lastModel = savedNetwork + "/actor_iteration_" + str(game) + "_Player_"+str(thisPlayer)+".hd5"
        #
        #
        # print (" -- E:" + str(self.epsilon) + " - Lp:" + str(numpy.mean(lossOnline)) + " - Lr" + str(numpy.mean(lossReward)))


        """
        Policy network generate trajectories
        """

        self.actor.trainable = False

        #Train on real data
        lossReward1 = self.combined.train_on_batch([s,possibleActions], numpy.ones(self.batchSize))

        #Train on demonstrator data
        d_action = numpy.zeros((self.batchSize,200))
        for x in range(self.batchSize):
            d_action[x][d_a[x]] = 1

        featureInput = numpy.concatenate([d_s,d_action], axis=1)

        lossReward2 = self.combinedDemonstrator.train_on_batch([featureInput], numpy.zeros(self.batchSize))

        lossReward = 0.5*(lossReward1+lossReward2)

        #
        #
        # """
        # Obtain policy network outputs of current batch
        # """
        #
        # Apply Bellman Equation on batch samples to train our DDQN

        action = numpy.zeros((self.batchSize,200))
        for x in range(self.batchSize):
            action[x][a[x]] = 1

        featureInput = numpy.concatenate([s,action], axis=1)

        new_r = self.rewardNetwork.predict([featureInput])
        q = self.actor.predict([s, possibleActions])
        next_q = self.actor.predict([new_s, newPossibleActions])
        q_targ = self.targetNetwork.predict([new_s, newPossibleActions])

        # self.successNetwork.compile(loss=self.loss, optimizer=Adam(lr=self.learning_rate), metrics=["mse"])

        for i in range(s.shape[0]):
            if d[i]:
                q[i, a[i]] = new_r[i]
            else:
                next_best_action = numpy.argmax(next_q[i, :])
                q[i, a[i]] = new_r[i] + self.gamma * q_targ[i, next_best_action]


        # # Train on policy batch with new reward
        self.actor.trainable = True
        lossPolicy = self.actor.train_on_batch([s, possibleActions], q)[0]
        # lossReward2 = self.rewardNetwork.train_on_batch([d_s], numpy.ones(self.batchSize))
        #
        # lossPolicy = 0.5*(lossPolicy1+lossPolicy2)
        # lossReward = 0.5*(lossReward1+lossReward2)
        self.losses.append([lossPolicy,lossReward])

        if (game + 1) % 1000 == 0:
            self.actor.save(savedNetwork + "/actor_iteration_" + str(game) + "_Player_"+str(thisPlayer)+".hd5")
            self.rewardNetwork.save(
                savedNetwork + "/reward_iteration_" + str(game) + "_Player_" + str(thisPlayer) + ".hd5")
            self.lastModel = savedNetwork + "/actor_iteration_" + str(game) + "_Player_"+str(thisPlayer)+".hd5"


        print (" -- E:" + str(self.epsilon) + " - Lp:" + str(lossPolicy) + " - Lr" + str(lossReward))



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

        if done:

            meanRewardTHisGame = numpy.average(self.currentReward)
            self.meanReward.append(meanRewardTHisGame)
            self.currentReward = []


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

            #memorize
            action = numpy.argmax(action)
            # state = numpy.expand_dims(numpy.array(state), 0)
            # next_state = numpy.expand_dims(numpy.array(next_state), 0)
            # possibleActions = numpy.expand_dims(numpy.array(possibleActions), 0)

            self.memorize(state, action, reward, next_state, done, possibleActions, newPossibleActions)

            #
            # self.memory.append((state, action, reward, next_state, done, possibleActions))

            # if self.memory.size() > self.batchSize:
            if self.memory.size() > self.batchSize and done:
                self.updateModel(savedNetwork, game, thisPlayer)
                self.updateTargetNetwork()

                # Update the decay
                if self.epsilon > self.epsilon_min:
                    self.epsilon *= self.epsilon_decay





