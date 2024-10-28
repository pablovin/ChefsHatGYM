Environment
============================================================

 .. image:: ../../gitImages/GameCommunicationDiagram_Env.png
	:alt: Chef's Hat Environment Diagram
	:align: center


The Chef`s Hat Environment implements an OpenAI GYM scenario, and includes a 1:1 representation of the Chef`s Hat Game.	

The environment implement specific action and observation spaces, and calculates scores and performances after the game is done. 

While the gaming is happening, the environment communicates with the Rooms and Agents using a specific dictionary, called info that contains the following information:

.. list-table:: **Dictionary info that is used for communication between the environment and the rooms/agents**
   :widths: auto
   :header-rows: 1

   * - Parameter
     - Type
     - Description
   * - Matches
     - int
     - The current number of matches
   * - Rounds
     - int
     - The current number of rounds       
   * - Player_Names 
     - list
     - list with the names of all Players     
   * - Author_Index
     - int  
     - the index of the player that did this action
   * - Author_Possible_Actions
     - list
     - The possible actions that the author received when he did this action. A list in the format CQJ. Only present to the agent that did the action.
   * - Observation_Before
     - list
     - Full game observation state before this action was done. Only present to the agent that did the action.
   * - Observation_After
     - list
     - Full game observation state after this action was done. Only present to the agent that did the action.            
   * - Action_Valid
     - bool
     - If the action performed by the agent was a valid action based on the game rules.   
   * - Action_Random
     - bool
     - If the action performed by the agent was randomly selected - usually True when the action performed by the agent was invalid. Only present to the agent that did the action.
   * - Action_Index
     - int
     - The index of the selected action over all the 200 possible actions.
   * - Action_Decoded
     - str
     - The action that was done, in the format CQJ.
   * - Is_Pizza
     - bool
     - Did this action caused a pizza.
   * - Pizza_Author
     - int
     - The index o the player that declared pizza.
   * - Finished_Players
     - list
     - List indicating if each player finished the match or not.
   * - Cards_Per_Player 
     - list
     - list with the amount of cards each player has at hand after the action was done.    
   * - Last_action_Per_Player
     - list
     - list with the last action each player did.      
   * - Next_Player 
     - int
     - the next player to play.     
   * - Board_Before
     - list
     - board before the action was done.
   * - Board_After
     - list
     - board after the action was done.
   * - Current_Roles 
     - list
     - list with the current roles of each player. 
   * - Match_Score 
     - list
     - list with the score each player obtained at the end of this match.      
   * - Game_Score 
     - list
     - list with the curernt acumulated game score each player has.            
   * - Game_Performance_Score 
     - list
     - list with the current performanceScore for all players. See bellow the performance score formula.
          

When sending the info dictionary to the players that did not do the action (observe other players and match update actions), both the "actionIsRandom" and "possibleActions" informations are hidden, to avoid leaking of information.

Action and Observation Space
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
	
The environment represents the current game state, called observation, for each player as the concatenation of the cards the player has at hand, the current cards in the playing field, and the possible actions for that move. For each player, there are a total of 200 allowed actions: to discard one card of face value 1 represents one move or to discard 3 cards of face value 1 and a joker is another move, while passing is considered another move. Each player can only do one action per game turn.

Each action taken by a player is validated based on a look-up table, the possible actions, created in real-time based on the player's hand and the cards in the playing field. This is a crucial step to guarantee that a taken action is allowed given the game context and to guarantee that the game rules are maintained. The Figure above illustrates an example of calculated possible actions given a game state. The blue areas mark all the possible action states, while the gray areas mark actions that are not allowed due to the game's mechanics. We observed that, given this particular game state, this player would only be allowed to perform one of three actions (marked in green), while any other action (marked in red) would be considered as invalid and not would be carried on by the simulator.

.. image:: ../../gitImages/possibleActions.png
	:alt: Chef's Hat Card Game
	:align: center


Score and Performance Score
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After each match of the Chef's Hat game, players are rewarded with points (from 3 to 0, depending on the finishing position). We also calculate a performance score, based on the following:

.. code-block:: python

	performanceScore = ((points*10)/rounds)/matches

The performance score allows us to represent better the behavior of an agent in terms of the number of rounds it needed to win the match, and number of matches needed to win the game.

Datasets
^^^^^^^^^^^^^^

The environment allows the generation of datasets, which are .csv and .pkl files that contain all the actions of the entire game in an easy-to-parse format. These datasets can be used to collect data from players, to generate analysis and interpretation about the game, or to log an entire match, for example.
