import gym

import ChefsHatEnv.ChefsHatEnv

from Agents.AgentDQL import AgentDQL
from Agents.AgentRandom import AgentRandom

from KEF import ExperimentManager

# from KEF import RenderManager

# render = RenderManager.RenderManager("/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/testRender/")

#Parameters for the game
playersAgents = [AgentRandom.name, AgentRandom.name, AgentRandom.name, AgentRandom.name]

numMaxCards = 11
trainingEpoches = 500
numGames = 2# amount of training games
experimentDescriptor = "Joker_Trial_QL"

# loadModel = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/Gym_Experiments/Player_4_Cards_11_games_10TrainAgents_['DQL', 'RANDOM', 'RANDOM', 'RANDOM']_Experiment2_GameRules_QL_Condition1_2020-02-28_19:39:20.262467/Model/actor_iteration_8.hd5"

loadModel = ""

isLogging = True #Logg the experiment

# #Parameters for controling the experiment
createDataset = True # weather to save the dataset
saveExperimentsIn = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/Gym_Experiments" # where the experiment will be saved

experimentName = "Player_" + str(len(playersAgents)) + "_Cards_" + str(numMaxCards) + "_games_" + str(numGames) + "TrainAgents_" + str(playersAgents) + "_" + experimentDescriptor

experimentManager = ExperimentManager.ExperimentManager(saveExperimentsIn,
                                                        experimentName,
                                                        verbose=True)
#Logging
logger = experimentManager.logManager
logger.newLogSession("Game parameters!")
logger.write("Max Num Cards:"+ str(numMaxCards))
logger.write("Players :" + str(len(playersAgents)))
logger.write("Played games :"+ str(numGames))

#Experimental variables

players = [] # hold the players of the game

env = gym.make('chefshat-v0') #starting the game Environment
env.startNewGame(maxCardNumber=numMaxCards, numberPlayers=len(playersAgents)) # initialize the environment
env.reset() # to calculate the initial variables

logger.newLogSession("Initializing players: " + str(len(playersAgents)))
for i in range(len(playersAgents)):
    if playersAgents[i] == AgentDQL.name:
        players.append(AgentDQL(numMaxCards, env.numberOfCardsPerPlayer, trainingEpoches, loadModel))
    elif playersAgents[i] == AgentRandom.name:
        players.append(AgentRandom(numMaxCards, env.numberOfActions))

#start the experiment
for game in range(numGames):

    #Log the dataset
    if createDataset:
        experimentManager.dataSetManager.startNewGame(game)

    logger.newLogSession("Game : " + str(game))
    logger.write("Environment started.")

    exchangedCards = env.reset() # start a new game

    if createDataset:
        experimentManager.dataSetManager.dealAction(env.playersHand, env.allScores)

    logger.write("Deck: " + str(env.cards))

    for i in range(len(playersAgents)):
        logger.write("Player " + str(i) + ":" + str(env.playersHand[i]))

    roles = ""
    if game > 0:
        roles = env.currentRoles
        logger.newLogSession("Changind roles!")

        if not env.currentSpecialAction == "":
            logger.write("- Player :" + str(env.currentPlayerDeclaredSpecialAction) + " declared "+ str(env.currentSpecialAction) + "!")

        if env.currentSpecialAction == "FoodFight":
            logger.newLogSession("New roles updated!")

        logger.write("- Waiter: Player " + str(env.currentRoles[3] +1 ))
        logger.write("- Dishwasher Player:" + str(env.currentRoles[2] +1))
        logger.write("- Souschef Player:" + str(env.currentRoles[1] + 1))
        logger.write("- Chef Player:" + str(env.currentRoles[0] + 1))

        dishwasherCards, waiterCard, souschefCard, chefCards = env.exchangedCards
        if env.currentSpecialAction == "" or env.currentSpecialAction == "FoodFight" :

            logger.newLogSession("Changing cards!")
            logger.write("--- Dishwasher gave:" + str(dishwasherCards))
            logger.write("--- Waiter gave:" + str(waiterCard))
            logger.write("--- Souschef gave:" + str(souschefCard))
            logger.write("--- Chef gave:" + str(chefCards))

        if createDataset:
            experimentManager.dataSetManager.exchangeRolesAction(env.playersHand, roles, (env.currentSpecialAction, env.currentPlayerDeclaredSpecialAction, dishwasherCards, waiterCard, souschefCard, chefCards), env.allScores)


    # #Start the game
    gameFinished = env.hasGameFinished()
    #while the game is not over
    while not gameFinished:
        logger.newLogSession("Round:"+str(env.rounds))
        for numPlayer in range(len(playersAgents)):
            thisPlayer = env.currentPlayer
            logger.write(" -- Player " + str(thisPlayer))
            logger.write(" --- Board Before: " + str(env.board))

            wrongActions = 0
            if not env.hasPlayerFinished(thisPlayer):
                validActionPlayer = False

                #while the action is not valid, loop over the actions until it is valid

                players[thisPlayer].resetActionsTaken()  # resets the list of actions taken

                while not validActionPlayer:
                    state = env.getCurrentPlayerState()

                    action = players[thisPlayer].getAction(state)
                  #  print ("Action:" + str(action))
                  #   if not thisPlayer in trainingAgents:
                    action = players[thisPlayer].getRandomAction(action)

                    newState, reward, validActionPlayer = env.step(action)
                    # print("action: "+str(numpy.argmax(action)) + " - Valid: " + str(validActionPlayer))

                    if not playersAgents[thisPlayer] == AgentRandom.name:
                        if  playersAgents[thisPlayer] == AgentDQL.name:
                            # logger.write("Training the Agent Player " + str(thisPlayer))
                            done = False
                            if env.lastActionPlayers[thisPlayer] == "Finish":
                                done = True
                            if wrongActions < 5:
                               players[thisPlayer].memorize(state, action, reward, newState, done, experimentManager.modelDirectory,game)
                        #


                    if not validActionPlayer :
                        wrongActions = wrongActions+1

                players[thisPlayer].resetActionsTaken() #resets the list of actions taken
                logger.write(" ---  Reward: " + str(reward))
                logger.write(" ---  Wrong actions: " + str(wrongActions))

            env.nextPlayer()

            logger.write(" ---  Action: " + str(env.lastActionPlayers[thisPlayer]))
            logger.write(" ---  Hand: " + str(env.playersHand[thisPlayer]))
            logger.write(" --- Board After: " + str(env.board))

            if createDataset:
                playersStatus = []
                for i in range(len(playersAgents)):
                    playersStatus.append(env.lastActionPlayers[i])

                experimentManager.dataSetManager.doActionAction(thisPlayer, env.rounds, env.lastActionPlayers[thisPlayer], env.board, wrongActions, reward , env.playersHand, roles,
                                                                     env.score, playersStatus)

        #input("here")
        env.nextRound() # All players played, now one more round
        pizzaReady = env.isEndRound() # check if the pizza is ready
        if pizzaReady:
            logger.newLogSession("Pizza ready!!!")

            if createDataset:
                experimentManager.dataSetManager.doActionPizzaReady(env.rounds,
                                                                env.board, env.playersHand, roles,
                                                                env.score, playersStatus)


        gameFinished = env.hasGameFinished()
        logger.write("Game finished:" + str(gameFinished))


    logger.newLogSession("Plotting...")
    logger.write("Plots saved in:" + str(experimentManager.plotManager.plotsDirectory))

    # for i in range(len(playersAgents)):
    #     if not playersAgents[i] == AgentRandom.name:
    #         if playersAgents[i] == AgentReinforcement.name:
    #             players[i].trainSimpleModel(experimentManager.modelDirectory,game)
    #         elif playersAgents[i] == AgentDQL.name:
    #             if env.score[0] == i:
    #                 players[i].trainSimpleModel(128, experimentManager.modelDirectory,game)
    #             else:
    #                 players[i].cleanMemory()


    experimentManager.plotManager.plotRewardsAll(len(playersAgents), env.allRewards, game)
    experimentManager.plotManager.plotWrongActions(len(playersAgents), env.allWrongActions, game)
    experimentManager.plotManager.plotHistoryAllPLayers(len(playersAgents), env.allScores, env.winners, game)
    experimentManager.plotManager.plotWinners(len(playersAgents), env.winners, game)

    # render.renderGameStatus(experimentManager.dataSetManager.currentDataSetFile)
    #


    # env.allScores.append([0, 1, 2, 3])

