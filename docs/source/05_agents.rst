Agents
============================


 .. image:: ../../gitImages/GameCommunicationDiagram_Agents.png
	:alt: Chef's Hat Environment Diagram
	:align: center


The ChefsHatGym implements two types of agents: Players and Spectators.

Players are the agents that actually play the game. They are the ones that receive the game information, and have to send a decision back to the simulator.
Players are implemented using the ChefsHatGym.agents.base_classes.chefs_hat_player.ChefsHatPlayer base interface.

Spectators are special types of agents that only observe the game. They do not have access to any sensitive information from any player, but receive all the game status change (when someone did an action, for example) from the simulator. Spectators are ideal to create passive observer applications, such as automatic narrators or game analysers.
Spectators are implemented using the from ChefsHatGym.agents.base_classes.chefs_hat_spectator.ChefsHatSpectator base interface.

Both Players and Spectators are fully compatible with both local and server rooms, and are fully customizable.

In the next links, you will get more information about each of them, and how to create and customize your own agents.
