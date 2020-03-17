#Adapted from: https://github.com/germain-hug/Deep-RL-Keras


from Agents import IAgent
import numpy
import copy

from collections import deque
from keras.layers import Input, Dense, Flatten, Concatenate
from keras.models import Model
from keras.optimizers import Adam
from keras.optimizers import RMSprop
import tensorflow as tf

import keras.backend as K

from keras.models import load_model

import random

class AgentDDPG(IAgent.IAgent):

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
        self.name = "DDPG"
        pass


    def startAgent(self, params=[]):
        numMaxCards, numCardsPerPlayer, actionNumber, loadModel, agentParams = params

        self.numMaxCards = numMaxCards
        self.numCardsPerPlayer = numCardsPerPlayer
        self.outputSize = actionNumber  # all the possible ways to play cards plus the pass action

        if len(agentParams) > 1:

            self.hiddenLayers, self.hiddenUnits, self.gamma, self.tau, self.batchSize  = agentParams

        else:

            self.hiddenLayers = 1
            self.hiddenUnits = 32
            self.batchSize = 256
            self.gamma = 0.99  # discount rate
            self.tau = 0.01 # Weight transfer rate


        self.learning_rate = 0.0001
        #Game memory
        self.memory = deque(maxlen=5000)

        if loadModel == "":
            self.buildModel()
        else:
            self.loadModel(loadModel)

    def buildActorNetwork(self):

        inputSize = self.numCardsPerPlayer + self.numMaxCards
        inp = Input((inputSize,), name="Actor_State")

        for i in range(self.hiddenLayers + 1):
            if i == 0:
                previous = inp
            else:
                previous = dense

            dense = Dense(self.hiddenUnits * (i + 1), name="Actor_Dense" + str(i), activation="relu")(previous)


        outputActor = Dense(self.outputSize, activation='softmax', name="actor_output")(dense)

        self.actor = Model(inp,outputActor)

        inputSize = self.numCardsPerPlayer + self.numMaxCards
        inp = Input((inputSize,), name="Actor_State")

        for i in range(self.hiddenLayers + 1):
            if i == 0:
                previous = inp
            else:
                previous = dense

            dense = Dense(self.hiddenUnits * (i + 1), name="Actor_Dense" + str(i), activation="relu")(previous)


        outputActor = Dense(self.outputSize, activation='softmax', name="actor_output")(dense)

        self.actorTarget = Model(inp,outputActor)

        #actor optmizer
        # action_gdts = K.placeholder(shape=(None, self.outputSize))
        # params_grad = tf.gradients(self.actor.output, self.actor.trainable_weights, -action_gdts)
        # grads = zip(params_grad, self.actor.trainable_weights)
        # self.actorOptmizer = K.function([self.actor.input, action_gdts], [tf.train.AdamOptimizer(self.learning_rate).apply_gradients(grads)])
        #

    def getOptmizers(self):
        k_constants = K.variable(0)
        action_gdts = K.placeholder(shape=(None, self.outputSize))
        params_grad = tf.gradients(self.actor.output, self.actor.trainable_weights, -action_gdts)
        grads = zip(params_grad, self.actor.trainable_weights)
        # self.actorOptmizer =  K.function([self.actor.input, action_gdts], [tf.train.AdamOptimizer(self.learning_rate).apply_gradients(grads)])

        self.actorOptmizer = K.function(inputs=[self.actor.input, action_gdts], outputs=k_constants,
                   updates=[tf.train.AdamOptimizer(self.learning_rate).apply_gradients(grads)][1:])


        # Function to compute Q-value gradients (Actor Optimization)
        self.criticGrandients = K.function([self.critic.input[0], self.critic.input[1]],outputs=
                                       K.gradients(self.critic.output, [self.critic.input[1]]))
        #
        #
        # self.actor.compile(Adam(self.learning_rate), 'mse')
        # self.actorTarget.compile(Adam(self.learning_rate), 'mse')




    def buildCriticNetwork(self):

        # Critic model
        inputSize = self.numCardsPerPlayer + self.numMaxCards

        inp = Input((inputSize,), name="Critic_State")
        actionInput = Input((self.outputSize,), name="Critic_Action")

        # dense1 = Dense(256, activation='relu', name="critic_dense_1")(inp)

        for i in range(self.hiddenLayers + 1):
            if i == 0:
                previous = inp
            else:
                previous = dense

            dense = Dense(self.hiddenUnits * (i + 1), name="Critic_Dense" + str(i), activation="relu")(previous)


        # outputActor = Dense(self.outputSize, activation='softmax', name="actor_output")(dense)


        concatenated = Concatenate()([dense, actionInput])

        dense2 = Dense(128, activation='relu', name="critic__dense_2")(concatenated)
        outputCritic = Dense(1, activation='linear', name="critic_output")(dense2)

        self.critic = Model([inp, actionInput], outputCritic)


        #critic target
        inp = Input((inputSize,), name="Critic_State")
        actionInput = Input((self.outputSize,), name="Critic_Action")

        for i in range(self.hiddenLayers + 1):
            if i == 0:
                previous = inp
            else:
                previous = dense

            dense = Dense(self.hiddenUnits * (i + 1), name="Critic_Dense" + str(i), activation="relu")(previous)

        concatenated = Concatenate()([dense, actionInput])

        dense2 = Dense(128, activation='relu', name="critic__dense_2")(concatenated)
        outputCritic = Dense(1, activation='linear', name="critic_output")(dense2)

        self.criticTarget = Model([inp, actionInput], outputCritic)

        self.critic.compile(Adam(self.learning_rate), 'mse')
        self.criticTarget.compile(Adam(self.learning_rate), 'mse')


    def buildModel(self):

       self.buildActorNetwork()
       self.buildCriticNetwork()
       self.getOptmizers()


    def transferWeights(self):
        """ Transfer actor weights to actor target model with a factor of Tau
        """
        W, target_W = self.actor.get_weights(), self.actorTarget.get_weights()
        for i in range(len(W)):
            target_W[i] = self.tau * W[i] + (1 - self.tau)* target_W[i]
        self.actorTarget.set_weights(target_W)

        """ Transfer critic model weights to critic target model with a factor of Tau
        """
        W, target_W = self.critic.get_weights(), self.criticTarget.get_weights()
        for i in range(len(W)):
            target_W[i] = self.tau * W[i] + (1 - self.tau) * target_W[i]
        self.criticTarget.set_weights(target_W)


    def getAction(self, params):

        stateVector, possibleActionsOriginal = params
        stateVector = numpy.expand_dims(numpy.array(stateVector), 0)

        # print ("Shape vector: " + str(stateVector.shape))

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
            # print ("Correct action!")
            self.currentCorrectAction = self.currentCorrectAction+1

        self.totalActionPerGame = self.totalActionPerGame+1



        # testIndex = numpy.where(numpy.array(possibleActions) == 1)
        #
        # print ("testIndex:" + str(testIndex))
        #
        # print ("AIndex:" + str(aIndex))


        # if possibleActions[aIndex] == 0:
        #     # print("Incorrect action!")
        #     # print ("Predictions:", prediction)
        #     # input("here")
        #
        #     number = random.random()
        #     if number < 0.5:
        #         a = numpy.zeros(self.outputSize)
        #         aIndex = numpy.random.choice(numpy.arange(self.outputSize), 1, p=prediction)[0]
        #         a[aIndex] = 1
        #
        #         number = random.random()
        #
        #         if possibleActions[aIndex] == 0:
        #              if number < 0.5:
        #                 itemindex = numpy.where(numpy.array(possibleActions) == 1)
        #                 numpy.random.shuffle(itemindex)
        #                 aIndex = itemindex[0]
        #                 a = numpy.zeros(self.outputSize)
        #                 a[aIndex] = 1
        #
        # else:
        #     # print ("Correct action!")
        #     self.currentCorrectAction = self.currentCorrectAction+1
        #
        # self.totalActionPerGame = self.totalActionPerGame+1
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
        self.actorTarget = load_model(actorModel)

        self.critic = load_model(criticModel)
        self.criticTarget = load_model(criticModel)

        self.getOptmizers()



    def bellman(self, rewards, q_values, dones):
        """ Use the Bellman Equation to compute the critic target
        """
        critic_target = numpy.asarray(q_values)
        for i in range(q_values.shape[0]):
            if dones[i]:
                critic_target[i] = rewards[i]
            else:
                critic_target[i] = rewards[i] + self.gamma * q_values[i]
        return critic_target


    def updateModel(self, savedNetwork, game):

        # Sample experience from buffer
        minibatch = random.sample(self.memory, self.batchSize)

        minibatch = numpy.swapaxes(numpy.array(copy.copy(minibatch)),0,1)
        states,actions,rewards,nextStates, done = minibatch

        states = states.tolist()
        nextStates = nextStates.tolist()
        actions = actions.tolist()
        rewards = rewards.tolist()
        dones = done.tolist()

        #auxiliary
        actions2 = numpy.array(actions)
        states2 = numpy.array(states)

        # Predict target q-values using target networks
        actorTarget = self.actorTarget.predict([nextStates])
        q_values = self.criticTarget.predict([nextStates, actorTarget])
        # Compute critic target
        critic_target = self.bellman(rewards, q_values, dones)

        # Train both networks on sampled batch, update target networks

        # Train critic

        self.critic.train_on_batch([states2, actions2], critic_target)

        # Q-Value Gradients under Current Policy
        actions = self.actor.predict([states])
        grads = self.criticGrandients([states2, actions2])

        # Train actor
        self.actorOptmizer([states2, numpy.array(grads).reshape((-1, self.outputSize))])

        # self.actorOptmizer([state[0], numpy.array(grads).reshape((-1, self.outputSize))])

        # Transfer weights to target networks at rate Tau
        self.transferWeights()

        if (game + 1) % 100 == 0:
            self.actor.save(savedNetwork + "/actor_iteration_" + str(game) + ".hd5")
            self.critic.save(savedNetwork + "/critic_iteration_" + str(game) + ".hd5")

            self.lastModel = (savedNetwork + "/actor_iteration_" + str(game) + ".hd5",
                              savedNetwork + "/critic_iteration_" + str(game) + ".hd5")


    def train(self, params=[]):

        state, action, reward, next_state, done, savedNetwork, game, possibleActions = params
        if done:
            self.totalCorrectAction.append(self.currentCorrectAction)
            self.totalAction.append(self.totalActionPerGame)

            self.currentCorrectAction = 0
            self.totalActionPerGame = 0

        if self.training:
            #memorize

            # action = numpy.argmax(action)

            # state = [numpy.expand_dims(numpy.array(state), 0)]
            # # #
            # next_state = numpy.expand_dims(numpy.array(next_state), 0)
            #
            # action = numpy.expand_dims(numpy.array(action), 0)

            self.memory.append((state,action,reward,next_state, done))
            if len(self.memory) > self.batchSize and done:# if a game is over for this player, train it.
             self.updateModel(savedNetwork, game)





