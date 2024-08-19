Dataset
============================

You can generate, for every Chef\\`s Hat simulation, a dataset that contains all the actions taken by all the agents playing the game.

The gane dataset is a great resource for studying agent behavior, extracting game statistics and much more.

Using the 'save_dataset' parameter on any game room, the dataset is saved on the 'log_directory/Dataset' directory. It will be saved in two formats: an easily redable .csv file, and a easily processable .pkl pandas Dataframe.

Dataset Structure
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The game dataset has the following columns:


.. list-table:: **Dataset Columns**
   :widths: auto
   :header-rows: 1

   * - Parameter
     - Description     
   * - index
     - It saves the date on which the action happened.     
   * - round_number
     - The number of the round that the action happened. Everytime someone declares a pizza, a new round is computed.
   * - agent_names
     - The name and order of the agents thaat are currently playing the game.     
   * - source
     - Indicates if it was an agent, or the system, who did the action    
   * - action_type
     - Displays the action type: START_EXPERIMENT, NEW_MATCH, DEAL_CARDS, DISCARD, DECLARE_PIZZA, END_MATCH, CARD_EXCHANGE, DECLARE_SPECIAL_ACTION, END_EXPERIMENT     
   * - action_description
     - Gives more information for each action. If it was a discard action, it follows the standard action representation notation: C11;Q1;J0 = 1x card value 11, with 0 jokers.      
   * - player_finished
     - Indicates if the player that did this action finished all the cards at his hand.     
   * - player_hands
     - Shows the current cards at every player hands, following the format [player1[], player2[], player3[], player4[]]     
   * - board_before
     - The board before the player made his action     
   * - board_after
     - The board after the player made his action          
   * - possible_actions
     - Display all the possible actions that player could do, following the standard action representation notation.
   * - current_roles
     - Display the current roles of each player in the format [player1, player2, player3, player4].
   * - match_score
     - Display the score of this match in the format [player1, player2, player3, player4]. 
   * - game_score
     - Display the cumulative score of the entire game in the format [player1, player2, player3, player4].      
   * - game_performance_score
     - Display the cumulative game performance of the entire game in the format [player1, player2, player3, player4].            


Every row of the dataset represents one action during the game. And for each action, there are specific information that are stored on the dataset rows.

The action flow within the dataset is as follows:

.. code-block:: python


  action_type = "NEW_EXPERIMENT"# Information saved in this row: match_number, game_score, current_roles
  
  while (not stop_criteria):
      action_type ="NEW_MATCH" # Information saved in this row: current_roles, game_score
      action_type ="DEAL_CARDS" # Information saved in this row:  match_number, player_hands
      action_type ="DECLARE_SPECIAL_ACTION"# (only if someone declare it). match_number, source, current_roles, action_description (which special action was declared)
      action_type = "CARD_EXCHANGE"# (only after the first match). Information saved in this row: match_number, action_description (who gave cards to who), and updated players_hand
      
      
      while players not finished:
        action_type = "DISCARD"# Information saved in this row: match_numner, game_number, source (author of the discard), action description (the discarded cards/pass), player hands, board before, board after, possible actions, and if this player has finished his cards or not
        if pizza:
          action_type= "PIZZA" # Information saved in this row: match_number, round_numner, source(author of the pizza)


      action_type= "END_MATCH" #Information saved in this row: match_score, current_roles
  
  action_type = "END_EXPERIMENT"#Information saved in this row: current_roles, game_score, performance_score

 
