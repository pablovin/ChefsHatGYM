Learning Agents
============


The IAgent Interface
^^^^^^^^^^^^^^^


You can create a new agent by implementing the iAgent interface. Each new agent must implement the getAction() and getReward() functions, which are necessary to mantain the common gameflow. To create a valid agent, the getAction() function must return a one-hot encoding for the 200 allowed actions. The getReward() must return a float number with the agent's reward.

Besides these methods, each agent can implement the following methods:

Method | Description 
------------ | -------------
actionUpdate | It can be called when an agent performs an action, and can be used to update the agent's decision-making process.
matchUpdate | It can be called when a match is over.
observeOthers | It will be called as soon as any of the opponents makes an action.


Chef's Hat Players Club
^^^^^^^^^^^^^^^

Besides the naive random agent present on the Chef's Hat environment, we also let available the Chef's Hat Player's Club <https://github.com/pablovin/ChefsHatPlayersClub>, a collection of ready-to-use players. Each of these agents where implemented, evaluated and discussed in specific peer-reviewed publications and can be used at any time. If you want your agent to be included to the Player's Club, send us a message.

