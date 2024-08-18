Spectators
============================



An Spectator is a special type of player that, when connected to a room, receives all the public game information on real-time. The Spectator does not receive any sensitive information about any player - as the cards in their hands, or how they decide to do an action.
The Spectator agent is a great method to add a third-person perspective to the game - weather by providing some just-in-time analytics about the game, or by providing a visual renderer for watching the game, for example.

All Spectators receive a set of informations from the game simulator, and must implement how to handle them using the interface present in: ChefsHatGym.agents.base_classes.chefs_hat_spectator.ChefsHatSpectator.

The examples folder contains examples on how to add Spectators to both local and server rooms.

In a similar manner as the players, all the functions to send/receive messages are already implemented, and if you want to create your own Spectator you must implement the following abstract methods:

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
	

	def update_game_over(self):
        """This method that is called after the game is over."""

Logger Spectator
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The environment comes with a Spectator implementation that generates a high-level description of what is happening in the game `here <https://github.com/pablovin/ChefsHatGYM/blob/master/src/ChefsHatGym/agents/spectator_logger.py>`_

You can add spectators to a room very similarly to Players:

Here is an example of adding a Spectator in a local room:


.. code-block:: python

	
	from ChefsHatGym.agents.spectator_logger import SpectatorLogger

	# Create spectators
	s1 = SpectatorLogger(name="01", log_directory=logDirectory, verbose_log=agentVerbose)
	s2 = SpectatorLogger(name="02", log_directory=logDirectory, verbose_log=agentVerbose)

	# Adding players to the room
	for s in [s1, s2]:
		room.add_spectator(s)


And here an example of adding an Spectator in a server room:


.. code-block:: python

	from ChefsHatGym.agents.spectator_logger import SpectatorLogger

	room_pass = "password"
	room_url = "localhost"
	room_port = 10003

	# Create the players
	s1 = SpectatorLogger(name="01", verbose_console=True, verbose_log=True)
	s2 = SpectatorLogger(name="02", verbose_console=True, verbose_log=True)

	# Join spectators
	s1.joinGame(room_pass=room_pass, room_url=room_url, room_port=room_port)
	s2.joinGame(room_pass=room_pass, room_url=room_url, room_port=room_port)
