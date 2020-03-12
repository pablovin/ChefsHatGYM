# -*- coding: utf-8 -*-
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy


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


            plt.savefig(self._plotsDirectory  + "/Player_HistoryWinners_player_"+str(i)+"_iteration_"+str(iteraction)+"_TotalWin_"+str(totalWins)+".png")

            fig.clf()

    def plotNumberOfActions(self, numPLayers, actions, iteraction):

        # fig = plt.figure()
        # ax = fig.add_subplot(111)

        largest = 0
        for i in range(numPLayers):
            if len(actions[i]) > largest:
                largest = len(actions[i])

        # Plot winning history all players
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
                passesCount = currentQuarter[0]
                discardCount = len(quarter) - passesCount

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

            plt.savefig(self._plotsDirectory + "/Player_Discards_player_" + str(i) + "_iteration_" + str(
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

            plt.savefig(self._plotsDirectory + "/Player_RewardValidAction_player_" + str(i) +"_iteration_"+str(iteraction)+"_meanReward_"+str(meanReward)+".png")

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
                plt.savefig(self._plotsDirectory  + "/Game_TimeLine_iteration_"+str(iteration)+"_Player_"+str(i)+".png")
            else:
                plt.savefig(
                    directory + "/Game_TimeLine_iteration_" + str(iteration) + "_Player_" + str(i) + ".png")

            fig.clf()


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

            plt.savefig(self._plotsDirectory + "/Player_WrongActionsPlot_player_" + str(i) +"_iteration_"+str(iteraction)+"WrongActions_"+str(totalWrongActions)+".png")

            plt.clf()


