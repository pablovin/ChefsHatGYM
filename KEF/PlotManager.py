# -*- coding: utf-8 -*-
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy

import os


from KEF import DataSetManager

from matplotlib.collections import PolyCollection

class PlotManager():

    @property
    def plotsDirectory(self):
        return self._plotsDirectory

    def __init__(self, plotDirectory):

        self._plotsDirectory = plotDirectory


    def plotWinners(self, numPLayers, winners, iteraction):

        fig, ax = plt.subplots()
        plt.grid()
        ax.hist(winners, bins=numPLayers)

        ax.set_xlabel('Players')
        ax.set_ylabel('Victories')

        plt.xticks(numpy.arange(0, numPLayers, 1.0))
        # plt.xticks(numpy.arange(0, len(dataY) + 1, 500))

        plt.xlim(0, numPLayers)
        # plt.xlim(0, range(len(dataY)))

        plt.savefig(self._plotsDirectory + "/Game_WinnersHistogram_iteration_"+str(iteraction)+".png")

        plt.clf()


    def plotRounds(self, allRounds, iteraction):

        dataY = range(len(allRounds))

        fig = plt.figure()
        ax = fig.add_subplot(111)

        ax.set_xlabel('Games')
        ax.set_ylabel('Number of Rounds')

        # ax.text(1, 1, "TotalWin:"+str(totalWins), style='italic',
        #          bbox={'facecolor': 'red', 'alpha': 0.5, 'pad': 10})

        plt.yticks(numpy.arange(0, numpy.max(allRounds) +1 , 5))
        # plt.xticks(numpy.arange(0, len(dataY) + 1, 1.0))

        plt.ylim(0,  numpy.max(allRounds))
        plt.xlim(0, len(dataY))

        plt.grid()
        ax.plot(dataY, allRounds)

        roundsNumber = 0
        if len(allRounds)> 0:
            roundsNumber = allRounds[-1]

        plt.savefig(self._plotsDirectory + "/Game_Rounds_iteration_"+str(iteraction)+"_Rounds_"+str(roundsNumber)+".png")

        plt.clf()

    def plotFinishPositionAllPlayers(self, numPLayers, scoresAll, winners, iteraction):

        # fig = plt.figure()
        # ax = fig.add_subplot(111)

        # Plot winning history all players
        for i in range(numPLayers):
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

            plt.yticks(numpy.arange(0, numPLayers+1, 1.0))
            # plt.xticks(numpy.arange(0, len(dataY) + 1, 1.0))

            plt.ylim(0, numPLayers+1)
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

            directory = self._plotsDirectory  + "/FinishingPosition_Players/"

            if not os.path.exists(directory):
                os.mkdir(directory)

            plt.savefig(directory + "/HistoryWinners_player_"+str(i)+"_iteration_"+str(iteraction)+"_TotalWin_"+str(totalWins)+".png")

            fig.clf()

    def plotNumberOfActions(self, numPLayers, actions, iteraction):

        # fig = plt.figure()
        # ax = fig.add_subplot(111)

        largest = 0
        for i in range(numPLayers):
            if len(actions[i]) > largest:
                largest = len(actions[i])

        # Plot discard plot for all players
        for i in range(numPLayers):

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
            quarterInterval = int(len(actionsTotal) / 4)

            labels = ['Q1', 'Q2', 'Q3', 'Q4']
            quartersPass = []
            quarterDiscard = []

            x = numpy.arange(len(labels))  # the label locations
            width = 0.35  # the width of the bars


            for q in range(4):
                # first quarter
                quarter = actionsTotal[q * quarterInterval:q * quarterInterval + quarterInterval]
                unique, counts = numpy.unique(quarter, return_counts=True)
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

            directory = self._plotsDirectory + "/ActionBehavior_LastGame_Players/"

            if not os.path.exists(directory):
                os.mkdir(directory)

            plt.savefig(directory + "/ActionBehavior_" + str(i) + "_iteration_" + str(
                iteraction) + ".png")

            fig.clf()


    def plotNumberOfActionsTotal(self, numPLayers, actions, iteraction):

        # fig = plt.figure()
        # ax = fig.add_subplot(111)

        largest = 0
        for i in range(numPLayers):
            if len(actions[i]) > largest:
                largest = len(actions[i])



        # Plot discard plot for all players
        for i in range(numPLayers):


            allPasses = []
            allDiscards = []

            for i in range(4):
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
                quarterInterval = int(len(actionsTotal) / 4)

                labels = ['Q1', 'Q2', 'Q3', 'Q4']
                quartersPass = []
                quarterDiscard = []

                x = numpy.arange(len(labels))  # the label locations
                width = 0.35  # the width of the bars


                for q in range(4):
                    # first quarter
                    quarter = actionsTotal[q * quarterInterval:q * quarterInterval + quarterInterval]
                    unique, counts = numpy.unique(quarter, return_counts=True)
                    currentQuarter = dict(zip(unique, counts))

                    if 0 in currentQuarter:
                     allPasses[q].append(currentQuarter[0])
                    else:
                        allPasses[q].append(0)

                    if 1 in currentQuarter:
                        allDiscards[q].append(currentQuarter[1])
                    else:
                        allDiscards[q].append(0)



            fig, axs = plt.subplots(4, 2)

            y = range(len(allPasses[0]))

            rect1 = axs[0, 0].plot(y, allPasses[0])
            axs[0, 0].set_title('Passes Q1')

            rect2 =axs[1, 0].plot(y, allPasses[1])
            axs[1, 0].set_title('Passes Q2')

            rect3 =axs[2, 0].plot(y, allPasses[2])
            axs[2, 0].set_title('Passes Q3')

            rect4 =axs[3, 0].plot(y, allPasses[3])
            axs[3, 0].set_title('Passes Q4')

            rect5 =axs[0, 1].plot(y, allDiscards[0])
            axs[0, 1].set_title('Discards Q1')

            rect6 =axs[1, 1].plot(y, allDiscards[1])
            axs[1, 1].set_title('Discards Q2')

            rect7 =axs[2, 1].plot(y, allDiscards[2])
            axs[2, 1].set_title('Discards Q3')

            rect8 =axs[3, 1].plot(y, allDiscards[3])
            axs[3, 1].set_title('Discards Q4')

            # for ax in axs.flat:
            #     ax.set(xlabel='Quarter', ylabel='Number of Actions')

            # Hide x labels and tick labels for top plots and y ticks for right plots.
            for ax in axs.flat:
                ax.label_outer()
            #
            #
            # rects1 = ax.bar(x - width / 2, quartersPass, width, label='Pass')
            # rects2 = ax.bar(x + width / 2, quarterDiscard, width, label='Discard')

            # Add some text for labels, title and custom x-axis tick labels, etc.
            ax.set_ylabel('N° Actions')
            # ax.set_title('Number of Actions')
            ax.set_ylabel('Game Quarters')
            # ax.set_xticks(x)
            # ax.set_xticklabels(labels)
            # ax.legend()

            # def autolabel(rects):
            #     """Attach a text label above each bar in *rects*, displaying its height."""
            #     for rect in rects:
            #         height = rect.get_height()
            #         ax.annotate('{}'.format(height),
            #                     xy=(rect.get_x() + rect.get_width() / 2, height),
            #                     xytext=(0, 3),  # 3 points vertical offset
            #                     textcoords="offset points",
            #                     ha='center', va='bottom')
            #
            #
            # autolabel(rect1)
            # autolabel(rect2)

            directory = self._plotsDirectory + "/ActionBehavior_AllGames_Players/"

            if not os.path.exists(directory):
                os.mkdir(directory)

            plt.savefig(directory + "/ActionBehavior_AllGames" + str(i) + "_iteration_" + str(
                iteraction) + ".png", dpi=500)

            fig.clf()

    def plotDiscardBehavior(self, numPLayers, actions, iteraction):

        # fig = plt.figure()
        # ax = fig.add_subplot(111)

        largest = 0
        for i in range(numPLayers):
            if len(actions[i]) > largest:
                largest = len(actions[i])

        # Plot discard plot for all players
        for i in range(numPLayers):


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

            for q in range(4):

                # first quarter
                quarter = currentPlayerActions[q*quarterInterval:q*quarterInterval+quarterInterval]
                unique, counts = numpy.unique(quarter, return_counts=True)
                currentQuarter = dict(zip(unique, counts))

                if 0 in currentQuarter:
                    passesCount = currentQuarter[0]
                else:
                    passesCount = 0
                if 1 in currentQuarter:
                    discardCount = len(quarter) - passesCount
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
            # plt.xticks(numpy.arange(0, len(dataY) + 1, 1.0))

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

            directory = self._plotsDirectory + "/DiscardBehavior_LastGame_Players/"

            if not os.path.exists(directory):
                os.mkdir(directory)


            plt.savefig(directory + "/Player_Discards_player_" + str(i) + "_iteration_" + str(
                iteraction) + ".png")

            fig.clf()


    def plotRewardsAll(self, numPLayers, rewards, iteraction):

        # Plot mean reward all players
        # fig = plt.figure()
        # ax = fig.add_subplot(111)

        # print ("Rewards: ", numpy.array(rewards).shape)

        for i in range(numPLayers):

            averageRewards = []
            for a in range(len(rewards[i])):

                # thisReward = rewards[i]
                # print ("A:", a)
                # print("Rewards:" , len(rewards))
                # print("Rewards[i]:", len(rewards[i]))
                # print("Rewards[i][0]:", len(rewards[i][0]))
                # print("Rewards[i]:", len(rewards[i][0]))
                averageRewards.append(numpy.average(rewards[i][a]))

            reward = averageRewards

            dataY = range(len(reward))
            # input("here")
            meanReward = numpy.average(numpy.array(reward))

            fig = plt.figure()
            ax = fig.add_subplot(111)

            ax.set_xlabel('Games')
            ax.set_ylabel('Average Reward')

            plt.yticks(numpy.arange(-1.0, 1.0, 0.1))
            # plt.xticks(numpy.arange(0, len(dataY) + 1, 500))

            plt.ylim(-1.1, 1.2)
            # plt.xlim(0, range(len(dataY)))
            plt.grid()
            ax.plot(dataY, reward)


            directory = self._plotsDirectory + "/Rewards_Players/"

            if not os.path.exists(directory):
                os.mkdir(directory)

            plt.savefig(directory + "/Reward_player_" + str(i) +"_iteration_"+str(iteraction)+"_meanReward_"+str(meanReward)+".png")

            fig.clf()

    def plotTimeLine(self, actions, numPLayers, iteration=0, directory=""):

        largest = 0
        for i in range(numPLayers):
            if len(actions[i]) > largest:
                largest = len(actions[i])

        for i in range(numPLayers):
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

            if directory == "":

                directory = self._plotsDirectory + "/TimeLine_LastGame_Players/"

                if not os.path.exists(directory):
                    os.mkdir(directory)

                plt.savefig(directory  + "/Game_TimeLine_iteration_"+str(iteration)+"_Player_"+str(i)+".png")
            else:
                plt.savefig(
                    directory + "/Game_TimeLine_iteration_" + str(iteration) + "_Player_" + str(i) + ".png")

            fig.clf()


    def plotCorrectActions(self, numPLayers, wrongActions, totalActions, iteraction):

        # print("wrong actions plot:" + str(wrongActions[0]))
        # print("wrong actions plot:" + str(wrongActions[0][0]))
        # input("here")
        # Plot wrong actions all players
        for i in range(numPLayers):


            correctActionsPlot = wrongActions[i]
            totalCorrectActionsPlot = totalActions[i]

            # correlation = numpy.corrcoef(correctActionsPlot, totalCorrectActionsPlot)[0, 1]

            #
            # print ("Wrong action plot shape:" + wrongActionsPlot.shape)
            # input("here")

            dataY = range(len(correctActionsPlot))
            dataY2 = range(len(totalCorrectActionsPlot))

            fig = plt.figure()
            ax = fig.add_subplot(111)

            totalCorrectActions = numpy.array(correctActionsPlot).sum()
            totalActionsGame = numpy.array(totalActions[i]).sum()
            # ax.text(0,0, "Wrong actions:"+str(totalWrongActions), style='italic',
            #         bbox={'facecolor': 'red', 'alpha': 0.5, 'pad': 10})

            # print ("DataY:", dataY)
            # print ("WrongActionPlots:", wrongActionsPlot)

            ax.set_xlabel('Games')
            ax.set_ylabel('Average Correct Actions')


            # plt.yticks(numpy.arange(-1.0, 121, 20))
            # plt.xticks(numpy.arange(0, len(dataY) + 1, 500))

            # plt.ylim(-1., 600)
            # plt.xlim(0, range(len(dataY)))

            ax.plot(dataY, correctActionsPlot, label="Correct Actions ")
            ax.plot(dataY2, totalCorrectActionsPlot, label="Total Actions ")
            ax.legend()
            plt.grid()

            directory = self._plotsDirectory + "/CorrectActions_Players/"

            if not os.path.exists(directory):
                os.mkdir(directory)

            plt.savefig(directory + "/CorrectActionsPlot_player_" + str(i) +"_iteration_"+str(iteraction)+"CorrectActions_"+str(totalCorrectActions)+"("+str(totalActionsGame)+").png")

            plt.clf()

    def plotWrongActions(self, numPLayers, wrongActions, iteraction):

        # Plot wrong actions all players
        for i in range(numPLayers):
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

            directory = self._plotsDirectory + "/WrongActions_Players/"

            if not os.path.exists(directory):
                os.mkdir(directory)


            plt.savefig(directory + "/WrongActionsPlot_player_" + str(i) +"_iteration_"+str(iteraction)+"WrongActions_"+str(totalWrongActions)+".png")

            plt.clf()

    def plotLosses(self, numPLayers, losses, iteraction):

        # Plot wrong actions all players

        for i in range(numPLayers):

            directory = self._plotsDirectory + "/Losses_Players/"

            if not os.path.exists(directory):
                os.mkdir(directory)

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

                plt.savefig(directory + "/CriticLoss_player_" + str(i) + "_iteration_" + str(iteraction) + "WrongActions.png")

                plt.clf()

                fig = plt.figure()
                ax = fig.add_subplot(111)

                ax.set_xlabel('Training Steps')
                ax.set_ylabel('Loss')


                plt.plot(dataY, lossActor, label="Actor")
                plt.legend()
                plt.savefig(
                    directory + "/ActorLoss_player_" + str(i) + "_iteration_" + str(iteraction) + "WrongActions.png")
            else:
                fig = plt.figure()
                ax = fig.add_subplot(111)

                ax.set_xlabel('Training Steps')
                ax.set_ylabel('Loss')
                plt.plot(dataY, loss)
                plt.grid()
                plt.savefig(directory + "/Loss_player_" + str(i) +"_iteration_"+str(iteraction)+"WrongActions.png")

                plt.clf()

