# -*- coding: utf-8 -*-
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy
import pandas as pd

import os

import csv

from ChefsHatGym.KEF import DataSetManager
from ChefsHatGym.KEF.DataSetManager import actionFinish, actionPass, actionDiscard, actionDeal, actionPizzaReady

from matplotlib.collections import PolyCollection
import matplotlib.patches as mpatches


plots = {
    "all": "all",
    "Experiment_Winners":"expWin",
    "Experiment_Rounds":"expRound",
    "Experiment_Points":"expPoints",
    "Experiment_TotalActions":"expTotalActionsActions",
    "Experiment_FinishingPosition":"expFinish",
    "Experiment_ActionsBehavior":"expActionBeh",

    "Experiment_Mood":"expMood",
    "Experiment_MoodNeurons": "expNeuronsMood",
    "Experiment_SelfProbabilitySuccess":"expSelfProb",
    "Experiment_MoodFaces": "expFacesMood",
    "Experiment_TimeLimeMood": "timelineMood",

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

    plt.yticks(numpy.arange(0, numpy.max(allRounds) + 2, 5))
    # plt.xticks(numpy.arange(0, len(dataY) + 1, 1.0))

    plt.ylim(0, numpy.max(allRounds)+2)
    plt.xlim(0, len(dataY))

    plt.grid()
    ax.plot(dataY, allRounds)

    roundsNumber = 0
    if len(allRounds) > 0:
        roundsNumber = allRounds[-1]

    plt.savefig(
        plotDirectory + "/Game_Rounds_iteration_" + str(iteraction) + "_Rounds_" + str(roundsNumber) + ".png")

    plt.clf()

def plotPoints(names, pointsAll, iteraction, plotDirectory):

    # Plot winning history all players
    for i in range(len(names)):

        points = pointsAll[i]

        dataY = range(len(points))

        fig = plt.figure()
        ax = fig.add_subplot(111)

        ax.set_xlabel('Games')
        ax.set_ylabel('Points')

        plt.yticks(numpy.arange(0, 20, 1))
        # plt.xticks(numpy.arange(0, len(dataY) + 1, 1.0))

        plt.ylim(0, 20)
        plt.xlim(0, len(dataY))
        plt.grid()
        ax.plot(dataY, points)

        directory = plotDirectory  + "/Points_Players/"

        if not os.path.exists(directory):
            os.mkdir(directory)

        plt.savefig(directory + "/Points_player_"+str(names[i])+"("+str(i)+")"+"_iteration_"+str(iteraction)+".png")

        fig.clf()

def plotTotalActions(names, totalActionsAll, iteraction, plotDirectory):

    # Plot winning history all players
    for i in range(len(names)):

        actions = totalActionsAll[i]

        dataY = range(len(actions))

        fig = plt.figure()
        ax = fig.add_subplot(111)

        ax.set_xlabel('Games')
        ax.set_ylabel('Actions')

        plt.xlim(0, len(dataY))
        plt.grid()
        ax.plot(dataY, actions)

        directory = plotDirectory  + "/TotalActions_Players/"

        if not os.path.exists(directory):
            os.mkdir(directory)

        plt.savefig(directory + "/TotalActions_player_"+str(names[i])+"("+str(i)+")"+"_iteration_"+str(iteraction)+".png")

        fig.clf()

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

def plotTimeLineMood(names, moodNeurons, moodReading, iteraction, playersAction, totalActions, totalColors, arousalValenceInput, selfExpectation, plotsDirectory):



    # ax[0].invert_yaxis()
    # ax[0].xaxis.set_visible(False)
    # ax[0].set_xlim(0, len(moodReading[0]))
    #
    # for indexPlayer, player in enumerate(names):
    #     player1Actions = totalActions[indexPlayer]
    #     player1Colors = totalColors[indexPlayer]
    #     data = numpy.array(player1Actions)
    #     data_cum = data.cumsum(axis=0)
    #
    #     for i, (colname, color) in enumerate(zip(player1Actions, player1Colors)):
    #         widths = data[i]
    #         starts = data_cum[i] - widths
    #
    #         ax[0].barh(list([player]), widths, left=starts, height=1,
    #                    label=colname, color=color)
    #
    # fig.set_size_inches(21.0, 10.5)
    # fig.tight_layout(pad=1.0)
    #
    # green = mpatches.Patch(color='green', label='Discard')
    # blue = mpatches.Patch(color='blue', label='Pass')
    # orange = mpatches.Patch(color='orange', label='Pizza')
    # red = mpatches.Patch(color='red', label='Finish')
    # ax[0].legend(handles=[green, blue, orange, red])
    #

    for i in range(len(names)):
        moodReading = numpy.array(moodReading)
        # print ("Name:"  + str(names[i]) + " - "+str(moodReading[0]))
        if len(moodReading[i]) > 0:

            directory = plotsDirectory + "/TimeLine_MoodNeurons_Players/"
            if not os.path.exists(directory):
                os.mkdir(directory)
            plotName = directory + "/Mood_Player_" + str(names[i]) + "(" + str(
                i) + ")" + "_iteration_" + str(iteraction) + ".png"

            thisPlayerNeurons = moodNeurons[i]
            moodReading = numpy.array(moodReading)
            neuronsPleasureX = []
            neuronsArousalX = []
            neuronsY = []
            neuronsAge = []

            for indexA, action in enumerate(thisPlayerNeurons):

                for n in action[0]:
                    neuronsArousalX.append(n[0])
                    neuronsPleasureX.append(n[1])
                    neuronsY.append(indexA)

                for n in action[1]:
                    neuronsAge.append(n)


            averageNeuronA = numpy.array(moodReading[i])[:, 0]
            averageNeuronP = numpy.array(moodReading[i])[:, 1]
            dataYAverageNeuron = range(len(averageNeuronA))


            cmap = plt.cm.rainbow
            norm = matplotlib.colors.Normalize(vmin=0, vmax=1)
            fig, ax = plt.subplots(3, 1)
            ax[0].set_xlabel('Actions')
            ax[0].set_ylabel('Self Expectation')
            ax[0].set_yticks(numpy.arange(0, 1.1, 0.1))
            ax[0].set_xlim(0, len(thisPlayerNeurons))
            ax[0].set_ylim(-0.1, 1.1)
            ax[0].grid()


            ax[1].set_yticks(numpy.arange(0, 1.1, 0.1))
            ax[1].set_xlim(0, len(thisPlayerNeurons))
            ax[1].set_ylim(-0.1, 1.1)
            ax[1].set_xticks([], [])
            ax[1].set_ylabel('Arousal')
            ax[1].grid()

            # ax[1].set_xlabel('Actions')
            ax[2].set_ylabel('Valence')
            ax[2].set_yticks(numpy.arange(0, 1.1, 0.1))
            ax[2].set_ylim(-0.1, 1.1)
            ax[2].set_xlim(0, len(thisPlayerNeurons))
            ax[2].grid()



            # for nindex,neuron in enumerate(neuronsPleasureX):
            #     alpha = neuronsAge[nindex]
            #     ax[0].scatter(neuronsY[nindex], neuronsArousalX[nindex],  c="red")
            #
            #     alpha = neuronsAge[nindex]
            #     ax[1].scatter(neuronsY[nindex], neuronsPleasureX[nindex],  c="red")

            ax[1].plot(dataYAverageNeuron,averageNeuronA,label="Avg Value", c="red")
            ax[2].plot(dataYAverageNeuron, averageNeuronP, label="Avg Value", c="red")

            print("Size plot: " + str(len(averageNeuronA)))

            for actionIndex in range(len(totalActions[i])):
                if totalColors[i][actionIndex] == "red":
                    ax[1].axvline(x=actionIndex, c="red", alpha=0.1, linestyle='dashed')
                    ax[2].axvline(x=actionIndex, c="red", alpha=0.1, linestyle='dashed')

                # if playersAction[i][actionIndex] == DataSetManager.actionPizzaReady:
                #     ax[1].axvline(x=actionIndex, c="green", linestyle='dashed')
                #     ax[0].axvline(x=actionIndex, c="green", linestyle='dashed')
                #

            avThisPlayer = numpy.array(arousalValenceInput[i])

            # green = mpatches.Patch(color='green', label='Discard')
            # blue = mpatches.Patch(color='blue', label='Pass')
            # orange = mpatches.Patch(color='orange', label='Pizza')
            # red = mpatches.Patch(color='red', label='Finish')
            # ax[0].legend(handles=[green, blue, orange, red])

            color = ["green", "blue", "red", "orange"]
            labels = ["Ev1_Action", "Ev2_Pizza", "Ev3_Finish", "Ev4_LongTerm"]
            markers = [".","^","X","."]
            sizes = [200, 200, 200, 200]

            for a in range(len(avThisPlayer)):
                thisEvent = numpy.array(avThisPlayer[a])
                # print("This event:" + str(thisEvent))
                # print("Len This event:" + str(len(thisEvent)))
                if len(thisEvent) > 0:
                    thisEventY = []
                    thisEventArousal = []
                    thisEventValence = []
                    for values in thisEvent:
                        thisEventY.append([values[0]])
                        av = values[1]
                        thisEventArousal.append(av[0])
                        thisEventValence.append(av[1])

                    ax[1].scatter(thisEventY, thisEventArousal, c=color[a], label=labels[a], marker=markers[a], s=sizes[a])
                    ax[2].scatter(thisEventY, thisEventValence, c=color[a], label=labels[a], marker=markers[a], s=sizes[a])

                    # centerValue = numpy.full((len(thisEventY)), 0.5)
                    # ax[0].scatter(thisEventY, centerValue, c=color[a], label=labels[a], marker=markers[a],
                    #               s=sizes[a])
            #     print("Y:" + str(len(thisEventY)))
            #     print("Arousal:" + str(len(thisEventArousal)))
            #     print("Valence:" + str(len(thisEventValence)))
            #     print("-")
            # input("here")

            ax[0].plot(range(len(selfExpectation[i])), selfExpectation[i], label="Avg Value", c="red")


            ax[2].legend( loc = 'upper center', bbox_to_anchor = (0.5, -0.05),
            fancybox = True, shadow = True, ncol = 5)

            fig.set_size_inches(21.0, 10.5)
            fig.tight_layout(pad=1.0)
            # plt.legend()
            # print ("Saving:" + str(plotName))
            plt.savefig(plotName)
            # print("Plotting!")
            ax[0].cla()
            ax[1].cla()
            fig.clf()
            # input("next!")

def plotMoodNeurons(names, moodNeurons, moodReading, iteraction, plotsDirectory):

    for i in range(len(names)):

        if len(moodNeurons) > i:

            for index, moodNeuronReadings in enumerate(moodNeurons[i]):

                if len(moodNeuronReadings) > 0:
                    directory = plotsDirectory + "/MoodNeurons_Players/"
                    if not os.path.exists(directory):
                        os.mkdir(directory)

                    if index == i:
                        directory = plotsDirectory + "/MoodNeurons_Players/Self/"
                        plotName = directory + "/Mood_Player_" + str(names[i]) + "(" + str(
                            i) + ")" + "_iteration_" + str(iteraction) + ".png"

                    else:
                        directory = plotsDirectory + "/MoodNeurons_Players/Oponents/"

                        newIndexes = numpy.array(range(4)).tolist()
                        newIndexes.remove(i)
                        newNames = names.copy()
                        newNames.remove(names[i])

                        plotName = directory + "/MoodNeurons_Player_" + str(names[i]) + "(" + str(
                            i) + ")" + "_AboutPlayer_" + str(names[index]) + "(" + str(
                            names[index]) + ")" +"("+ str(index)+ ")_iteration_" + str(
                            iteraction) + ".png"

                    if not os.path.exists(directory):
                        os.mkdir(directory)

                    thisPlayerNeurons = moodNeuronReadings

                    neuronsPleasureX = []
                    neuronsArousalX = []
                    neuronsY = []
                    neuronsAge = []

                    for indexA, action in enumerate(thisPlayerNeurons):

                        for n in action[0]:
                            neuronsArousalX.append(n[0])
                            neuronsPleasureX.append(n[1])
                            neuronsY.append(indexA)


                        for n in action[1]:
                            neuronsAge.append(n)

                    # neuronsPleasureX = numpy.tanh(numpy.array(neuronsPleasureX).flatten())
                    # neuronsArousalX = numpy.tanh(numpy.array(neuronsArousalX).flatten())

                    averageNeuronA = numpy.array(moodReading[i][index])[:, 0]
                    averageNeuronP = numpy.array(moodReading[i][index])[:, 1]
                    dataYAverageNeuron = range(len(averageNeuronA))


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
                    #
                    for nindex,neuron in enumerate(neuronsPleasureX):
                        alpha = neuronsAge[nindex]
                        ax.scatter(neuronsY[nindex], neuronsArousalX[nindex], alpha = alpha, c="red")

                        alpha = neuronsAge[nindex]
                        ax.scatter(neuronsY[nindex], neuronsPleasureX[nindex], alpha = alpha, c="red")

                    ax.plot(dataYAverageNeuron,averageNeuronA,label="Avg Arousal", c="blue")
                    ax.plot(dataYAverageNeuron, averageNeuronP, label="Avg Pleasure", c="green")
                    # ax.plot(dataYAverageNeuron, neuronsAge, label="Avg Dominance", c="red")

                    # with open(csvName, mode='w') as employee_file:
                    #     employee_writer = csv.writer(employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    #
                    #     employee_writer.writerow(['Action', 'NeuronAverageValue'])
                    #
                    #     for nI, nvalue in enumerate(averageNeuron):
                    #       employee_writer.writerow([str(nI), str(nvalue)])
                    #


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
                if len(moodReadings) > 0:
                    directory = plotsDirectory + "/Mood_Players/"
                    if not os.path.exists(directory):
                        os.mkdir(directory)

                    if index == i:
                        directory = plotsDirectory + "/Mood_Players/Self/"
                        plotName = directory + "/Mood_Player_" + str(names[i]) + "(" + str(
                            i) + ")" + "_iteration_" + str(iteraction) + ".png"

                    else:
                        directory = plotsDirectory + "/Mood_Players/Oponents/"

                        directory + "/Mood_Players" + str(names[i]) + "(" + str(
                            i) + ")" + "_AboutPlayer_" + str(names[index]) + "(" + str(
                            names[index]) + ")" + "(" + str(index) + ")_iteration_" + str(
                            iteraction) + ".png"


                    if not os.path.exists(directory):
                        os.mkdir(directory)

                    reward = numpy.array(moodReadings)
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
                    ax.plot(dataY, reward[:,0], label="Arousal", c="blue")
                    ax.plot(dataY, reward[:, 1], label="Pleasure", c="green")
                    plt.legend()

                    plt.savefig(plotName)

                    fig.clf()

def plotSelfProbabilitySuccess(names, prob, iteraction, plotsDirectory, name=""):

    for i in range(len(names)):
        if len(prob) >i:

            for index, probabilities in enumerate(prob[i]):


                if len(probabilities) > 0:
                    #
                    # print ("---------")
                    # print ("I:" + str(names[i]))
                    # print ("Index: " + str(index))

                    directory = plotsDirectory + "/ProbabilitySuccess_Players/"
                    if not os.path.exists(directory):
                        os.mkdir(directory)

                    if index == i:
                        directory = plotsDirectory + "/ProbabilitySuccess_Players/Self/"
                        plotName = directory + "/ProbabilitySuccess_Players" + str(names[i])+"("+str(i)+")" +"_iteration_"+str(iteraction)+".png"

                    else:
                        directory = plotsDirectory + "/ProbabilitySuccess_Players/Oponents/"

                        plotName = directory + "/ProbabilitySuccess_Players_" + str(names[i]) + "(" + str(
                            i) + ")" + "_AboutPlayer_" + str(names[index]) + "(" + str(
                            i) + ")" + ")_iteration_" + str(
                            iteraction) + ".png"


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

                    #
                    # with open(csvName, mode='w') as employee_file:
                    #     employee_writer = csv.writer(employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    #
                    #     employee_writer.writerow(['Action', 'NeuronAverageValue'])
                    #
                    #     for nI, nvalue in enumerate(reward):
                    #       employee_writer.writerow([str(nI), str(nvalue)])

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
        averagedQValues = []

        fig, axs = plt.subplots(1, 1)

        gameNumber =1
        for a in qValue:
            valueGame = []

            for q in a:
                if len(q)>1:
                    sortedA = numpy.array(q)
                    sortedA.sort()
                    selectedQValues.append(sortedA[-1])
                    summedQValues.append(sortedA.sum())
                    valueGame.append(sortedA.sum())
            # print ("Vlaue:" + str(len(valueGame)) + "-avg: " + str(numpy.average(valueGame)))
            averagedQValues.append(numpy.average(valueGame))

            # print("Shape A:" + str(numpy.array(qValue).shape))
            # input("here")

            axs.plot(range(len(valueGame)), valueGame, label="Game: " + str(gameNumber))
            gameNumber = gameNumber+1

            plt.ylim(0, 0.5)
        plt.legend()
        plt.savefig(directory + "/Player_" + str(names[i])+"("+str(i)+")" + "_iteration_" + str(iteraction) + "_BestQValues_Agregated.png")

        plt.clf()


        if len(selectedQValues) > 1:
            dataY = range(len(selectedQValues))

            fig, axs = plt.subplots(1, 1)
            axs.plot(dataY, selectedQValues)

            plt.ylim(0, 1)

            plt.savefig(directory + "/Player_" + str(names[i])+"("+str(i)+")" + "_iteration_" + str(iteraction) + "_BestQValue.png")

            plt.clf()

            dataY = range(len(summedQValues))
            fig, axs = plt.subplots(1, 1)
            axs.plot(dataY, summedQValues)

            plt.ylim(0, 1)

            plt.savefig(directory + "/Player_" + str(names[i])+"("+str(i)+")" + "_iteration_" + str(iteraction) + "_SummedQValue.png")

            plt.clf()

            dataY = range(len(averagedQValues))
            fig, axs = plt.subplots(1, 1)
            axs.plot(dataY, averagedQValues)

            plt.ylim(0, 1)

            plt.savefig(directory + "/Player_" + str(names[i])+"("+str(i)+")" + "_iteration_" + str(iteraction) + "_AvgQValue.png")

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
        loss = losses[i]


        actorLoss = []
        criticLoss = []
        for a in loss:
            if len(a) > 0:
                l = a[0]
                if len(a[0]) > 1:
                    criticLoss.append(a[0][1])

                actorLoss.append(a[0][0])

        if len(actorLoss) > 1:
            fig = plt.figure()
            ax = fig.add_subplot(111)

            dataY = range(len(actorLoss))
            ax.set_xlabel('Training Steps')
            ax.set_ylabel('Loss')
            plt.plot(dataY, actorLoss)
            plt.xticks(numpy.arange(0, len(dataY) + 1, 1.0))
            plt.grid()
            plt.savefig(directory + "/Player_" + str(names[i])+"("+str(i)+")" +"_iteration_"+str(iteraction)+"_Actor.png")

            plt.clf()

            if len(criticLoss)> 1:
                fig = plt.figure()
                ax = fig.add_subplot(111)

                dataY = range(len(criticLoss))
                ax.set_xlabel('Training Steps')
                ax.set_ylabel('Loss')
                plt.plot(dataY, criticLoss)
                plt.xticks(numpy.arange(0, len(dataY) + 1, 1.0))
                plt.grid()
                plt.savefig(directory + "/Player_" + str(names[i]) + "(" + str(i) + ")" + "_iteration_" + str(
                    iteraction) + "_Critic.png")

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

def generateIntrinsicPlotsFromDataset(plotsToGenerate, IntrinsicDataset, gameNumber=-1, specificLine=-1, saveDirectory=""):

    readFile = pd.read_pickle(IntrinsicDataset)

    moodReadingsAll = []
    probabilitiesAll = []
    moodNeuronsAll = []

    playerAction = []

    moodReadingsPerAgent = []
    moodNeuronsPerAgent = []

    totalActions = []
    totalColors = []

    arousalValenceInput = []

    selfExpectations = []
    #Each player
    for a in range(4):
        moodReadingsAll.append([])
        probabilitiesAll.append([])
        moodNeuronsAll.append([])
        playerAction.append([])

        moodReadingsPerAgent.append([])
        moodNeuronsPerAgent.append([])

        totalActions.append([])
        totalColors.append([])
        arousalValenceInput.append([])

        selfExpectations.append([])

        for i in range(4):
            moodReadingsAll[a].append([])
            probabilitiesAll[a].append([])
            moodNeuronsAll[a].append([])
            arousalValenceInput[a].append([])

    agentsNames = []
    currentLine = 0
    for lineCounter, row in readFile.iterrows():
        game = row["Game Number"]

        if len(agentsNames) == 0:
            agentsNames = row["Agent Names"]

        if gameNumber == -1 or  game <= gameNumber:

            if specificLine == -1 or currentLine <= specificLine:
                player = row["Player"]
                action = row["Action Type"]
                for a in range(4):
                    if action == actionDiscard:
                        color = "green"
                    elif action == actionPass:
                        color = "blue"
                    elif action == actionPizzaReady:
                        color = "orange"
                    elif action == actionFinish:
                        color = "red"

                    if player == a:
                        totalActions[a].append(1)
                        totalColors[a].append(color)
                    else:
                        totalActions[a].append(1)
                        totalColors[a].append("white")

                if not player == "" :

                    playerAction[player].append(action)

                    avInputP1 = row["P1 AVStimuli"]
                    avInputP2 = row["P2 AVStimuli"]
                    avInputP3 = row["P3 AVStimuli"]
                    avInputP4 = row["P4 AVStimuli"]

                    selfExpP1 = row["P1 Expectation"]
                    selfExpP2 = row["P2 Expectation"]
                    selfExpP3 = row["P3 Expectation"]
                    selfExpP4 = row["P4 Expectation"]

                    P1Prob = row["P1 probability"]
                    P2Prob = row["P2 probability"]
                    P3Prob = row["P3 probability"]
                    P4Prob = row["P4 probability"]

                    P1Mood = row["P1 Mood Reading"]
                    P2Mood = row["P2 Mood Reading"]
                    P3Mood = row["P3 Mood Reading"]
                    P4Mood = row["P4 Mood Reading"]

                    P1Neurons = row["P1 Mood Neuron"]
                    P2Neurons= row["P2 Mood Neuron"]
                    P3Neurons = row["P3 Mood Neuron"]
                    P4Neurons = row["P4 Mood Neuron"]

                    if P1Prob > -1:
                        probabilitiesAll[0][player].append(P1Prob)
                    if P2Prob > -1:
                        probabilitiesAll[1][player].append(P2Prob)
                    if P3Prob > -1:
                      probabilitiesAll[2][player].append(P3Prob)
                    if P4Prob > -1:
                     probabilitiesAll[3][player].append(P4Prob)

                    if P1Mood[0] > -1:
                        moodReadingsAll[0][player].append(P1Mood)
                        moodReadingsPerAgent[0].append(P1Mood)
                    if P2Mood[0] > -1:
                        moodReadingsAll[1][player].append(P2Mood)
                        moodReadingsPerAgent[1].append(P2Mood)
                    if P3Mood[0] > -1:
                      moodReadingsAll[2][player].append(P3Mood)
                      moodReadingsPerAgent[2].append(P3Mood)
                    if P4Mood[0] > -1:
                     moodReadingsAll[3][player].append(P4Mood)
                     moodReadingsPerAgent[3].append(P4Mood)

                    if isinstance(P1Neurons, tuple):
                        moodNeuronsAll[0][player].append(P1Neurons)
                        moodNeuronsPerAgent[0].append(P1Neurons)
                    if isinstance(P2Neurons, tuple):
                        moodNeuronsAll[1][player].append(P2Neurons)
                        moodNeuronsPerAgent[1].append(P2Neurons)
                    if isinstance(P3Neurons, tuple):
                      moodNeuronsAll[2][player].append(P3Neurons)
                      moodNeuronsPerAgent[2].append(P3Neurons)
                    if isinstance(P4Neurons, tuple):
                     moodNeuronsAll[3][player].append(P4Neurons)
                     moodNeuronsPerAgent[3].append(P4Neurons)

                    # print ("av1:" + str(avInputP1))
                    # input("here")
                    for indexAV, av in enumerate(avInputP1):
                        if not (av[0]==-1):
                            arousalValenceInput[0][indexAV].append([currentLine,av])


                    for indexAV, av in enumerate(avInputP2):
                        if not (av[0]==-1):
                            arousalValenceInput[1][indexAV].append([currentLine,av])

                    for indexAV, av in enumerate(avInputP3):
                        if not (av[0] == -1):
                            arousalValenceInput[2][indexAV].append([currentLine, av])

                    for indexAV, av in enumerate(avInputP4):
                        if not (av[0]==-1):
                            arousalValenceInput[3][indexAV].append([currentLine,av])

                    if selfExpP1 > -1:
                        selfExpectations[0].append(selfExpP1)

                    if selfExpP2 > -1:
                        selfExpectations[1].append(selfExpP2)

                    if selfExpP3 > -1:
                        selfExpectations[2].append(selfExpP3)

                    if selfExpP4 > -1:
                        selfExpectations[3].append(selfExpP4)

            currentLine = currentLine + 1

    if specificLine >0:
        gameNumber = str(gameNumber)+"_"+str(specificLine)


    # print ("MoodReadings: " + str(numpy.array(moodReadingsPerAgent[0]).shape))
    # input("Here")
    if plots["Experiment_SelfProbabilitySuccess"] in plotsToGenerate:
        print("Generating:" + str(plots["Experiment_SelfProbabilitySuccess"]))
        plotSelfProbabilitySuccess(agentsNames, probabilitiesAll, gameNumber, saveDirectory, name="Self")
    #
    if plots["Experiment_Mood"] in plotsToGenerate:
        print ("Generating:" + str(plots["Experiment_Mood"]))
        plotMood(agentsNames, moodReadingsAll, gameNumber,  saveDirectory)
    #
    if plots["Experiment_MoodNeurons"] in plotsToGenerate:
        print ("Generating:" + str(plots["Experiment_MoodNeurons"]))
        plotMoodNeurons(agentsNames, moodNeuronsAll, moodReadingsAll, gameNumber, saveDirectory)

    if plots["Experiment_MoodFaces"] in plotsToGenerate:
        print("Generating:" + str(plots["Experiment_MoodNeurons"]))

    if plots["Experiment_TimeLimeMood"] in plotsToGenerate:
        print ("Generating:" + str(plots["Experiment_TimeLimeMood"]))
        plotTimeLineMood(agentsNames, moodNeuronsPerAgent, moodReadingsPerAgent, gameNumber, playerAction, totalActions, totalColors, arousalValenceInput, selfExpectations, saveDirectory)


def generateSingleGamePlotsFromDataset(plotsToGenerate, dataset, gameNumber, saveDirectory = ""):

    readFile = pd.read_pickle(dataset)
    gameNumber = gameNumber-1

    playersAction = []
    playersActionName = []
    for a in range(4):
        playersAction.append([])
        playersActionName.append([])

    agentsNames = []
    for lineCounter, row in readFile.iterrows():
        game = row["Game Number"]
        # print ("GameNumber: " + str(gameNumber) + "- " + str(game))

        if game == gameNumber:
            if len(agentsNames) == 0:
                agentNames = str(row["Agent Names"])
                agentsNames = agentNames.split(",")

            player = row["Player"]
            action = row["Players Status"]
            if not player=="":
                # print ("player:" + str(player))
                thisPlayerAction = action[player]
                # print("action:" + str(thisPlayerAction) + " - Len:" + str(len(thisPlayerAction)))
                if len(thisPlayerAction) == 2:
                    actionName = thisPlayerAction[0]
                    actionComplete = thisPlayerAction
                else:
                    actionName = thisPlayerAction
                    actionComplete = thisPlayerAction

                playersActionName[player].append(actionName)
                playersAction[player].append(actionComplete)

    if plots["OneGame_NumberOfActions"] in plotsToGenerate:
        print ("Generating:" + str(plots["OneGame_NumberOfActions"]))
        plotNumberOfActions(agentsNames, playersAction, gameNumber, saveDirectory)

    if plots["OneGame_DiscardBehavior"] in plotsToGenerate:
        print("Generating:" + str(plots["OneGame_DiscardBehavior"]))
        plotDiscardBehavior(agentsNames, playersAction, gameNumber, saveDirectory)

    if plots["OneGame_Timeline"] in plotsToGenerate:
        print("Generating:" + str(plots["OneGame_Timeline"]))
        plotTimeLine(agentsNames, playersActionName, gameNumber, saveDirectory)

def generateExperimentPlotsFromDataset(plotsToGenerate, dataset, specificGame=-1, saveDirectory = ""):

    readFile = pd.read_pickle(dataset)

    agentsNames = []
    winners = []
    scoresAll = []

    rounds = []
    rounds.append(0)

    playersActionComplete = []
    playersActionName = []

    totalActionsAll = []
    correctActionsAll = []
    qValuesAll = []
    qValuesPerGame = []
    lossesAll = []
    meanQValuesAll = []
    rewardsAll = []

    pointsAll = []

    #auxiliary variables
    currentGameTotalActions = []
    currentGameWrongActions = []
    currentGameQValues = []

    for a in range(4):

        currentGameQValues.append([])
        pointsAll.append([])

        playersActionComplete.append([])
        playersActionComplete[a].append([])

        rewardsAll.append([])
        rewardsAll[a].append([])

        qValuesAll.append([])
        qValuesAll[a].append([])

        qValuesPerGame.append([])
        qValuesAll[a].append([])

        lossesAll.append([])
        lossesAll[a].append([])

        playersActionName.append([])

        meanQValuesAll.append([])

        totalActionsAll.append([])
        totalActionsAll[a].append(0)
        correctActionsAll.append([])
        correctActionsAll[a].append(0)

        currentGameTotalActions.append(0)
        currentGameWrongActions.append(0)

    currentGame = 0
    first = True



    for lineCounter, row in readFile.iterrows():
        game = row["Game Number"]
        player = row["Player"]

        if len(agentsNames) == 0:
            agentsNames = row["Agent Names"]

        actionType = row["Action Type"]
        # # Update game
        # if actionType == actionDeal:
        #     if first:
        #         first = False
        #     else:
        #         currentGame = currentGame + 1
        #
        #
        # game = currentGame


        if not player == "":

            totalActionsThisPLayer = row["Total Actions"]
            wrongActionsThisPlayer = row["Wrong Actions"]
            score = row["Scores"]
            roundNumber = row["Round Number"]
            action = row["Players Status"]
            reward = row["Reward"]
            qValues = row["Qvalues"]
            loss = row["Loss"]

            #Update all the victories
            if len(score) == 4:
                winners.append(score[0])
                scoresAll.append(score.tolist())

            #Update the number of rounds
            if game > len(rounds)-1:
                rounds.append(0)
            rounds[game] = roundNumber

            #Update the total and wrong actions
            if game > len(totalActionsAll[player])-1:
                totalActionsAll[player].append(0)
                correctActionsAll[player].append(0)

            if actionType == actionFinish or actionType == actionPass or actionType == actionDiscard:
                totalActionsAll[player][game] += totalActionsThisPLayer
                correctActionsAll[player][game] += totalActionsThisPLayer-wrongActionsThisPlayer

            #ActionComplete

            actionComplete = action[player]

            # if len(thisPlayerAction) == 2:
            #     actionComplete = thisPlayerAction[0]
            # else:
            #     actionComplete = (thisPlayerAction, [0])

            if game > len(playersActionComplete[player])-1:
                playersActionComplete[player].append([])

            playersActionComplete[player][game].append(actionComplete)

            #Rewards
            if game > len(rewardsAll[player]) - 1:
                rewardsAll[player].append([])

            rewardsAll[player][game].append(reward)

            #Qvalues
            if game > len(qValuesAll[player]) - 1:
                qValuesAll[player].append([])


            qValuesAll[player][game].append(qValues)

            #Losses
            if game > len(lossesAll[player]) - 1:
                lossesAll[player].append([])

            if actionType == actionFinish and len(loss) > 0:
                lossesAll[player][game].append(loss)

            #Points attribution

            if actionType == actionFinish:
                # print ("---")
                # print ("Game: " + str(game))
                # print("Player:" + str(player))
                # print ("Action type:" + str(actionFinish))

                positionPlayer = score.tolist().index(player)
                points = 3 - positionPlayer
                if len(pointsAll[player]) > 0:
                    summedPoints = pointsAll[player][-1] + points
                else:
                    summedPoints = points
                pointsAll[player].append(summedPoints)


    if specificGame == -1:
        specificGame = game


    if plots["Experiment_Points"] in plotsToGenerate:
        print ("Plotting:" + str(plots["Experiment_Points"]))
        plotPoints(agentsNames, pointsAll, specificGame, saveDirectory)

    if plots["Experiment_TotalActions"] in plotsToGenerate:
        print ("Plotting:" + str(plots["Experiment_TotalActions"]))
        plotTotalActions(agentsNames, totalActionsAll, specificGame, saveDirectory)

    if plots["Experiment_Winners"] in plotsToGenerate:
        print ("Plotting:" + str(plots["Experiment_Winners"]))
        plotWinners(len(agentsNames), winners, specificGame, agentsNames, saveDirectory)

    if plots["Experiment_Rounds"] in plotsToGenerate:
        print("Plotting:" + str(plots["Experiment_Rounds"]))
        plotRounds(rounds, game, saveDirectory)

    if plots["Experiment_FinishingPosition"] in plotsToGenerate:
        print("Plotting:" + str(plots["Experiment_FinishingPosition"]))
        plotFinishPositions(agentsNames, scoresAll, winners, specificGame, saveDirectory)

    if plots["Experiment_ActionsBehavior"] in plotsToGenerate:
        print("Plotting:" + str(plots["Experiment_ActionsBehavior"]))
        plotActionBehavior(agentsNames, playersActionComplete, specificGame, saveDirectory)

    if plots["Experiment_Reward"] in plotsToGenerate:
        print("Plotting:" + str(plots["Experiment_Reward"]))
        plotRewardsAll(agentsNames, rewardsAll, specificGame, saveDirectory)

    if plots["Experiment_CorrectActions"] in plotsToGenerate:
        print("Plotting:" + str(plots["Experiment_CorrectActions"]))
        plotCorrectActions(agentsNames, correctActionsAll, totalActionsAll, specificGame, saveDirectory)

    if plots["Experiment_QValues"] in plotsToGenerate:
        print("Plotting:" + str(plots["Experiment_QValues"]))
        plotQValues(agentsNames, qValuesAll, specificGame, saveDirectory)
    #
    if plots["Experiment_Losses"] in plotsToGenerate:
        print("Plotting:" + str(plots["Experiment_Losses"]))
        plotLosses(agentsNames, lossesAll, specificGame, "Player", saveDirectory)


    # print ("Winners:" + str(winners))
    # print("Rounds:" + str(rounds))
    # print("Scores:" + str(scoresAll))
    # print ("Total actions:" + str(totalActionsAll))
    # print ("Total Correct actions:" + str(correctActionsAll))
    # print("Losses:" + str(len(lossesAll[0])))
    # print("Losses:" + str(len(lossesAll[1])))


class PlotManager():

    @property
    def plotsDirectory(self):
        return self._plotsDirectory

    def __init__(self, plotDirectory):

        self._plotsDirectory = plotDirectory


    def generateAllPlots(self, plotsToGenerate, dataset, gameRound, intrinsicDataset=""):
        generateSingleGamePlotsFromDataset(plots, dataset, gameRound, self._plotsDirectory)
        generateExperimentPlotsFromDataset(plotsToGenerate, dataset, saveDirectory=self._plotsDirectory)

        if not intrinsicDataset == "":
            intrinsicDataset = intrinsicDataset+"/"+"IntrinsicDataset.pkl"
            generateIntrinsicPlotsFromDataset(plotsToGenerate,intrinsicDataset, saveDirectory=self._plotsDirectory)
