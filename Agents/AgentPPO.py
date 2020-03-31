#Adapted from: https://github.com/LuEE-C/PPO-Keras/blob/master/Main.py


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

import tensorflow.compat.v1 as tfc

import random

def proximal_policy_optimization_loss():
    def loss(y_true, y_pred):
        LOSS_CLIPPING = 0.2  # Only implemented clipping for the surrogate loss, paper said it was best
        ENTROPY_LOSS = 5e-3
        y_tru_valid = y_true[:, 0:200]
        old_prediction = y_true[:, 200:400]
        advantage = y_true[:, 400][0]

        prob = K.sum(y_tru_valid * y_pred, axis=-1)
        old_prob = K.sum(y_tru_valid * old_prediction, axis=-1)
        r = prob/(old_prob + 1e-10)

        return -K.mean(K.minimum(r * advantage, K.clip(r, min_value=1 - LOSS_CLIPPING,
                                                       max_value=1 + LOSS_CLIPPING) * advantage) + ENTROPY_LOSS * -(
                    prob * K.log(prob + 1e-10)))
    return loss


#Adapted from: https://github.com/germain-hug/Deep-RL-Keras


class AgentPPO(IAgent.IAgent):

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

        self.name = "PPO"
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


        self.memory = []

        #Game memory
        self.resetMemory()

        self.losses = []
        self.QValues = []

        self.learning_rate = 1e-4

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

        self.DUMMY_ACTION, self.DUMMY_VALUE = numpy.zeros((1, self.outputSize)), numpy.zeros((1, 1))

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

        old_prediction = Input(shape=(self.outputSize,), name="oldPrediction")

        self.actor.compile(optimizer=Adam(lr=self.learning_rate),
                      loss=[proximal_policy_optimization_loss()])

        # advantage = Input(shape=(1,), name="advantage")
        # old_prediction = Input(shape=(self.outputSize,), name="oldPrediction")
        # old_prediction = K.variable(0)
        # # advantage = K.variable(0)
        #
        # self.actor.compile(optimizer=Adam(lr=self.learning_rate),
        #               loss=[proximal_policy_optimization_loss(
        #                   advantage=advantage,
        #                   old_prediction=old_prediction)])
        #
        # self.actor.compile(optimizer=Adam(lr=self.learning_rate),
        #               loss=["mse"])

        # advantage = actual_value - predicted_value
        #
        # def loss(y_true, y_pred):
        #     prob = K.sum(y_true * y_pred)
        #     old_prob = K.sum(y_true * old_prediction)
        #     r = prob / (old_prob + 1e-10)
        #
        #     return -K.log(prob + 1e-10) * K.mean(
        #         K.minimum(r * advantage, K.clip(r, min_value=0.8, max_value=1.2) * advantage))
        #
        # return loss


        # rmsOptmizer = Adam(lr=self.learning_rate)
        # LOSS_CLIPPING = K.variable(0.2 )  # Only implemented clipping for the surrogate loss, paper said it was best
        # ENTROPY_LOSS =  K.variable(5e-3)
        #
        # action_pl= K.placeholder(shape=(None, self.outputSize))
        # advantage_pl = K.placeholder(shape=(None,))
        # oldPredictions_pl = K.placeholder(shape=(None, self.outputSize))
        # k_constants = K.variable(0)
        #
        # # prob = K.sum(y_true * y_pred, axis=-1)
        # # old_prob = K.sum(y_true * old_prediction, axis=-1)
        #
        # # prob = K.sum(action_pl * self.actor.output, axis=-1)
        # # old_prob = K.sum(action_pl * oldPredictions_pl, axis=-1)
        # # r = prob / (old_prob + 1e-10)
        # # loss = -K.mean(K.minimum(r * advantage_pl, K.clip(r, min_value=1 - LOSS_CLIPPING,
        # #                                                max_value=1 + LOSS_CLIPPING) * advantage_pl) + ENTROPY_LOSS * -(
        # #             prob * tfc.log(prob + 1e-10)))
        #
        #
        # # return loss
        # #
        #
        # prob = K.sum(self.actor.output, axis=-1)
        # old_prob = K.sum(action_pl * oldPredictions_pl, axis=-1)
        # # old_prob = prob
        # # r = prob / (old_prob + 1e-10)
        # # r = K.sum(prob,old_prob, axis=-1)
        #
        # loss = K.sum(prob)
        # # loss = -K.mean(K.minimum(r * advantage_pl, K.clip(r, min_value=1 - LOSS_CLIPPING,
        # #                                                    max_value=1 + LOSS_CLIPPING) * advantage_pl) + ENTROPY_LOSS * -(
        # #                 prob * tfc.log(prob + 1e-10)))
        #
        # updates = rmsOptmizer.get_updates(self.actor.trainable_weights, [], loss)
        #
        # self.actorOptmizer = K.function([self.actor.input, action_pl, advantage_pl, oldPredictions_pl], loss, updates=updates)
        #


    def buildCriticNetwork(self):

        # Critic model
        inputSize = self.numCardsPerPlayer + self.numMaxCards

        inp = Input((inputSize,), name="Critic_State")

        # dense1 = Dense(256, activation='relu', name="critic_dense_1")(inp)

        for i in range(self.hiddenLayers + 1):
            if i == 0:
                previous = inp
            else:
                previous = dense

            dense = Dense(self.hiddenUnits * (i + 1), name="Critic_Dense" + str(i), activation="relu")(previous)

        outputCritic = Dense(1, activation='linear', name="critic_output")(dense)

        self.critic = Model([inp], outputCritic)

        self.critic.compile(Adam(self.learning_rate), 'mse')

    def buildModel(self):

       self.buildCriticNetwork()
       self.buildActorNetwork()
       self.loadQValueReader()


    def loadQValueReader(self):
        softmaxLayer = self.actor.get_layer(index=-2)
        self.QValueReader = Model(self.actor.inputs, softmaxLayer.output)

    def calculateProbabilityOfSuccess(self, QValue):
        theta = 0.0
        maxreward = 1
        probability = (1-theta) * (1/2*numpy.log10(QValue/maxreward)+1)

        if probability <= 0:
            probability = 0
        if probability >= 1:
            probability =1

        self.Probability.append(probability)


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

            self.QValues.append(qvalues)
            self.calculateProbabilityOfSuccess(qvalues[aIndex])
            if possibleActionsOriginal[aIndex] == 1:
                self.currentCorrectAction = self.currentCorrectAction + 1

        # possibleActionsVector = numpy.expand_dims(numpy.array(possibleActions2), 0)
        # a = self.online_network.predict([stateVector, possibleActionsVector])[0]
        # aIndex = numpy.argmax(a)
        #
        # if numpy.sum(possibleActions2) > 1 and aIndex == 199:
        #     itemindex = numpy.array(numpy.where(numpy.array(possibleActions2) == 1))[0].tolist()
        #     random.shuffle(itemindex)
        #     aIndex = itemindex[0]
        #     a = numpy.zeros(self.outputSize)
        #     a[aIndex] = 1
        #
        # self.QValues.append(a)
        # if possibleActionsOriginal[aIndex] == 1:
        #     self.currentCorrectAction = self.currentCorrectAction + 1
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
        def loss(y_true, y_pred):
            LOSS_CLIPPING = 0.2  # Only implemented clipping for the surrogate loss, paper said it was best
            ENTROPY_LOSS = 5e-3
            y_tru_valid = y_true[:, 0:200]
            old_prediction = y_true[:, 200:400]
            advantage = y_true[:, 400][0]

            prob = K.sum(y_tru_valid * y_pred, axis=-1)
            old_prob = K.sum(y_tru_valid * old_prediction, axis=-1)
            r = prob / (old_prob + 1e-10)

            return -K.mean(K.minimum(r * advantage, K.clip(r, min_value=1 - LOSS_CLIPPING,
                                                           max_value=1 + LOSS_CLIPPING) * advantage) + ENTROPY_LOSS * -(
                    prob * K.log(prob + 1e-10)))

        actorModel, criticModel = model
        self.actor  = load_model(actorModel, custom_objects={'loss':loss})
        self.critic = load_model(criticModel, custom_objects={'loss':loss})
        self.loadQValueReader()


    def updateModel(self, savedNetwork, game, thisPlayer):

        # print ("Updating the model!")
        self.memory = numpy.array(self.memory)
        # print ("self.memory: " + str(self.memory.shape))

        state =  numpy.array(self.states)
        # state =  self.states
        action = self.actions
        reward = self.rewards
        possibleActions = numpy.array(self.possibleActions)
        # possibleActions = self.possibleActions
        realEncoding = numpy.array(self.realEncoding)

        # Compute discounted rewards and Advantage (TD. Error)
        discounted_rewards = self.discount(reward)
        state_values = self.critic.predict(numpy.array(state))
        advantages = discounted_rewards - numpy.reshape(state_values, len(state_values))

        # advantages = numpy.array(advantages)

        criticLoss = self.critic.train_on_batch([state], [reward])

        # actorLoss = self.actorOptmizer([[state, possibleActions], action, advantages, realEncoding])

        # advantages = numpy.zeros(43)

        # actions = numpy.array(action)
        #
        actions = []
        for i in range(len(action)):
            # print ("Action:" + str(action[i]))
            # concatenated = numpy.concatenate((action[i], numpy.zeros(numpy.array(action[i].shape))))
            advantage = numpy.zeros(numpy.array(action[i]).shape)
            advantage[0] = advantages[i]
            concatenated = numpy.concatenate((action[i], realEncoding[i], advantage))
            actions.append(concatenated)

        # print ("SHape y_tru_valid: ", numpy.array(actions).shape)
        # print("SHape old_prediction: ", numpy.array(actions)[:, 200:].shape)
        #
        # print ("array:" + str(numpy.array(actions)[:, 200:][0]))


        actorLoss = self.actor.train_on_batch([state, possibleActions], [actions])

        # historyLoss = self.actor.fit([state, possibleActions], [action], shuffle=True,
        #                             epochs=1, verbose=False)

        # historyLoss = self.actor.train_on_batch([[state, possibleActions], advantages], [action])
        #
        #
        # actorLoss = historyLoss.history['loss']

        # self.losses.append(actorLoss)

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
        self.realEncoding = []


    def train(self, params=[]):

        state, action, reward, next_state, done, savedNetwork, game, possibleActions, newPossibleActions, thisPlayer = params

        if done:
            self.totalCorrectAction.append(self.currentCorrectAction)
            self.totalAction.append(self.totalActionPerGame)

            self.currentCorrectAction = 0
            self.totalActionPerGame = 0

        if self.training:
            # print ("train")
            #memorize

            # action = numpy.argmax(action)


            realEncoding = action
            action = numpy.zeros(action.shape)
            action[numpy.argmax(realEncoding)] = 1

            self.states.append(state)
            self.actions.append(action)
            self.rewards.append(reward)
            self.possibleActions.append(possibleActions)
            self.realEncoding.append(realEncoding)

            if done: # if a game is over for this player, train it.
                self.updateModel(savedNetwork, game, thisPlayer)
                self.resetMemory()





