#Adapted from: https://github.com/germain-hug/Deep-RL-Keras


from Agents import IAgent
import numpy
import copy

from collections import deque
from keras.layers import Input, Dense, Flatten, Concatenate
from keras.models import Model
from keras.optimizers import Adam
from keras.optimizers import RMSprop

import keras.backend as K

from keras.models import load_model

import random

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

    def __init__(self, params=[]):
        self.training = params[0]
        self.name = "A2C"
        pass


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
            self.hiddenLayers = 1
            self.hiddenUnits = 256
            self.gamma = 0.945  # discount rate

            #My Estimation
            # self.hiddenLayers = 2
            # self.hiddenUnits = 64
            # self.gamma = 0.99  # discount rate


        self.outputActivation = "linear"
        self.loss = "mse"


        self.memory = []
        self.learning_rate = 0.0001

        #Game memory
        self.states = []
        self.actions = []
        self.rewards = []



        if loadModel == "":
            self.buildModel()
        else:
            # print ("loading from:" + str(loadModel))
            self.loadModel(loadModel)


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

        #Critic network
        densec1 = Dense(128, activation='relu', name="critic_dense_3")(dense)
        outCritic = Dense(1, activation='linear', name="critic_Output")(densec1)


        #build networks
        self.critic = Model(inp, outCritic)
        self.actor = Model(inp, outActor)

        #get optmizers
        self.getOptmizers()

    def getOptmizers(self):
        rmsOptmizer = RMSprop(lr=self.learning_rate, epsilon=0.1, rho=0.99)

        #optmizers

        #optmizer actor

        """ Actor Optimization: Advantages + Entropy term to encourage exploration
                (Cf. https://arxiv.org/abs/1602.01783)
                """

        action_pl= K.placeholder(shape=(None, self.outputSize))
        advantage_pl = K.placeholder(shape=(None,))
        outputPlaceholder = K.placeholder(shape=(None,))
        k_constants = K.variable(0)

        weighted_actions = K.sum(action_pl * self.actor.output, axis=1)
        eligibility = K.log(weighted_actions + 1e-10) * K.stop_gradient(advantage_pl)
        entropy = K.sum(self.actor.output * K.log(self.actor.output + 1e-10), axis=1)
        loss = 0.001 * entropy - K.sum(eligibility)

        updates = rmsOptmizer.get_updates(self.actor.trainable_weights, [], loss)

        self.actorOptmizer = K.function([self.actor.input, action_pl, advantage_pl], k_constants, updates=updates)


        #Critic optmizer

        """ Critic Optimization: Mean Squared Error over discounted rewards
                """

        discounted_r = K.placeholder(shape=(None,))
        critic_loss = K.mean(K.square(discounted_r - self.critic.output))
        updates = rmsOptmizer.get_updates(self.critic.trainable_weights, [], critic_loss)
        self.criticOptmizer = K.function([self.critic.input, discounted_r], k_constants, updates=updates)


    def getAction(self, params):

        stateVector, possibleActionsOriginal = params
        stateVector = numpy.expand_dims(numpy.array(stateVector), 0)

        possibleActions = copy.copy(possibleActionsOriginal)

        prediction = self.actor.predict([stateVector])[0]
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
            self.currentCorrectAction = self.currentCorrectAction + 1

        self.totalActionPerGame = self.totalActionPerGame+1
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
        # print ("loading:" + str(model))
        # input("here")
        actorModel, criticModel = model
        self.actor  = load_model(actorModel)
        self.critic = load_model(criticModel)
        self.getOptmizers()


    def updateModel(self, savedNetwork, game):

        # print ("Updating the model!")
        self.memory = numpy.array(self.memory)
        # print ("self.memory: " + str(self.memory.shape))

        state =  numpy.array(self.states)
        action = self.actions
        reward = self.rewards
        #
        #
        # state, action, reward, done = self.memory[:, 0], self.memory[:, 1], self.memory[:, 2], self.memory[:, 3]
        # print ("Shape state:", state[0].shape)

        # Compute discounted rewards and Advantage (TD. Error)
        discounted_rewards = self.discount(reward)
        state_values = self.critic.predict(numpy.array(state))
        advantages = discounted_rewards - numpy.reshape(state_values, len(state_values))

        # Networks optimization
        self.actorOptmizer([state, action, advantages])
        self.criticOptmizer([state, discounted_rewards])

        # print ("train")

        if (game + 1) % 100 == 0:
            self.actor.save(savedNetwork + "/actor_iteration_" + str(game) + ".hd5")
            self.critic.save(savedNetwork + "/critic_iteration_" + str(game) + ".hd5")
            self.lastModel = (savedNetwork + "/actor_iteration_" + str(game) + ".hd5", savedNetwork + "/critic_iteration_" + str(game) + ".hd5")


    def resetMemory (self):
        self.states = []
        self.actions = []
        self.rewards = []


    def train(self, params=[]):

        state, action, reward, next_state, done, savedNetwork, game, possibleActions = params

        if done:
            self.totalCorrectAction.append(self.currentCorrectAction)
            self.totalAction.append(self.totalActionPerGame)

            self.currentCorrectAction = 0
            self.totalActionPerGame = 0

        if self.training:
            # print ("train")
            #memorize

            action = numpy.argmax(action)

            self.states.append(state)
            self.actions.append(action)
            self.rewards.append(reward)

            if done: # if a game is over for this player, train it.
                self.updateModel(savedNetwork, game)
                self.resetMemory()




