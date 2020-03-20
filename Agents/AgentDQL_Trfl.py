from Agents import IAgent
import numpy
import copy

from collections import deque
from keras.layers import Input, Dense, Flatten, Concatenate
from keras.models import Model
from keras.optimizers import Adam

from tensorflow.saved_model import tag_constants

from keras.models import load_model


import tensorflow as tf
import trfl

import random

class AgentDQL_Trfl(IAgent.IAgent):

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

        tf.get_logger().setLevel('INFO')
        tf.autograph.set_verbosity(1)


        self.training = params[0]
        self.name = "DQL"

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
        self.outputActivation = "linear"
        self.loss = "mse"

        self.epsilon_min = 0.1
        self.epsilon_decay = 0.990

        if self.training:
            self.epsilon = 1.0  # exploration rate while training
        else:
            self.epsilon = 0.1 #no exploration while testing



        self.memory = deque(maxlen=QSize)
        self.learning_rate = 0.001


        tf.reset_default_graph()


        if loadModel == "":
            self.buildModel()
        else:
            self.loadModel(loadModel)


    def buildModel(self):

        self.buildSimpleModel()

    def buildSimpleModel(self):

        init_op = tf.initialize_all_variables()

        with tf.variable_scope(self.name):
            # Input

            inputSize = self.numCardsPerPlayer + self.numMaxCards
            self.inputs = tf.placeholder(tf.float32, [None, inputSize], name='inputsLayer')

            # Layers
            self.fc1 = tf.contrib.layers.fully_connected(self.inputs, self.hiddenUnits)
            self.fc2 = tf.contrib.layers.fully_connected(self.fc1, self.hiddenUnits)
            self.output = tf.contrib.layers.fully_connected(self.fc2, self.outputSize, activation_fn=None)

            self.buildOptmizer()

            # Commented out => prior to TRFL
            #             # Output and target
            #             self.actions = tf.placeholder(tf.int32, [None], name='actions')
            #             one_hot_actions = tf.one_hot(self.actions, action_size)
            #             self.Q = tf.reduce_sum(tf.multiply(self.output, one_hot_actions), axis=1)
            #             self.targetQ = tf.placeholder(tf.float32, [None], name='target')

            #             # Minimize mean squared error between target Q and current Q
            #             self.loss = tf.reduce_mean(tf.square(self.targetQ - self.Q))
            #             self.optimize = tf.train.AdamOptimizer(learning_rate).minimize(self.loss)


    def buildOptmizer(self):
            self.actions = tf.placeholder(tf.int32, [None], name='actions')
            self.targetQ = tf.placeholder(tf.float32, [self.batchSize, self.outputSize], name='target')
            self.reward = tf.placeholder(tf.float32, [self.batchSize], name='reward')
            self.discount = tf.constant(self.gamma, tf.float32, [self.batchSize], name='discount')

            q_loss, q_learning = trfl.qlearning(self.output, self.actions, self.reward, self.discount, self.targetQ)
            self.loss = tf.reduce_mean(q_loss)
            self.optimize = tf.train.AdamOptimizer(self.learning_rate).minimize(self.loss)

            self.saver = tf.train.Saver()


    def getAction(self, params):

        stateVector, possibleActionsOriginal = params
        # stateVector = numpy.expand_dims(numpy.array(stateVector), 0)

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
            with tf.Session() as sess:
                tf.initialize_all_variables().run()
                a= sess.run(self.output, feed_dict={self.inputs: numpy.expand_dims(stateVector, axis=0)})
                aIndex = numpy.argmax(a)
                # aIndex = a

            # a = self.online_network.predict([stateVector])[0]
            # aIndex = numpy.argmax(a)

            if possibleActionsOriginal[aIndex] == 1:
                self.currentCorrectAction = self.currentCorrectAction + 1

        self.totalActionPerGame = self.totalActionPerGame + 1
        return a


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

        # stateVector, possibleActionsOriginal = params
        # stateVector = numpy.expand_dims(numpy.array(stateVector), 0)
        #
        # possibleActions = copy.copy(possibleActionsOriginal)
        #
        # prediction = self.online_network.predict([stateVector])[0]
        # aIndex = numpy.argmax(prediction)
        # a = prediction
        #
        # if possibleActions[aIndex] == 0:
        #     a = numpy.zeros(self.outputSize)
        #     aIndex = numpy.random.choice(numpy.arange(self.outputSize), 1, p=prediction)[0]
        #     a[aIndex] = 1
        #
        #     if possibleActions[aIndex] == 0:
        #
        #         itemindex = numpy.array(numpy.where(numpy.array(possibleActions) == 1))[0].tolist()
        #         random.shuffle(itemindex)
        #
        #         aIndex = itemindex[0]
        #         a = numpy.zeros(self.outputSize)
        #         a[aIndex] = 1
        #     else:
        #         # print ("Correct action!")
        #         self.currentCorrectAction = self.currentCorrectAction + 1
        # else:
        #     self.currentCorrectAction = self.currentCorrectAction+1
        #
        # self.totalActionPerGame = self.totalActionPerGame+1
        # return a



    def loadModel(self, model):

        graph = tf.Graph()
        with graph.as_default():
            with tf.Session() as sess:
                tf.saved_model.loader.load(
                    sess,
                    [tag_constants.SERVING],
                    model,
                )
                # batch_size_placeholder = graph.get_tensor_by_name('batch_size_placeholder:0')
                # features_placeholder = graph.get_tensor_by_name('features_placeholder:0')
                # labels_placeholder = graph.get_tensor_by_name('labels_placeholder:0')
                # prediction = restored_graph.get_tensor_by_name('dense/BiasAdd:0')
                #
                # sess.run(prediction, feed_dict={
                #     batch_size_placeholder: some_value,
                #     features_placeholder: some_other_value,
                #     labels_placeholder: another_value
                # })
                #

        self.online_network  = load_model(model)
        self.targetNetwork = load_model(model)


    def updateTargetNetwork(self):

        self.online_network.set_weights(self.online_network.get_weights())


    def updateModel(self, savedNetwork, game, thisPlayer):

        batch = random.sample(self.memory, self.batchSize)

        # Experience replay & train
        states = numpy.array([e[0] for e in batch])
        actions = numpy.array([e[1] for e in batch])
        rewards = numpy.array([e[2] for e in batch])
        next_states = numpy.array([e[3] for e in batch])
        # Predict targets
        with tf.Session() as sess:
            tf.initialize_all_variables().run()
            targetQ = sess.run(self.output, feed_dict={self.inputs: next_states})
            # Set targets to zero where an episode ended
            episode_ends = (next_states == numpy.zeros(states[0].shape)).all(axis=1)
            targetQ[episode_ends] = (0,) * self.outputSize

            # Commented out => prior to TRFL
            #             targetQ = rewards + gamma * np.max(targetQ, axis=1)
            #             loss, _ = sess.run([main_dqn.loss, main_dqn.optimize], feed_dict={
            #                 main_dqn.inputs: states,
            #                 main_dqn.targetQ: targetQ,
            #                 main_dqn.actions: actions
            #             })
            loss, _ = sess.run([self.loss, self.optimize], feed_dict={
                self.inputs: states,
                self.targetQ: targetQ,
                self.reward: rewards,
                self.actions: actions
            })

            # if (game + 1) % 100 == 0:
            self.saveModel(savedNetwork, game, thisPlayer)

                # save_path = self.saver.save(sess, "/tmp/model.ckpt")
                # print("Model saved in path: %s" % save_path)

        #Update the decay
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        print (" -- Epsilon:" + str(self.epsilon) + " - Loss: " + str(loss))


    def saveModel(self, savedNetwork, game, thisPlayer):



        inputSize = self.numCardsPerPlayer + self.numMaxCards
        self.inputs = tf.placeholder(tf.float32, [None, inputSize], name='inputsLayer')

        # Layers
        self.fc1 = tf.contrib.layers.fully_connected(self.inputs, self.hiddenUnits)
        self.fc2 = tf.contrib.layers.fully_connected(self.fc1, self.hiddenUnits)
        self.output = tf.contrib.layers.fully_connected(self.fc2, self.outputSize, activation_fn=None)



        with tf.Graph().as_default():
            with tf.Session() as sess:
                tf.initialize_all_variables().run()
                # Saving
                inputs = {
                    "inputLayer":  self.inputs,
                    "fc1": self.fc1,
                    "fc2":  self.fc2,
                }
                outputs = {"output": self.output }
                tf.saved_model.simple_save(
                    sess, savedNetwork + "/actor_iteration_" + str(game) + "_Player_"+str(thisPlayer)+".ckpt" , inputs, outputs
                )

        self.lastModel = savedNetwork + "/actor_iteration_" + str(game) + "_Player_" + str(thisPlayer) + ".ckpt"



    trainTime = 0
    def train(self, params=[]):

        state, action, reward, next_state, done, savedNetwork, game, possibleActions, thisPlayer = params

        action = numpy.argmax(action)
        if done:
            self.totalCorrectAction.append(self.currentCorrectAction)
            self.totalAction.append(self.totalActionPerGame)

            self.currentCorrectAction = 0
            self.totalActionPerGame = 0

        if self.training:
            #memorize


            # action = numpy.argmax(action)
            # state = numpy.expand_dims(numpy.array(state), 0)
            # next_state = numpy.expand_dims(numpy.array(next_state), 0)
            # possibleActions = numpy.expand_dims(numpy.array(possibleActions), 0)

            self.memory.append((state, action, reward, next_state, done, possibleActions))

            if len(self.memory) > self.batchSize and done:
                self.trainTime = self.trainTime + 1
                self.updateModel(savedNetwork, game, thisPlayer)



