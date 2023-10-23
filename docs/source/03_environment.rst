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
   * - actionIsRandom
     - bool
     - If the action performed by the agent was randomly selected - usually True when the action performed by the agent was invalid.
   * - matches
     - int
     - The current number of matches
   * - rounds
     - int
     - The current number of rounds   
   * - score
     - list
     - the current score for all players
   * - performanceScore
     - list
     - the current performanceScore for all players  
   * - thisPlayer
     - int  
     - the index of the player that did the action
   * - thisPlayerFinished
     - bool
     - if the player that did this action finished the match
   * - isPizzaReady
     - bool
     - if the pizza is ready after this action
   * - boardBefore
     - list
     - board before the action was done
   * - boardAfter
     - list
     - board after the action was done
   * - board
     - list
     - the current board
   * - possibleActions
     - list
     - the indices of all possible actions that the player could have done during this action
   * - action
     - list
     - the action the player did
   * - thisPlayerPosition
     - int
     - the position this player is in the score
   * - lastPlayerAction 
     - list
     - the previous action all the players did
   * - lastActionPlayers 
     - list
     - all the previous actions this player did
   * - lastActionTypes 
     - list
     - all the types of the previous actions all players did
   * - RemainingCardsPerPlayer 
     - list
     - the amount of cards each player has at hand after the action was done
   * - players 
     - list
     - list of current players names
   * - currentRoles 
     - list
     - list of current players roles
   * - currentPlayer 
     - int
     - the next player to play               

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
