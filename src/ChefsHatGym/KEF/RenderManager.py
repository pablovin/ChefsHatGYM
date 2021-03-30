# -*- coding: utf-8 -*-
import cv2
import csv
import copy
import shutil

import subprocess

import numpy
import os
import pandas as pd

from ChefsHatGym.KEF.PlotManager import generateIntrinsicPlotsFromDataset, plots

from ChefsHatGym.KEF import DataSetManager


class RenderManager():
    fps = 10
    imageSize = (2160, 3840, 3)

    playField = ""
    playingFieldDirectory = "playingField.png"

    currentGameDirectory = ""
    currentFrameNumber = 0

    cards = ""
    cardsDirectory = "deck/"

    actionCardsDirectory = "actionCards/"
    passCard = ""
    roleCards = []

    saveVideoDirectory = ""
    resourcesFolder = ""

    blackCard = ""

    @property
    def renderDirectory(self):
        return self._renderDirectory

    def __init__(self, saveVideoDirectory, resourcesFolder, fps=1):

        self.resourcesFolder = resourcesFolder
        self._renderDirectory = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/renderTest/renderTMP/"
        self.renderMoodDirectory = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/renderTest/renderTMPMood/"
        self.saveVideoDirectory = saveVideoDirectory

        if os.path.exists(self.renderDirectory):
            shutil.rmtree(self.renderDirectory)

        os.mkdir(self.renderDirectory)

        self.fps = fps

        self.getImages()

    def writeHeader(self, originalImage, message, detailedMessage=[]):

        images = []
        image = copy.copy(originalImage)
        font = cv2.FONT_HERSHEY_SIMPLEX

        yPosition = int((image.shape[0] - self.playField.shape[0]) / 2) + 800
        xPosition = int((image.shape[1] - self.playField.shape[1]) / 2) - 800
        baseposition = (yPosition, xPosition)

        cv2.putText(image, message, baseposition, font, 2, (255, 255, 255), 8, cv2.LINE_AA)

        if len(detailedMessage) > 0:

            yPosition = int((image.shape[0] - self.playField.shape[0]) / 2) + 500
            xPosition = int((image.shape[1] - self.playField.shape[1]) / 2) + 800

            for i in range(len(detailedMessage)):
                baseposition = (yPosition, xPosition)
                cv2.putText(image, detailedMessage[i], baseposition, font, 1, (255, 255, 255), 2, cv2.LINE_AA)
                xPosition = xPosition + 40

        return image

    def getImagesSeconds(self, image, seconds):

        totalFrames = seconds

        frames = []

        for i in range(totalFrames):
            # image = numpy.array(image).astype(numpy.uint8)
            # image = cv2.cvtColor(numpy.array(image), cv2.COLOR_BGR2RGB)
            frames.append(image)

        return frames

    def getImages(self):
        if self.playField == "":
            self.playField = numpy.array(cv2.imread(self.resourcesFolder + "/" + self.playingFieldDirectory))

        if self.cards == "":

            self.cards = {}

            cardImages = os.listdir(self.resourcesFolder + "/" + self.cardsDirectory)
            cardImages.sort(key=lambda f: int(f.split(".")[0]))
            cardNumber = 1
            for card in cardImages:
                # self.cards[cardNumber] = cv2.resize(numpy.array(cv2.imread(self.resourcesFolder+"/"+self.cardsDirectory+"/"+card)), (141,195))
                self.cards[cardNumber] = cv2.resize(
                    numpy.array(cv2.imread(self.resourcesFolder + "/" + self.cardsDirectory + "/" + card)), (70, 90))
                cardNumber = cardNumber + 1
            # print ("Size:", self.playField.shape)

        # Pass Card
        self.passCard = numpy.array(
            cv2.resize(cv2.imread(self.resourcesFolder + "/" + self.actionCardsDirectory + "/pass.png"), (176, 243)))

        self.roleCards.append(
            cv2.resize(cv2.imread(self.resourcesFolder + "/" + self.actionCardsDirectory + "/dishwasher.png"),
                       (176, 243)))
        self.roleCards.append(
            cv2.resize(cv2.imread(self.resourcesFolder + "/" + self.actionCardsDirectory + "/wait.png"), (176, 243)))
        self.roleCards.append(
            cv2.resize(cv2.imread(self.resourcesFolder + "/" + self.actionCardsDirectory + "/souschef.png"),
                       (176, 243)))
        self.roleCards.append(
            cv2.resize(cv2.imread(self.resourcesFolder + "/" + self.actionCardsDirectory + "/chef.png"), (176, 243)))

        self.blackCard = cv2.resize(
            numpy.array(cv2.imread(self.resourcesFolder + "/" + self.actionCardsDirectory + "/cardBlack.png")),
            (70, 90))

        # self.playField = numpy.array(cv2.resize(self.playField,(1920, 1080)))

    def drawPlayers(self, playerHands, originalImage, agentsNames):

        font = cv2.FONT_HERSHEY_SIMPLEX

        images = []
        # Player 1

        basePosition = (50, 50)
        cv2.putText(originalImage, "Player:" + agentsNames[0], basePosition, font, 2, (255, 255, 255), 2, cv2.LINE_AA)
        basePosition = (5, 5)
        yPosition = basePosition[0]
        xPosition = basePosition[1]

        # player1 cards
        for i in range(len(playerHands[0])):
            if playerHands[0][i] == 0:
                card = self.blackCard
            else:
                card = self.cards[playerHands[0][i]]

            if i % 10 == 0:
                yPosition = yPosition + card.shape[0] + 10
                xPosition = basePosition[1]
            else:
                xPosition = xPosition + card.shape[1] + 10

            originalImage[yPosition:yPosition + card.shape[0], xPosition:xPosition + card.shape[1]] = card
            #
            # for img in self.getImagesSeconds(originalImage, 1):
            #     images.append(img)

        # player 2
        if len(playerHands) > 1:
            basePosition = (
            int(originalImage.shape[0] - (self.playField.shape[0] / 2) + self.playField.shape[0]) + 100, 50)
            cv2.putText(originalImage, "Player " + agentsNames[1], basePosition, font, 2, (255, 255, 255), 2,
                        cv2.LINE_AA)

            basePosition = (
            int(originalImage.shape[0] - (self.playField.shape[0] / 2) + self.playField.shape[0]) + 100, 5)

            yPosition = basePosition[1]
            xPosition = basePosition[0]
            # player 2 cards
            for i in range(len(playerHands[0])):

                if playerHands[1][i] == 0:
                    card = self.blackCard
                    # print ("Black card!")
                    # print ("Shape:", card.shape)
                else:
                    card = self.cards[playerHands[1][i]]

                if i % 10 == 0:
                    yPosition = yPosition + card.shape[0] + 10
                    xPosition = basePosition[0]
                else:
                    xPosition = xPosition + card.shape[1] + 10

                # print("Key:", playerHands[1][i])
                # print("Card:", card.shape)
                # print ("X:" + str(xPosition) + " - Y:"+str(yPosition))
                # print("yPosition:" + str(yPosition) + ":" + str(yPosition + card.shape[0]))
                # print("xPosition:" + str(xPosition) + ":" + str(xPosition + card.shape[1]))
                # print("Shape:" + str(originalImage.shape))

                originalImage[yPosition:yPosition + card.shape[0], xPosition:xPosition + card.shape[1]] = card

                # for img in self.getImagesSeconds(originalImage, 1):
                #     images.append(img)
                # originalImage[0:0 + card.shape[0], 0:0 + card.shape[1]] = card

        # player 3
        if len(playerHands) > 2:
            basePosition = (50, int(originalImage.shape[1] - (self.playField.shape[1] * 1.3)))
            cv2.putText(originalImage, "Player " + agentsNames[2], basePosition, font, 2, (255, 255, 255), 2,
                        cv2.LINE_AA)

            # basePosition = (5, int(originalImage.shape[1] - (self.playField.shape[1] * 1.125)))
            basePosition = (5, int(originalImage.shape[1] - (self.playField.shape[1] * 1.125)))

            yPosition = basePosition[1] - 400
            xPosition = basePosition[0]
            # player 3 cards
            for i in range(len(playerHands[2])):

                if playerHands[2][i] == 0:
                    card = self.blackCard
                else:
                    card = self.cards[playerHands[2][i]]

                if i % 10 == 0:
                    yPosition = yPosition + card.shape[0] + 10
                    xPosition = basePosition[0]
                else:
                    xPosition = xPosition + card.shape[1] + 10
                #
                # print("Key:", playerHands[1][i])
                # print("Card:", card.shape)
                # print ("X:" + str(xPosition) + " - Y:"+str(yPosition))
                # print("yPosition:" + str(yPosition) + ":" + str(yPosition + card.shape[0]))
                # print("xPosition:" + str(xPosition) + ":" + str(xPosition + card.shape[1]))
                # print("Shape:" + str(originalImage.shape))

                originalImage[yPosition:yPosition + card.shape[0], xPosition:xPosition + card.shape[1]] = card
                # for img in self.getImagesSeconds(originalImage, 1):
                #     images.append(img)
                # originalImage[0:0 + card.shape[0], 0:0 + card.shape[1]] = card

        # player 4
        if len(playerHands) > 3:
            basePosition = (int(originalImage.shape[0] - (self.playField.shape[0] / 2) + self.playField.shape[0]) + 100,
                            int(originalImage.shape[1] - (self.playField.shape[1] * 1.3)))
            cv2.putText(originalImage, "Player " + agentsNames[3], basePosition, font, 2, (255, 255, 255), 2,
                        cv2.LINE_AA)

            basePosition = (int(originalImage.shape[0] - (self.playField.shape[0] / 2) + self.playField.shape[0]) + 100,
                            int(originalImage.shape[1] - (self.playField.shape[1] * 1.125)))

            yPosition = basePosition[1] - 400
            xPosition = basePosition[0]
            # player 3 cards
            for i in range(len(playerHands[3])):

                if playerHands[3][i] == 0:
                    card = self.blackCard
                else:
                    card = self.cards[playerHands[3][i]]

                if i % 10 == 0:
                    yPosition = yPosition + card.shape[0] + 10
                    xPosition = basePosition[0]
                else:
                    xPosition = xPosition + card.shape[1] + 10
                #
                # print("Key:", playerHands[1][i])
                # print("Card:", card.shape)
                # print ("X:" + str(xPosition) + " - Y:"+str(yPosition))
                # print("yPosition:" + str(yPosition) + ":" + str(yPosition + card.shape[0]))
                # print("xPosition:" + str(xPosition) + ":" + str(xPosition + card.shape[1]))
                # print("Shape:" + str(originalImage.shape))

                originalImage[yPosition:yPosition + card.shape[0], xPosition:xPosition + card.shape[1]] = card

        # images = []
        # for img in self.getImagesSeconds(originalImage, 3):
        #     images.append(img)
        #
        # self.saveImages(images)

        return originalImage

    def drawPlayField(self, image):

        yPosition = int((image.shape[0] - self.playField.shape[0]) / 2) - 200
        xPosition = int((image.shape[1] - self.playField.shape[1]) / 2) - 50
        image[yPosition:yPosition + self.playField.shape[0],
        xPosition:xPosition + self.playField.shape[1]] = self.playField

        return image

    def drawBoard(self, originalImage, board):

        currentBoardPlace = 0
        for i in range(len(board)):

            if int(board[i]) > 0 and not int(board[i]) == 13:
                card = numpy.array(self.cards[int(board[i])])
                # cv2.resize(numpy.array(cv2.imread(self.cardsDirectory + "/" + card)), (141, 195))
                card = cv2.resize(card, (176, 243))
                if currentBoardPlace < 3:
                    yPosition = int((originalImage.shape[0] - self.playField.shape[0]) / 2) + 120
                    xPosition = int((originalImage.shape[1] - self.playField.shape[1]) / 2) + 840 + (
                                currentBoardPlace * 225)

                elif currentBoardPlace >= 3 and currentBoardPlace < 8:

                    yPosition = int((originalImage.shape[0] - self.playField.shape[0]) / 2) + 420
                    xPosition = int((originalImage.shape[1] - self.playField.shape[1]) / 2) + 1070 + ((
                                                                                                              currentBoardPlace - 5) * 225)

                elif currentBoardPlace >= 8:

                    yPosition = int((originalImage.shape[0] - self.playField.shape[0]) / 2) + 720
                    xPosition = int((originalImage.shape[1] - self.playField.shape[1]) / 2) + 840 + ((
                                                                                                             currentBoardPlace - 8) * 225)

                originalImage[yPosition:yPosition + self.roleCards[0].shape[0],
                xPosition:xPosition + self.roleCards[0].shape[1]] = card

            currentBoardPlace = currentBoardPlace + 1

        return originalImage

    def drawRoleCards(self, originalImage, roles):
        # Dishwasher role
        # roles = roles[1:-1].split(",")

        # Player 1
        for i in range(4):

            card = self.roleCards[i]

            if int(roles[i]) == 0:
                yPosition = int((originalImage.shape[0] - self.playField.shape[0]) / 2) + 45 - 200
                xPosition = int((originalImage.shape[1] - self.playField.shape[1]) / 2) + 390 - 50
                originalImage[yPosition:yPosition + self.roleCards[0].shape[0],
                xPosition:xPosition + self.roleCards[0].shape[1]] = card

            if int(roles[i]) == 1:
                yPosition = int((originalImage.shape[0] - self.playField.shape[0]) / 2) + 45 - 200
                xPosition = int((originalImage.shape[1] - self.playField.shape[1]) / 2) + 1850 - 50
                originalImage[yPosition:yPosition + self.roleCards[0].shape[0],
                xPosition:xPosition + self.roleCards[0].shape[1]] = card

            if int(roles[i]) == 2:
                yPosition = int((originalImage.shape[0] - self.playField.shape[0]) / 2) + 1210 - 200
                xPosition = int((originalImage.shape[1] - self.playField.shape[1]) / 2) + 390 - 50
                originalImage[yPosition:yPosition + self.roleCards[0].shape[0],
                xPosition:xPosition + self.roleCards[0].shape[1]] = card

            if int(roles[i]) == 3:
                yPosition = int((originalImage.shape[0] - self.playField.shape[0]) / 2) + 1210 - 200
                xPosition = int((originalImage.shape[1] - self.playField.shape[1]) / 2) + 1850 - 50
                originalImage[yPosition:yPosition + self.roleCards[0].shape[0],
                xPosition:xPosition + self.roleCards[0].shape[1]] = card

        return originalImage

    def drawFinishingPosition(self, originalImage, playerStatus, score):

        # playerStatus = playerStatus.split("_")

        # print ("Player status:" + str(playerStatus))
        if playerStatus[0][0] == DataSetManager.actionFinish:
            if int(score[0]) == 0:
                card = self.roleCards[3]
            elif int(score[1]) == 0:
                card = self.roleCards[2]
            elif int(score[2]) == 0:
                card = self.roleCards[1]
            elif int(score[3]) == 0:
                card = self.roleCards[0]

            card = numpy.array(cv2.resize(card, (518, 719)))
            basePosition = (100, 100)
            yPosition = basePosition[0]
            xPosition = basePosition[1]

            originalImage[yPosition:yPosition + card.shape[0],
            xPosition:xPosition + card.shape[1]] = card

        if playerStatus[1][0] == DataSetManager.actionFinish:
            if int(score[0]) == 1:
                card = self.roleCards[3]
            elif int(score[1]) == 1:
                card = self.roleCards[2]
            elif int(score[2]) == 1:
                card = self.roleCards[1]
            elif int(score[3]) == 1:
                card = self.roleCards[0]

            card = numpy.array(cv2.resize(card, (518, 719)))

            basePosition = (100, 3048)

            yPosition = basePosition[0]
            xPosition = basePosition[1]

            originalImage[yPosition:yPosition + card.shape[0],
            xPosition:xPosition + card.shape[1]] = card

        if playerStatus[2][0] == DataSetManager.actionFinish:
            if int(score[0]) == 2:
                card = self.roleCards[3]
            elif int(score[1]) == 2:
                card = self.roleCards[2]
            elif int(score[2]) == 2:
                card = self.roleCards[1]
            elif int(score[3]) == 2:
                card = self.roleCards[0]

            card = numpy.array(cv2.resize(card, (518, 719)))

            basePosition = (1200, 100)

            yPosition = basePosition[0]
            xPosition = basePosition[1]

            originalImage[yPosition:yPosition + card.shape[0],
            xPosition:xPosition + card.shape[1]] = card

        if playerStatus[3][0] == DataSetManager.actionFinish:
            if int(score[0]) == 3:
                card = self.roleCards[3]
            elif int(score[1]) == 3:
                card = self.roleCards[2]
            elif int(score[2]) == 3:
                card = self.roleCards[1]
            elif int(score[3]) == 3:
                card = self.roleCards[0]

            card = numpy.array(cv2.resize(card, (518, 719)))

            # basePosition = (50 + int(originalImage.shape[0] - (self.playField.shape[0] / 2) + self.playField.shape[0]) + 100, 50 + int(originalImage.shape[1] - ( self.playField.shape[1]*1.3 )))

            basePosition = (1200, 3048)

            yPosition = basePosition[0]
            xPosition = basePosition[1]

            originalImage[yPosition:yPosition + card.shape[0],
            xPosition:xPosition + card.shape[1]] = card

        return originalImage

    def drawPassCard(self, originalImage, playerCurrentStatus):
        # Dishwasher role

        # playerStatus =  playerStatus.split("_")

        # print ("Player status:" + str(playerStatus[0]))
        # print ("Pass in player status:" + str(DataSetManager.actionPass in playerStatus[0]))
        # print ("-")
        card = self.passCard
        # print ("Player status:" + str(playerStatus))
        # if (DataSetManager.actionPass in playerStatus[0] and not lastTurnPizza) or (DataSetManager.actionPass in playerStatus[0] and lastTurnPizza and player==0):
        if (DataSetManager.actionPass == playerCurrentStatus[0]):
            yPosition = int((originalImage.shape[0] - self.playField.shape[0]) / 2) + 120
            xPosition = int((originalImage.shape[1] - self.playField.shape[1]) / 2) + 620

            originalImage[yPosition:yPosition + self.roleCards[0].shape[0],
            xPosition:xPosition + self.roleCards[0].shape[1]] = card

        if (DataSetManager.actionPass == playerCurrentStatus[1]):
            yPosition = int((originalImage.shape[0] - self.playField.shape[0]) / 2) + 120
            xPosition = int((originalImage.shape[1] - self.playField.shape[1]) / 2) + 1510
            originalImage[yPosition:yPosition + self.roleCards[0].shape[0],
            xPosition:xPosition + self.roleCards[0].shape[1]] = card

        if (DataSetManager.actionPass == playerCurrentStatus[2]):
            yPosition = int((originalImage.shape[0] - self.playField.shape[0]) / 2) + 720
            xPosition = int((originalImage.shape[1] - self.playField.shape[1]) / 2) + 620
            originalImage[yPosition:yPosition + self.roleCards[0].shape[0],
            xPosition:xPosition + self.roleCards[0].shape[1]] = card

        # print ("PlayerStatus3:"  + str( playerStatus[3]) + " - " + str(DataSetManager.actionPass in playerStatus[3]))
        if (DataSetManager.actionPass == playerCurrentStatus[3]):
            yPosition = int((originalImage.shape[0] - self.playField.shape[0]) / 2) + 720
            xPosition = int((originalImage.shape[1] - self.playField.shape[1]) / 2) + 1510
            originalImage[yPosition:yPosition + self.roleCards[0].shape[0],
            xPosition:xPosition + self.roleCards[0].shape[1]] = card

        return originalImage

    def saveImages(self, image, seconds):

        images = self.getImagesSeconds(image, seconds)

        for i in images:
            cv2.imwrite(self.currentGameDirectory + "/" + str(self.currentFrameNumber) + ".png", i)
            self.currentFrameNumber = self.currentFrameNumber + 1

    def createVideo(self, gamesToRender):

        gameToRender = str(gamesToRender).replace("[", "_").replace(" ", "_").replace(",", "_").replace("]", "_")
        command = "ffmpeg -i " + str(self.currentGameDirectory) + "/%d.png -framerate 1 -pix_fmt yuv420p -r " + str(
            self.fps) + " -vcodec libx264 -acodec aac " + str(self.saveVideoDirectory) + "_Game_" + str(
            gameToRender) + "_video.mp4"

        subprocess.call(command, shell=True)

        shutil.rmtree(self.currentGameDirectory)


    def getMoodPlots(self, intrinsicDataset, gameNumber, currentLine, originalImage):

        if os.path.exists(self.renderMoodDirectory):
            shutil.rmtree(self.renderMoodDirectory)

        os.mkdir(self.renderMoodDirectory)

        plot = plots["Experiment_MoodNeurons"]
        generateIntrinsicPlotsFromDataset(plot, intrinsicDataset, gameNumber=gameNumber, specificLine=currentLine,
                                          saveDirectory=self.renderMoodDirectory)

        selfMoodDirectory = self.renderMoodDirectory + "/MoodNeurons_Players/Self"
        listSelfMood = os.listdir(selfMoodDirectory)

        xPosition = 0
        yPosition = 0

        font = cv2.FONT_HERSHEY_SIMPLEX

        for moodImg in listSelfMood:
            img = cv2.imread(selfMoodDirectory + "/" + moodImg)
            playerNumber = int(moodImg.split("(")[1][0])

            if playerNumber == 0:
                xPosition = 0
                yPosition = 500

            if playerNumber == 1:
                xPosition = 3000
                yPosition = 500

            if playerNumber == 2:
                xPosition = 0
                yPosition = 1600

            if playerNumber == 3:
                xPosition = 3000
                yPosition = 1600

            baseposition = (xPosition + 250, yPosition - 50)
            cv2.putText(originalImage, "Mood", baseposition, font, 2, (255, 255, 255), 2, cv2.LINE_AA)
            originalImage[yPosition:yPosition + img.shape[0],
            xPosition:xPosition + img.shape[1]] = img

        return originalImage

    def renderGameStatus(self, dataSet, intrinsicData=None, gamesToRender=[], createVideo=False):

        thisGameDirectory = self._renderDirectory + "/" + dataSet.split("/")[-1].split(".")[0]

        renderIntrinsicInfo = False
        if not intrinsicData == None:
            renderIntrinsicInfo = True
            # self.imageSize = (self.imageSize[0] + 400, self.imageSize[1] + 400, 3)

        if not os.path.exists(thisGameDirectory):
            os.mkdir(thisGameDirectory)

        self.currentGameDirectory = thisGameDirectory

        # gameToRender = gameToRender-1
        # Read the gamelog

        images = []
        self.currentFrameNumber = 0

        originalImage = numpy.zeros(self.imageSize)
        originalImage = self.drawPlayField(originalImage)
        image = self.writeHeader(originalImage, "Game starting!")
        self.saveImages(image, 1)

        currentPizza = 0
        lastPassPizza = 0

        lineCounter = 0

        player1LastAction = ""
        player2LastAction = ""
        player3LastAction = ""
        player4LastAction = ""

        readFile = pd.read_pickle(dataSet)

        moodCounter = 0
        agentsNames = []
        previousHand = []
        previousBoard = []
        previousPlayerStatus = ["","","",""]
        lastTurnPizza = False
        pizzaLastRoud = 0
        for lineCounter, row in readFile.iterrows():
            # if moodCounter < 10:
            print("Processing line:" + str(lineCounter))
            actionType = row["Action Type"]
            gameNumber = row["Game Number"]

            if len(agentsNames) == 0:
                agentsNames = row["Agent Names"]

            # print ("Game Number :" + str(gameNumber) + " - Render: " + str(gameToRender))
            if not actionType == "" and gameNumber in gamesToRender:
                playerHand = row["Player Hand"]
                board = row["Board"]
                cardsAction = row["Cards Action"]
                wrongAction = row["Wrong Actions"]
                reward = row["Reward"]
                score = row["Scores"]
                roles = row["Roles"]
                rounds = row["Round Number"]
                player = row["Player"]
                playerStatus = row["Players Status"]


                if not player == "":
                    player = int(player)

                if not rounds == "":
                    rounds = int(rounds) + 1

                if player== 0:
                   player1LastAction = actionType
                if player ==1:
                    player2LastAction = actionType
                if player == 2:
                    player3LastAction = actionType
                if player == 3:
                    player4LastAction = actionType

                # Always draw these
                originalImage = numpy.zeros(self.imageSize)
                originalImage = self.drawPlayField(originalImage)

                #Finishing Position
                if not actionType == DataSetManager.actionChangeRole and len(score) > 0:
                    originalImage = self.drawFinishingPosition(originalImage, playerStatus, score)


                # Draw the mood if possible
                if (
                        actionType == DataSetManager.actionPass or actionType == DataSetManager.actionDiscard or actionType == DataSetManager.actionFinish) and renderIntrinsicInfo:
                    originalImage = self.getMoodPlots(intrinsicData, gameNumber, moodCounter, originalImage)
                    moodCounter = moodCounter + 1

                if not roles == "":
                    originalImage = self.drawRoleCards(originalImage, roles)

                if not player == "" and len(previousHand) > 0:
                    originalImage = self.drawPlayers(previousHand, originalImage, agentsNames)

                    header = "Round: " + str(rounds) + " - Turn: Player " + str(agentsNames[player])
                    originalImage = self.writeHeader(originalImage, header)
                    if not previousBoard == []:
                        originalImage = self.drawBoard(originalImage, previousBoard)

                    if len(previousPlayerStatus) > 0:
                        originalImage = self.drawPassCard(originalImage,previousPlayerStatus)

                    self.saveImages(originalImage, 2)

                previousHand = playerHand
                previousBoard = board
                previousPlayerStatus = (
                    player1LastAction, player2LastAction, player3LastAction, player4LastAction)
                originalImage = self.drawPlayers(playerHand, originalImage, agentsNames)

                if not board == []:
                    originalImage = self.drawBoard(originalImage, board)

                if len(playerStatus) > 0:
                    if lastTurnPizza and pizzaLastRoud < rounds:
                        lastTurnPizza = False
                    originalImage = self.drawPassCard(originalImage, (
                    player1LastAction, player2LastAction, player3LastAction, player4LastAction))

                # IF action is to deal cards
                # print ("Action type:" + str(actionType))
                if actionType == DataSetManager.actionDeal:
                    originalImage = self.writeHeader(originalImage, "Dealing cards!")

                elif actionType == DataSetManager.actionChangeRole:

                    actionCards = cardsAction
                    message = []

                    if not actionCards[0] == "":
                        message.append("- Player :" + str(agentsNames[actionCards[1]]) + " declared " + str(
                            actionCards[0]) + "!")

                    if actionCards[0] == "FoodFight":
                        message.append("New roles updated!")

                    message.append("- Dishwasher: Player " + str(agentsNames[int(roles[3])]))
                    message.append("- Waiter: Player" + str(agentsNames[int(roles[2])]))
                    message.append("- Souschef: Player" + str(agentsNames[int(roles[1])]))
                    message.append("- Chef: Player" + str(agentsNames[int(roles[0])]))

                    if actionCards[0] == "" or actionCards[0] == "FoodFight":
                        message.append("")
                        message.append("Cards Exchanged!")
                        message.append(
                            "Dishwasher gave " + str(actionCards[2]) + " - received " + str(actionCards[3]))
                        message.append("Waiter gave " + str(actionCards[3]) + " - received " + str(actionCards[2]))
                        message.append(
                            "Souschef gave " + str(actionCards[4]) + " - received " + str(actionCards[1]))
                        message.append("Chef gave " + str(actionCards[5]) + " - received " + str(actionCards[0]))

                    originalImage = self.writeHeader(originalImage, "Exchanging roles and cards!",
                                                     detailedMessage=message)

                elif actionType == DataSetManager.actionDiscard:

                    header = "Round: " + str(rounds) + " - Turn: Player " + str(agentsNames[player])

                    message = []
                    message.append("Player " + str(agentsNames[player]) + " Discarded: " + str(cardsAction))
                    message.append("Reward: " + str(reward))
                    message.append("Wrong actions: " + str(wrongAction))

                    originalImage = self.writeHeader(originalImage, header,
                                                     detailedMessage=message)

                elif actionType == DataSetManager.actionPass:

                    if int(player) == 0:
                        player1LastAction = DataSetManager.actionPass
                    elif int(player) == 1:
                        player2LastAction = DataSetManager.actionPass
                    elif int(player) == 2:
                        player3LastAction = DataSetManager.actionPass
                    elif int(player) == 3:
                        player4LastAction = DataSetManager.actionPass

                    header = "Round: " + str(rounds) + " - Turn: Player " + str(agentsNames[player])

                    message = []
                    message.append("Player " + str(agentsNames[player]) + " Passed!")
                    message.append("Reward: " + str(reward))
                    message.append("Wrong actions: " + str(wrongAction))

                    originalImage = self.writeHeader(originalImage, header,
                                                     detailedMessage=message)

                elif actionType == DataSetManager.actionFinish:

                    header = "Round: " + str(rounds) + " - Turn: Player " + str(agentsNames[player])

                    message = []
                    message.append("Player " + str(agentsNames[player]) + " Finished!!")

                    originalImage = self.writeHeader(originalImage, header,
                                                     detailedMessage=message)

                elif actionType == DataSetManager.actionPizzaReady:
                    header = "Pizza ready!"
                    originalImage = self.writeHeader(originalImage, header)

                    player1LastAction = ""
                    player2LastAction = ""
                    player3LastAction = ""
                    player4LastAction = ""

                    lastTurnPizza = True
                    pizzaLastRoud = rounds
                    print ("Clear PlayerActions!")

                self.saveImages(originalImage, 3)

                # print ("Line:" + str(lineCounter))
            # lineCounter = lineCounter + 1
            # if lineCounter > 30:
            #     break

        if createVideo:
            self.createVideo(gamesToRender)
