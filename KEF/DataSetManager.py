# -*- coding: utf-8 -*-
import datetime
import sys
import datetime
import csv
import pandas as pd
import numpy

# Action types
actionDeal = "DEAL"
actionDiscard = "DISCARD"
actionPizzaReady = "PIZZA_READY"
actionChangeRole ="ROLE_CHANGE"
actionPass = "PASS"
actionFinish = "FINISH"
actionInvalid = "INVALID"

actionNewGame = "New_Game"


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


    dataFrame = ""
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


    def addDataFrame(self, gameNumber ="", roundNumber ="", player="", actionType="", playersHand=[], board=[],
                     cardsAction="", reward="", qvalues="", loss="", wrongActions="", totalActions="",
                     score=[], roles="", playersStatus=[], agentNames="", possibleActions=[], performanceScore = []):

        #Guarantee is a copy

        score = numpy.copy(score)
        playersHand = numpy.copy(playersHand)
        board = numpy.copy(board)
        reward = numpy.copy(reward)
        qvalues = numpy.copy(qvalues)
        loss = numpy.copy(loss)
        roles= numpy.copy(roles)
        playersStatus = numpy.copy(playersStatus)

        date =  str(datetime.datetime.now()).replace(" ", "_")
        dataframe= [date, gameNumber,roundNumber,player,actionType,playersHand,board,possibleActions, cardsAction,reward,qvalues,loss,wrongActions,totalActions,
                    score,roles,playersStatus,agentNames, performanceScore]

        self.dataFrame.loc[-1] = dataframe
        self.dataFrame.index = self.dataFrame.index + 1


    def startNewGame(self):

        self._currentDataSetFile = self._dataSetDirectory+"/Dataset.pkl"

        columns = ["Time", "Game Number", "Round Number", "Player", "Action Type", "Player Hand",  "Board", "Possible Actions","Cards Action", "Reward",
                   "Qvalues", "Loss", "Wrong Actions", "Total Actions", # Current turn actions
                     "Scores", "Roles", "Players Status", "Agent Names", "Performance Score" # Game status
                         ]

        self.dataFrame = pd.DataFrame(columns = columns)


    def startNewMatch(self, gameNumber, agentsNames):

        self.addDataFrame(gameNumber=gameNumber, agentNames=agentsNames)


    def dealAction(self, playersHand, game):

        actionType = actionDeal

        self.addDataFrame(actionType=actionType, playersHand=playersHand, gameNumber=game)



    def doActionPizzaReady(self, roundNumber, board, playersHand, roles, score, playersStatus, game):

        actionType = actionPizzaReady

        self.addDataFrame(actionType=actionType, playersHand=playersHand, score=score,
                                      roundNumber=roundNumber, board=board,
                                      roles=roles, playersStatus=playersStatus, gameNumber=game)



    def doActionAction(self, game, player, roundNumber, action, board, wrongActions, reward,
                       playersHand, roles, score, playersStatus, qValue, loss, totalActions, possibleActions):

        actionCards = ""
        actionType = action[0]
        actionCards = action[1]

        self.addDataFrame(gameNumber=game, roundNumber=roundNumber, player=player,
                                      actionType=actionType, playersHand=playersHand,
                                      board=board, cardsAction=actionCards, reward=reward,
                                      qvalues=qValue, loss=loss, wrongActions=wrongActions,
                                      totalActions=totalActions, score=score, roles=roles, playersStatus=playersStatus, possibleActions=possibleActions
                                      )



    def exchangeRolesAction(self, playersHand, roles, cardsAction, game):

        actionType = actionChangeRole
        self.addDataFrame(actionType=actionType, playersHand=playersHand, cardsAction=cardsAction, roles=roles, gameNumber=game)



    def saveFile(self):
        self.dataFrame.to_pickle(self.currentDataSetFile)
        self.dataFrame.to_csv(self.currentDataSetFile+".csv", index=False, header=True)

