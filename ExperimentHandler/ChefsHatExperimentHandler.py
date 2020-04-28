import gym
import numpy

from KEF import ExperimentManager

from KEF import DataSetManager

from ChefsHatEnv import ChefsHatEnv


def runExperiment(numGames=-1, maximumScore=-1, playersAgents=[], experimentDescriptor="",isLogging=True,createDataset=True, isPlotting=True, saveExperimentsIn="", loadModel=[], agentParams=[], rewardFunction ="", plots=[]):

    numMaxCards = 11

    playersNames = []
    for i in range(len(playersAgents)):
     playersNames.append(playersAgents[i].name)

    experimentName = "Player_" + str(len(playersAgents)) + "_Cards_" + str(numMaxCards) + "_games_" + str(numGames) + "TrainingAgents_" + str(playersNames) + "_Reward_" + str(rewardFunction.rewardName)+"_"+experimentDescriptor

    modelDirectory = ""
    if isLogging or createDataset:
        experimentManager = ExperimentManager.ExperimentManager(saveExperimentsIn,
                                                                experimentName,
                                                                verbose=True)
        modelDirectory = experimentManager.modelDirectory

    #Logging
    if isLogging:
        logger = experimentManager.logManager
        logger.newLogSession("Game parameters!")
        logger.write("Max Num Cards:"+ str(numMaxCards))
        logger.write("Players :" + str(len(playersAgents)))
        logger.write("Played games :"+ str(numGames))

    env = gym.make('chefshat-v0') #starting the game Environment
    env.startNewGame(maxCardNumber=numMaxCards, numberPlayers=len(playersAgents), rewardFunction=rewardFunction) # initialize the environment
    env.reset() # to calculate the initial variables

    if isLogging:
        logger.newLogSession("Initializing players: " + str(len(playersAgents)))

    params = []
    if len(agentParams)>0:
        params = agentParams[0]

    #Experimental variables

    players = [] # hold the players of the game
    playersObservingOthers = [] #hold the index of the players that are observign the oponent moves

    for i in range(len(playersAgents)):
         playersAgents[i].startAgent((numMaxCards, env.numberOfCardsPerPlayer,  env.numberOfActions, loadModel[i], params))
         players.append(playersAgents[i])
         if not playersAgents[i].intrinsic == None and playersAgents[i].intrinsic.isUsingOponentMood:
            playersObservingOthers.append(i)

    metrics = []
    qvaluesStore = []
    for a in range (len(playersAgents)):
        qvaluesStore.append([])

        #Log the dataset
        if createDataset:
            experimentManager.dataSetManager.startNewExperiment()

    #Collect game points
    gamePoints = []

    for i in range(len(players)):
        gamePoints.append(0)

    #Check stopping condition is points or numGames
    if numGames == -1:
        numGames = 500000

    #start the experiment
    for game in range(numGames):

        # print ("Starting Game number:" + str(game))
        metricsPerGame = []
        metricsPerGame.append(game) # add the game number

        #Log the dataset
        if createDataset:
            experimentManager.dataSetManager.startNewGame(game, playersNames)

        if isLogging:
            logger.newLogSession("Game : " + str(game))
            logger.write("Environment started.")
            logger.write("Deck: " + str(env.cards))
            for i in range(len(playersAgents)):
                logger.write("Player " + str(i) + ":" + str(env.playersHand[i]))

        if createDataset:
            experimentManager.dataSetManager.dealAction(env.playersHand, game)

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
                experimentManager.dataSetManager.exchangeRolesAction(env.playersHand, roles, (env.currentSpecialAction, env.currentPlayerDeclaredSpecialAction, dishwasherCards, waiterCard, souschefCard, chefCards), game)

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
                totalActions = 0


                if not env.hasPlayerFinished(thisPlayer):
                    validActionPlayer = False

                    #while the action is not valid, loop over the actions until it is valid
                    while not validActionPlayer:
                        state = env.getCurrentPlayerState()
                        cardsInHandN = numpy.nonzero(env.playersHand[thisPlayer])[0]
                        cardsInHand = len(cardsInHandN)

                        #get an action
                        validAction = env.getPossibleActions(thisPlayer)
                        action = players[thisPlayer].getAction((state, validAction))

                        newState, reward, validActionPlayer = env.step(action)
                        newPossibleActions =  env.getPossibleActions(thisPlayer)

                        done = False
                        if validActionPlayer:

                            if env.lastActionPlayers[thisPlayer][0] == DataSetManager.actionFinish:
                                done = True
                                newState =  numpy.zeros(len(state))

                        else:
                            wrongActions = wrongActions+1

                        totalActions = totalActions+1


                        players[thisPlayer].train((state, action, reward, newState, done,
                                                 modelDirectory, game, validAction, newPossibleActions, thisPlayer, env.score))

                    if isLogging:
                        logger.write(" ---  Reward: " + str(reward))
                        logger.write(" ---  Correct actions: " + str(totalActions-wrongActions) + "/" + str(totalActions))
                        logger.write(" ---  Wrong actions: " + str(wrongActions))


                    if createDataset:
                        # if len(players[thisPlayer].QValues) >= 1:
                        #     qvalues = players[thisPlayer].QValues[-1]
                        # else:
                        #     qvalues = []
                        if len(players[thisPlayer].losses) >= 1:
                            loss = players[thisPlayer].losses[-1]
                        else:
                            loss = []

                        playersStatus = []
                        for i in range(len(playersAgents)):
                            playersStatus.append(env.lastActionPlayers[i])

                        # print ("Player " + str(thisPlayer) + " - Wrong: " + str(wrongActions) + " - Total:" + str(totalActions))
                        # print ("Player: " + str(thisPlayer) + " - Round:" + str(env.rounds))
                        experimentManager.dataSetManager.doActionAction(game, thisPlayer, env.rounds,
                                                                        env.lastActionPlayers[thisPlayer], env.board,
                                                                        wrongActions, reward,
                                                                        env.playersHand, roles,
                                                                        env.score, playersStatus,
                                                                        action, loss, totalActions,validAction)

                env.nextPlayer()
                if isLogging:
                    logger.write(" ---  Action: " + str(env.lastActionPlayers[thisPlayer]))
                    logger.write(" ---  Valid Actions: " + str(validAction))
                    logger.write(" ---  Hand: " + str(env.playersHand[thisPlayer]))
                    logger.write(" --- Board After: " + str(env.board))


            env.nextRound() # All players played, now one more round

            pizzaReady = env.isEndRound() # check if the pizza is ready
            if pizzaReady:
                if isLogging:
                    logger.newLogSession("Pizza ready!!!")

                if createDataset:
                    # print ("Pizza!")
                    experimentManager.dataSetManager.doActionPizzaReady(env.rounds,
                                                                    env.board, env.playersHand, roles,
                                                                    env.score, playersStatus, game)
            gameFinished = env.hasGameFinished()


        if isLogging:
            logger.write("Game finished:" + str(gameFinished))

        #saving the metrics
        for p in range(len(playersAgents)):
            metricsPerGame.append(env.score.index(p)) #p_position
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
                if 0 in currentQuarter:
                 passesCount = currentQuarter[0]
                else:
                    passesCount = 0

                discardCount = len(quarter) - passesCount
                metricsPerGame.append(passesCount) #p__q_passes
                metricsPerGame.append(discardCount) #p__q_discard

        env.reset()  # start a new game


        unique, counts = numpy.unique(env.winners, return_counts=True)
        winners = dict(zip(unique, counts))
        print( "Game " + str(game) + " - Victories:" +str(winners) )

        metrics.append(metricsPerGame)

        #Points attribution
        winningPlayerPoint = 0
        for positionIndex in range(len(players)):
            positionPlayer = env.allScores[-1].index(positionIndex)
            points = 3 - positionPlayer
            gamePoints[positionIndex] += points
            if gamePoints[positionIndex] > winningPlayerPoint:
                winningPlayerPoint = gamePoints[positionIndex]

        if maximumScore > -1:
            if winningPlayerPoint >= maximumScore:
                break


    if isLogging or createDataset:
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
            logger.write(" -- Correct Actions: " + str(players[i].totalCorrectAction))

        playerReturn.append(averageRewards) #rewards
        playerReturn.append(env.allWrongActions[i])  # wrong actions
        playerReturn.append(players[i].lastModel)
        playerReturn.append(players[i].totalAction) # total actions per game

        QValues = players[i].QValues
        playerReturn.append(QValues)

        returns.append(playerReturn)


    #Total actions per player
    #Total points per player
    returns.append(gamePoints) #Total score
    returns.append(game)#Total games


    if createDataset:
        experimentManager.dataSetManager.saveFile()

    if createDataset and isPlotting:
        if isLogging:
            logger.newLogSession("Plotting...")
            logger.write("Plots saved in:" + str(experimentManager.plotManager.plotsDirectory))

        qvalueModels = []
        intrinsicMoods = []
        for p in players:
            if not p.intrinsic == None:
                qvalueModels.append(p.actor)
                intrinsicMoods.append(p.intrinsic)

        intrinsicDataset = ""
        if len(intrinsicMoods) >0:
            from MoodyFramework.Mood.Intrinsic import GenerateMoodFromDataset
            GenerateMoodFromDataset.generateMoodFromDataset(intrinsicModels=intrinsicMoods,
                                                            dataset=experimentManager.dataSetManager.currentDataSetFile,
                                                            qModels=qvalueModels, saveDirectory=experimentManager.dataSetManager.dataSetDirectory)
            intrinsicDataset = experimentManager.dataSetManager.dataSetDirectory

        experimentManager.plotManager.generateAllPlots(plots, experimentManager.dataSetManager.currentDataSetFile, game, intrinsicDataset=intrinsicDataset)

    return returns

