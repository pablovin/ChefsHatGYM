# -*- coding: utf-8 -*-
import datetime
import numpy as np
import pandas as pd
from copy import copy
from typing import Literal

# Action types
actionDeal = "DEAL"
actionDiscard = "DISCARD"
actionPizzaReady = "PIZZA_READY"
actionChangeRole = "ROLE_CHANGE"
actionPass = "PASS"
actionFinish = "FINISH"
actionInvalid = "INVALID"

actionNewGame = "New_Game"


ACTION_TYPES = {
    "START_EXPERIMENT": "START_EXPERIMENT",
    "NEW_MATCH": "NEW_MATCH",
    "DEAL_CARDS": "DEAL_CARDS",
    "DISCARD": "DISCARD",
    "DECLARE_PIZZA": "DECLARE_PIZZA",
    "END_MATCH": "END_MATCH",
    "CARD_EXCHANGE": "CARD_EXCHANGE",
    "DECLARE_SPECIAL_ACTION": "DECLARE_SPECIAL_ACTION",
    "END_EXPERIMENT": "END_EXPERIMENT",
}


class DataSetManager:
    """DataSet Manager Class

    This class manages the function of the framework to create datasets. Here each datapoint is created, and written if necessary.


    Attributes:
        dataSetDiretory (String): This variable keeps the directory which the dataSet files are stored.

    Author: Pablo Barros
    Created on: 26.02.2020
    Last Update: 19.08.2024

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

    # @property
    # def verbose(self):
    #     return self._verbose

    dataFrame = ""

    def __init__(self, dataSetDirectory=None):
        # sys.stdout = open(logDirectory+"2.txt",'w')
        """
        Constructor function, which basically verifies if the dataSetdirectory is correct,
        and if so, or creates or loads the log file.

        Args:
            logDirectory (String): the directory where the dataSet will be is saved
            verbose(Boolean): Indicates if the log will also be printed in the console
        """
        self._save_dataset = False
        if dataSetDirectory:
            self._dataSetDirectory = dataSetDirectory
            self._currentDataSetFile = self._dataSetDirectory + "/Dataset.pkl"
            self._save_dataset = True

    def _create_row(
        self,
        match_number: int = 0,
        round_number: int = 0,
        agent_names: list = np.nan,
        source: str = "SYSTEM",
        action_type: str = np.nan,
        action_description: str = np.nan,
        player_finished: bool = np.nan,
        player_hands: list = np.nan,
        board_before: list = np.nan,
        board_after: list = np.nan,
        possible_actions: list = np.nan,
        current_roles: list = np.nan,
        match_score: list = np.nan,
        game_score: list = np.nan,
        game_performance_score: list = np.nan,
    ):

        player_hands = copy(player_hands)
        board_before = copy(board_before)
        board_after = copy(board_after)
        possible_actions = copy(possible_actions)
        current_roles = copy(current_roles)
        match_score = copy(match_score)
        game_score = copy(game_score)
        game_performance_score = copy(game_performance_score)

        this_row = {}
        this_row["Match"] = match_number
        this_row["Round"] = round_number
        this_row["Agent_Names"] = [agent_names]
        this_row["Source"] = source
        this_row["Action_Type"] = action_type
        this_row["Action_Description"] = action_description
        this_row["Player_Finished"] = player_finished
        this_row["Player_Hands"] = [player_hands]
        this_row["Board_Before"] = [board_before]
        this_row["Board_After"] = [board_after]
        this_row["Possible_Actions"] = [possible_actions]
        this_row["Current_Roles"] = [current_roles]
        this_row["Match_Score"] = [match_score]
        this_row["Game_Score"] = [game_score]
        this_row["Game_Performance_Score"] = [game_performance_score]
        # print(this_row)
        date = str(datetime.datetime.now()).replace(" ", "_")
        return pd.DataFrame(this_row, index=[date])

    def addDataFrame(self, row_df):

        self.dataFrame = pd.concat([self.dataFrame, row_df])

    def startNewGame(self, agent_names):
        if self._save_dataset:
            self.dataFrame = self._create_row(
                match_number=0,
                round_number=0,
                agent_names=agent_names,
                source="SYSTEM",
                action_type=ACTION_TYPES["START_EXPERIMENT"],
            )

    def startNewMatch(
        self,
        match_number,
        game_score,
        current_roles,
    ):
        if self._save_dataset:
            if len(current_roles) == 0:
                current_roles = np.nan

            this_row = self._create_row(
                match_number=match_number,
                round_number=0,
                source="SYSTEM",
                game_score=game_score,
                action_type=ACTION_TYPES["NEW_MATCH"],
                current_roles=current_roles,
            )

            self.addDataFrame(this_row)

    def end_match(
        self,
        match_number,
        round_number,
        match_score,
        game_score,
        current_roles,
    ):
        if self._save_dataset:
            this_row = self._create_row(
                match_number=match_number,
                round_number=round_number,
                source="SYSTEM",
                match_score=match_score,
                game_score=game_score,
                action_type=ACTION_TYPES["END_MATCH"],
                current_roles=current_roles,
            )

            self.addDataFrame(this_row)

    def end_experiment(
        self,
        match_number,
        round_number,
        current_roles,
        game_score,
        game_performance,
    ):
        if self._save_dataset:
            this_row = self._create_row(
                match_number=match_number,
                round_number=round_number,
                source="SYSTEM",
                game_score=game_score,
                game_performance_score=game_performance,
                action_type=ACTION_TYPES["END_EXPERIMENT"],
                current_roles=current_roles,
            )

            self.addDataFrame(this_row)

    def dealAction(self, match_number, player_hands):
        if self._save_dataset:
            this_row = self._create_row(
                match_number=match_number,
                round_number=0,
                source="SYSTEM",
                player_hands=player_hands,
                action_type=ACTION_TYPES["DEAL_CARDS"],
            )

            self.addDataFrame(this_row)
        # actionType = actionDeal
        # self.addDataFrame(
        #     actionType=actionType, playersHand=playersHand, gameNumber=game
        # )

    def declare_pizza(
        self,
        match_number,
        round_number,
        source,
    ):
        if self._save_dataset:
            this_row = self._create_row(
                match_number=match_number,
                round_number=round_number,
                source=source,
                action_type=ACTION_TYPES["DECLARE_PIZZA"],
            )

            self.addDataFrame(this_row)

    def doDiscard(
        self,
        match_number,
        round_number,
        source,
        action_description,
        player_hands,
        board_before,
        board_after,
        possible_actions,
        player_finished,
    ):
        if self._save_dataset:
            this_row = self._create_row(
                match_number=match_number,
                round_number=round_number,
                source=source,
                player_hands=player_hands,
                action_type=ACTION_TYPES["DISCARD"],
                action_description=action_description,
                board_before=board_before,
                board_after=board_after,
                possible_actions=possible_actions,
                player_finished=bool(player_finished),
            )

            self.addDataFrame(this_row)

    def do_card_exchange(
        self,
        match_number,
        action_description,
        player_hands,
    ):
        if self._save_dataset:
            this_row = self._create_row(
                match_number=match_number,
                round_number=0,
                source="SYSTEM",
                player_hands=player_hands,
                action_type=ACTION_TYPES["CARD_EXCHANGE"],
                action_description=[action_description],
            )

            self.addDataFrame(this_row)

    def do_special_action(
        self, match_number, source, current_roles, action_description
    ):
        if self._save_dataset:
            this_row = self._create_row(
                match_number=match_number,
                round_number=0,
                source=source,
                action_type=ACTION_TYPES["DECLARE_SPECIAL_ACTION"],
                current_roles=current_roles,
                action_description=action_description,
            )

            self.addDataFrame(this_row)

    def saveFile(self):
        self.dataFrame.to_pickle(self.currentDataSetFile)
        self.dataFrame.to_csv(
            self.currentDataSetFile + ".csv", index=False, header=True
        )
