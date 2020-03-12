# -*- coding: utf-8 -*-
import datetime
import sys
import datetime
import csv

class MetricsManager:
    """DataSet Manager Class

    This class manages the function of the framework to create a metrics summary. Here each metric data point is created, and written if necessary.


    Attributes:
        dataSetDiretory (String): This variable keeps the directory which the dataSet files are stored.


    Author: Pablo Barros
    Created on: 12.03.2020
    Last Update: 12.03.2020

    Todo:
        * Create functions to log images and graphs as well.
    """

    @property
    def actions(self):
        return self._actions

    @property
    def dataSetDirectory(self):
        return self._metricDirectory


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

        self._metricDirectory = dataSetDirectory

        self._verbose = verbose

        self._actions = []

    def saveMetricPlayer(self, metrics):

        self._currentDataSetFile = self._metricDirectory + "/Metrics_Player.csv"

        with open(self._currentDataSetFile, mode='a') as employee_file:
            employee_writer = csv.writer(employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            employee_writer.writerow(
                ["Game", "P1_position",  "P1_average_reward",  "P1_Q1_passes", "P1_Q1_discards",
                 "P1_Q2_passes", "P1_Q2_discards", "P1_Q3_passes", "P1_Q3_discards", "P1_Q4_passes", "P1_Q4_discards",
                 "P2_position", "P2_average_reward",  "P2_Q1_passes", "P2_Q1_discards",
                 "P2_Q2_passes", "P2_Q2_discards", "P2_Q3_passes", "P2_Q3_discards", "P2_Q4_passes", "P2_Q4_discards",
                 "P3_position", "P3_average_reward",  "P3_Q1_passes", "P3_Q1_discards",
                 "P3_Q2_passes", "P3_Q2_discards", "P3_Q3_passes", "P3_Q3_discards", "P3_Q4_passes", "P3_Q4_discards",
                 "P4_position", "P4_average_reward", "P4_Q1_passes", "P4_Q1_discards",
                 "P4_Q2_passes", "P4_Q2_discards", "P4_Q3_passes", "P4_Q3_discards", "P4_Q4_passes", "P4_Q4_discards",
                 ])
            for m in metrics:
                employee_writer.writerow(
                    m)

