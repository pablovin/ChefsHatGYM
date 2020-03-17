# -*- coding: utf-8 -*-
import datetime
import sys
import datetime
import csv

# Action types
actionDeal = "DEAL"
actionDiscard = "DISCARD"
actionPizzaReady = "PIZZA_READY"
actionChangeRole ="ROLE_CHANGE"
actionPass = "PASS"
actionFinish = "FINISH"


class DataSetManager:
    """DataSet Manager Class

    This class manages the function of the framework to create datasets. Here each datapoint is created, and written if necessary.


    Attributes:
        dataSetDiretory (String): This variable keeps the directory which the dataSet files are stored.


    Author: Pablo Barros
    Created on: 26.02.2020
    Last Update: 26.02.2020

    Todo:
        * Create functions to log images and graphs as well.
    """

    @property
    def actions(self):
        return self._actions

    @property
    def dataSetDirectory(self):
        return self._dataSetDirectory


    @property
    def currentDataSetFile(self):
        return self._currentDataSetFile

    @property
    def verbose(self):
        return self._verbose

    def __init__(self, dataSetDirectory=None, verbose=True):

        # sys.stdout = open(logDirectory+"2.txt",'w')

        """
        Constructor function, which basically verifies if the dataSetdirectory is correct,
        and if so, or creates or loads the log file.

        Args:
            logDirectory (String): the directory where the dataSet will be is saved
            verbose(Boolean): Indicates if the log will also be printed in the console


        """

        self._dataSetDirectory = dataSetDirectory

        self._verbose = verbose

        self._actions = []

    def startNewGame(self, gameNumber):

        self._currentDataSetFile = self._dataSetDirectory+"/Game_"+str(gameNumber)+".csv"

        with open(self._currentDataSetFile, mode='a') as employee_file:
            employee_writer = csv.writer(employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            employee_writer.writerow(
                ["Time", "Action Type", "Player Hand",  "Board", "Cards Action",
                 "Wrong Actions", "Correct Actions", "Reward", "Score", "Roles", "Round Number", "Player", "Players Status"])


    def logAction(self, actionType,  playersHand="",  board="", cardsAction="", wrongActions="", reward="", score="", roles="", roundNumber ="", player="", playersStatus ="", correctActions=""):

        time = str(datetime.datetime.now()).replace(" ", "_")
        # message = time + ";" + actionType + ";" + playersHandBefore + ";" + playersHandAfter + ";" + boardBefore + ";" + boardAfter + ";" + cardsAction + ";" + wrongActions + ";" + reward + ";" + score

        with open(self._currentDataSetFile, mode='a') as employee_file:
            employee_writer = csv.writer(employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            employee_writer.writerow([time, actionType , playersHand , board ,cardsAction , wrongActions , correctActions, reward , score, roles, roundNumber, player, playersStatus])

        #
        # try:
        #     logFile = open(self._currentDataSetFile, "a")
        # except:
        #     raise Exception("Dataset file not found!")
        #
        # else:
        #     logFile.write(str(message) + "\n")
        #     logFile.close

    def dealAction(self, playersHand, score):

        actionType = actionDeal

        playersHandAfter = ""
        for i in range(len(playersHand)):
            playersHandAfter += str(playersHand[i])
            if i < len(playersHand)-1:
                playersHandAfter+="_"

        score = ""
        for i in range(len(score)):
            score+= str(score[i])
            if i <len(playersHand)-1:
                score+="_"

        self.logAction(actionType=actionType, playersHand=playersHandAfter, score=score)


    def doActionPizzaReady(self, roundNumber, board, playersHand, roles, score, playersStatus):


        actionType = actionPizzaReady

        playersHandAfter = ""
        for i in range(len(playersHand)):
            playersHandAfter += str(playersHand[i])
            if i < len(playersHand) - 1:
                playersHandAfter += "_"

        boardList = ""
        for i in range(len(board)):
            boardList += str(board[i])
            if i < len(board) - 1:
                boardList += "_"

        playStatusList = ""
        for i in range(len(playersStatus)):
            playStatusList += str(playersStatus[i])
            if i < len(playersHand) - 1:
                playStatusList += "_"

        roles = str(roles)

        playersStatus = str(playStatusList)

        self.logAction(actionType=actionType, playersHand=playersHandAfter, score=score,
                       roundNumber=roundNumber, board=board,
                       roles=roles, playersStatus=playersStatus)



    def doActionAction(self, player, roundNumber, action, board, wrongActions, correctActions, reward, playersHand, roles, score, playersStatus):

        actionCards = ""

        if action == "Pass":
            actionType = actionPass
        elif action == "Finish" :
            actionType = actionFinish
        else:
            actionType = actionDiscard
            actionCards = action[1]


        playersHandAfter = ""
        for i in range(len(playersHand)):
            playersHandAfter += str(playersHand[i])
            if i < len(playersHand)-1:
                playersHandAfter+="_"

        boardList = ""
        for i in range(len(board)):
            boardList += str(board[i])
            if i < len(board)-1:
                boardList+="_"

        playStatusList = ""
        for i in range(len(playersStatus)):
            playStatusList += str(playersStatus[i])
            if i < len(playersHand)-1:
                playStatusList+="_"

        roles = str(roles)

        playersStatus = str(playStatusList)


        self.logAction(actionType=actionType, cardsAction =actionCards, playersHand=playersHandAfter, score=score, roundNumber=roundNumber, board=board, player=player, wrongActions=wrongActions, correctActions=correctActions, reward=reward, roles=roles, playersStatus=playersStatus)



    def exchangeRolesAction(self, playersHand, roles, cardsAction, score):

        actionType = actionChangeRole

        playersHandAfter = ""
        for i in range(len(playersHand)):
            playersHandAfter += str(playersHand[i])
            if i < len(playersHand)-1:
                playersHandAfter+="_"


        cardsActionList = ""
        for i in range(len(cardsAction)):
            cardsActionList += str(cardsAction[i])
            if i < len(cardsAction) - 1:
                cardsActionList += "_"


        roles = str(roles)

        self.logAction(actionType=actionType, playersHand=playersHandAfter, roles=roles, score=score, cardsAction=cardsActionList)

