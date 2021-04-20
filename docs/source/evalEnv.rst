The Tournament Environment
===========================

The Chef's Hat Gym allows artificial agents to play the game, following an OpenAI.GYM-like structure.

To support further the training and evaluation of the agents, we also provide an embedded tournament scenario.

In a tournament, several agents are separated into groups of four players and put to play against each other. The two best agents of each group, advance to the next phase and play against each other. This is repeated until the last game, with the last four players, is played.

The tournament implementation allows for two types of agents: competitive and cooperative ones. Competitive agents are the ones that aim on winning the entire tournament, while cooperative agents must focus on helping a partner win the game. Both agent's types can play the same game and follow the same rules, the difference is on how they are evaluated at the end of the tournament.

Competitive Tournament
^^^^^^^^^^^^^^^^^^^^^^

The competitive agents will be ranked based on how many games they played, and when they play the same game, on their final score. 


Cooperative Tournament
^^^^^^^^^^^^^^^^^^^^^^

For each cooperative agent, the environment creates a single teammate agent, with a random agent implementation. This agent will have the same name as the cooperative agent, concatenated with the term "TeamMate_". Each TeamMate and the cooperative agent are paired together on the first round of the tournament, and the goal of the cooperative agent is to make itself and its TeamMate the two best players of the game. The final rank of the cooperative agents is calculated based on how many games the TeamMate agent played together with the cooperative agent. In the case several pairs of TeamMate and cooperative agent played the same number of games, the final score is used to rank them.

Tournament Structure
^^^^^^^^^^^^^^^^^^^^

The tournament can be instantiated easily:

.. code-block:: python

  tournament = Tournament.Tournament(saveTournamentDirectory, opponentsComp=compAgents, opponentsCoop=coopAgents, oponentsCompCoop=compCoopAgents, threadTimeOut=5,  actionTimeOut=5, gameType=ChefsHatEnv.GAMETYPE["MATCHES"], gameStopCriteria=1)


You have to indicate the list (of iAgent implementations) of the exclusively competitive agents (opponentsComp), exclusively cooperative agents (opponentsCoop), and agents that will be evaluated as both competitive and cooperative (compCoopAgents).

The threadTimeOut and actionTimeOut properties allow us to control how much time each of these agents is allowed to execute a certain function, to maintain the game flow, and give equal treatment to each agent. 

The actionTimeOut property controls how much time, in seconds, each agent has when the getAction() function is called. 
The threadTimeOut propertie controls the time, in seconds, that each agent has to execute the actionUpdate(), observeOthers() and matchUpdate() functions.

An example of the tournament can be found in the examples folder.

Tournament Game Flow
^^^^^^^^^^^^^^^^^^^^

Each game of the tournament, implements the following game flow:

.. code-block:: python

  while not env.gameFinished:
      currentPlayer = group[env.currentPlayer]

      observations = env.getObservation()
 
      info = {"validAction": False}
      
      #While the provided action is not valid, try to obtain an action from the agent.
      while not info["validAction"]:
       
          action = []
          with currentPlayer.timeout(self.actionTimeout):
              action = currentPlayer.getAction(observations)
          if len(action) == 0:
              action = self.getRandomAction(observations[28:])
              
          nextobs, reward, isMatchOver, info = env.step(action)

   
      # If this player just did an action, call the actionUpdate() function.
      with currentPlayer.timeout(self.threadTimeOut):
          currentPlayer.actionUpdate(observations, nextobs, action, reward, info)
          
      # For every player in the group, call the observeOthers() function
      for p in group:
          with p.timeout(self.threadTimeOut):
              p.observeOthers(info)
              
      #After the match is over, call the matchUpdate() function for all players on the group
      if isMatchOver:
          for p in group:
              with p.timeout(self.threadTimeOut):
                  p.matchUpdate(info)



Tournament Score
^^^^^^^^^^^^^^^^

After the execution of the tournament, two score files are created, one for the competitive agents and one for the cooperative agents.

