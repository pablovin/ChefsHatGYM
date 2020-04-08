# -*- coding: utf-8 -*-
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy

import os

import csv

from KEF import DataSetManager

from matplotlib.collections import PolyCollection


plots = {
    "all": "all",
    "Experiment_Winners":"expWin",
    "Experiment_Rounds":"expRound",
    "Experiment_FinishingPosition":"expFinish",
    "Experiment_ActionsBehavior":"expActionBeh",
    "Experiment_Mood":"expMood",
    "Experiment_MoodNeurons": "expMoodNeurons",
    "Experiment_SelfProbabilitySuccess":"expSelfProb",
    "Experiment_Reward": "expReward",
    "Experiment_SelfReward": "expSelfReward",
    "Experiment_CorrectActions":"expCorrect",
    "Experiment_WrongActions": "expWrong",
    "Experiment_QValues": "expQValue",
    "Experiment_MeanQValues": "expMeanQ",
    "Experiment_Losses": "expLoss",

    "OneGame_NumberOfActions": "oneGNumbAct",
    "OneGame_DiscardBehavior": "oneGDiscard",
    "OneGame_Timeline": "oneGTimeline",

    "SeveralGames_QValues": "sevQVal",
    "SeveralGames_Victories:":"sevVic"


}

"""
#Experiment-related Plots
"""

def plotWinners(numPLayers, winners, iteraction, names, plotDirectory):
    clippedNames = []

    for a in names:
        newName = a.split("_")[0]
        clippedNames.append(newName)

    fig, ax = plt.subplots()
    plt.grid()
    ax.hist(winners, bins=numPLayers, width=0.35, align="right")
    #
    # ax = plt.subplot(111)
    # width = 0.3
    # bins = map(lambda x: x - width / 2, range(1, len(winners) + 1))
    # ax.bar(bins, winners, width=width)
    # ax.set_xticks(map(lambda x: x, range(1, len(winners) + 1)))
    plt.xlim(-1, 5)
    plt.ylim(0, len(winners))
    ax.set_xticklabels(clippedNames)

    ax.set_xlabel('Players')
    ax.set_ylabel('Games')

    # print ("Names:" + str(clippedNames))
    plt.xticks(numpy.arange(0, numPLayers, 1.0))
    # plt.xticks(numpy.arange(0, len(dataY) + 1, 500))

    plt.xlim(0, numPLayers)
    # plt.xlim(0, range(len(dataY)))

    plt.savefig(plotDirectory + "/Game_WinnersHistogram_iteration_" + str(iteraction) + ".png")

    plt.clf()

def plotRounds(allRounds, iteraction, plotDirectory):
    dataY = range(len(allRounds))

    fig = plt.figure()
    ax = fig.add_subplot(111)

    ax.set_xlabel('Games')
    ax.set_ylabel('Number of Rounds')

    # ax.text(1, 1, "TotalWin:"+str(totalWins), style='italic',
    #          bbox={'facecolor': 'red', 'alpha': 0.5, 'pad': 10})

    plt.yticks(numpy.arange(0, numpy.max(allRounds) + 1, 5))
    # plt.xticks(numpy.arange(0, len(dataY) + 1, 1.0))

    plt.ylim(0, numpy.max(allRounds))
    plt.xlim(0, len(dataY))

    plt.grid()
    ax.plot(dataY, allRounds)

    roundsNumber = 0
    if len(allRounds) > 0:
        roundsNumber = allRounds[-1]

    plt.savefig(
        plotDirectory + "/Game_Rounds_iteration_" + str(iteraction) + "_Rounds_" + str(roundsNumber) + ".png")

    plt.clf()

def plotFinishPositions(names, scoresAll, winners, iteraction, plotDirectory):

    # fig = plt.figure()
    # ax = fig.add_subplot(111)

    # Plot winning history all players
    for i in range(len(names)):
        winners = numpy.array(winners)
        currentPLayerData = []

        # print("Score:", scoresAll)
        totalWins = 0
        for a in range(len(winners)):
            result = scoresAll[a].index(i) +1
            currentPLayerData.append(result)
            if result == 1:
                totalWins = totalWins+1

        # print("Player: " + str(i) + " - data:" + str(currentPLayerData))
        dataY = range(len(winners))
        # print("Player: " + str(i) + " - dataY:" + str(dataY))

        fig = plt.figure()
        ax = fig.add_subplot(111)

        ax.set_xlabel('Games')
        ax.set_ylabel('Position')

        # ax.text(1, 1, "TotalWin:"+str(totalWins), style='italic',
        #          bbox={'facecolor': 'red', 'alpha': 0.5, 'pad': 10})

        plt.yticks(numpy.arange(0, len(names)+1, 1.0))
        # plt.xticks(numpy.arange(0, len(dataY) + 1, 1.0))

        plt.ylim(0, len(names)+1)
        plt.xlim(0, len(dataY))
        plt.grid()
        ax.plot(dataY, currentPLayerData)

        #ax.bar(dataY, currentPLayerData, align='center')

        # ax.set_ylim([0, 4])
        #
        # my_xticks = [1, 2, 3 , 4]
        # plt.yticks(dataY, my_xticks)
        # # plt.yticks(np.arange(y.min(), y.max(), 0.005))
        #

        directory = plotDirectory  + "/FinishingPosition_Players/"

        if not os.path.exists(directory):
            os.mkdir(directory)

        plt.savefig(directory + "/HistoryWinners_player_"+str(names[i])+"("+str(i)+")"+"_iteration_"+str(iteraction)+"_TotalWin_"+str(totalWins)+".png")

        fig.clf()

def plotActionBehavior(names, actions, iteraction, plotsDirectory):

    largest = 0
    for i in range(len(names)):
        if len(actions[i]) > largest:
            largest = len(actions[i])



    # Plot discard plot for all players
    for i in range(len(names)):


        allPasses = []
        allDiscards = []

        for ua in range(4):
            allPasses.append([])
            allDiscards.append([])

        for gameIndex in range(len(actions[i])):

            game = actions[i][gameIndex]

        # obtain all the actions of this player in a vector
            actionsTotal = []
            for a in range(len(game)):
                if game[a][0] == DataSetManager.actionPass:
                    actionsTotal.append(0)
                else:
                    actionsTotal.append(1)

            # obtain all the actions of this player in a vector
            quarterInterval = int(len(actionsTotal) / 3)

            labels = ['Q1', 'Q2', 'Q3']

            x = numpy.arange(len(labels))  # the label locations
            width = 0.35  # the width of the bars


            for q in range(3):
                # first quarter
                if q< 2:
                    third = actionsTotal[q * quarterInterval:q * quarterInterval + quarterInterval]
                else:
                    third = actionsTotal[q * quarterInterval:]

                unique, counts = numpy.unique(third, return_counts=True)
                currentQuarter = dict(zip(unique, counts))

                if 0 in currentQuarter:
                 allPasses[q].append(currentQuarter[0])
                else:
                    allPasses[q].append(0)

                if 1 in currentQuarter:
                    allDiscards[q].append(currentQuarter[1])
                else:
                    allDiscards[q].append(0)



        fig, axs = plt.subplots(3, 2)

        y = range(len(allPasses[0]))

        rect1 = axs[0, 0].plot(y, allPasses[0])
        axs[0, 0].set_title('Passes Q1')
        axs[0, 0].set_ylim([0, 12])

        rect2 = axs[1, 0].plot(y, allPasses[1])
        axs[1, 0].set_title('Passes Q2')
        axs[1, 0].set_ylim([0, 12])

        rect3 = axs[2, 0].plot(y, allPasses[2])
        axs[2, 0].set_title('Passes Q3')
        axs[2, 0].set_ylim([0, 12])

        rect5 = axs[0, 1].plot(y, allDiscards[0])
        axs[0, 1].set_title('Discards Q1')
        axs[0, 1].set_ylim([0, 12])

        rect6 = axs[1, 1].plot(y, allDiscards[1])
        axs[1, 1].set_title('Discards Q2')
        axs[1, 1].set_ylim([0, 12])

        rect7 = axs[2, 1].plot(y, allDiscards[2])
        axs[2, 1].set_title('Discards Q3')
        axs[2, 1].set_ylim([0, 12])


        fig.tight_layout(pad=1.0)

        # for ax in axs.flat:
        #     ax.set(xlabel='Quarter', ylabel='Number of Actions')

        # Hide x labels and tick labels for top plots and y ticks for right plots.
        for ax in axs.flat:
            ax.label_outer()

        directory = plotsDirectory + "/ActionBehavior_AllGames_Players/"

        if not os.path.exists(directory):
            os.mkdir(directory)

        plt.savefig(directory + "/ActionBehavior_AllGames_Player_" + str(names[i])+"("+str(i)+")" + "_iteration_" + str(
            iteraction) + ".png", dpi=500)

        fig.clf()

def plotMoodNeurons(names, moodNeurons, moodReading, iteraction, plotsDirectory):

    for i in range(len(names)):

        if len(moodNeurons) > i:

            for index, moodNeuronReadings in enumerate(moodNeurons[i]):

                directory = plotsDirectory + "/MoodNeurons_Players/"
                if not os.path.exists(directory):
                    os.mkdir(directory)

                if index == 0:
                    directory = plotsDirectory + "/MoodNeurons_Players/Self/"
                    plotName = directory + "/Mood_Player_" + str(names[i]) + "(" + str(
                        i) + ")" + "_iteration_" + str(iteraction) + ".png"

                    csvName = directory + "/Mood_Player_" + str(names[i]) + "(" + str(
                        i) + ")" + "_iteration_" + str(iteraction) + ".csv"
                else:
                    directory = plotsDirectory + "/MoodNeurons_Players/Oponents/"

                    newIndexes = numpy.array(range(4)).tolist()
                    newIndexes.remove(i)
                    newNames = names.copy()
                    newNames.remove(names[i])

                    plotName = directory + "/MoodNeurons_Player_" + str(names[i]) + "(" + str(
                        i) + ")" + "_AboutPlayer_" + str(newNames[index - 1]) + "(" + str(
                        newIndexes[index - 1]) + ")" + ")_iteration_" + str(
                        iteraction) + ".png"

                    csvName = directory + "/MoodNeurons_Player_" + str(names[i]) + "(" + str(
                        i) + ")" + "_AboutPlayer_" + str(newNames[index - 1]) + "(" + str(
                        newIndexes[index - 1]) + ")" + ")_iteration_" + str(
                        iteraction) + "..csv"



                if not os.path.exists(directory):
                    os.mkdir(directory)


                thisPlayerNeurons = moodNeuronReadings

                neuronsX = []
                neuronsY = []
                neuronsAge = []

                for indexA, action in enumerate(thisPlayerNeurons):
                    neuronsAction = []
                    for n in action[0]:
                        neuronsX.append(n[0])
                        neuronsY.append(indexA)
                        neuronsAction.append(n[0])

                    for n in action[1]:
                        neuronsAge.append(n)

                neuronsX = numpy.tanh(numpy.array(neuronsX).flatten())
                averageNeuron = moodReading[i][index]
                dataYAverageNeuron = range(len(averageNeuron))


                fig = plt.figure()
                ax = fig.add_subplot(111)

                cmap = plt.cm.rainbow
                norm = matplotlib.colors.Normalize(vmin=0, vmax=1)

                ax.set_xlabel('Actions')
                ax.set_ylabel('Mood Neurons')

                plt.yticks(numpy.arange(0, 1.1, 0.1))
                # plt.xticks(numpy.arange(0, len(dataY) + 1, 2))

                plt.ylim(-0.1, 1.1)
                # plt.xlim(0, range(len(dataY)))
                plt.grid()

                for nindex,neuron in enumerate(neuronsX):
                    alpha = neuronsAge[nindex]
                    ax.scatter(neuronsY[nindex], neuron, alpha = alpha, c="red")

                ax.plot(dataYAverageNeuron,averageNeuron,label="Avg Mood")

                with open(csvName, mode='w') as employee_file:
                    employee_writer = csv.writer(employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

                    employee_writer.writerow(['Action', 'NeuronAverageValue'])

                    for nI, nvalue in enumerate(averageNeuron):
                      employee_writer.writerow([str(nI), str(nvalue)])



                # # sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
                # fig.colorbar(sm)
                plt.legend()
                plt.savefig(plotName)

                fig.clf()


def plotMood(names, moodReading, iteraction, plotsDirectory):

    # Plot mean reward all players
    # fig = plt.figure()
    # ax = fig.add_subplot(111)

    # print ("Rewards: ", numpy.array(rewards).shape)

    for i in range(len(names)):

        if len(moodReading) > i:

            for index, moodReadings in enumerate(moodReading[i]):

                directory = plotsDirectory + "/Mood_Players/"
                if not os.path.exists(directory):
                    os.mkdir(directory)

                if index == 0:
                    directory = plotsDirectory + "/Mood_Players/Self/"
                    plotName = directory + "/Mood_Player_" + str(names[i]) + "(" + str(
                        i) + ")" + "_iteration_" + str(iteraction) + ".png"

                    csvName = directory + "/Mood_Player_" + str(names[i]) + "(" + str(
                        i) + ")" + "_iteration_" + str(iteraction) + ".csv"
                else:
                    directory = plotsDirectory + "/Mood_Players/Oponents/"

                    newIndexes = numpy.array(range(4)).tolist()
                    newIndexes.remove(i)
                    newNames = names.copy()
                    newNames.remove(names[i])
                    # Get the correct name for each plot
                    # nameIndex = (i+index) % 4

                    plotName = directory + "/Mood_Player_" + str(names[i]) + "(" + str(
                        i) + ")" + "_AboutPlayer_" + str(newNames[index - 1]) + "(" + str(
                        newIndexes[index - 1]) + ")" + ")_iteration_" + str(
                        iteraction) + ".png"

                    csvName = directory + "/Mood_Player_" + str(names[i]) + "(" + str(
                        i) + ")" + "_AboutPlayer_" + str(newNames[index - 1]) + "(" + str(
                        newIndexes[index - 1]) + ")" + ")_iteration_" + str(
                        iteraction) + ".csv"

                if not os.path.exists(directory):
                    os.mkdir(directory)

                reward = moodReadings
                dataY = range(len(reward))
                # input("here")

                fig = plt.figure()
                ax = fig.add_subplot(111)

                ax.set_xlabel('Actions')
                ax.set_ylabel('Mood Value')

                plt.yticks(numpy.arange(0, 1.1, 0.1))
                # plt.xticks(numpy.arange(0, len(dataY) + 1, 2))

                plt.ylim(-0.1, 1.1)
                # plt.xlim(0, range(len(dataY)))
                plt.grid()
                ax.plot(dataY, reward)

                plt.savefig(plotName)

                fig.clf()

def plotSelfProbabilitySuccess(names, prob, iteraction, plotsDirectory, name=""):

    for i in range(len(names)):

        if len(prob) >i:

            for index, probabilities in enumerate(prob[i]):
                #
                # print ("---------")
                # print ("I:" + str(names[i]))
                # print ("Index: " + str(index))

                directory = plotsDirectory + "/ProbabilitySuccess_Players/"
                if not os.path.exists(directory):
                    os.mkdir(directory)

                if index == 0:
                    directory = plotsDirectory + "/ProbabilitySuccess_Players/Self/"
                    plotName = directory + "/ProbabilitySuccess_Players" + str(names[i])+"("+str(i)+")" +"_iteration_"+str(iteraction)+".png"
                    csvName =  directory + "/ProbabilitySuccess_Players" + str(names[i])+"("+str(i)+")" +"_iteration_"+str(iteraction)+".csv"
                else:
                    directory = plotsDirectory + "/ProbabilitySuccess_Players/Oponents/"


                    newIndexes = numpy.array(range(4)).tolist()
                    newIndexes.remove(i)
                    newNames = names.copy()
                    newNames.remove(names[i])
                    #Get the correct name for each plot
                    # nameIndex = (i+index) % 4


                    plotName = directory + "/ProbabilitySuccess_Players_" + str(names[i])+"("+str(i)+")" + "_AboutPlayer_"+str(newNames[index-1])+"("+str(newIndexes[index-1])+")" +")_iteration_" + str(
                        iteraction) + ".png"

                    csvName = directory + "/ProbabilitySuccess_Players_" + str(names[i]) + "(" + str(
                        i) + ")" + "_AboutPlayer_" + str(newNames[index - 1]) + "(" + str(
                        newIndexes[index - 1]) + ")" + ")_iteration_" + str(
                        iteraction) + ".csv"

                if not os.path.exists(directory):
                    os.mkdir(directory)


                reward = probabilities
                dataY = range(len(reward))
                # input("here")

                fig = plt.figure()
                ax = fig.add_subplot(111)

                ax.set_xlabel('Actions')
                ax.set_ylabel('Probability')

                plt.yticks(numpy.arange(0, 1.1, 0.1))
                # plt.xticks(numpy.arange(0, len(dataY) + 1, 1))

                plt.ylim(-0.1, 1.1)
                # plt.xlim(0, range(len(dataY)))
                plt.grid()
                ax.plot(dataY, reward)


                with open(csvName, mode='w') as employee_file:
                    employee_writer = csv.writer(employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

                    employee_writer.writerow(['Action', 'NeuronAverageValue'])

                    for nI, nvalue in enumerate(reward):
                      employee_writer.writerow([str(nI), str(nvalue)])

                plt.savefig(plotName)

                fig.clf()

def plotRewardsAll(names, rewards, iteraction, plotsDirectory):

    for i in range(len(names)):

        averageRewards = []
        for a in range(len(rewards[i])):
            averageRewards.append(numpy.average(rewards[i][a]))

        reward = averageRewards

        dataY = range(len(reward))
        # input("here")
        meanReward = numpy.average(numpy.array(reward))

        fig = plt.figure()
        ax = fig.add_subplot(111)

        ax.set_xlabel('Games')
        ax.set_ylabel('Average Reward')

        plt.yticks(numpy.arange(0, 0.2, 0.1))
        # plt.xticks(numpy.arange(0, len(dataY) + 1, 500))

        plt.ylim(-0.1, 0.2)
        # plt.xlim(0, range(len(dataY)))
        plt.grid()
        ax.plot(dataY, reward)

        directory = plotsDirectory + "/Rewards_Players/"

        if not os.path.exists(directory):
            os.mkdir(directory)

        plt.savefig(directory + "/Reward_player_" + str(names[i])+"("+str(i)+")" +"_iteration_"+str(iteraction)+"_meanReward_"+str(meanReward)+".png")

        fig.clf()

def plotSelfRewardsAll(names, meanReward, allReward, iteraction, plotsDirectory):

    for i in range(len(names)):

        directory = plotsDirectory + "/Self_Rewards_Players/"

        if not os.path.exists(directory):
            os.mkdir(directory)

        reward = allReward[i]

        dataY = range(len(reward))


        fig = plt.figure()
        ax = fig.add_subplot(111)

        ax.set_xlabel('Games')
        ax.set_ylabel('Self Reward')

        plt.yticks(numpy.arange(-1, 1, 0.1))
        # plt.xticks(numpy.arange(0, len(dataY) + 1, 500))

        plt.ylim(-1, 1)
        # plt.xlim(0, range(len(dataY)))
        plt.grid()
        ax.plot(dataY, reward)

        plt.savefig(directory + "/Reward_player_" + str(names[i])+"("+str(i)+")" +"_iteration_"+str(iteraction)+".png")

        fig.clf()

        reward = meanReward[i]

        dataY = range(len(reward))
        # input("here")

        fig = plt.figure()
        ax = fig.add_subplot(111)

        ax.set_xlabel('Games')
        ax.set_ylabel('Self Average Reward')

        plt.yticks(numpy.arange(-1, 1, 0.1))
        # plt.xticks(numpy.arange(0, len(dataY) + 1, 500))

        plt.ylim(-1, 1)
        # plt.xlim(0, range(len(dataY)))
        plt.grid()
        ax.plot(dataY, reward)

        plt.savefig(directory + "/AverageReward_player_" + str(names[i]) + "(" + str(i) + ")" + "_iteration_" + str(
            iteraction) +".png")

        fig.clf()

def plotCorrectActions(names, wrongActions, totalActions, iteraction, plotsDirectory):

    for i in range(len(names)):

        correctActionsPlot = wrongActions[i]
        totalCorrectActionsPlot = totalActions[i]

        dataY = range(len(correctActionsPlot))
        dataY2 = range(len(totalCorrectActionsPlot))

        fig = plt.figure()
        ax = fig.add_subplot(111)

        totalCorrectActions = numpy.array(correctActionsPlot).sum()
        totalActionsGame = numpy.array(totalActions[i]).sum()

        ax.set_xlabel('Games')
        ax.set_ylabel('Average Correct Actions')

        ax.plot(dataY, correctActionsPlot, label="Correct Actions ")
        ax.plot(dataY2, totalCorrectActionsPlot, label="Total Actions ")
        ax.legend()
        plt.grid()

        directory = plotsDirectory + "/CorrectActions_Players/"

        if not os.path.exists(directory):
            os.mkdir(directory)

        plt.savefig(directory + "/CorrectActionsPlot_player_" + str(names[i])+"("+str(i)+")" +"_iteration_"+str(iteraction)+"CorrectActions_"+str(totalCorrectActions)+"("+str(totalActionsGame)+").png")

        plt.clf()

def plotWrongActions( names, wrongActions, iteraction, plotsDirectory):

    # Plot wrong actions all players
    for i in range(len(names)):
        wrongActionsPlot = wrongActions[i]

        dataY = range(len(wrongActionsPlot))

        fig = plt.figure()
        ax = fig.add_subplot(111)

        totalWrongActions = numpy.array(wrongActionsPlot).sum()
        # ax.text(0,0, "Wrong actions:"+str(totalWrongActions), style='italic',
        #         bbox={'facecolor': 'red', 'alpha': 0.5, 'pad': 10})

        # print ("DataY:", dataY)
        # print ("WrongActionPlots:", wrongActionsPlot)

        ax.set_xlabel('Games')
        ax.set_ylabel('Average Wrong Actions')

        # plt.yticks(numpy.arange(-1.0, 121, 20))
        # plt.xticks(numpy.arange(0, len(dataY) + 1, 500))

        # plt.ylim(-1., 600)
        # plt.xlim(0, range(len(dataY)))

        plt.plot(dataY, wrongActionsPlot)
        plt.grid()

        directory = plotsDirectory + "/WrongActions_Players/"

        if not os.path.exists(directory):
            os.mkdir(directory)

        plt.savefig(directory + "/WrongActionsPlot_player_" + str(names[i])+"("+str(i)+")" +"_iteration_"+str(iteraction)+"WrongActions_"+str(totalWrongActions)+".png")

        plt.clf()

def plotQValues( names, Qvalues, iteraction, plotsDirectory):

    # Plot selected QValues for an agent.

    for i in range(len(names)):

        directory = plotsDirectory + "/QValues_Players/"

        if not os.path.exists(directory):
            os.mkdir(directory)
        # actionThisPlayer = actions[i]
        qValue = Qvalues[i]
        selectedQValues = []
        summedQValues = []

        for a in qValue:
            sortedA = numpy.array(a)
            sortedA.sort()

            selectedQValues.append(sortedA[-1])
            summedQValues.append(sortedA.sum())

        dataY = range(len(selectedQValues))

        fig, axs = plt.subplots(1, 1)
        axs.plot(dataY, selectedQValues)

        plt.ylim(0, 1)

        plt.savefig(directory + "/BestQValues_player_" + str(names[i])+"("+str(i)+")" + "_iteration_" + str(iteraction) + ".png")

        plt.clf()

        dataY = range(len(summedQValues))
        fig, axs = plt.subplots(1, 1)
        axs.plot(dataY, summedQValues)

        plt.ylim(0, 1)

        plt.savefig(directory + "/SummedQValues_player_" + str(names[i])+"("+str(i)+")" + "_iteration_" + str(iteraction) + ".png")

        plt.clf()

def plotMeanQValuesGames( names, meanQValues, iteraction, plotsDirectory):

    # Plot selected QValues for an agent.

    for i in range(len(names)):

        directory = plotsDirectory + "/Mean_QValues_Players/"

        if not os.path.exists(directory):
            os.mkdir(directory)

        qValue = meanQValues[i]

        dataY = range(len(qValue))

        fig, axs = plt.subplots(1, 1)
        axs.plot(dataY, qValue)

        plt.ylim(0, 1)

        plt.savefig(directory + "/MeanValues_player_" + str(names[i])+"("+str(i)+")" + "_iteration_" + str(iteraction) + ".png")

        plt.clf()


def plotLosses(names, losses, iteraction, name, plotsDirectory):

    # Plot wrong actions all players
    directory = plotsDirectory + "/Losses_" + str(name) + "/"

    if not os.path.exists(directory):
        os.mkdir(directory)


    for i in range(len(names)):

        if len(losses) > i:

            loss = losses[i]
            isList = False

            try:

                if isinstance(loss[0], list):
                    isList = True
                    loss = numpy.array(loss)
                    # print ("Shape:" + str(loss.shape))
                    # loss = numpy.swapaxes(loss, 0, 1)
                    lossActor = []
                    lossCritic = []
                    for u in loss:
                        lossActor.append(u[0])
                        lossCritic.append(u[1])
                    # lossActor = loss[:, 0]
                    # lossCritic =  loss[:, 1]

                    dataY = range(len(lossActor))

            except:
                     isList = False
                     dataY = range(len(loss))

            fig = plt.figure()
            ax = fig.add_subplot(111)

            ax.set_xlabel('Training Steps')
            ax.set_ylabel('Loss')


            if isList:
                fig = plt.figure()
                ax = fig.add_subplot(111)

                ax.set_xlabel('Training Steps')
                ax.set_ylabel('Loss')

                plt.plot(dataY, lossCritic, label="Critic")
                plt.legend()

                plt.savefig(directory + "/"+str(name)+"CriticLoss_player_" + str(names[i])+"("+str(i)+")" + "_iteration_" + str(iteraction) + "WrongActions.png")

                plt.clf()

                fig = plt.figure()
                ax = fig.add_subplot(111)

                ax.set_xlabel('Training Steps')
                ax.set_ylabel('Loss')


                plt.plot(dataY, lossActor, label="Actor")
                plt.legend()
                plt.savefig(
                    directory + "/ActorLoss_player_" + str(names[i])+"("+str(i)+")" + "_iteration_" + str(iteraction) + "WrongActions.png")
            else:
                fig = plt.figure()
                ax = fig.add_subplot(111)

                dataY = range(len(loss))
                ax.set_xlabel('Training Steps')
                ax.set_ylabel('Loss')
                plt.plot(dataY, loss)
                plt.grid()
                plt.savefig(directory + "/Loss_player_" + str(names[i])+"("+str(i)+")" +"_iteration_"+str(iteraction)+"WrongActions.png")

                plt.clf()


"""
#One game-related Plots
"""

def plotNumberOfActions(names, actions, gameNumber, plotsDirectory):

    # fig = plt.figure()
    # ax = fig.add_subplot(111)

    largest = 0
    for i in range(len(names)):
        if len(actions[i]) > largest:
            largest = len(actions[i])

    # Plot discard plot for all players
    for i in range(len(names)):

        fig = plt.figure()
        ax = fig.add_subplot(111)

        #obtain all the actions of this player in a vector
        actionsTotal = []
        for a in range(len(actions[i])):

            if actions[i][a][0] == DataSetManager.actionPass:
                actionsTotal.append(0)
            else:
                actionsTotal.append(1)

        # obtain all the actions of this player in a vector
        quarterInterval = int(len(actionsTotal) / 3)

        labels = ['Q1', 'Q2', 'Q3']
        quartersPass = []
        quarterDiscard = []

        x = numpy.arange(len(labels))  # the label locations
        width = 0.35  # the width of the bars


        for q in range(3):
            # first third
            if q< 2:
                third = actionsTotal[q * quarterInterval:q * quarterInterval + quarterInterval]
            else:
                third = actionsTotal[q * quarterInterval:]

            unique, counts = numpy.unique(third, return_counts=True)
            currentQuarter = dict(zip(unique, counts))

            if 0 in currentQuarter:
             quartersPass.append(currentQuarter[0])
            else:
                quartersPass.append(0)

            if 1 in currentQuarter:
                quarterDiscard.append(currentQuarter[1])
            else:
                quarterDiscard.append(0)


        rects1 = ax.bar(x - width / 2, quartersPass, width, label='Pass')
        rects2 = ax.bar(x + width / 2, quarterDiscard, width, label='Discard')

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel('Number of Actions')
        ax.set_title('Number of Actions')
        ax.set_ylabel('Game Quarters')
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()

        def autolabel(rects):
            """Attach a text label above each bar in *rects*, displaying its height."""
            for rect in rects:
                height = rect.get_height()
                ax.annotate('{}'.format(height),
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom')


        autolabel(rects1)
        autolabel(rects2)

        directory = plotsDirectory + "/ActionBehavior_LastGame_Players/"

        if not os.path.exists(directory):
            os.mkdir(directory)

        plt.savefig(directory + "/ActionBehavior_" + str(names[i])+"("+str(i)+")" + "_Game_"+str(gameNumber)+".png")

        fig.clf()

def plotDiscardBehavior( names, actions, gameNumber, plotsDirectory):

        # fig = plt.figure()
        # ax = fig.add_subplot(111)

        largest = 0
        for i in range(len(names)):
            if len(actions[i]) > largest:
                largest = len(actions[i])

        # Plot discard plot for all players
        for i in range(len(names)):


            fig = plt.figure()
            ax = fig.add_subplot(111)


            actions = numpy.array(actions)
            currentPlayerActions = []

            # print("Score:", scoresAll)
            totalWins = 0
            for a in range(len(actions[i])):

                if actions[i][a][1][0] == 0:
                    result = 0
                else:
                  result = len(actions[i][a][1])
                currentPlayerActions.append(result)


            quarterInterval = int(len(currentPlayerActions)/4)

            for q in range(3):

                # first quarter
                if q < 2:
                   third = currentPlayerActions[q*quarterInterval:q*quarterInterval+quarterInterval]
                else:
                    third = currentPlayerActions[q * quarterInterval:]

                unique, counts = numpy.unique(third, return_counts=True)
                currentQuarter = dict(zip(unique, counts))

                if 0 in currentQuarter:
                    passesCount = currentQuarter[0]
                else:
                    passesCount = 0
                if 1 in currentQuarter:
                    discardCount = len(third) - passesCount
                else:
                    discardCount = 0

                ax.axvline(q*quarterInterval, ymin=0, ymax=11, color="r", linestyle='--', label="Q "+str(q)+" - Passes:" + str(passesCount) + " - Discards:" + str(discardCount))


            ax.legend()


            # print("Player: " + str(i) + " - data:" + str(currentPLayerData))
            dataY = range(len(currentPlayerActions))
            # print("Player: " + str(i) + " - dataY:" + str(dataY))


            ax.set_xlabel('Rounds')
            ax.set_ylabel('Discards')

            # ax.text(1, 1, "TotalWin:"+str(totalWins), style='italic',
            #          bbox={'facecolor': 'red', 'alpha': 0.5, 'pad': 10})

            plt.yticks(numpy.arange(0, 12, 1.0))
            plt.xticks(numpy.arange(0, len(dataY) + 1, 1.0))

            plt.ylim(0, 12)
            plt.xlim(0, largest)
            plt.grid()
            ax.plot(dataY, currentPlayerActions)

            # ax.bar(dataY, currentPLayerData, align='center')

            # ax.set_ylim([0, 4])
            #
            # my_xticks = [1, 2, 3 , 4]
            # plt.yticks(dataY, my_xticks)
            # # plt.yticks(np.arange(y.min(), y.max(), 0.005))
            #

            directory = plotsDirectory + "/DiscardBehavior_LastGame_Players/"

            if not os.path.exists(directory):
                os.mkdir(directory)


            plt.savefig(directory + "/Player_Discards_player_" + str(names[i])+"("+str(i)+")" + "_Game_" + str(
                gameNumber) + ".png")

            fig.clf()

def plotTimeLine (names,actions,  gameNumber=0, plotsDirectory=""):

    largest = 0
    for i in range(len(names)):
        if len(actions[i]) > largest:
            largest = len(actions[i])

    for i in range(len(names)):
        actionsPlot = actions[i]

        data2 = []
        for actionIndex in range(len(actionsPlot)):
            data2.append([0+actionIndex,1+actionIndex, actionsPlot[actionIndex]])

        cats = {DataSetManager.actionPass: 1, DataSetManager.actionDiscard: 2, DataSetManager.actionFinish: 3}
        colormapping = {DataSetManager.actionDiscard: "C0", DataSetManager.actionPass: "C1", DataSetManager.actionFinish: "C2"}

        verts2 = []
        colors2 = []
        for d in data2:
            v = [(d[0], cats[d[2]] - .4),
                 (d[0], cats[d[2]] + .4),
                 (d[1], cats[d[2]] + .4),
                 (d[1], cats[d[2]] - .4),
                 (d[0], cats[d[2]] - .4)]
            verts2.append(v)
            colors2.append(colormapping[d[2]])

        bars = PolyCollection(verts2, facecolors=colors2)

        fig, ax = plt.subplots()
        ax.add_collection(bars)
        ax.autoscale()
        ax.set_xlabel('Actions')
        ax.set_yticks([1, 2, 3])
        ax.set_yticklabels([DataSetManager.actionDiscard, DataSetManager.actionPass,DataSetManager.actionFinish])


        directory = plotsDirectory + "/TimeLine_LastGame_Players"

        if not os.path.exists(directory):
            os.mkdir(directory)

        plt.savefig(directory  + "/Game_TimeLine_Game_"+str(gameNumber)+"_Player_"+str(names[i])+"("+str(i)+")"+".png")

        fig.clf()


"""
#Several Experiments related Plots
"""

def plotQValuesOverSeveralGames(numPLayers, Qvalues, experimentName, saveDirectory):
    # Plot selected QValues for an agent.

    for i in range(numPLayers):
        # actionThisPlayer = actions[i]
        qValue = Qvalues[i]

        if len(qValue) > 1:
            fig, axs = plt.subplots(1, 1)
            axs.set_title('Best Q-Value')
            gamenumber  = 0
            for qvalueGame in qValue:
                gamenumber = gamenumber+1
                maxQValues = []

                for qvalueAction in qvalueGame:
                    maxQValues.append(numpy.max(qvalueAction))

                # yinterp = numpy.interp(range(100), range(len(maxQValues)), maxQValues)
                # dataY = range(len(yinterp))
                rect1 = axs.plot(range(len(maxQValues)), maxQValues)

            plt.ylim(0, 1)
            plt.legend()

            plt.savefig(saveDirectory + "/"+experimentName+"_SelectedQValues_player_" + str(i) + ".png")

            plt.clf()


def plotVictoriesTotal(winsP1, winsP2, winsP3, winsP4, maxNumGames, experimentName, savingFolder):
    fig, ax = plt.subplots()

    x = numpy.arange(4)  # the number of players

    averageP1 = numpy.average(numpy.array(winsP1))
    averageP1 = float("{0:.2f}".format(averageP1))
    stdP1 = numpy.std(winsP1)
    stdP1 = float("{0:.2f}".format(stdP1))

    averageP2 = numpy.average(numpy.array(winsP2))
    averageP2 = float("{0:.2f}".format(averageP2))
    stdP2 = numpy.std(winsP2)
    stdP2 = float("{0:.2f}".format(stdP2))

    averageP3 = numpy.average(numpy.array(winsP3))
    averageP3 = float("{0:.2f}".format(averageP3))
    stdP3 = numpy.std(winsP3)
    stdP3 = float("{0:.2f}".format(stdP3))

    averageP4 = numpy.average(numpy.array(winsP4))
    averageP4 = float("{0:.2f}".format(averageP4))
    stdP4 = numpy.std(winsP4)
    stdP4 = float("{0:.2f}".format(stdP4))
    width = 0.35
    rects1 = ax.bar(1, averageP1, width=width)
    rects2 = ax.bar(2, averageP2, width=width)
    rects3 = ax.bar(3, averageP3, width=width)
    rects4 = ax.bar(4, averageP4, width=width)

    plt.ylim(0, maxNumGames)
    plt.xlim(0, 5)

    def autolabel(rects, std):
        """Attach a text label above each bar in *rects*, displaying its height."""

        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(height) + " (+/- " + str(std)+")",
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')

    autolabel(rects1, stdP1)
    autolabel(rects2, stdP2)
    autolabel(rects3, stdP3)
    autolabel(rects4, stdP4)

    plt.savefig(savingFolder + "/" + str(experimentName) + "_TotalVictories.png")

    plt.clf()


class PlotManager():

    @property
    def plotsDirectory(self):
        return self._plotsDirectory

    def __init__(self, plotDirectory):

        self._plotsDirectory = plotDirectory


    def generateSingleGame(self, plotsToGenerate, env,players, gameRound):

        if len(plotsToGenerate) >= 1:
            if plotsToGenerate[0] == plots["all"]:
                plotsToGenerate = []
                for  i in plots.keys() :
                    plotsToGenerate.append(plots[i])

            agentNames = []
            for index, p in enumerate(players):
                agentNames.append(p.name+"_"+str(index))

            if plots["OneGame_NumberOfActions"] in plotsToGenerate:
                plotNumberOfActions(agentNames, env.playerActionsComplete, gameRound, self.plotsDirectory)

            if plots["OneGame_DiscardBehavior"] in plotsToGenerate:
                plotDiscardBehavior(agentNames, env.playerActionsComplete, gameRound, self.plotsDirectory)

            if plots["OneGame_Timeline"] in plotsToGenerate:
                plotTimeLine(agentNames, env.playerActionsTimeLine, gameRound, self.plotsDirectory)

    def generateExperimentPlots(self, plotsToGenerate, env, players, gameRound):

        if len(plotsToGenerate) >= 1:
            if plotsToGenerate[0] == plots["all"]:
                plotsToGenerate = []
                for  i in plots.keys():
                    plotsToGenerate.append(plots[i])


            agentNames = []
            moodReadings = []
            moodNeurons = []
            selfProbabilities = []
            selfProbabilitiesNames = []
            correctActions = []
            totalActions = []
            qvalues = []
            losses = []
            lossesPModel = []
            meanQValues = []

            selfReward = []
            selfRewardAvg = []

            for index, p in enumerate(players):
                agentNames.append(p.name+"_"+str(index))
                correctActions.append(p.totalCorrectAction)
                totalActions.append(p.totalAction)
                qvalues.append(p.QValues)
                losses.append(p.losses)
                meanQValues.append(p.MeanQValuesPerGame)
                selfReward.append(p.selfReward)
                selfRewardAvg.append(p.meanReward)
                if not p.intrinsic == None:
                    selfProbabilities.append(p.intrinsic.probabilities)
                    moodReadings.append(p.intrinsic.moodReadings)
                    selfProbabilitiesNames.append(p.intrinsic.selfConfidenceType)
                    moodNeurons.append(p.intrinsic.moodNeurons)
                    if not p.intrinsic.pModel == None:
                        lossesPModel.append(p.intrinsic.pModel.losses)

            if plots["Experiment_Winners"] in plotsToGenerate:
                plotWinners(len(agentNames), env.winners, gameRound, agentNames, self._plotsDirectory)

            if plots["Experiment_Rounds"] in plotsToGenerate:
                plotRounds(env.allRounds, gameRound, self._plotsDirectory)

            if plots["Experiment_FinishingPosition"] in plotsToGenerate:
                plotFinishPositions(agentNames, env.allScores, env.winners, gameRound, self._plotsDirectory)

            if plots["Experiment_ActionsBehavior"] in plotsToGenerate:
                plotActionBehavior(agentNames, env.playerActionsCompleteAllGames, gameRound, self._plotsDirectory)

            if plots["Experiment_Mood"] in plotsToGenerate:
                plotMood(agentNames, moodReadings, gameRound,  self._plotsDirectory)

            if plots["Experiment_MoodNeurons"] in plotsToGenerate:
                plotMoodNeurons(agentNames, moodNeurons, moodReadings, gameRound, self._plotsDirectory)

            if plots["Experiment_SelfProbabilitySuccess"] in plotsToGenerate:
                plotSelfProbabilitySuccess(agentNames, selfProbabilities, gameRound, self._plotsDirectory, name=selfProbabilitiesNames)

            if plots["Experiment_Reward"] in plotsToGenerate:
                plotRewardsAll(agentNames, env.allRewards, gameRound, self._plotsDirectory)

            if plots["Experiment_CorrectActions"] in plotsToGenerate:
                plotCorrectActions(agentNames, env.allWrongActions, totalActions, gameRound, self._plotsDirectory)

            if plots["Experiment_WrongActions"] in plotsToGenerate:
                plotWrongActions( agentNames, env.allWrongActions, gameRound, self._plotsDirectory)

            if plots["Experiment_QValues"] in plotsToGenerate:
                plotQValues( agentNames, qvalues, gameRound, self._plotsDirectory)

            if plots["Experiment_Losses"] in plotsToGenerate:
                plotLosses(agentNames, losses, gameRound, "Player", self._plotsDirectory)
                plotLosses(agentNames, lossesPModel, gameRound, "PModel", self._plotsDirectory)

            if plots["Experiment_MeanQValues"] in plotsToGenerate:
                plotMeanQValuesGames( agentNames, meanQValues, gameRound, self._plotsDirectory)

            if plots["Experiment_SelfReward"] in plotsToGenerate:
                plotSelfRewardsAll(agentNames, selfRewardAvg, selfReward, gameRound, self._plotsDirectory)



