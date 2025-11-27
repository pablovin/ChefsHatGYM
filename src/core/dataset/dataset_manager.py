# -*- coding: utf-8 -*-
import datetime
import numpy as np
import pandas as pd
import os

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
    @property
    def actions(self):
        return self._actions

    @property
    def dataSetDirectory(self):
        return self._dataSetDirectory

    @property
    def currentDataSetFile(self):
        return self._currentDataSetFile

    def __init__(self, dataSetDirectory=None, flush_interval: int = 1):
        self._save_dataset = False
        self._buffer = []
        self._flush_interval = max(1, int(flush_interval))
        self._matches_since_flush = 0

        if dataSetDirectory:
            self._dataSetDirectory = os.path.join(dataSetDirectory, "dataset")
            os.makedirs(self._dataSetDirectory, exist_ok=True)

            # Base path for dataset files.  Despite the ``.pkl`` extension the
            # binary file is written using the HDF5 format which allows
            # efficient appends.
            self._currentDataSetFile = os.path.join(
                self._dataSetDirectory, "game_dataset.pkl"
            )
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
        current_roles: dict = np.nan,
        match_score: list = np.nan,
        game_score: dict = np.nan,
        game_performance_score: list = np.nan,
    ):

        if self._save_dataset:

            this_row = {
                "Match": match_number,
                "Round": round_number,
                "Agent_Names": agent_names,
                "Source": source,
                "Action_Type": action_type,
                "Action_Description": action_description,
                "Player_Finished": player_finished,
                "Player_Hands": player_hands,
                "Board_Before": board_before,
                "Board_After": board_after,
                "Possible_Actions": possible_actions,
                "Current_Roles": current_roles,
                "Match_Score": match_score,
                "Game_Score": game_score,
                "Game_Performance_Score": game_performance_score,
            }

            date = str(datetime.datetime.now()).replace(" ", "_")

            return pd.DataFrame([this_row], index=[date])

    def addDataFrame(self, row_df):
        if self._save_dataset and row_df is not None:
            self._buffer.append(row_df)

    def flush_to_disk(self):
        if self._save_dataset and self._buffer:
            combined_df = pd.concat(self._buffer, ignore_index=False)

            # Save to CSV
            csv_file = self.currentDataSetFile + ".csv"
            write_header = not os.path.exists(csv_file)
            combined_df.to_csv(csv_file, mode="a", header=write_header, index=False)

            # Efficiently append to HDF5 instead of rewriting a pickle file
            # combined_df.reset_index(drop=True, inplace=True)

            # Ensure numeric columns use a consistent dtype when saving to HDF5
            # Values might come through as strings or ``None`` which would
            # normally cause ``astype`` to fail. ``to_numeric`` coerces
            # non-numeric values to ``NaN`` so they can be stored using the
            # nullable ``Int64`` dtype.
            # if "Match" in combined_df.columns:
            #     combined_df["Match"] = (
            #         pd.to_numeric(combined_df["Match"], errors="coerce")
            #         .astype("Int64")
            #     )
            # if "Round" in combined_df.columns:
            #     combined_df["Round"] = (
            #         pd.to_numeric(combined_df["Round"], errors="coerce")
            #         .astype("Int64")
            #     )
            # combined_df.to_hdf(
            #     self.currentDataSetFile,
            #     key="data",
            #     format="table",
            #     append=True,
            #     mode="a",
            # )
            self._buffer = []
            self._matches_since_flush = 0

    def startNewGame(self, agent_names):
        self._buffer = []  # Reset buffer on new game
        self._matches_since_flush = 0
        self.addDataFrame(
            self._create_row(
                match_number=0,
                round_number=0,
                agent_names=agent_names,
                source="SYSTEM",
                action_type=ACTION_TYPES["START_EXPERIMENT"],
            )
        )

    def startNewMatch(self, match_number, game_score, current_roles):
        if len(current_roles) == 0:
            current_roles = np.nan
        self.addDataFrame(
            self._create_row(
                match_number=match_number,
                round_number=0,
                source="SYSTEM",
                game_score=game_score,
                action_type=ACTION_TYPES["NEW_MATCH"],
                current_roles=current_roles,
            )
        )

    def end_match(
        self, match_number, round_number, match_score, game_score, current_roles
    ):
        if self._save_dataset:
            self.addDataFrame(
                self._create_row(
                    match_number=match_number,
                    round_number=round_number,
                    source="SYSTEM",
                    match_score=match_score,
                    game_score=game_score,
                    action_type=ACTION_TYPES["END_MATCH"],
                    current_roles=current_roles,
                )
            )
            self._matches_since_flush += 1
            if self._matches_since_flush >= self._flush_interval:
                self.flush_to_disk()

    def end_experiment(
        self, match_number, round_number, current_roles, game_score, game_performance
    ):
        self.addDataFrame(
            self._create_row(
                match_number=match_number,
                round_number=round_number,
                source="SYSTEM",
                game_score=game_score,
                game_performance_score=game_performance,
                action_type=ACTION_TYPES["END_EXPERIMENT"],
                current_roles=current_roles,
            )
        )
        self.flush_to_disk()

    def dealAction(self, match_number, player_hands):

        # print(f"SAVING PLAYER HANDS: {player_hands}")
        self.addDataFrame(
            self._create_row(
                match_number=match_number,
                round_number=0,
                source="SYSTEM",
                player_hands=player_hands,
                action_type=ACTION_TYPES["DEAL_CARDS"],
            )
        )

    def declare_pizza(self, match_number, round_number, source):
        self.addDataFrame(
            self._create_row(
                match_number=match_number,
                round_number=round_number,
                source=source,
                action_type=ACTION_TYPES["DECLARE_PIZZA"],
            )
        )

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
        self.addDataFrame(
            self._create_row(
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
        )

    def do_card_exchange(self, match_number, action_description, player_hands):
        self.addDataFrame(
            self._create_row(
                match_number=match_number,
                round_number=0,
                source="SYSTEM",
                player_hands=player_hands,
                action_type=ACTION_TYPES["CARD_EXCHANGE"],
                action_description=action_description,
            )
        )

    def do_special_action(
        self, match_number, source, current_roles, action_description
    ):
        self.addDataFrame(
            self._create_row(
                match_number=match_number,
                round_number=0,
                source=source,
                action_type=ACTION_TYPES["DECLARE_SPECIAL_ACTION"],
                current_roles=current_roles,
                action_description=action_description,
            )
        )

    def saveFile(self):
        self.flush_to_disk()
