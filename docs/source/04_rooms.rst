Rooms
========================================================

 .. image:: ../../gitImages/GameCommunicationDiagram_Room.png
	:alt: Chef's Hat Environment Diagram
	:align: center


The Rooms are available in two different settings: a local room, where the room and the agents run in the same process, and a server room that allows the room and the agents to room in different processes.

While the local room is ideal for training and evaluating simulations on artificial agents, the remote room allows the agents to run on different machines, for example, which can extend the type of agents you can use.


Both rooms share the same game parameters:
         		
.. list-table:: **Rooms parameters**
   :widths: auto
   :header-rows: 1

   * - Parameter
     - Description
     - Default Value
   * - room_name
     - name of the room, no special character is allowed
     - 
   * - game_type
     - The type of end game criteria game: "POINTS", based on score or "MATCHES", based on played matches. 
     - "MATCHES"
   * - stop_criteria
     - The max value of "POINTS" or "MATCHES" to determine the end of the game.
     - 10
   * - max_rounds
     - The maximum number of rounds per match, if -1, the players will play until all of them have 0 cards at hand.
     - -1
   * - verbose_console
     - display the room logs in the console
     - False
   * - verbose_log
     - save the room logs in a file
     - False      
   * - game_verbose_console
     - display the simulation logs in the console
     - False
   * - game_verbose_log
     - save the simulation logs in a file
     - False            
   * - save_dataset
     - If the simulation dataset, both the .pkl and .csv files, will be saved.
     - False     
   * - log_directory
     - The directory where the room and game logs will be saved. If none, it will be saved in temp/
     - None
   * - timeout_player_response
     - Amount in seconds that the room will wait until a player do its action. If the timeout is reached, the player will perform a pass action.
     - 5          
     

Local Rooms
^^^^^^^^^^^^^^^^^^^
When initializing a local room, the room parameters have to be passed. As that implement the ChefsHatGym.agents.base_classes.chefs_hat_player.ChefsHatPlayer class, have to be added. And the game can start, by calling the .start_new_game() function:

.. code-block:: python

	
	from ChefsHatGym.gameRooms.chefs_hat_room_local import ChefsHatRoomLocal
	from ChefsHatGym.env import ChefsHatEnv
	from ChefsHatGym.agents.agent_random import AgentRandon
	from ChefsHatGym.agents.spectator_logger import SpectatorLogger

	# Room parameters
	room_name = "Testing_2_Local"

	# Game parameters
	game_type = ChefsHatEnv.GAMETYPE["MATCHES"]
	stop_criteria = 3
	maxRounds = -1

	# Logging information
	verbose_console = True
	verbose_log = True
	game_verbose_console = False
	game_verbose_log = True
	save_dataset = True


	# Start the room
	room = ChefsHatRoomLocal(
		room_name,
		game_type=game_type,
		stop_criteria=stop_criteria,
		max_rounds=maxRounds,
		verbose_console=verbose_console,
		verbose_log=verbose_log,
		game_verbose_console=game_verbose_console,
		game_verbose_log=game_verbose_log,
		save_dataset=save_dataset,
	)

	# Create agents config
	logDirectory = room.get_log_directory()
	agentVerbose = True

	# Create players
	p1 = AgentRandon(name="01", log_directory=logDirectory, verbose_log=agentVerbose)
	p2 = AgentRandon(name="02", log_directory=logDirectory, verbose_log=agentVerbose)
	p3 = AgentRandon(name="03", log_directory=logDirectory, verbose_log=agentVerbose)
	p4 = AgentRandon(name="04", log_directory=logDirectory, verbose_log=agentVerbose)

	# Adding players to the room
	for p in [p1, p2, p3, p4]:
		room.add_player(p)


	# Start the game	
	info = room.start_new_game()

	print(f"Performance score: {info['performanceScore']}")
	print(f"Scores: {info['score']}")


In this example, both dataset and gamelog will be generated from the room and game simulation. After the game is played, a game summary dictionary is passed.


Server Rooms
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
	
To setup a server room, besides using the room parameters, you have to set a url and port for the TCP/IP connection.

The remote room uses sockets to communicate with the agents, mantaining an open channel during the entire game.

The messages shared between the agents and the room follow a pre-defined protocol, and are encapsulated in a dictionary.

The messages from the room are send on a broadcast manner, that updates the agent about the different events that happen during the game, 
or in a response request manner, where the room requires an action from a specific agent. 

For more information on the communication prtocol, please check:

* [Server Room](https://github.com/pablovin/ChefsHatGYM/blob/master/src/ChefsHatGym/gameRooms/chefs_hat_room_server.py)
* [Random Agent](https://github.com/pablovin/ChefsHatGYM/blob/master/src/ChefsHatGym/agents/agent_random.py)


Here is an example of a server room, that will wait for connections on a specified url and port:


.. code-block:: python

	
	from ChefsHatGym.gameRooms.chefs_hat_room_server import ChefsHatRoomServer
	from ChefsHatGym.env import ChefsHatEnv


	# Room parameters
	room_name = "server_room1"
	room_password = "password"
	room_port = 10003
	timeout_player_subscribers = 5  # In seconds
	timeout_player_response = 5  # In seconds

	verbose_console = True
	verbose_log = True
	game_verbose_console = False
	game_verbose_log = True
	save_dataset = True


	# Game parameters
	game_type = ChefsHatEnv.GAMETYPE["MATCHES"]
	stop_criteria = 3
	maxRounds = -1


	# Create the room
	room = ChefsHatRoomServer(
		room_name,
		room_pass=room_password,
		room_port=room_port,
		timeout_player_subscribers=timeout_player_subscribers,
		timeout_player_response=timeout_player_response,
		game_type=game_type,
		stop_criteria=stop_criteria,
		max_rounds=maxRounds,
		verbose_console=verbose_console,
		verbose_log=verbose_log,
		game_verbose_console=game_verbose_console,
		game_verbose_log=game_verbose_log,
		save_dataset=save_dataset,
	)

	room.start_room()

And here an example of agents connecting to the room. Once the room has four valid agents connected, it will start the game.


.. code-block:: python

	from ChefsHatGym.agents.agent_random import AgentRandon

	room_pass = "password"
	room_url = "localhost"
	room_port = 10003


	# Create the players
	p1 = AgentRandon(name="01", verbose_console=True, verbose_log=True)
	p2 = AgentRandon(name="02", verbose_console=True, verbose_log=True)
	p3 = AgentRandon(name="03", verbose_console=True, verbose_log=True)
	p4 = AgentRandon(name="04", verbose_console=True, verbose_log=True)

	# Join agents

	p1.joinGame(room_pass=room_pass, room_url=room_url, room_port=room_port)
	p2.joinGame(room_pass=room_pass, room_url=room_url, room_port=room_port)
	p3.joinGame(room_pass=room_pass, room_url=room_url, room_port=room_port)
	p4.joinGame(room_pass=room_pass, room_url=room_url, room_port=room_port)
