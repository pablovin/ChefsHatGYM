Installation and Quickstart Guide
================================================

Here you will find instructions regarding how to install the environment, run your first games and implement your first agent!

Instalation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To install ChefsHatGym, you will need python >= 3.10. The environment has a list of `requirements <https://pypi.org/project/ChefsHatGym/>`_ that will be installed automatically if you run:

.. code-block:: bash

    pip install chefshatgym


Understanding Chef's Hat
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Chef's Hat is a card game designed with multimodal and competitive interactions in mind, which allows it to be followed and modeled by artificial agents with ease. It is simple to understand, but difficult to master, rules that provide an excellent opportunity for learning agents. 
For a complete overview of the development of the game, refer to:

* `Barros, P., Sciutti, A., Bloem, A. C., Hootsmans, I. M., Opheij, L. M., Toebosch, R. H., & Barakova, E. (2021, March). It's Food Fight! Designing the Chef's Hat Card Game for Affective-Aware HRI. In Companion of the 2021 ACM/IEEE International Conference on Human-Robot Interaction (pp. 524-528). <https://dl.acm.org/doi/abs/10.1145/3434074.3447227>`_

And for a complete understanding of the game's rules, please check:

* The Chef's Hat rulebook `The Chef's Hat rulebook <https://github.com/pablovin/ChefsHatGYM/blob/master/gitImages/RulebookMenuv08.pdf>`_.


Starting a Chef`s Hat Game
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To start a game, you can quickly implement a room from the ChefsHatGYM.gameRooms.local_room class.


.. code-block:: python
    
    from ChefsHatGym.gameRooms.chefs_hat_room_local import ChefsHatRoomLocal

    # Room parameters
    room_name = "Testing_2_Local"


    # Game parameters
    game_type = ChefsHatEnv.GAMETYPE["MATCHES"]
    stop_criteria = 3


    # Start the room
    room = ChefsHatRoomLocal(
        room_name,
        game_type=game_type,
        stop_criteria=stop_criteria,
    )

This example will run a game composed of three matches. Once the room is created, you have to add players to it. The Chef`s Hat Gym environment provides a simple random player, that only selects random actions.
Using the ChefsHatGym.agents interface, you will be able to create your own agents, and use it in the simulator.

Each agent must have a unique name to be able to play the game.

.. code-block:: python

    from ChefsHatGym.agents.agent_random import AgentRandon

    p1 = AgentRandon(name="01")
    p2 = AgentRandon(name="02")
    p3 = AgentRandon(name="03")
    p4 = AgentRandon(name="04")

    # Adding players to the room
    for p in [p1, p2, p3, p4]:
        room.add_player(p)

Once all the players are added to the room, you just have to start the game.

.. code-block:: python

   # Start the game
    info = room.start_new_game()

    print(f"Performance score: {info['performanceScore']}")
    print(f"Scores: {info['score']}")


A full-running example can be found in the examples folder.
