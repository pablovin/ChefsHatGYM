#Adapted from: https://github.com/germain-hug/Deep-RL-Keras


from Agents import IAgent
import numpy
import copy

from collections import deque
from keras.layers import Input, Dense, Flatten, Concatenate, Multiply
from keras.models import Model
from keras.optimizers import Adam
from keras.optimizers import RMSprop

import keras.backend as K

from keras.models import load_model

import tensorflow.compat.v1 as tfc

import random

def actorLoss():

    def loss(y_true, y_pred):

        y_tru_valid = y_true[:, 0:200]
        advantage = y_true[:, 200][0]

        weighted_actions = K.sum(y_tru_valid * y_pred, axis=0)
        eligibility = -tfc.log(weighted_actions + 1e-5) * advantage
        entropy = K.sum(y_pred * K.log(y_pred + 1e-10), axis=1)
        return K.mean(0.001 * entropy - K.sum(eligibility))

    return loss


class AgentA2C(IAgent.IAgent):

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

        if len(params) > 2:
            agentName = "_" + params[2]
        else:
            agentName = ""

        if len(params) > 3:
            self.intrinsic = params[3]
        else:
            self.intrinsic = None

        self.name = "A2C" + agentName


        self.totalAction = []
        self.totalActionPerGame = 0

        self.currentCorrectAction = 0

        self.totalCorrectAction = []


    def startAgent(self, params=[]):
        numMaxCards, numCardsPerPlayer, actionNumber, loadModel, agentParams = params

        self.numMaxCards = numMaxCards
        self.numCardsPerPlayer = numCardsPerPlayer
        self.outputSize = actionNumber  # all the possible ways to play cards plus the pass action

        if len(agentParams) > 1:

             self.hiddenLayers, self.hiddenUnits, self.gamma = agentParams

        else:

            # space = hp.choice('a',
            #                   [
            #                       (hp.choice("layers", [1, 2, 3, 4]), hp.choice("hiddenUnits", [8, 32, 64, 128, 256]),
            #                        hp.uniform("gamma", 0.01, 0.99),
            #                        )
            #                   ])
            #Hyperopt Best: Best:{'a': 0, 'gamma': 0.9450742180420258, 'hiddenUnits': 4, 'layers': 0}

            # BEst: (1, 64, 0.24343370808558662)
            # Best: {'a': 0, 'gamma': 0.24343370808558662, 'hiddenUnits': 2, 'layers': 0}
            # avg
            # best
            # error: 65.0


            # self.hiddenLayers = 1
            # self.hiddenUnits = 64
            # self.gamma = 0.24 # discount rate


            #My Estimation
            self.hiddenLayers = 2
            self.hiddenUnits = 64
            self.gamma = 0.95  # discount rate


        self.outputActivation = "linear"
        self.loss = "mse"


        self.memory = []

        #Game memory
        self.states = []
        self.actions = []
        self.rewards = []
        self.possibleActions = []

        self.losses = []
        self.QValues = []

        self.learning_rate = 0.001

        if self.training:
            self.epsilon = self.initialEpsilon  # exploration rate while training
        else:
            self.epsilon = 0.0 #no exploration while testing

        self.epsilon_min = 0.1
        self.epsilon_decay = 0.990

        if loadModel == "":
            self.buildModel()
        else:
            # print ("loading from:" + str(loadModel))
            self.loadModel(loadModel)

        self.MeanQValuesPerGame = []
        self.currentGameQValues = []


    def buildModel(self):

        inputSize = self.numCardsPerPlayer + self.numMaxCards
        #shared part of the model
        inp = Input((inputSize, ), name="State")
        # dense1= Dense(64, activation='relu', name="dense_1")(inp)
        # dense2 = Dense(128, activation='relu', name="dense_2")(dense1)

        for i in range(self.hiddenLayers + 1):
            if i == 0:
                previous = inp
            else:
                previous = dense

            dense = Dense(self.hiddenUnits * (i + 1), name="Dense" + str(i), activation="relu")(previous)

        #Actor network
        densea1 = Dense(128, activation='relu', name="actor_dense_3")(dense)

        outActor = Dense(self.outputSize, activation='softmax', name="Actor_output")(densea1)

        possibleActions = Input(shape=(self.outputSize,),
                                name="PossivleActions")
        outputPossibleActor = Multiply()([possibleActions, outActor])

        #Critic network
        densec1 = Dense(128, activation='relu', name="critic_dense_3")(dense)
        outCritic = Dense(1, activation='linear', name="critic_Output")(densec1)


        #build networks
        self.critic = Model(inp, outCritic)
        self.actor = Model([inp,possibleActions] , outputPossibleActor)
        #
        # self.actor.compile(optimizer=Adam(lr=self.learning_rate),
        #               loss=[actorLoss()])
        #get optmizers
        self.getOptmizers()

        self.loadQValueReader()




    def getOptmizers(self):

        # rmsOptmizer = RMSprop(lr=self.learning_rate, epsilon=0.1, rho=0.99)
        rmsOptmizer = Adam(lr=self.learning_rate)

        #optmizers

        #optmizer actor

        """ Actor Optimization: Advantages + Entropy term to encourage exploration
                (Cf. https://arxiv.org/abs/1602.01783)
                """

        action_pl= K.placeholder(shape=(None, self.outputSize))
        advantage_pl = K.placeholder(shape=(None,))
        k_constants = K.variable(0)

        weighted_actions = K.sum(action_pl * self.actor.output, axis=0)
        eligibility = -tfc.log(weighted_actions + 1e-5) * advantage_pl
        entropy = K.sum(self.actor.output * K.log(self.actor.output + 1e-10), axis=1)
        loss = 0.001 * entropy - K.sum(eligibility)

        updates = rmsOptmizer.get_updates(self.actor.trainable_weights, [], loss)

        self.actorOptmizer = K.function([self.actor.input, action_pl, advantage_pl], loss, updates=updates)


        #Critic optmizer

        """ Critic Optimization: Mean Squared Error over discounted rewards
                """

        discounted_r = K.placeholder(shape=(None,))
        critic_loss = K.mean(K.square(discounted_r - self.critic.output))
        updates = rmsOptmizer.get_updates(self.critic.trainable_weights, [], critic_loss)
        self.criticOptmizer = K.function([self.critic.input, discounted_r], critic_loss, updates=updates)

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

            self.currentGameQValues.append(0)

        else:
            # if numpy.sum(possibleActions2) > 1:
            #     possibleActions2[199] = 0

            possibleActionsVector = numpy.expand_dims(numpy.array(possibleActions2), 0)
            a = self.actor.predict([stateVector, possibleActionsVector])[0]
            aIndex = numpy.argmax(a)

            qvalues = self.QValueReader.predict([stateVector, possibleActionsVector])[0]

            # def softmax(x):
            #     """Compute softmax values for each sets of scores in x."""
            #     e_x = numpy.exp(x - numpy.max(x))
            #     return e_x / e_x.sum(axis=0)  # only difference
            #     # aSort = numpy.sort(a)
            #     # aSortShort = aSort
            #
            # softMaxA = softmax(numpy.sort(a))
            #
            # argSoftMax = numpy.argmax(softMaxA)
            # print("AIndex: " + str(a[aIndex]) + " - SoftmaxA: " + str(softMaxA[argSoftMax]))

            self.QValues.append(a)
            self.currentGameQValues.append(numpy.sum(a))
            #
            # if not self.intrinsic == None:
            #     self.intrinsic.doSelfAction(a, params)

            if possibleActionsOriginal[aIndex] == 1:
                self.currentCorrectAction = self.currentCorrectAction + 1
            else:
                a = numpy.zeros(self.outputSize)
                a[-1] = 1

        self.totalActionPerGame = self.totalActionPerGame + 1
        return a



    def discount(self, r):
        """ Compute the gamma-discounted rewards over an episode
        """
        discounted_r, cumul_r = numpy.zeros_like(r), 0
        for t in reversed(range(0, len(r))):
            cumul_r = r[t] + cumul_r * self.gamma
            discounted_r[t] = cumul_r
        return discounted_r


    def loadModel(self, model):
        actorModel, criticModel = model
        self.actor  = load_model(actorModel)
        self.critic = load_model(criticModel)
        self.getOptmizers()
        self.loadQValueReader()






    def updateModel(self, savedNetwork, game, thisPlayer):

        # print ("Updating the model!")
        self.memory = numpy.array(self.memory)
        # print ("self.memory: " + str(self.memory.shape))

        state =  numpy.array(self.states)
        action = self.actions
        reward = self.rewards
        possibleActions = numpy.array(self.possibleActions)
        #
        #
        # state, action, reward, done = self.memory[:, 0], self.memory[:, 1], self.memory[:, 2], self.memory[:, 3]
        # print ("Shape state:", state[0].shape)

        # Compute discounted rewards and Advantage (TD. Error)
        discounted_rewards = self.discount(reward)
        state_values = self.critic.predict(numpy.array(state))
        advantages = discounted_rewards - numpy.reshape(state_values, len(state_values))

        # newAction = []
        # for index, h in enumerate(action):
        #     hlist = h.tolist()
        #     hlist.append(advantages[index])
        #     newAction.append(numpy.array(hlist))
        #
        # newAction = numpy.array(newAction)
        #     # h.tolist().append(advantages[index])
        #
        # # # Networks optimization
        # # flattenActions = numpy.array(action).flatten()
        #
        # # concatenatedYTrue = numpy.concatenate((flattenActions,advantages))
        # # actions = y_true[0:200]
        # # advantages = y_true[200:]
        #
        # historyA = self.actor.fit([state, possibleActions], newAction, verbose=False)
        # self.losses.append(historyA.history['loss'])
        #
        #
        # historyC = self.critic.fit(state , discounted_rewards,  verbose=False)
        # self.losses.append(historyC.history['loss'])


        # actions = []
        # for i in range(len(action)):
        #     # print ("Action:" + str(action[i]))
        #     # concatenated = numpy.concatenate((action[i], numpy.zeros(numpy.array(action[i].shape))))
        #     advantage = numpy.zeros(numpy.array(action[i]).shape)
        #     advantage[0] = advantages[i]
        #     concatenated = numpy.concatenate((action[i], advantage))
        #     actions.append(concatenated)

        #
        # actorLoss = self.actor.train_on_batch([state, possibleActions], [actions])

        actorLoss = self.actorOptmizer([[state, possibleActions], action, advantages])

        actorLoss = numpy.average(actorLoss)

        criticLoss = self.criticOptmizer([state, discounted_rewards])

        criticLoss = numpy.mean(criticLoss)

        self.losses.append([actorLoss,criticLoss])

        # print ("Loss Critic:" + str(history.history['loss']))

        #Update the decay
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        #save model
        if (game + 1) % 1000 == 0:
            self.actor.save(savedNetwork + "/actor_iteration_" + str(game) + "_Player_"+str(thisPlayer)+".hd5")
            self.critic.save(savedNetwork + "/critic_iteration_"  + str(game) + "_Player_"+str(thisPlayer)+".hd5")
            self.lastModel = (savedNetwork + "/actor_iteration_" + str(game) + "_Player_"+str(thisPlayer)+".hd5", savedNetwork + "/critic_iteration_"  + str(game) + "_Player_"+str(thisPlayer)+".hd5")

        print(" -- Epsilon:" + str(self.epsilon) + " - ALoss:" + str(actorLoss) + " - " + "CLoss: " + str(criticLoss))

    def resetMemory (self):
        self.states = []
        self.actions = []
        self.rewards = []
        self.possibleActions = []


    def train(self, params=[]):

        state, action, reward, next_state, done, savedNetwork, game, possibleActions, newPossibleActions, thisPlayer, score = params

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


            # print ("train")
            #memorize

            # action = numpy.argmax(action)

            self.states.append(state)
            self.actions.append(action)
            self.rewards.append(reward)
            self.possibleActions.append(possibleActions)

            if done: # if a game is over for this player, train it.
                self.updateModel(savedNetwork, game, thisPlayer)
                self.resetMemory()




