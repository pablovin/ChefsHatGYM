Quickstart Guide
================

Here you will find instructions regarding how to install the environment, run your first games and implement your first agent!

Instalation
^^^^^^^^^^^

To install ChefsHatGym, you will need python >= 3.6. The environment has a list of `requirements <https://pypi.org/project/ChefsHatGym/>`_ that will be installed automatically if you run:

.. code-block:: bash

    pip install chefshatgym


Understanding Chef's Hat
^^^^^^^^^^^^^^^^^^^^^^^^

Chef's Hat is a card game designed with multimodal and competitive interactions in mind, which allows it to be followed and modeled by artificial agents with ease. It is simple to understand, but difficult to master, rules that provide an excellent opportunity for learning agents. 
For a complete overview of the development of the game, refer to:

* `Barros, P., Sciutti, A., Bloem, A. C., Hootsmans, I. M., Opheij, L. M., Toebosch, R. H., & Barakova, E. (2021, March). It's Food Fight! Designing the Chef's Hat Card Game for Affective-Aware HRI. In Companion of the 2021 ACM/IEEE International Conference on Human-Robot Interaction (pp. 524-528). <https://dl.acm.org/doi/abs/10.1145/3434074.3447227>`_

And for a complete understanding of the game's rules, please check:

* The Chef's Hat rulebook `The Chef's Hat rulebook <https://github.com/pablovin/ChefsHatGYM/blob/master/gitImages/RulebookMenuv08.pdf>`_.

Creating new players!
^^^^^^^^^^^^^^^^^^^^^

To run a game in Chef's Hat, first, you need four players. The Environment provides a naive type of agent, that will execute random actions. To initiate the agents, simply call them:

.. code-block:: python

    """Player Parameters"""
    agent1 = Agent_Naive_Random.AgentNaive_Random("Random1")
    agent2 = Agent_Naive_Random.AgentNaive_Random("Random2")
    agent3 = Agent_Naive_Random.AgentNaive_Random("Random3")
    agent4 = Agent_Naive_Random.AgentNaive_Random("Random4")

Starting a Chef's Hat Game!
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Once you have all four players, you must collect the agent's names and implemented reward functions. There are two game types: MATCHES, which will run a limited number of matches, and POINTS, which will run until one of the players reaches a limited number of points. You have to define the type of game and the stoping criteria when starting a new game:


.. code-block:: python

    agentNames = [agent1.name, agent2.name, agent3.name, agent4.name]
    playersAgents = [agent1, agent2, agent3, agent4]


    gameType = ChefsHatEnv.GAMETYPE["MATCHES"]
    gameStopCriteria = 10

    env = gym.make('chefshat-v0') #starting the game Environment
    env.startExperiment(rewardFunctions=rewards, playerNames=agentNames,gameType=gameType, stopCriteria=gameStopCriteria,)

Once the game started, each agent must act until the game is finished:

.. code-block:: python

    observations = env.reset()

    while not env.gameFinished:
        currentPlayer = playersAgents[env.currentPlayer]

        observations = env.getObservation()
        action = currentPlayer.getAction(observations)

        info = {"validAction":False}
        while not info["validAction"]:
            nextobs, reward, isMatchOver, info = env.step(action)

        if isMatchOver:
            print ("-------------")
            print ("Match:" + str(info["matches"]))
            print ("Score:" + str(info["score"]))
            print("Performance:" + str(info["performanceScore"]))
            print("-------------")

The environment controls the game flow, and after each action, indicates which agent will perform the next action. The info, returned by the environment, contains important information about the game status, and might be primordial for learning agents!

A full-running example can be found in the examples folder.
