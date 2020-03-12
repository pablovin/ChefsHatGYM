import gym
import numpy

import ChefsHatEnv.ChefsHatEnv
from Agents.AgentType import  DUMMY_RANDOM, DUMMY_DISCARDONECARD, DQL_v1, DQL_v2
from Agents.AgentDQL import AgentDQL
from Agents.AgentDQLV2 import AgentDQLV2
from Agents.AgentRandom import AgentRandom
from Agents.AgentAlwaysOneCard import AgentAlwaysOneCard

from KEF import ExperimentManager

from KEF import DataSetManager


def runExperiment(numGames=10, playersAgents=[DQL_v2, DUMMY_RANDOM, DUMMY_RANDOM, DUMMY_RANDOM], experimentDescriptor="",isLogging=True,createDataset=True, isPlotting=True, plotFrequency=1, saveExperimentsIn="", loadModel="", agentParams=[]):

    numMaxCards = 11

    experimentName = "Player_" + str(len(playersAgents)) + "_Cards_" + str(numMaxCards) + "_games_" + str(numGames) + "TrainAgents_" + str(playersAgents) + "_" + experimentDescriptor

    experimentManager = ExperimentManager.ExperimentManager(saveExperimentsIn,
                                                            experimentName,
                                                            verbose=True)
    #Logging
    if isLogging:
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

    if isLogging:
        logger.newLogSession("Initializing players: " + str(len(playersAgents)))

    params = []
    if len(agentParams)>0:
        params = agentParams[0]

    for i in range(len(playersAgents)):

        if playersAgents[i] == DUMMY_RANDOM:
            players.append(AgentRandom(DUMMY_RANDOM,numMaxCards, env.numberOfActions))
        elif  playersAgents[i] == DUMMY_DISCARDONECARD:
            players.append(AgentRandom(DUMMY_DISCARDONECARD,numMaxCards, env.numberOfActions))
        elif playersAgents[i] == DQL_v1:
            players.append(
                AgentDQL(numMaxCards, env.numberOfCardsPerPlayer, env.numberOfActions, loadModel))
        elif playersAgents[i] == DQL_v2:
            players.append(
                AgentDQLV2(numMaxCards, env.numberOfCardsPerPlayer,  env.numberOfActions, loadModel, params))

        # if playersAgents[i] == AgentDQL.name:
        #     players.append(AgentDQL(numMaxCards, env.numberOfCardsPerPlayer, trainingEpoches, env.numberOfActions, loadModel))
        # elif playersAgents[i] == AgentRandom.name:
        #     players.append(AgentRandom("RANDOM",numMaxCards, env.numberOfActions))
        # elif playersAgents[i] == AgentReinforcement.name:
        #     players.append(AgentReinforcement(numMaxCards, env.numberOfCardsPerPlayer, trainingEpoches))
        # elif playersAgents[i] == AgentQL.name:
        #     players.append(AgentQL(numMaxCards, env.numberOfCardsPerPlayer, trainingEpoches, env.numberOfActions))
        # elif playersAgents[i] == AgentAlwaysOneCard.name:
        #     players.append(AgentAlwaysOneCard(numMaxCards, numActions = env.numberOfActions))

    metrics = []
    #start the experiment
    for game in range(numGames):

        print ("Starting Game number:" + str(game))
        metricsPerGame = []
        metricsPerGame.append(game) # add the game number

        #Log the dataset
        if createDataset:
            experimentManager.dataSetManager.startNewGame(game)

        if isLogging:
            logger.newLogSession("Game : " + str(game))
            logger.write("Environment started.")
            logger.write("Deck: " + str(env.cards))
            for i in range(len(playersAgents)):
                logger.write("Player " + str(i) + ":" + str(env.playersHand[i]))

        if createDataset:
            experimentManager.dataSetManager.dealAction(env.playersHand, env.allScores)

        roles = ""
        if game > 0:
            roles = env.currentRoles
            dishwasherCards, waiterCard, souschefCard, chefCards = env.exchangedCards

            if isLogging:
                logger.newLogSession("Changind roles!")

                if not env.currentSpecialAction == "":
                    logger.write("- Player :" + str(env.currentPlayerDeclaredSpecialAction) + " declared "+ str(env.currentSpecialAction) + "!")

                if env.currentSpecialAction == "FoodFight":
                    logger.newLogSession("New roles updated!")

                logger.write("- Waiter: Player " + str(env.currentRoles[3] +1 ))
                logger.write("- Dishwasher Player:" + str(env.currentRoles[2] +1))
                logger.write("- Souschef Player:" + str(env.currentRoles[1] + 1))
                logger.write("- Chef Player:" + str(env.currentRoles[0] + 1))


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
            if isLogging:
                logger.newLogSession("Round:"+str(env.rounds))
            for numPlayer in range(len(playersAgents)):
                thisPlayer = env.currentPlayer

                if isLogging:
                    logger.write(" -- Player " + str(thisPlayer))
                    logger.write(" --- Board Before: " + str(env.board))

                wrongActions = 0
                if not env.hasPlayerFinished(thisPlayer):
                    validActionPlayer = False

                    #while the action is not valid, loop over the actions until it is valid

                    # players[thisPlayer].resetActionsTaken()  # resets the list of actions taken

                    while not validActionPlayer:
                        state = env.getCurrentPlayerState()


                      #  print ("Action:" + str(action))
                      #   if not thisPlayer in trainingAgents:


                        #do an action
                        if "DUMMY" in playersAgents[thisPlayer]:
                            validAction = env.getPossibleActions(thisPlayer)
                            action = players[thisPlayer].getAction(validAction)
                        elif playersAgents[thisPlayer] == DQL_v1:
                            action = players[thisPlayer].getAction(state)
                        elif playersAgents[thisPlayer] == DQL_v2:
                            validAction = env.getPossibleActions(thisPlayer)
                            action = players[thisPlayer].getAction(state, validAction)
                        #
                        newState, reward, validActionPlayer = env.step(action)

                        #learn something
                        if playersAgents[thisPlayer] == DQL_v1:
                            done = False
                            if env.lastActionPlayers[thisPlayer] == DataSetManager.actionFinish:
                                done = True
                            if validActionPlayer:
                               players[thisPlayer].memorize(state, action, reward, newState, done, experimentManager.modelDirectory,game)
                        elif playersAgents[thisPlayer] == DQL_v2:
                            done = False
                            if env.lastActionPlayers[thisPlayer] == DataSetManager.actionFinish:
                                done = True
                            if validActionPlayer:
                               players[thisPlayer].memorize(state, action, reward, newState, done, experimentManager.modelDirectory,game, validAction)


                        # if playersAgents[thisPlayer] == AgentAlwaysOneCard.name:
                        #     if env.playerStartedGame == thisPlayer and env.rounds == 0:
                        #         firstAction = True
                        #     else:
                        #         firstAction = False
                        #
                        #     # action = players[thisPlayer].getAction(state)
                        #     action = players[thisPlayer].getAction(env.playersHand[thisPlayer], firstAction, env.board)
                        # else:
                        #
                        #     action = players[thisPlayer].getAction(state)
                        #     action = players[thisPlayer].getRandomAction(action)


                        # action = players[thisPlayer].getRandomAction(action)


                        # print("action: "+str(numpy.argmax(action)) + " - Valid: " + str(validActionPlayer))

                        # if not playersAgents[thisPlayer] == AgentRandom.name:
                        #     if playersAgents[thisPlayer] == AgentReinforcement.name:
                        #         aIndex = players[thisPlayer].getActionIndex(action)
                        #         players[thisPlayer].memorize(state, aIndex, action, reward)
                        #     elif  playersAgents[thisPlayer] == AgentDQL.name:
                        #         # logger.write("Training the Agent Player " + str(thisPlayer))
                        #         done = False
                        #         if env.lastActionPlayers[thisPlayer] == "Finish":
                        #             done = True
                        #         if validActionPlayer:
                        #            players[thisPlayer].memorize(state, action, reward, newState, done, experimentManager.modelDirectory,game)
                        #     #
                        #     elif playersAgents[thisPlayer] == AgentQL.name:
                        #         if validActionPlayer:
                        #           players[thisPlayer].trainSimpleModel(action, reward, state, newState, experimentManager.modelDirectory,game)

                        if not validActionPlayer :
                            wrongActions = wrongActions+1

                    # players[thisPlayer].resetActionsTaken() #resets the list of actions taken
                    if isLogging:
                        logger.write(" ---  Reward: " + str(reward))
                        logger.write(" ---  Wrong actions: " + str(wrongActions))

                env.nextPlayer()
                if isLogging:
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
                if isLogging:
                    logger.newLogSession("Pizza ready!!!")

                if createDataset:
                    experimentManager.dataSetManager.doActionPizzaReady(env.rounds,
                                                                    env.board, env.playersHand, roles,
                                                                    env.score, playersStatus)
            gameFinished = env.hasGameFinished()

        if isLogging:
            logger.write("Game finished:" + str(gameFinished))

        if isLogging:
            logger.newLogSession("Plotting...")
            logger.write("Plots saved in:" + str(experimentManager.plotManager.plotsDirectory))

        if isPlotting and game%plotFrequency==0:
            experimentManager.plotManager.plotTimeLine(env.playerActionsTimeLine, len(playersAgents), game)

            experimentManager.plotManager.plotNumberOfActions( len(playersAgents), env.playerActionsComplete, game)

        #saving the metrics
        for p in range(len(playersAgents)):
            metricsPerGame.append(env.score.index(0)) #p_position
            metricsPerGame.append(numpy.average(env.currentGameRewards[p]))  # p_averageReward

            currentPlayerActions = []
            for a in range(len(env.playerActionsComplete[p])):

                if env.playerActionsComplete[p][a][1][0] == 0:
                    result = 0
                else:
                    result = len(env.playerActionsComplete[p][a][1])
                currentPlayerActions.append(result)

            quarterInterval = int(len(currentPlayerActions) / 4)

            for q in range(4):
                # first quarter
                quarter = currentPlayerActions[q * quarterInterval:q * quarterInterval + quarterInterval]
                unique, counts = numpy.unique(quarter, return_counts=True)
                currentQuarter = dict(zip(unique, counts))
                passesCount = currentQuarter[0]
                discardCount = len(quarter) - passesCount
                metricsPerGame.append(passesCount) #p__q_passes
                metricsPerGame.append(discardCount) #p__q_discard






        env.reset()  # start a new game


        metrics.append(metricsPerGame)





        if isPlotting and game%plotFrequency==0:
            experimentManager.plotManager.plotRounds(env.allRounds, game)
            experimentManager.plotManager.plotRewardsAll(len(playersAgents), env.allRewards, game)
            experimentManager.plotManager.plotWinners(len(playersAgents), env.winners, game)
            experimentManager.plotManager.plotWrongActions(len(playersAgents), env.allWrongActions, game)
            experimentManager.plotManager.plotFinishPositionAllPlayers(len(playersAgents), env.allScores, env.winners, game)


        # experimentManager.plotManager.plotWrongActions(len(playersAgents), env.allWrongActions, game)
        #
        #


    experimentManager.metricManager.saveMetricPlayer(metrics)
    returns = []
    returns.append(env.allRounds) #total rounds per game
    returns.append(env.startGameFinishingPosition) #starting finishing position

    if isLogging:
        logger.newLogSession("Metrics")
        logger.write("Total Games:" + str(numGames))
        logger.write("Total rounds per game:" + str(env.allRounds))
        logger.write("Starting game/finishing position chances: " + str(env.startGameFinishingPosition))

        for a in range(len(env.startGameFinishingPosition)):
            logger.write(" -- Position "+str(a+1) +" :" + str(float(env.startGameFinishingPosition[a] / numGames)))


        logger.write("Per Player")
    winsPerPlayer = []
    positionsPerPlayer = []
    for i in range(len(playersAgents)):
        playerReturn = []
        if isLogging:
            logger.write(" - Player " + str(i + 1))
        winners = numpy.array(env.winners)
        currentPLayerData = []

        # print("Score:", scoresAll)
        totalWins = 0
        for a in range(len(winners)):
            result = env.allScores[a].index(i) + 1
            currentPLayerData.append(result)
            if result == 1:
                totalWins = totalWins + 1

        winsPerPlayer.append(totalWins)
        positionsPerPlayer.append(currentPLayerData)
        if isLogging:
            logger.write(" -- Wins  "+str(totalWins))
            logger.write(" -- Positions  " + str(currentPLayerData))

        playerReturn.append(totalWins) #total wins
        playerReturn.append(currentPLayerData)  # Positions
        averageRewards = []
        for a in range(len(env.allRewards[i])):
            averageRewards.append(numpy.average(env.allRewards[i][a]))

        if isLogging:
            logger.write(" -- Average Reward Valid Actions: " + str(averageRewards))
            logger.write(" -- Wrong Actions: " + str(env.allWrongActions[i]))

        playerReturn.append(env.allRewards[i][a]) #rewards
        playerReturn.append(env.allWrongActions[i])  # wrong actions

        returns.append(playerReturn)


    return returns

