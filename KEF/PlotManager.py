# -*- coding: utf-8 -*-
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
# import seaborn as sns
import numpy
from keras.utils import plot_model

import pylab as P


class PlotManager():

    @property
    def plotsDirectory(self):
        return self._plotsDirectory

    def __init__(self, plotDirectory):

        self._plotsDirectory = plotDirectory


    def plotWinners(self, numPLayers, winners, iteraction):

        fig, ax = plt.subplots()
        ax.hist(winners, bins=numPLayers)

        ax.set_xlabel('Players')
        ax.set_ylabel('Victories')

        plt.xticks(numpy.arange(0, numPLayers, 1.0))
        # plt.xticks(numpy.arange(0, len(dataY) + 1, 500))

        plt.xlim(0, numPLayers)
        # plt.xlim(0, range(len(dataY)))

        plt.savefig(self._plotsDirectory + "/WinnersHistogram_iteration_"+str(iteraction)+".png")

        plt.clf()

    def plotHistoryAllPLayers(self, numPLayers, scoresAll, winners, iteraction):

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

            ax.text(1, 1, "TotalWin:"+str(totalWins), style='italic',
                     bbox={'facecolor': 'red', 'alpha': 0.5, 'pad': 10})

            plt.yticks(numpy.arange(0, numPLayers+1, 1.0))
            # plt.xticks(numpy.arange(0, len(dataY) + 1, 1.0))

            plt.ylim(0, numPLayers+1)
            plt.xlim(0, len(dataY))

            ax.plot(dataY, currentPLayerData)

            #ax.bar(dataY, currentPLayerData, align='center')

            # ax.set_ylim([0, 4])
            #
            # my_xticks = [1, 2, 3 , 4]
            # plt.yticks(dataY, my_xticks)
            # # plt.yticks(np.arange(y.min(), y.max(), 0.005))
            #


            plt.savefig(self._plotsDirectory  + "/HistoryWinners_player_"+str(i)+"_iteration_"+str(iteraction)+".png")

            fig.clf()


    def plotRewardsAll(self, numPLayers, rewards, iteraction):

        # Plot mean reward all players
        # fig = plt.figure()
        # ax = fig.add_subplot(111)

        # print ("Rewards: ", numpy.array(rewards).shape)


        for i in range(numPLayers):
            reward = rewards[i]

            dataY = range(len(reward))

            # input("here")
            meanReward = numpy.average(numpy.array(reward))

            fig = plt.figure()
            ax = fig.add_subplot(111)

            #totalWrongActions = numpy.array(wrongActionsPlot).sum()
            # ax.text(1, 1, "meanReward:"+str(meanReward), style='italic',
            #          bbox={'facecolor': 'red', 'alpha': 0.5, 'pad': 10})

            # print ("Mean reward:" + str(meanReward))

            # print ("DataY:", dataY)
            # print ("WrongActionPlots:", wrongActionsPlot)

            ax.set_xlabel('Games')
            ax.set_ylabel('Average Reward')

            plt.yticks(numpy.arange(-1.0, 1.0, 0.1))
            # plt.xticks(numpy.arange(0, len(dataY) + 1, 500))

            plt.ylim(-1.1, 1.2)
            # plt.xlim(0, range(len(dataY)))

            ax.plot(dataY, reward)

            plt.savefig(self._plotsDirectory + "/RewardPlot_player_" + str(i) +"_iteration_"+str(iteraction)+"_meanReward_"+str(meanReward)+".png")

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

            plt.ylim(-1., 600)
            # plt.xlim(0, range(len(dataY)))

            plt.plot(dataY, wrongActionsPlot)

            plt.savefig(self._plotsDirectory + "/WrongActionsPlot_player_" + str(i) +"_iteration_"+str(iteraction)+"WrongActions_"+str(totalWrongActions)+".png")

            plt.clf()

    def createListPlot(self, lists, names):

        for l in range(len(lists)):
            plt.plot(lists[l])
            plt.title(names[l])

            plt.ylabel(names[l])
            plt.xlabel('Iteration')
            plt.savefig(self.plotsDirectory + "/" + names[l] + ".png")
            plt.clf()

    def createCategoricalHistogram(self, dataPoints, dataName):

        dataClasses = []
        for y in dataPoints.dataY:
            dataClasses.append(numpy.argmax(y))

        dataClasses = numpy.array(dataClasses)

        n, bins, patches = plt.hist(dataClasses, len(dataPoints.dataY[0]), facecolor='green', alpha=0.75)
        P.setp(patches, 'facecolor', 'g', 'alpha', 0.75)

        plt.savefig(self.plotsDirectory + "/" + dataName + "Histogram" + ".png")
        plt.clf()

    def createDataArousalValenceHistograms(self, arousals, valences, dataName):

        # arousals = []
        # valences = []
        # print "Shape:", numpy.shape(dataPoints.dataY)
        # print dataPoints.dataY[0]
        # for y in dataPoints.dataY:
        #
        #     arousals.append(y[0])
        #     valences.append(y[1])

        arousals = numpy.array(arousals)
        arousals = numpy.interp(arousals, (arousals.min(), arousals.max()), (-1, +1))
        valences = numpy.array(valences)

        n, bins, patches = plt.hist(arousals, 20, facecolor='green', alpha=0.75)
        P.setp(patches, 'facecolor', 'g', 'alpha', 0.75)

        plt.savefig(self.plotsDirectory + "/" + dataName + "arousal" + ".png")
        plt.clf()

        n, bins, patches = plt.hist(valences, 20, facecolor='green', alpha=0.75)
        P.setp(patches, 'facecolor', 'g', 'alpha', 0.75)

        plt.savefig(self.plotsDirectory + "/" + dataName + "valence" + ".png")
        plt.clf()

        plt.scatter(arousals, valences, 0.3)
        # draw a default hline at y=1 that spans the xrange
        l = plt.axhline(y=0)
        l = plt.axvline(x=0)
        plt.axis([-1, 1, -1, 1])
        plt.xlabel("Arousal")
        plt.ylabel("Valence")

        plt.savefig(self.plotsDirectory + "/" + dataName + "Arousal_Valence" + ".png")
        plt.clf()

    def createDataArousalValenceHistogram(self, dataPoints, dataName):

        arousals = []
        valences = []
        # print "Shape:", numpy.shape(dataPoints.dataY)
        # print dataPoints.dataY[0]
        for y in dataPoints.dataY:
            arousals.append(y[0])
            valences.append(y[1])

        arousals = numpy.array(arousals)
        arousals = numpy.interp(arousals, (arousals.min(), arousals.max()), (-1, +1))
        valences = numpy.array(valences)

        n, bins, patches = plt.hist(arousals, 20, facecolor='green', alpha=0.75)
        P.setp(patches, 'facecolor', 'g', 'alpha', 0.75)

        plt.savefig(self.plotsDirectory + "/" + dataName + "arousal" + ".png")
        plt.clf()

        n, bins, patches = plt.hist(valences, 20, facecolor='green', alpha=0.75)
        P.setp(patches, 'facecolor', 'g', 'alpha', 0.75)

        plt.savefig(self.plotsDirectory + "/" + dataName + "valence" + ".png")
        plt.clf()

        plt.scatter(arousals, valences, 0.3)
        # draw a default hline at y=1 that spans the xrange
        l = plt.axhline(y=0)
        l = plt.axvline(x=0)
        plt.axis([-1, 1, -1, 1])
        plt.xlabel("Arousal")
        plt.ylabel("Valence")

        plt.savefig(self.plotsDirectory + "/" + dataName + "Arousal_Valence" + ".png")
        plt.clf()

    def creatModelPlot(self, model, modelName=""):
        print
        "Creating Plot at: " + str(self.plotsDirectory) + "/" + str(modelName) + "_plot.png"
        plot_model(model, to_file=self.plotsDirectory + "/" + modelName + "_plot.png", show_layer_names=True,
                   show_shapes=True)

    def createTrainingPlot(self, trainingHistory, modelName=""):

        print
        "Creating Training Plot"

        metrics = trainingHistory.history.keys()

        for m in metrics:
            if m.startswith('lr'):
                metrics.remove(m)

        for i in range(len(metrics)):

            if not "val" in metrics[i]:
                # print "Models:"+ metrics[i]+" - "+ str(trainingHistory.history[metrics[i]])
                # print "Models:val_"+ metrics[i]+" - "+ str(trainingHistory.history["val_"+metrics[i]])
                # print "-"

                plt.plot(trainingHistory.history[metrics[i]])
                plt.plot(trainingHistory.history["val_" + metrics[i]])

                plt.title("Model's " + metrics[i])

                plt.ylabel(metrics[i])
                plt.xlabel('epoch')
                plt.legend(['train', 'validation'], loc='upper left')
                # print "Saving Plot:", self.plotsDirectory+"/"+modelName+metrics[i]+".png"
                plt.savefig(self.plotsDirectory + "/" + modelName + metrics[i] + ".png")
                plt.clf()

    def plotLoss(self, loss_history):
        plt.gcf().clear()
        plt.figure(1)
        plt.ylabel('Loss')
        plt.xlabel('Epochs')
        plt.plot(loss_history, c='b')
        plt.savefig("loss.png")

    def plotAcc(self, acc_history):
        plt.gcf().clear()
        plt.figure(1)
        plt.ylabel('Accuracy')
        plt.xlabel('Epochs')
        plt.plot(acc_history, c='b')
        plt.savefig("acc.png")

    def plotOutput(self, faceX, faceY):
        plt.gcf().clear()
        plt.figure(1)
        plt.ylabel('Y')
        plt.xlabel('X')
        plt.plot(faceX, c='b')
        plt.plot(numpy.tranpose(faceY), c='r')
        plt.savefig("face_plot.png")

    def plotReward(self, avg_reward):
        plt.gcf().clear()
        plt.figure(1)
        plt.ylabel('Avg. Reward ')
        plt.xlabel('Episodes x 1000')
        plt.plot(avg_reward, c='b')
        plt.savefig(self.plotsDirectory + "/avg_reward.png")