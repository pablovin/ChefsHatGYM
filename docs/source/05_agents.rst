Agents
============================


 .. image:: ../../gitImages/GameCommunicationDiagram_Agents.png
	:alt: Chef's Hat Environment Diagram
	:align: center


The agents accepted by the ChefsHatGym are all implementation of the ChefsHatGym.agents.chefs_hat_agent.ChefsHatAgent interface.
Implement an agent using this interface allows for a full compatibility with both local and remote rooms. 


An agent must implement a series of functions, which are called from the room and environment, you can use them to create your own agent.


**Agent Required Functions**

.. code-block:: python

	def update_start_game(cards : envInfo):
	"""

		This will be called everytime the gane is starting. You might use to update yourself about the game start.

		:param info: the info dictionary
        :type info: dict

	"""

.. code-block:: python

	def get_action(observation : list[float]):
	"""

		Given a certain observation, produce an action.

		:param observation: an array with 228 elements. The first 11 elements represent the board game card placeholder (the pizza area). 
		The game cards are represented by an integer, where 0 (zero) means no card. 
		The following 17 elements (from index 11 to 27) represent the current player hand cards in the sequence. 
		By the end, the last 200 elements (from index 28 to 227) represent all possible actions in the game. 
		The allowed actions for the current player are filled with one, while invalid actions are filled with 0.
		
        :type observation: list

		:return: a hot-encoded array with 200 elements. The chosen action is filled with one, while all other actions are filled with 0.
        :rtype: list[int]

	"""

.. code-block:: python

	def get_exhanged_cards(cards : list[float], amount:int):
	"""

		Given the cards at your hand, chose a given number of cards to be exchanged with other player.W


		:param cards: a list with 17 elements represent the current player hand cards				
        :type cards: list

		:param amount: the amount of cards to be exchanged				
        :type amount: int

		:return: the values of the cards to be exchanged
        :rtype: list[int]

	"""

.. code-block:: python
	
	def do_special_action(cards : info, specialAction):
	"""

		You are able to perform an special action, decide if you want to do it.

		:param info: the info dictionary
        :type info: dict

		:param specialAction: the special action you are allowed to do
        :type specialAction: str

		:return: the decision of do or not do the special action
        :rtype: bool

	"""

.. code-block:: python
	
	def update_my_action(cards : envInfo):
	"""

		This will be called everytime the consequences of your action are calculated by the environment. You might use this to update yourself about them.

		:param info: the info dictionary
        :type info: dict

	"""

.. code-block:: python
	
	def update_action_others(cards : envInfo):
	"""

		This will be called everytime the consequences of the actions of another player are calculated by the environment. You might use this to update yourself about them.

		:param info: the info dictionary
        :type info: dict

	"""

.. code-block:: python
	
	def update_end_match(cards : envInfo):
	"""

		This will be called everytime the match is over. You might use this to update youself about the game.

		:param info: the info dictionary
        :type info: dict

	"""

.. code-block:: python
	
	def get_reward(cards : envInfo):
	"""

		Calculate your reward.

		:param info: the info dictionary
        :type info: dict

	"""	

Random Agent
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The environment comes with a random agent implementation `here <https://github.com/pablovin/ChefsHatGYM/blob/master/src/ChefsHatGym/agents/agent_random.py>`_

You can use it to run random agents in your game, but also to serve as inspiration to create your own agents.
