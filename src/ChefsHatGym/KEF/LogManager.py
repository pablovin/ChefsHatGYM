# -*- coding: utf-8 -*-
import datetime
import sys
import logging


class Logger:
    """Log Manager Class

    This class manager the log function of the framework. Here the log is created, and written if necessary.


    Attributes:
        logDiretory (String): This variable keeps the directory which the log file is saved.


    Author: Pablo Barros
    Created on: 02.02.2017
    Last Update: 20.02.2017

    Todo:
        * Create functions to log images and graphs as well.
    """

    @property
    def logDirectory(self):
        return self._logDirectory

    @property
    def verbose(self):
        return self._verbose

    def __init__(
        self, logDirectory=None, saveLog=True, verbose=True, experimentName=""
    ):
        """
        Constructor function, which basically verifies if the logdirectory is correct,
        and if so, or creates or loads the log file.

        Args:
            logDirectory (String): the directory where the log is / will be is saved
            saveLog(Boolean): Indicates if the log will be created or not
            verbose(Boolean): Indicates if the log will be displayed on the console or not
            experimentName(Boolean): Indicates the experiment name, to be used as log name

        Raises:

            Exception: if the logDirectory is invalid.

        """

        # if saveLog:
        #     try:
        #         self.isLogDirectoryValid(logDirectory)
        #     except:
        #         raise Exception("Log file not found!")

        #     else:
        #         self._logDirectory = logDirectory

        self._verbose = verbose

        self._saveLog = saveLog

        # Creating logger

        logger = logging.getLogger(experimentName)
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            fmt="%(asctime)s %(levelname)-8s %(message)s",
            datefmt="%Y %m %d %H:%M:%S",
        )
        # print(f"Game Log: {experimentName} - {logger}")

        # print(f"Save Log: {saveLog}")
        if saveLog:

            file_handler = logging.FileHandler(
                logDirectory,
                mode="w",
                encoding="utf-8",
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        print(f"Verbose: {verbose}")
        if verbose:
            # Create a stream handler to print logs to the console
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        self.logger = logger

    def write(self, message):
        """
        Function that writes messages in the log.

        Args:
            message (String): The message which will be written in the log.

        Raises:

            Exception: if the logDirectory is invalid.

        """

        self.logger.info(message)

        # try:
        #     logFile = open(self.logDirectory, "a")
        # except:
        #     raise Exception("Log file not found!")

        # else:
        #     if self._saveLog:
        #         logFile.write(
        #             str(datetime.datetime.now()).replace(" ", "_")
        #             + "-"
        #             + str(message)
        #             + "\n"
        #         )
        #         logFile.close

        #     if self._verbose:
        #         print(
        #             str(datetime.datetime.now()).replace(" ", "_") + "-" + str(message)
        #         )

    def newLogSession(self, sessionName):
        """
        Function that writes a new session in the Log.

        Args:
            sessionName (String): The name of the new session

        Raises:

            Exception: if the logDirectory is invalid.

        """
        self.write(
            "-----------------------------------------------------------------------------------------------------"
        )
        self.write(sessionName)
        self.write(
            "-----------------------------------------------------------------------------------------------------"
        )

        # try:
        #     logFile = open(self.logDirectory, "a")
        # except:
        #     raise Exception("Log file not found! Looked at:", self.logDirectory)

        # else:
        #     if self._saveLog:
        #         logFile.write(
        #             "-----------------------------------------------------------------------------------------------------\n"
        #         )
        #         logFile.write(str(sessionName + "\n"))
        #         logFile.write(
        #             "-----------------------------------------------------------------------------------------------------\n"
        #         )
        #         logFile.close

        #     if self._verbose:
        #         print(
        #             "-----------------------------------------------------------------------------------------------------\n"
        #         )
        #         print(str(sessionName))
        #         print(
        #             "-----------------------------------------------------------------------------------------------------\n"
        #         )

    def endLogSession(self):
        """
        Function that writes the end of a session in the Log.

        Args:
            sessionName (String): The name of the new session

        Raises:

            Exception: if the logDirectory is invalid.

        """
        self.write(
            "-----------------------------------------------------------------------------------------------------"
        )
        self.write(
            "-----------------------------------------------------------------------------------------------------"
        )

        # try:
        #     logFile = open(self.logDirectory, "a")
        # except:
        #     raise Exception("Log file not found! Looked at:", self.logDirectory)

        # else:
        #     if self._saveLog:
        #         logFile.write(
        #             "-----------------------------------------------------------------------------------------------------\n"
        #         )
        #         logFile.write(
        #             "-----------------------------------------------------------------------------------------------------\n"
        #         )
        #         logFile.close

        #     if self._verbose:
        #         print(
        #             "-----------------------------------------------------------------------------------------------------\n"
        #         )
        #         print(
        #             "-----------------------------------------------------------------------------------------------------\n"
        #         )
