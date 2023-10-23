The Chef`s Hat Game and Gym
============================================================

The Chef's Hat Game 
^^^^^^^^^^^^^^^^^^^

During each game there are three phases: Start of the game, Making Pizzas, End of the game. The game starts with the cards been shuffled and dealt with by the players. Then, starting from the second game, the exchange of roles takes place based on the last games' finishing positions. The player who finished first becomes the Chef, the one that finished second becomes the Sous-Chef, the one that finished third becomes the Waiter, and the last one the Dishwasher. Once the roles are exchanged, the exchange of the cards starts. The Dishwasher has to give the two cards with the highest values to the Chef, who in return gives back two cards of their liking. The Waiter has to give their lowest valued card to the Sous-Chef, who in return gives one card of their liking.

If, after the exchange of roles, any of the players have two jokers at hand, they can perform a special action: in the case of the Dishwasher, this is "Food Fight" (the hierarchy is inverted), in case of the other roles it is "Dinner is served" (there will be no card exchange during that game).

Once all of the cards and roles are exchanged, the game starts. The goal of each player is to discard all the cards at hand. They can do this by making a pizza by laying down the cards into the playing field, represented by a pizza dough. The person who possesses a Golden 11 card at hand starts making the first pizza of the game. A pizza is done when no one can, or wants, to lay down any ingredients anymore. A player can play cards by discarding their ingredient cards on the pizza base. To play cards, they need to be rarer (i.e. lowest face values) than the previously played cards. The ingredients are played from highest to the lowest number, which means from 11 to 1. Players can play multiple copies of an ingredient at once, but always have to play an equal or greater amount of copies than the previous player did. If a player cannot (or does not want) to play, they pass until the next pizza starts. A joker card is also available and when played together with other cards, it assumes their value. When played alone, the joker has the highest face value (12). Once everyone has passed, they start a new pizza by cleaning the playing field, and the last player to play an ingredient is the first one to start the new pizza.

.. image:: ../../gitImages/ChefsHatAlgorithm.png
	:alt: Chef's Hat Card Game
	:align: center 
	
The Chef's Hat Gym
^^^^^^^^^^^^^^^^^^^

This library implements the Chef`s Hat game, described above, in a OpenAI GYM environment. As such, we separate the library into three entities: the environment, the room, and the agents.

 The communication between these three entities is controlled by this library, allowing users to focus on the creation and evaluation of different experiments.

 The information flow of the library is exhibit in the image below. 

 .. image:: ../../gitImages/GameCommunicationDiagram.png
	:alt: Chef's Hat Environment Diagram
	:align: center

In the next pages, each of these entities, and their details, is explained.
