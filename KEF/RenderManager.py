# -*- coding: utf-8 -*-
import cv2
import csv
import copy
import shutil

import subprocess

import numpy
import os


from KEF import DataSetManager

class RenderManager():

    fps = 10
    imageSize = (2160,3840, 3)

    playField =""
    playingFieldDirectory = "images/playingField.png"

    currentGameDirectory = ""
    currentFrameNumber = 0

    cards = ""
    cardsDirectory = "images/deck"

    actionCardsDirectory = "images/actionCards/"
    passCard =""
    roleCards = []

    saveVideoDirectory = ""

    blackCard = ""

    @property
    def renderDirectory(self):
        return self._renderDirectory

    def __init__(self, saveVideoDirectory, fps=1):

        self._renderDirectory = "renderTMP/"
        self.saveVideoDirectory  = saveVideoDirectory

        if os.path.exists(self.renderDirectory):
            shutil.rmtree(self.renderDirectory)

        os.mkdir(self.renderDirectory)

        self.fps = fps

        self.getImages()


    def writeHeader(self, originalImage, message, detailedMessage=[]):


        images = []
        image = copy.copy(originalImage)
        font = cv2.FONT_HERSHEY_SIMPLEX

        yPosition = int((image.shape[0] - self.playField.shape[0]) / 2) +800
        xPosition = int((image.shape[1] - self.playField.shape[1]) / 2) - 800
        baseposition = (yPosition,xPosition)

        cv2.putText(image, message, baseposition, font, 2, (255, 255, 255), 8, cv2.LINE_AA)


        if len(detailedMessage)>0:

            yPosition = int((image.shape[0] - self.playField.shape[0]) / 2) + 500
            xPosition = int((image.shape[1] - self.playField.shape[1]) / 2) + 800

            for i in range(len(detailedMessage)):
                baseposition = (yPosition, xPosition)
                cv2.putText(image, detailedMessage[i], baseposition, font, 1, (255, 255, 255), 2, cv2.LINE_AA)
                xPosition = xPosition+40

        return image



    def getImagesSeconds(self, image, seconds):

        totalFrames = seconds

        frames = []

        for i in range (totalFrames):

            # image = numpy.array(image).astype(numpy.uint8)
            # image = cv2.cvtColor(numpy.array(image), cv2.COLOR_BGR2RGB)
            frames.append(image)

        return frames

    def getImages(self):

        if self.playField == "":
            self.playField = numpy.array(cv2.imread(self.playingFieldDirectory))

        if self.cards == "":

            self.cards = {}

            cardImages = os.listdir(self.cardsDirectory)
            cardImages.sort(key=lambda f: int(f.split(".")[0]))
            cardNumber = 1
            for card in cardImages:
                self.cards[cardNumber] = cv2.resize(numpy.array(cv2.imread(self.cardsDirectory+"/"+card)), (141,195))
                cardNumber = cardNumber+1
            # print ("Size:", self.playField.shape)

        #Pass Card
        self.passCard = numpy.array(cv2.resize(cv2.imread(self.actionCardsDirectory+"/pass.png"), (176,243)))

        self.roleCards.append(cv2.resize(cv2.imread(self.actionCardsDirectory + "/dishwasher.png"), (176, 243)))
        self.roleCards.append(cv2.resize(cv2.imread(self.actionCardsDirectory + "/wait.png"), (176, 243)))
        self.roleCards.append(cv2.resize(cv2.imread(self.actionCardsDirectory + "/souschef.png"), (176, 243)))
        self.roleCards.append(cv2.resize(cv2.imread(self.actionCardsDirectory+"/chef.png"), (176 ,243)))

        self.blackCard = cv2.resize(numpy.array(cv2.imread(self.actionCardsDirectory + "/cardBlack.png")), (141,195))


        # self.playField = numpy.array(cv2.resize(self.playField,(1920, 1080)))

    def drawPlayers(self, playerHands, originalImage):

        font = cv2.FONT_HERSHEY_SIMPLEX

        images = []
        #Player 1

        basePosition = (50,50)
        cv2.putText(originalImage, "Player 1", basePosition, font, 2, (255, 255, 255), 2, cv2.LINE_AA)
        basePosition = (5, 5)
        yPosition = basePosition[0]
        xPosition = basePosition[1]


        #player1 cards

        for i in range(len(playerHands[0])):
            if playerHands[0][i] == 0:
                card = self.blackCard
            else:
                card = self.cards[playerHands[0][i]]

            if i % 5 == 0:
                yPosition = yPosition + card.shape[0] + 10
                xPosition = basePosition[1]
            else:
                xPosition = xPosition + card.shape[1] + 10

            originalImage[yPosition:yPosition + card.shape[0], xPosition:xPosition + card.shape[1]] = card
            #
            # for img in self.getImagesSeconds(originalImage, 1):
            #     images.append(img)


        #player 2
        if len(playerHands)>1:
            basePosition = (int(originalImage.shape[0] - (self.playField.shape[0] / 2) + self.playField.shape[0]) + 100, 50)
            cv2.putText(originalImage, "Player 2" , basePosition, font, 2, (255, 255, 255), 2, cv2.LINE_AA)

            basePosition = (int(originalImage.shape[0] - (self.playField.shape[0] / 2) + self.playField.shape[0]) + 100, 5)

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

                if i % 5 == 0:
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
                #originalImage[0:0 + card.shape[0], 0:0 + card.shape[1]] = card


        # player 3
        if len(playerHands)>2:
            basePosition = (50, int(originalImage.shape[1] - ( self.playField.shape[1]*1.3 )))
            cv2.putText(originalImage, "Player 3" , basePosition, font, 2, (255, 255, 255), 2, cv2.LINE_AA)

            # basePosition = (5, int(originalImage.shape[1] - (self.playField.shape[1] * 1.125)))
            basePosition = (5, int(originalImage.shape[1] - (self.playField.shape[1] * 1.125)))

            yPosition = basePosition[1]-500
            xPosition = basePosition[0]
            # player 3 cards
            for i in range(len(playerHands[2])):

                if playerHands[2][i] == 0:
                    card = self.blackCard
                else:
                    card = self.cards[playerHands[2][i]]

                if i % 5 == 0:
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
        if len(playerHands)>3:
            basePosition = (int(originalImage.shape[0] - (self.playField.shape[0] / 2) + self.playField.shape[0]) + 100, int(originalImage.shape[1] - ( self.playField.shape[1]*1.3 )))
            cv2.putText(originalImage, "Player 4" , basePosition, font, 2, (255, 255, 255), 2, cv2.LINE_AA)


            basePosition = (int(originalImage.shape[0] - (self.playField.shape[0] / 2) + self.playField.shape[0]) + 100, int(originalImage.shape[1] - (self.playField.shape[1] * 1.125)))

            yPosition = basePosition[1] - 500
            xPosition = basePosition[0]
            # player 3 cards
            for i in range(len(playerHands[3])):

                if playerHands[3][i] == 0:
                    card = self.blackCard
                else:
                    card = self.cards[playerHands[3][i]]

                if i % 5 == 0:
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

        yPosition = int((image.shape[0]  - self.playField.shape[0])/2) - 200
        xPosition = int((image.shape[1]  - self.playField.shape[1])/2) - 50
        image[yPosition:yPosition+self.playField.shape[0], xPosition:xPosition+self.playField.shape[1]] = self.playField

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
                    xPosition = int((originalImage.shape[1] - self.playField.shape[1]) / 2) + 840 + (currentBoardPlace*225)

                elif currentBoardPlace >=3 and currentBoardPlace < 8:

                    yPosition = int((originalImage.shape[0] - self.playField.shape[0]) / 2) + 420
                    xPosition = int((originalImage.shape[1] - self.playField.shape[1]) / 2) + 1070 + ((
                                currentBoardPlace-5) * 225)

                elif currentBoardPlace >= 8:

                    yPosition = int((originalImage.shape[0] - self.playField.shape[0]) / 2) + 720
                    xPosition = int((originalImage.shape[1] - self.playField.shape[1]) / 2) + 840 + ((
                                                                                                              currentBoardPlace - 8) * 225)

                originalImage[yPosition:yPosition + self.roleCards[0].shape[0],
                xPosition:xPosition + self.roleCards[0].shape[1]] = card



            currentBoardPlace = currentBoardPlace+1

        return originalImage

    def drawRoleCards(self, originalImage, roles):
        #Dishwasher role
        # roles = roles[1:-1].split(",")

        #Player 1
        for i in range (4):

            card = self.roleCards[i]

            if int(roles[i]) == 0:
                yPosition = int((originalImage.shape[0] - self.playField.shape[0]) / 2) + 45 - 200
                xPosition = int((originalImage.shape[1] - self.playField.shape[1]) / 2) + 390 -50
                originalImage[yPosition:yPosition + self.roleCards[0].shape[0], xPosition:xPosition + self.roleCards[0].shape[1]] = card

            if int(roles[i]) == 1:
                yPosition = int((originalImage.shape[0] - self.playField.shape[0]) / 2) + 45 - 200
                xPosition = int((originalImage.shape[1] - self.playField.shape[1]) / 2) + 1850 -50
                originalImage[yPosition:yPosition + self.roleCards[0].shape[0],
                xPosition:xPosition + self.roleCards[0].shape[1]] = card

            if int(roles[i]) == 2:
                yPosition = int((originalImage.shape[0] - self.playField.shape[0]) / 2) + 1210 - 200
                xPosition = int((originalImage.shape[1] - self.playField.shape[1]) / 2) + 390 -50
                originalImage[yPosition:yPosition + self.roleCards[0].shape[0],
                xPosition:xPosition + self.roleCards[0].shape[1]] = card

            if int(roles[i]) == 3:
                yPosition = int((originalImage.shape[0] - self.playField.shape[0]) / 2) + 1210 - 200
                xPosition = int((originalImage.shape[1] - self.playField.shape[1]) / 2) + 1850 -50
                originalImage[yPosition:yPosition + self.roleCards[0].shape[0],
                xPosition:xPosition + self.roleCards[0].shape[1]] = card


        return originalImage

    def drawFinishingPosition(self, originalImage, playerStatus, score):

        playerStatus = playerStatus.split("_")

        if playerStatus[0] == "Finish":
            if int(score[0]) == 0:
                card = self.roleCards[3]
            elif int(score[1]) == 0:
                card = self.roleCards[2]
            elif int(score[2]) == 0:
                card = self.roleCards[1]
            elif int(score[3]) == 0:
                card = self.roleCards[0]

            card = numpy.array(cv2.resize(card,(518, 719)))
            basePosition = (100, 100)
            yPosition = basePosition[0]
            xPosition = basePosition[1]

            originalImage[yPosition:yPosition + card.shape[0],
            xPosition:xPosition + card.shape[1]] = card

        if playerStatus[1] == "Finish":
            if int(score[0]) == 1:
                card = self.roleCards[3]
            elif int(score[1]) == 1:
                card = self.roleCards[2]
            elif int(score[2]) == 1:
                card = self.roleCards[1]
            elif int(score[3]) == 1:
                card = self.roleCards[0]

            card = numpy.array(cv2.resize(card,(518, 719)))

            basePosition = (100, 3048)

            yPosition = basePosition[0]
            xPosition = basePosition[1]

            originalImage[yPosition:yPosition + card.shape[0],
            xPosition:xPosition + card.shape[1]] = card

        if playerStatus[2] == "Finish":
            if int(score[0]) == 2:
                card = self.roleCards[3]
            elif int(score[1]) == 2:
                card = self.roleCards[2]
            elif int(score[2]) == 2:
                card = self.roleCards[1]
            elif int(score[3]) == 2:
                card = self.roleCards[0]

            card = numpy.array(cv2.resize(card,(518, 719)))

            basePosition = (1200, 100)

            yPosition = basePosition[0]
            xPosition = basePosition[1]

            originalImage[yPosition:yPosition + card.shape[0],
            xPosition:xPosition + card.shape[1]] = card

        if playerStatus[3] == "Finish":
            if int(score[0]) == 3:
                card = self.roleCards[3]
            elif int(score[1]) == 3:
                card = self.roleCards[2]
            elif int(score[2]) == 3:
                card = self.roleCards[1]
            elif int(score[3]) == 3:
                card = self.roleCards[0]

            card = numpy.array(cv2.resize(card,(518, 719)))

            # basePosition = (50 + int(originalImage.shape[0] - (self.playField.shape[0] / 2) + self.playField.shape[0]) + 100, 50 + int(originalImage.shape[1] - ( self.playField.shape[1]*1.3 )))

            basePosition = (1200, 3048)

            yPosition = basePosition[0]
            xPosition = basePosition[1]

            originalImage[yPosition:yPosition + card.shape[0],
            xPosition:xPosition + card.shape[1]] = card


        return originalImage


    def drawPassCard(self, originalImage, playerStatus, playerCurrentStatus):
        #Dishwasher role

        playerStatus =  playerStatus.split("_")

        card = self.passCard

        if playerStatus[0] == "Pass" and playerCurrentStatus[0]=="PASS":
            yPosition = int((originalImage.shape[0] - self.playField.shape[0]) / 2) + 120
            xPosition = int((originalImage.shape[1] - self.playField.shape[1]) / 2) + 620

            originalImage[yPosition:yPosition + self.roleCards[0].shape[0],
            xPosition:xPosition + self.roleCards[0].shape[1]] = card

        if playerStatus[1] == "Pass" and playerCurrentStatus[1]=="PASS":
            yPosition = int((originalImage.shape[0] - self.playField.shape[0]) / 2) + 120
            xPosition = int((originalImage.shape[1] - self.playField.shape[1]) / 2) + 1510
            originalImage[yPosition:yPosition + self.roleCards[0].shape[0],
            xPosition:xPosition + self.roleCards[0].shape[1]] = card

        if playerStatus[2] == "Pass" and playerCurrentStatus[2]=="PASS":
            yPosition = int((originalImage.shape[0] - self.playField.shape[0]) / 2) + 720
            xPosition = int((originalImage.shape[1] - self.playField.shape[1]) / 2) + 620
            originalImage[yPosition:yPosition + self.roleCards[0].shape[0],
            xPosition:xPosition + self.roleCards[0].shape[1]] = card

        if playerStatus[3] == "Pass" and  playerCurrentStatus[3]=="PASS":
            yPosition = int((originalImage.shape[0] - self.playField.shape[0]) / 2) + 720
            xPosition = int((originalImage.shape[1] - self.playField.shape[1]) / 2) + 1510
            originalImage[yPosition:yPosition + self.roleCards[0].shape[0],
            xPosition:xPosition + self.roleCards[0].shape[1]] = card

#
# " ['', ('Discard: ', [10, 10, 10, 12, 12]), '', ''] "
#         #Player 1
#         for i in range (4):
#             card = self.roleCards[i]
#
#             if int(roles[i]) == 0:
#                 yPosition = int((originalImage.shape[0] - self.playField.shape[0]) / 2) + 45
#                 xPosition = int((originalImage.shape[1] - self.playField.shape[1]) / 2) + 390
#                 originalImage[yPosition:yPosition + self.roleCards[0].shape[0], xPosition:xPosition + self.roleCards[0].shape[1]] = card
#
#             if int(roles[i]) == 1:
#                 yPosition = int((originalImage.shape[0] - self.playField.shape[0]) / 2) + 45
#                 xPosition = int((originalImage.shape[1] - self.playField.shape[1]) / 2) + 1850
#                 originalImage[yPosition:yPosition + self.roleCards[0].shape[0],
#                 xPosition:xPosition + self.roleCards[0].shape[1]] = card
#
#             if int(roles[i]) == 2:
#                 yPosition = int((originalImage.shape[0] - self.playField.shape[0]) / 2) + 1210
#                 xPosition = int((originalImage.shape[1] - self.playField.shape[1]) / 2) + 390
#                 originalImage[yPosition:yPosition + self.roleCards[0].shape[0],
#                 xPosition:xPosition + self.roleCards[0].shape[1]] = card
#
#             if int(roles[i]) == 3:
#                 yPosition = int((originalImage.shape[0] - self.playField.shape[0]) / 2) + 1210
#                 xPosition = int((originalImage.shape[1] - self.playField.shape[1]) / 2) + 1850
#                 originalImage[yPosition:yPosition + self.roleCards[0].shape[0],
#                 xPosition:xPosition + self.roleCards[0].shape[1]] = card


        return originalImage

    def saveImages(self, image, seconds):


        images = self.getImagesSeconds(image, seconds)

        for i in images:
            cv2.imwrite(self.currentGameDirectory + "/" + str(self.currentFrameNumber) + ".png", i)
            self.currentFrameNumber = self.currentFrameNumber+1


    def createVideo(self):

        command = "ffmpeg -i "+str(self.currentGameDirectory)+"/%d.png -framerate 1 -r "+str(self.fps)+"  "+str(self.saveVideoDirectory)+"video.avi"

        subprocess.call(command, shell=True)

        shutil.rmtree(self.currentGameDirectory)

        #
        # print ("Video here:", saveLocation+"/video.avi")
        #
        # # writer = cv2.VideoWriter(saveLocation+"/video.avi", cv2.VideoWriter_fourcc(*"MJPG"), self.fps, (self.imageSize[0], self.imageSize[1]))
        # # for frame in images:
        # #     writer.write(frame)
        # # writer.release()
        #
        # w = imageio.get_writer(saveLocation+"/video.avi", fps=self.fps)
        # for img in images:
        #     w.append_data(img)
        # w.close()
        #
        #
        # print("Video here:", saveLocation + "/video.avi")
        # #
        # # p = Popen(['ffmpeg', '-y', '-f', 'image2pipe', '-vcodec', 'mjpeg', '-r', '24', '-i', '-', '-vcodec', 'mpeg4',
        # #            '-qscale', '5', '-r', '24', saveLocation+"/video.avi"], stdin=PIPE)
        # # for img in images:
        # #     img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # #     im_pil = Image.fromarray(img)
        # #     im_pil.save(p.stdin, 'JPEG')
        # # p.stdin.close()
        # # p.wait()


    def renderGameStatus(self, gameLog, createVideo=False):

        thisGameDirectory = self._renderDirectory + "/"+gameLog.split("/")[-1].split(".")[0]
        if not os.path.exists(thisGameDirectory):
            os.mkdir(thisGameDirectory)

        self.currentGameDirectory = thisGameDirectory

        #Read the gamelog

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

        with open(gameLog, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            # line_count = 0

            for row in csv_reader:
                lineCounter = lineCounter + 1
                # if lineCounter>200:
                # if line_count == 0:
                #     line_count += 1

                actionType = row["Action Type"]
                playerHand = row["Player Hand"]
                board = row["Board"]
                cardsAction = row["Cards Action"]
                wrongAction = row["Wrong Actions"]
                reward = row["Reward"]
                score = row["Score"]
                roles = row["Roles"]
                rounds = row["Round Number"]
                player = row["Player"]
                playerStatus = row["Players Status"]

                #post-processin
                if not playerHand == "":
                    hands = playerHand.split("_")
                    playerHand = []
                    for hand in hands:
                        handAuxiliary = hand[1:-1].split(",")
                        currentHand = []
                        for a in handAuxiliary:
                            currentHand.append(int(a))
                        hand = numpy.array(currentHand)
                        playerHand.append(hand)

                if not board == "":
                    board = board[1:-1].split(",")

                if not roles =="":
                    roles = roles[1:-1].split(",")

                if not score =="":
                    score = score[1:-1].split(",")

                if not player=="":
                    player = int(player)+1

                if not rounds=="":
                    rounds = int(rounds)+1

                #Always draw these

                originalImage = numpy.zeros(self.imageSize)
                originalImage = self.drawPlayField(originalImage)

                originalImage = self.drawPlayers(playerHand, originalImage)

                if not roles == "":
                    originalImage = self.drawRoleCards(originalImage, roles)

                if not board =="":
                    originalImage = self.drawBoard(originalImage,board)

                if not playerStatus == "":
                    originalImage = self.drawPassCard(originalImage, playerStatus, (player1LastAction, player2LastAction, player3LastAction, player4LastAction))

                if not actionType == DataSetManager.actionChangeRole and  len(score) > 0 and not score[0]=="":
                    originalImage = self.drawFinishingPosition(originalImage,playerStatus,score)

                #IF action is to deal cards
                if actionType == DataSetManager.actionDeal:
                    originalImage = self.writeHeader(originalImage, "Dealing cards!")

                elif actionType == DataSetManager.actionChangeRole:

                    actionCards = cardsAction.split("_")
                    message = []

                    if not actionCards[0] == "":
                        message.append("- Player :" + str(actionCards[1]) + " declared " + str(
                            actionCards[0]) + "!")

                    if actionCards[0] == "FoodFight":
                        message.append("New roles updated!")

                    message.append("- Dishwasher: Player " + str(int(roles[3]) + 1))
                    message.append("- Waiter: Player" + str(int(roles[2]) + 1))
                    message.append("- Souschef: Player" + str(int(roles[1]) + 1))
                    message.append("- Chef: Player" + str(int(roles[0]) + 1))

                    if actionCards[0] == "" or actionCards[0] == "FoodFight" :
                        message.append("")
                        message.append("Cards Exchanged!")
                        message.append("Dishwasher gave " + str(actionCards[2] +" - received "+ str(actionCards[3])))
                        message.append("Waiter gave " + str(actionCards[3] +" - received "+ str(actionCards[2])))
                        message.append("Souschef gave " + str(actionCards[4] + " - received " + str(actionCards[1])))
                        message.append("Chef gave " + str(actionCards[5] + " - received " + str(actionCards[0])))


                    originalImage = self.writeHeader(originalImage, "Exchanging roles and cards!", detailedMessage=message)

                elif actionType == DataSetManager.actionDiscard:

                    header = "Round: " + str(rounds) + " - Turn: Player " + str(player)

                    message= []
                    message.append("Player " + str(player) + " Discarded: " + str(cardsAction))
                    message.append("Reward: " + str(reward))
                    message.append("Wrong actions: " + str(wrongAction))

                    originalImage = self.writeHeader(originalImage, header,
                                                     detailedMessage=message)

                elif actionType == DataSetManager.actionPass:

                    if int(player) == 1:
                        player1LastAction = "PASS"
                    elif int(player) == 2:
                        player2LastAction = "PASS"
                    elif int(player) == 3:
                        player3LastAction = "PASS"
                    elif int(player) == 4:
                        player4LastAction = "PASS"

                    header = "Round: " + str(rounds) + " - Turn: Player " + str(player)

                    message = []
                    message.append("Player " + str(player) + " Passed!")
                    message.append("Reward: " + str(reward))
                    message.append("Wrong actions: " + str(wrongAction))

                    originalImage = self.writeHeader(originalImage, header,
                                                     detailedMessage=message)

                elif actionType == DataSetManager.actionFinish:

                    header = "Round: " + str(rounds) + " - Turn: Player " + str(player)

                    message = []
                    message.append("Player " + str(player) + " Finished!!")

                    originalImage = self.writeHeader(originalImage, header,
                                                     detailedMessage=message)

                elif actionType == DataSetManager.actionPizzaReady:
                    header = "Pizza ready!"
                    originalImage = self.writeHeader(originalImage, header)

                    player1LastAction = ""
                    player2LastAction = ""
                    player3LastAction = ""
                    player4LastAction = ""





                self.saveImages(originalImage, 5)

                # if lineCounter == 10:
                #     break

                print ("Line:" + str(lineCounter))
                #

                # elif actionType == DataSetManager.actionPass:
                #
                    # self.createVideo(thisGameDirectory, images)
                    # frameNumber = self.saveImages(images, thisGameDirectory, frameNumber)

        if createVideo:
            self.createVideo()


# dataSet = "/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/Gym_Experiments/Player_4_Cards_11_games_2TrainAgents_['RANDOM', 'RANDOM', 'RANDOM', 'RANDOM']_Joker_Trial_QL_2020-02-29_16:30:17.444821/Datasets/Game_1.csv"
#
# render = RenderManager("/home/pablo/Documents/Datasets/ChefsHat_ReinforcementLearning/testRender/")
# render.renderGameStatus(dataSet)
#


