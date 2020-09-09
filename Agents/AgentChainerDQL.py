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


import chainer
import chainer.functions as F
import chainer.links as L
import chainerrl
from chainerrl import explorer as exp
from logging import getLogger


class AgentChainerDQL(IAgent.IAgent):

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

        self.name = "CHAINERDQL"+agentName

        self.totalAction = []
        self.totalActionPerGame = 0

        self.currentCorrectAction = 0

        self.totalCorrectAction = []
        self.losses = []


    def startAgent(self, params=[]):
        numMaxCards, numCardsPerPlayer, actionNumber, loadModel, agentParams = params

        self.outputSize = actionNumber

        class QFunction(chainer.Chain):

            def __init__(self, obs_size, n_actions, n_hidden_channels=50):
                super().__init__()
                with self.init_scope():
                    self.l0 = L.Linear(obs_size, n_hidden_channels)
                    self.l1 = L.Linear(n_hidden_channels, n_hidden_channels)
                    self.l2 = L.Linear(n_hidden_channels, n_actions)

            def __call__(self, x, test=False):
                """
                Args:
                    x (ndarray or chainer.Variable): An observation
                    test (bool): a flag indicating whether it is in test mode
                """
                h = F.relu(self.l0(x))
                h = F.softmax(self.l1(h))
                return chainerrl.action_value.DiscreteActionValue(self.l2(h))

        inputSize = self.numCardsPerPlayer + self.numMaxCards
        q_func = QFunction(28, 200, n_hidden_channels=256)
        q_func.to_gpu(0)

        # q_func = chainerrl.q_functions.FCStateQFunctionWithDiscreteAction(
        #     28, 200,
        #     n_hidden_layers=2, n_hidden_channels=50)

        phi = lambda x: x.astype(numpy.float32, copy=False)

        optimizer = chainer.optimizers.Adam(eps=1e-2)
        optimizer.setup(q_func)

        # Set the discount factor that discounts future rewards.
        gamma = 0.95
        # Use ChefsHatExploration for exploration
        explorer = chainerrl.explorers.ConstantEpsilonGreedy(
            epsilon=0.9, random_action_func=self.randomActionSelection)

        # DQN uses Experience Replay.
        # Specify a replay buffer and its capacity.
        replay_buffer = chainerrl.replay_buffer.ReplayBuffer(capacity=10 ** 6)

        # Now create an agent that will interact with the environment.
        agent = chainerrl.agents.DoubleDQN(
            q_func, optimizer, replay_buffer, gamma, explorer,
            replay_start_size=50, update_interval=1,
            target_update_interval=100, phi=phi)

        self.agent = agent

    def buildModel(self):
         pass


    def randomActionSelection(self):

        possibleActionsOriginal = self.possibleActions

        # print ("Possible Actions:" + str(possibleActionsOriginal))
        possibleActions2 = copy.copy(possibleActionsOriginal)
        itemindex = numpy.array(numpy.where(numpy.array(possibleActions2) == 1))[0].tolist()
        random.shuffle(itemindex)
        # print("itemindex:" + str(itemindex))

        aIndex = itemindex[0]
        a = numpy.zeros(self.outputSize)
        a[aIndex] = 1

        return aIndex


    def getAction(self, params):


        stateVector, possibleActionsOriginal, reward = params

        self.possibleActions = possibleActionsOriginal

        # print("stateVector:" + str(stateVector))

        stateVector = stateVector.astype(float)
        reward = float(reward)
        action = self.agent.act_and_train(stateVector, reward)

        # print ("Action:"  + str(action))

        # possibleActionsVector = numpy.expand_dims(numpy.array(possibleActions2), 0)

        #
        #
        #
        # # aIndex = numpy.argmax(a)
        a = numpy.zeros(self.outputSize)
        a[action] = 1

        a = a*possibleActionsOriginal
        # print ("Action:" +str(a))

        # print ("Action:" + str(numpy.array(a).shape))
        # print("possibleAction:" + str(numpy.array(possibleActionsOriginal).shape))

        return a

    def loadModel(self, model):

       pass


    def train(self, params=[]):

        state, action, reward, next_state, done, savedNetwork, game, possibleActions, newPossibleActions, thisPlayer, score = params

        reward = int(reward)
        # print("Reward:" + str(reward))
        self.agent.act_and_train(state, reward)
        self.agent.stop_episode_and_train(state, reward, done)

        if game % 50 ==0:
            print (str(self.agent.get_statistics()))







