Players
============================



A Player is the workforce of the ChefsHatGym. The players will make all the actions required by the simulator. And as such, they need to implement some abstract methods found on the agent base class: ChefsHatGym.agents.base_classes.chefs_hat_player.ChefsHatPlayer.

An agent receives messages from the game simulator, and needs to send responses. All the functions to send/receive messages are already implemented, and if you want to create your own agen you must implement the following abstract methods:

**Agent Required Functions**

.. code-block:: python

	def update_start_match(self, cards: list[float], players : list[str] , starting_player : int):
	"""

		This will be called everytime the gamee is starting. You might use to update yourself about the game start.

		:param cards: Cards at hand at the begining of the match
        :type cards: list[float]

        
        :param starting_player: the names of the starting players
        :type starting_player: list[str]        

        :param starting_player: the index of the starting player
        :type starting_player: list[float]    

	"""



	def get_action(self, observation : list[float]):
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


	def get_exhanged_cards(self, cards : list[float], amount:int):
	"""

		Given the cards at your hand, chose a given number of cards to be exchanged with other player.W


		:param cards: a list with 17 elements represent the current player hand cards				
        :type cards: list

		:param amount: the amount of cards to be exchanged				
        :type amount: int

		:return: the values of the cards to be exchanged
        :rtype: list[int]

	"""
	
	def do_special_action(self, cards : info, specialAction):
	"""

		You are able to perform an special action, decide if you want to do it.

		:param info: the info dictionary
        :type info: dict

		:param specialAction: the special action you are allowed to do
        :type specialAction: str

		:return: the decision of do or not do the special action
        :rtype: bool

	"""
	
	def update_my_action(self, cards : envInfo):
	"""

		This will be called everytime the consequences of your action are calculated by the environment. You might use this to update yourself about them.

		:param info: the info dictionary
        :type info: dict

	"""

	def update_action_others(self, cards : envInfo):
	"""

		This will be called everytime the consequences of the actions of another player are calculated by the environment. You might use this to update yourself about them.

		:param info: the info dictionary
        :type info: dict

	"""

	def update_end_match(self, cards : envInfo):
	"""

		This will be called everytime the match is over. You might use this to update youself about the game.

		:param info: the info dictionary
        :type info: dict

	"""
	
	def get_reward(self, cards : envInfo):
	"""

		Calculate your reward.

		:param info: the info dictionary
        :type info: dict

	"""	

	def update_game_over(self):
        """This method that is called after the game is over."""

Random Agent
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The environment comes with a random agent implementation `here <https://github.com/pablovin/ChefsHatGYM/blob/master/src/ChefsHatGym/agents/agent_random.py>`_

You can use it to run random agents in your game, but also to serve as inspiration to create your own agents.


Chef`s Hat Players Club
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We also provide a large amount of different agents, in the form of an agent collection:
`Players Club` <https://github.com/pablovin/ChefsHatPlayersClub>`_


This collection contains more than 30 different agents, implemented using a various techniques: from traditional machine learning, to game-based heuristic methods. All these agents are fully compatible with the Chef`s Hat simulator.