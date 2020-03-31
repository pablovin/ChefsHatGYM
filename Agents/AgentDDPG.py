#Adapted from: https://github.com/germain-hug/Deep-RL-Keras


from Agents import IAgent
import numpy
import copy

from collections import deque
from keras.layers import Input, Dense, Flatten, Concatenate, Multiply
from keras.models import Model
from keras.optimizers import Adam
from keras.optimizers import RMSprop
import tensorflow as tf

import keras.backend as K

from keras.models import load_model
from Agents import MemoryBuffer

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

    losses = []

    def __init__(self, params=[]):
        self.training = params[0]
        self.name = "DDPG"

        self.totalAction = []
        self.totalActionPerGame = 0

        self.currentCorrectAction = 0

        self.totalCorrectAction = []

        pass


    def startAgent(self, params=[]):
        numMaxCards, numCardsPerPlayer, actionNumber, loadModel, agentParams = params

        self.numMaxCards = numMaxCards
        self.numCardsPerPlayer = numCardsPerPlayer
        self.outputSize = actionNumber  # all the possible ways to play cards plus the pass action

        if len(agentParams) > 1:

            self.hiddenLayers, self.hiddenUnits, self.gamma, self.tau, self.batchSize  = agentParams

        else:

            #(4, 32, 0.9771889086404025, 0.021720838134133988, 512)
            # Hyperopt
            # self.hiddenLayers = 4
            # self.hiddenUnits = 32
            # self.batchSize = 512
            # self.gamma = 0.977  # discount rate
            # self.tau = 0.021 # Weight transfer rate

            #My estimations
            self.hiddenLayers = 1
            self.hiddenUnits = 32
            self.batchSize = 256
            self.gamma = 0.99  # discount rate
            self.tau = 0.01 # Weight transfer rate

        self.learning_rate = 0.0001
        #Game memory
        QSize = 5000
        self.memory = MemoryBuffer.MemoryBuffer(QSize, False)

        self.epsilon_min = 0.1
        self.epsilon_decay = 0.995

        if self.training:
            self.epsilon = 1.0  # exploration rate while training
        else:
            self.epsilon = 0.0 #no exploration while testing


        if loadModel == "":
            self.buildModel()
        else:
            self.loadModel(loadModel)

        self.losses = []

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

        actionsOutput = Input(shape=(self.outputSize,),
                                name="PossibleActions")


        outputPossibleActor = Multiply()([actionsOutput, outputActor])

        self.actor = Model([inp,actionsOutput], outputPossibleActor)

        inputSize = self.numCardsPerPlayer + self.numMaxCards
        inp = Input((inputSize,), name="Actor_State")

        for i in range(self.hiddenLayers + 1):
            if i == 0:
                previous = inp
            else:
                previous = dense

            dense = Dense(self.hiddenUnits * (i + 1), name="Actor_Dense" + str(i), activation="relu")(previous)


        outputActor = Dense(self.outputSize, activation='softmax', name="actor_output")(dense)

        actionsOutput = Input(shape=(self.outputSize,),
                                name="PossibleActions")



        outputPossibleActor = Multiply()([actionsOutput, outputActor])

        self.actorTarget = Model([inp,actionsOutput], outputPossibleActor)


        advantage = Input(shape=(1,))
        old_prediction = Input(shape=(self.outputSize,))

        self.actor.compile(optimizer=Adam(lr=self.learning_rate),
                      loss=[proximal_policy_optimization_loss(
                          advantage=advantage,
                          old_prediction=old_prediction)])

    def getOptmizers(self):
        k_constants = K.variable(0)
        action_gdts = K.placeholder(shape=(None, self.outputSize))
        params_grad = tf.gradients(self.actor.output, self.actor.trainable_weights, -action_gdts)
        grads = zip(params_grad, self.actor.trainable_weights)
        # self.actorOptmizer =  K.function([self.actor.input, action_gdts], [tf.train.AdamOptimizer(self.learning_rate).apply_gradients(grads)])

        self.actorOptmizer = K.function(inputs=[self.actor.input, action_gdts], outputs=k_constants,
                   updates=[tf.train.AdamOptimizer(self.learning_rate).apply_gradients(grads)][1:])


        # # Function to compute Q-value gradients (Actor Optimization)
        self.criticGrandients = K.function([self.critic.input[0], self.critic.input[1]],outputs=
                                       K.gradients(self.critic.output, [self.critic.input[1]]))
        #
        #
        # self.critic.compile(Adam(self.learning_rate), 'mse')
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

        possibleActions2 = copy.copy(possibleActionsOriginal)
        possibleActionsVector = numpy.expand_dims(numpy.array(possibleActions2), 0)

        if numpy.random.rand() <= self.epsilon:
            itemindex = numpy.array(numpy.where(numpy.array(possibleActionsOriginal) == 1))[0].tolist()
            random.shuffle(itemindex)
            aIndex = itemindex[0]
            a = numpy.zeros(self.outputSize)
            a[aIndex] = 1
            #
            #
            # aIndex = numpy.random.randint(0, self.outputSize)
            # a = numpy.zeros(self.outputSize)
            # a[aIndex] = 1
        else:
            a = self.actor.predict([stateVector, possibleActionsVector])[0]
            aIndex = numpy.argmax(a)

            if possibleActionsOriginal[aIndex] == 1:
              self.currentCorrectAction = self.currentCorrectAction + 1

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


    def updateModel(self, savedNetwork, game, thisPlayer):

        # Sample experience from buffer
        # minibatch = random.sample(self.memory, self.batchSize)
        #
        # minibatch = numpy.swapaxes(numpy.array(copy.copy(minibatch)),0,1)

        states, actions, rewards, dones, nextStates, possibleActions, newPossibleActions, idx = self.memory.sample_batch(self.batchSize)
        #
        #
        # states,actions,rewards,nextStates, done = minibatch

        # states = states.tolist()
        # nextStates = nextStates.tolist()
        # actions = actions.tolist()
        # rewards = rewards.tolist()
        # dones = done.tolist()
        # possibleActions = possibleActions.tolist()
        # newPossibleActions = newPossibleActions.tolist()
        #
        # #auxiliary
        # actions2 = numpy.array(actions)
        # states2 = numpy.array(states)

        # Predict target q-values using target networks
        actorTarget = self.actorTarget.predict([nextStates, newPossibleActions])
        q_values = self.criticTarget.predict([nextStates, actorTarget])
        # Compute critic target
        critic_target = self.bellman(rewards, q_values, dones)

        # Train both networks on sampled batch, update target networks

        # Train critic
        history = self.critic.fit([states, actions], critic_target, verbose=False)
        self.losses.append(history.history['loss'])

        # Q-Value Gradients under Current Policy
        actions = self.actor.predict([states, possibleActions])
        grads = self.criticGrandients([states, actions])

        # Train actor
        self.actorOptmizer([[states, possibleActions], numpy.array(grads).reshape((-1, self.outputSize))])

        # Transfer weights to target networks at rate Tau
        self.transferWeights()

        if (game + 1) % 100 == 0:
            if (game + 1) % 100 == 0:
                self.actor.save(savedNetwork + "/actor_iteration_" + str(game) + "_Player_" + str(thisPlayer) + ".hd5")
                self.critic.save(savedNetwork + "/critic_iteration_" + str(game) + "_Player_" + str(thisPlayer) + ".hd5")
                self.lastModel = (savedNetwork + "/actor_iteration_" + str(game) + "_Player_" + str(thisPlayer) + ".hd5",
                                  savedNetwork + "/critic_iteration_" + str(game) + "_Player_" + str(
                                      thisPlayer) + ".hd5")

        #Update the decay
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        print (" -- Epsilon:" + str(self.epsilon) + " - Loss:" + str(history.history['loss']))

    def memorize(self, state, action, reward, next_state, done, possibleActions, newPossibleActions):

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
            self.memorize(state, action, reward, next_state, done, possibleActions, newPossibleActions)

            if self.memory.size() > self.batchSize and done:
                self.updateModel(savedNetwork, game, thisPlayer)


