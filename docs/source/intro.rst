Introduction
============

Chef's Hat Game
^^^^^^^^^^^^^^^

Chef's Hat is a cardgame designed with specific HRI requirements in mind, which allows it to be followed and modeled by artificial agents with ease. Also, the game mechanics were designed to evoke different affective interactions within the game, which can be easily perceived and displayed by a robot. Furthermore, the game elements were design to facilitate the extraction of the game state through the use of QR-codes and specific turn taking actions, which do not break the game flow.

Fora a complete overview on the development of the game, refer to:

* `It's Food Fight! Introducing the Chef's Hat Card Game for Affective-Aware HRI <https://arxiv.org/abs/2002.11458>`_
* The Chef's Hat rulebook `The Chef's Hat rulebook <https://github.com/pablovin/ChefsHatGYM/blob/master/gitImages/RulebookMenuv08.pdf>`_.

During each game there are three phases: Start of the game, Making Pizzas, End of the game. The game starts with the cards been shuffled and dealt with the players. Then, starting from the second game, the exchange of roles takes place based on the last games' finishing positions. The player who finished first becomes the Chef, the one that finished second becomes the Sous-Chef, the one that finished third becomes the Waiter and the last one the Dishwasher. Once the roles are exchanged, the exchange of the cards starts. The Dishwasher has to give the two cards with the highest values to the Chef, who in return gives back two cards of their liking. The Waiter has to give their lowest valued card to the Sous-Chef, who in return gives one card of their liking.

If, after the exchange of roles, any of the players have two jokers at hand, they can perform a special action: in case of the Dishwasher, this is "Food Fight" (the hierarchy is inverted), in case of the other roles it is "Dinner is served" (there will be no card exchange during that game).

Once all of the cards and roles are exchanged, the game starts. The goal of each player is to discard all the cards at hand. They can do this by making a pizza by laying down the cards into the playing field, represented by a pizza dough. The person who possesses a Golden 11 card at hand starts making the first pizza of the game. A pizza is done when no one can, or wants, to lay down any ingredients anymore. A player can play cards by discarding their ingredient cards on the pizza base. To play cards, they need to be rarer (i.e. lowest face values) than the previously played cards. The ingredients are played from highest to the lowest number, that means from 11 to 1. Players can play multiple copies of an ingredient at once, but always have to play an equal or greater amount of copies than the previous player did. If a player cannot (or does not want) to play, they pass until the next pizza starts. A joker card is also available and when played together with other cards, it assumes their value. When played alone, the joker has the highest face value (12). Once everyone has passed, they start a new pizza by cleaning the playing field, and the last player to play an ingredient is the first one to start the new pizza.


Competition Description
^^^^^^^^^^^^^^^^^^^^^^^

Most of the current Reinforcement-Learning solutions, although having real-world-inspired scenarios, focus on a direct space-action-reward mapping between the agent's actions and the environment’s state. That translates to agents that can adapt to dynamic scenarios, but, when applied to competitive and/or cooperative cases, fail to assess and deal with the impact of their opponents. In most cases, when these agents choose an action, they do not take into consideration how other agents can affect the state of the scenario. In competitive scenarios, the agents have to learn decisions that a) maximize their chances of winning the game, and b) minimize their adversaries' goals, while in cooperative scenarios b) is inverted. Besides dealing with complex scenarios, such solutions would have to deal with the dynamics between the agents themselves. In this regard, social reinforcement learning is still behind the mainstream applications and demonstrations of the last years.

We recently introduced a card game scenario for reinforcement learning, named Chef’s Hat, which contains specific mechanics that allow complex dynamics between the players to be used in the development of a winning game strategy. A card game scenario allows us to have a naturally-constrained environment and yet obtain responses that are the same as the real-world counterpart application. Chef’s Hat implements game and interaction mechanics that make it easier to be transferred between the real-world scenario and the virtual environment.

Our challenge will be based on Chef’s Hat and will be separated into two tracks: a competitive and a cooperative scenario. In the first track, the participants will use the already available simulation environment to develop the most effective agents to play the Chef’s Hat card game and be the winner. In the second track, they will have to develop an agent that can increase the chances of a dummy agent winning the game.


Challenge Goals
^^^^^^^^^^^^^^^

The challenge has three main goals: To establish state-of-the-art artificial players as benchmarks for the Chef’s Hat Card Game; to provide a crowd-sourced collection of Chef’s Hat gameplay data from a variety of agents and humans, and to help on the advancement and understanding of cooperative and competitive multiplayer interaction with artificial agents.


Challenge Organization
^^^^^^^^^^^^^^^^^^^^^^

Each participant has to produce up to five agents that have learned how to play the game. For each track, the winner will be chosen based on the track’s specific goal. For both tracks, each competitor will pass through the following process:

* **Validation:** Each participant’s agent has to pass the baseline test. It will play a single 15 points game against three baseline competitors. The agent has to win the game to be eligible for the next step. 

* **Track 1:** The agents who pass the validation step will be organized in a competition. Brackets of 4 players will be randomly drawn and separated into a competition cup scenario.  For each bracket, the two best agents will pass to the next phase. The agent who finishes the championship in the first position will be crowned the winner of the first track.

* **Track 2:** The agents who pass the validation step will be organized in a competition. Brackets of 4 players, composed of 2 competitors agents and 2 dummy agents will be randomly drawn and separated into a competition cup scenario. Each competitor agent will be associated with one dummy agent. The two best players of each bracket will advance to the next competition phase. The agent who manages to reach the furthest, together with its associated dummy agent, will be crowned the winner of track 2.


Data Collection and Infrastructure
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We stress that the challenge does not rely on existing datasets, only on the simulation environment. We do provide a data collection tool, The Chef`s Hat Online, composed of a web-platform that allows a human to play the game against three agents, so participants can run their own data collection to improve/evaluate their models.

The entire simulation environment, baseline agents, evaluation protocol, and data collection tool are already available on the links listed below.

We will collect a team name, names, e-mails, and affiliation from all the participants in order to establish their teams. This information will be publicly available, but not used in any manner on the evaluation protocol.


Prizes
^^^^^^

The prizes will be sponsored by the Contact Unit at the Italian Institute of Technology, and will be organized as follows:

* **Competitive Track**
	#. Winner - 300€
	#. Second - 150€
	#. Third - 50€

* **Cooperative Track**
	#. Winner - 300€
	#. Second - 150€
	#. Third - 50€


Challenge Contingency Plan
^^^^^^^^^^^^^^^^^^^^^^^^^^

The entire simulation environment for the challenge is already developed and available. It was tested and used in recent benchmarking experiments. We have, however, a team ready to correct possible bugs and problems that may appear, to avoid delays in the development of the agents.


Simulation Details
^^^^^^^^^^^^^^^^^^

Each participant will have access to the Chef’s Hat simulation environment. It contains all the game’s mechanics implemented, and it allows the training of agents to play the game. The participant teams are forbidden to change the simulation environment by themselves to guarantee fair and equal competition to all participants. All the testing will happen in the standard simulation environment.


Data Collection Environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Together with the simulation environment, each competitor will receive a data collection environment. It is composed of a website that allows a human to play against three virtual agents. The environment collects the same details of the simulation environment and creates a dataset that can be used to train or fine-tune your agents. Also, the simulation environment can be used to assess the performance of your agents against human players. No personal data will be collected, and all the stored and analyzed data is fully anonymous.

The competitors can use the simulation environment as much as they want. We just ask that, together with their final submission, the data collected by the simulation environment has to be submitted. After the competition, we will release all the collected data to establish a dataset for people interested in training agents in our scenario.


Agents
^^^^^^

Each participant will have to develop and distribute at least one training agent. An agent is an algorithm that receives as input the established game state and returns a game-valid action. We also hand in together with the simulation environment a set of fourteen baseline agents distributed as the Chef's Hat Players Club. These agents can help to develop the participants’ models, but also will serve as a baseline for the first step of the competition. 


Knowledge Dissemination
^^^^^^^^^^^^^^^^^^^^^^^

Each participant will have to provide to the organizers a GitHub repository that will contain the agent’s implementation and instantiation, and all the instructions to run and install it. Also, the final submission must contain an Arxiv link with a paper describing their solution for the challenge. All this information will be publicly available.


Available Resources
^^^^^^^^^^^^^^^^^^^

* `Chef’s Hat Simulation Environment <https://github.com/pablovin/ChefsHatGYM>`_
* `Chef’s Hat Online <https://github.com/pablovin/ChefsHatWebServer>`_
* `Chef’s Hat Players Club <https://github.com/pablovin/ChefsHatPlayersClub>`_


Validation Infrastructure
^^^^^^^^^^^^^^^^^^^^^^^^^

To validate both tracks, we will use the instances of each agent given by the participants and run the entire simulation on a local computer. The machine specifications will be given to the participants. The computer will have access to the internet, so the participants’ agents will be able to communicate with an external server for extra processing power.


Publication Format and Review Process
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The participants must submit a short (up to 4 pages) or a long (up to 8 pages) paper describing their challenge candidate solution. We will enforce a single-blind review process and we will guarantee that each paper will receive at least two independent reviewers. The accepted papers will be published on a series related to the challenge at the Proceedings of Machine Learning Research (PLMR). The series was already pre-accepted by the PLMR chief editors. Using PLMR will allow us to achieve high-level publication proceedings, while at the same time the authors will maintain the copyright of their own papers.

We would also like to participate in the post-proceedings with a paper describing the lessons learned with the challenge.
