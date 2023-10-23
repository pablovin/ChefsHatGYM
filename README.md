![Chef's Hat Card Game](gitImages/chefsHatLogo.png)

## ChefsHatGym V2

This repository holds the ChefsHatGym2 environment, which contains all the necessary tools to run, train and evaluate your agents while they play the Chef`s Hat game.

With this library, you will be able to:

* Encapsulate existing agents into the game
* Run the game locally, on your machine
* Connect the game to remote agents (using a pub/sub architecture powered by a Redis server)
* Export experimental results, game summaries and agents behavior on a easy-to-read format
* Evaluate agents using different evaluation tools and visualizations

Full documentation can be found here: [Documentation.](https://chefshatgym.readthedocs.io/en/latest/)

We also provide a list of existing plugins and extensions for this library:

### Chef`s Hat Players Club

The [Chef’s Hat Player’s Club](https://github.com/pablovin/ChefsHatPlayersClub) is a collection of ready-to-use artificial agents. Each of these agents were implemented, evaluated, and discussed in specific peer-reviewed publications and can be used at any time. If you want your agent to be included in the Player’s Club, send us a message.

### Chef`s Hat Play With a Human Plugin
Comming soon...

## The Chef's Hat Card game

![Chef's Hat Card Game](gitImages/cardGame.jpg) 

The Chef's Hat Environment provides a simple and easy-to-use API, based on the OpenAI GYM interface, for implementing, embedding, deploying, and evaluating reinforcement learning agents.

Fora a complete overview on the development of the game, refer to:

- It's Food Fight! Introducing the Chef's Hat Card Game for Affective-Aware HRI (https://arxiv.org/abs/2002.11458)
- You Were Always on My Mind: Introducing Chef’s Hat and COPPER for Personalized Reinforcement Learning (https://www.frontiersin.org/articles/10.3389/frobt.2021.669990/full)
- The Chef's Hat rulebook  [The Chef's Hat rulebook.](gitImages/RulebookMenuv08.pdf)

If you want to have access to the game materials (cards and playing field), please contact us using the contact information at the end of the page.

## Chef`sHatGym2 Simulator

![Chef's Hat Card Game](gitImages/ChefsHat_GYM_-_Example_Random_Agent.gif) 

### Instalation

You can use our pip installation:

```python
   pip install chefshatgym

```

To use the **remote communication**, you need access to a redis server. To install your own redis server, please follow: https://redis.io/docs/getting-started/installation/

For Windows users, [Memurai](https://www.memurai.com/) is an alternative.

Refer to our full [documentation](https://chefshatgym.readthedocs.io/en/latest/) for a complete usage and development guide.
 

### Running a game locally
The basic structure of the simulator is a room, that will host four players, and initialize the game.
ChefsHatGym2 encapsulates the entire room structure, so it is easy to create a game using just a few lines of code:

```python
    # Start the room
    room = ChefsHatRoomLocal(
        room_name="local_room",
        verbose=False,
    )

    # Create the players
    p1 = AgentRandonLocal(name="01")
    p2 = AgentRandonLocal(name="02")
    p3 = AgentRandonLocal(name="03")
    p4 = AgentRandonLocal(name="04")

    # Adding players to the room
    for p in [p1, p2, p3, p4]:
        room.add_player(p)

    # Start the game
    info = room.start_new_game(game_verbose=True)

```

For a more detailed example, check the [examples folder.](https://github.com/pablovin/ChefsHatGYM/tree/master/examples)

### Running a game remotely

ChefsHatGym2 allows for communication with remote agents. It uses a pub/sub architecture, powered by a Redis server.
A remote room structure is provided by the library, as shown in our [examples folder](https://github.com/pablovin/ChefsHatGYM/tree/master/examples/remoteRoom).

### Chefs Hat Agents

ChefsHatGym2 provides an interface to encapsulate agents. It allows the extension of existing agents, but also the creation of new agents. Implementing from this interface, allow your agents to be inserted in any Chef`s Hat game run by the simulator.

Runing an agent from another machine is supported, by the ChefsHatRemote agent interface.

Here are examples of an agent that only select random actions, implementing both local and remote interfaces:
* [local ChefsHatAgent](https://github.com/pablovin/ChefsHatGYM/blob/master/src/ChefsHatGym/agents/local/random_agent_local.py)
* [local ChefsHatAgent](https://github.com/pablovin/ChefsHatGYM/tree/master/src/ChefsHatGym/agents/remote)


## Legacy Plugins and Extensions

 ### Chef's Hat Online (ChefsHatGymV1)
   ![Plots Example](gitImages/exampleOnline.png)
   
The [Chef’s Hat Online](https://github.com/pablovin/ChefsHatOnline) encapsulates the Chef’s Hat Environment and allows a human to play against three agents. The system is built using a web platform, which allows you to deploy it on a web server and run it from any device. The data collected by the Chef’s Hat Online is presented in the same format as the Chef’s Hat Gym, and can be used to train or update agents, but also to leverage human performance.
 
 ### Moody Framework (ChefsHatGymV1)
 
  ![Plots Example](gitImages/MoodPlotsExample.png)
  
 [Moody Framework]( https://github.com/pablovin/MoodyFramework) is a plugin that endowes each agent with an intrinsic state which is impacted by the agent's
  own actions. 
 

 ## Use and distribution policy

All the examples in this repository are distributed under a Non-Comercial license. If you use this environment, you have to agree with the following itens:

- To cite our associated references in any of your publication that make any use of these examples.
- To use the environment for research purpose only.
- To not provide the environment to any second parties.

## Citations

- Barros, P., Yalçın, Ö. N., Tanevska, A., & Sciutti, A. (2023). Incorporating rivalry in reinforcement learning for a competitive game. Neural Computing and Applications, 35(23), 16739-16752.

- Barros, P., & Sciutti, A. (2022). All by Myself: Learning individualized competitive behavior with a contrastive reinforcement learning optimization. Neural Networks, 150, 364-376.

- Barros, P., Yalçın, Ö. N., Tanevska, A., & Sciutti, A. (2022). Incorporating Rivalry in reinforcement learning for a competitive game. Neural Computing and Applications, 1-14.

- Barros, P., Tanevska, A., & Sciutti, A. (2021, January). Learning from learners: Adapting reinforcement learning agents to be competitive in a card game. In 2020 25th International Conference on Pattern Recognition (ICPR) (pp. 2716-2723). IEEE.

- Barros, P., Sciutti, A., Bloem, A. C., Hootsmans, I. M., Opheij, L. M., Toebosch, R. H., & Barakova, E. (2021, March). It's Food Fight! Designing the Chef's Hat Card Game for Affective-Aware HRI. In Companion of the 2021 ACM/IEEE International Conference on Human-Robot Interaction (pp. 524-528).

- Barros, P., Tanevska, A., Cruz, F., & Sciutti, A. (2020, October). Moody Learners-Explaining Competitive Behaviour of Reinforcement Learning Agents. In 2020 Joint IEEE 10th International Conference on Development and Learning and Epigenetic Robotics (ICDL-EpiRob) (pp. 1-8). IEEE.

- Barros, P., Sciutti, A., Bloem, A. C., Hootsmans, I. M., Opheij, L. M., Toebosch, R. H., & Barakova, E. (2021, March). It's food fight! Designing the chef's hat card game for affective-aware HRI. In Companion of the 2021 ACM/IEEE International Conference on Human-Robot Interaction (pp. 524-528).


## Events

### Chef`s Hat Cup: Revenge of the Agent!
Get more information here: https://www.chefshatcup.poli.br/home

### The First Chef's Hat Cup is online!
Get more information here: https://www.whisperproject.eu/chefshat#competition


## Contact

Pablo Barros - pablovin@gmail.com

Alexandre Rodolfo - armp@ecomp.poli.br

- [Twitter](https://twitter.com/PBarros_br)
- [Google Scholar](https://scholar.google.com/citations?user=LU9tpkMAAAAJ)
