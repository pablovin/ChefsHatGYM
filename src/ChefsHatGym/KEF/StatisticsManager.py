# -*- coding: utf-8 -*-
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy
import pandas as pd
import datetime

import csv

from dateutil import parser

import os

import csv

from ChefsHatGym.KEF import DataSetManager
from ChefsHatGym.KEF.DataSetManager import actionFinish, actionPass, actionDiscard, actionDeal

from matplotlib.collections import PolyCollection

statisticsGame = {
    "GameDuration": "gameDuration",
    "NumberGames":"numberGames",
    "NumberRounds": "numberRounds",
    "PlayerScore": "averagePoints",
    "AgregatedScore": "agregatedScore",
}

statisticsPreGame = {
    "Personality": "personality",
    "Competitiveness": "competitiveness",
    "Experience": "experience"
}

statisticsAfterGame = {
    "Personality": "personality"
}

statisticsIntegrated = {
    "Similarity": "similarity"
}

"""Plots per game"""
def plotPlayedTime(playedTimes, saveDirectory):
    fig, ax = plt.subplots()
    plt.grid()

    playedTimes = numpy.array(playedTimes)

    ax.set_xlabel('Players')
    ax.set_ylabel('Seconds')

    ax.bar(range(1, len(playedTimes)+1),playedTimes)

    plt.title('Game duration per participant')

    averagePlayedTime = playedTimes.mean()
    averageLabel = str("{:10.2f}".format(averagePlayedTime))
    ax.axhline(averagePlayedTime, color='red', linewidth=2, label='Avg: ' + str(averageLabel) + " s")

    plt.legend()
    plt.savefig(saveDirectory + "/Game_PlayedTime.png")

    plt.clf()

def plotNumberGames(numberGames, saveDirectory):
    fig, ax = plt.subplots()
    plt.grid()

    numberGames = numpy.array(numberGames)

    ax.set_xlabel('Players')
    ax.set_ylabel('# Games')

    plt.title('Games per participant')

    ax.bar(range(1, len(numberGames)+1),numberGames)

    averageGames = numberGames.mean()
    averageLabel = str("{:10.2f}".format(averageGames))
    ax.axhline(averageGames, color='red', linewidth=2, label='Avg: ' + str(averageLabel) + " games")

    plt.legend()
    plt.savefig(saveDirectory + "/Game_NumberGames.png")

    plt.clf()

def plotNumberRounds(numberRounds, saveDirectory):
    fig, ax = plt.subplots()
    plt.grid()

    numberRounds = numpy.array(numberRounds)

    ax.set_xlabel('Players')
    ax.set_ylabel('# Pizzas')

    plt.title('Rounds per participant')

    ax.bar(range(1, len(numberRounds)+1),numberRounds)

    averageGames = numberRounds.mean()
    averageLabel = str("{:10.2f}".format(averageGames))
    ax.axhline(averageGames, color='red', linewidth=2, label='Avg: ' + str(averageLabel) + " pizzas")

    plt.legend()
    plt.savefig(saveDirectory + "/Game_NumberPizzas.png")

    plt.clf()

def plotPlayerScore(playerScore, saveDirectory):
    fig, ax = plt.subplots()
    plt.grid()

    playerScore = numpy.array(playerScore)

    ax.set_xlabel('Players')
    ax.set_ylabel('Score')

    plt.title('Score per participant')
    ax.bar(range(1, len(playerScore)+1),playerScore)

    averageGames = playerScore.mean()
    averageLabel = str("{:10.2f}".format(averageGames))
    ax.axhline(averageGames, color='red', linewidth=2, label='Avg: ' + str(averageLabel) + " points")

    plt.legend()
    plt.savefig(saveDirectory + "/Game_Score.png")

    plt.clf()

def plotAgregatedScore(thisGameAgregatedScore, saveDirectory):
    fig, ax = plt.subplots()
    plt.grid()


    agregatedScore = numpy.array(thisGameAgregatedScore)

    # print ("agregated:" + str(thisGameAgregatedScore))
    ax.set_xlabel('Players')
    ax.set_ylabel('Agregated Score')

    plt.title('Aggregated score per participant')

    ax.bar(range(1, len(agregatedScore)+1),agregatedScore)

    averageGames = agregatedScore.mean()
    averageLabel = str("{:10.2f}".format(averageGames))
    ax.axhline(averageGames, color='red', linewidth=2, label='Avg: ' + str(averageLabel) + " points")

    plt.legend()
    plt.savefig(saveDirectory + "/Game_ScoreAgregated.png")

    plt.clf()

"""Plots pre-game"""

def plotPersonalitiesPreGame(agencies,competences,communnions,saveDirectory):

    plt.grid()

    examples = range(1, len(agencies)+1)

    agencies = numpy.array(agencies)
    competences = numpy.array(competences)
    communnions = numpy.array(communnions)

    width = 0.5

    p1 = plt.bar(examples, agencies, width, yerr=competences.std())
    p2 = plt.bar(examples, competences,  width, bottom=agencies, yerr=competences.std())
    p3 = plt.bar(examples, communnions,  width, bottom=agencies+competences, yerr=communnions.std())

    plt.title('Personalities per participant')

    # plt.legend((p1[0], p2[0],), ('Agency', 'Competence'))

    plt.legend((p1[0], p2[0], p3[0]), ('Agency', 'Competence', "Communnion"))

    plt.xlabel('Players')
    plt.ylabel('Value')

    # plt.legend()
    plt.savefig(saveDirectory + "/Player_Personalities.png")

    plt.clf()

def plotCompetitiveness(competitiveness, saveDirectory):
    fig, ax = plt.subplots()
    plt.grid()

    competitiveness = numpy.array(competitiveness)

    ax.set_xlabel('Players')
    ax.set_ylabel('Rating')

    ax.bar(range(1, len(competitiveness)+1),competitiveness)

    plt.title('Competitiveness per participant')

    averagePlayedTime = competitiveness.mean()
    averageLabel = str("{:10.2f}".format(averagePlayedTime))
    ax.axhline(averagePlayedTime, color='red', linewidth=2, label='Avg: ' + str(averageLabel) + " s")

    plt.legend()
    plt.savefig(saveDirectory + "/Player_Competitiveness.png")

    plt.clf()

def plotExperience(experience, saveDirectory):
    fig, ax = plt.subplots()
    plt.grid()

    experience = numpy.array(experience)

    ax.set_xlabel('Players')
    ax.set_ylabel('Rating')

    ax.bar(range(1, len(experience)+1),experience)

    plt.title('Experience per participant')

    averagePlayedTime = experience.mean()
    averageLabel = str("{:10.2f}".format(averagePlayedTime))
    ax.axhline(averagePlayedTime, color='red', linewidth=2, label='Avg: ' + str(averageLabel) + " s")

    plt.legend()
    plt.savefig(saveDirectory + "/Player_Experiences.png")

    plt.clf()


"""Plots after-game"""

def plotPersonalitiesAfterGame(agencies,competences,communnions,saveDirectory):


        finalAgency = []
        finalCompetence = []
        finaoComunion = []
        agencies = numpy.array(agencies)

        finalAgency.append(numpy.array(agencies[0]).mean())
        finalAgency.append(numpy.array(agencies[1]).mean())
        finalAgency.append(numpy.array(agencies[2]).mean())

        finalCompetence.append(numpy.array(competences[0]).mean())
        finalCompetence.append(numpy.array(competences[1]).mean())
        finalCompetence.append(numpy.array(competences[2]).mean())

        finaoComunion.append(numpy.array(communnions[0]).mean())
        finaoComunion.append(numpy.array(communnions[1]).mean())
        finaoComunion.append(numpy.array(communnions[2]).mean())

        plt.grid()

        examples = range(1, len(finalAgency)+1)

        agencies = numpy.array(finalAgency)
        competences = numpy.array(finalCompetence)
        communnions = numpy.array(finaoComunion)

        width = 0.5

        # print ("Agencies:" +str(agencies))
        p1 = plt.bar(examples, agencies, width, yerr=competences.std())
        p2 = plt.bar(examples, competences,  width, bottom=agencies, yerr=competences.std())
        p3 = plt.bar(examples, communnions,  width, bottom=agencies+competences, yerr=communnions.std())

        plt.xticks(examples, ('PPO', 'Random', "DQL"))

        plt.title('Personalities per Agent')

        # plt.legend((p1[0], p2[0],), ('Agency', 'Competence'))

        plt.legend((p1[0], p2[0], p3[0]), ('Agency', 'Competence', "Communnion"))

        plt.xlabel('Agents')
        plt.ylabel('Value')

        # plt.legend()
        plt.savefig(saveDirectory + "/Agents_Personalities.png")

        plt.clf()


"""Plots Integrated"""


def plotSimilaritiesIntegrated(agenciesAgent, competencesAgent, communnionsAgent,agenciesPlayer, competencesPlayer, communnionsPlayer, saveDirectory):
    finalAgency = []
    finalCompetence = []
    finaoComunion = []
    agencies = numpy.array(agenciesAgent)

    finalAgency.append(numpy.array(agencies[0]).mean())
    finalAgency.append(numpy.array(agencies[1]).mean())
    finalAgency.append(numpy.array(agencies[2]).mean())

    finalCompetence.append(numpy.array(competencesAgent[0]).mean())
    finalCompetence.append(numpy.array(competencesAgent[1]).mean())
    finalCompetence.append(numpy.array(competencesAgent[2]).mean())

    finaoComunion.append(numpy.array(communnionsAgent[0]).mean())
    finaoComunion.append(numpy.array(communnionsAgent[1]).mean())
    finaoComunion.append(numpy.array(communnionsAgent[2]).mean())


    finalDistancesAvery = []
    finalDistancesBeck = []
    finalDistancesCass = []
    for p in range(len(agenciesPlayer)):

        print ("p:"+str(p) + " - " + str(len(agenciesPlayer)))
        playerPoint = numpy.array([agenciesPlayer[p], competencesPlayer[p], communnionsPlayer[p]])

        averyPoint = numpy.array([finalAgency[0], finalCompetence[0], finaoComunion[0]])
        beckPoint = numpy.array([finalAgency[1], finalCompetence[1], finaoComunion[1]])
        cassPoint = numpy.array([finalAgency[2], finalCompetence[2], finaoComunion[2]])

        finalDistancesAvery.append(numpy.linalg.norm(playerPoint-averyPoint))
        finalDistancesBeck.append(numpy.linalg.norm(playerPoint - beckPoint))
        finalDistancesCass.append(numpy.linalg.norm(playerPoint - cassPoint))


    plt.grid()

    examples = range(1, len(finalDistancesAvery) + 1)

    width = 0.5

    # print ("Agencies:" +str(finalDistancesAvery))
    # print ("Agencies:" +str(finalDistancesBeck))
    # print("Agencies:" + str(finalDistancesCass))

    p1 = plt.bar(examples, finalDistancesAvery, width)
    p2 = plt.bar(examples, finalDistancesBeck, width, bottom=finalDistancesAvery)
    p3 = plt.bar(examples, finalDistancesCass, width, bottom=finalDistancesBeck )

    plt.title('Personalities per Agent')

    # plt.legend((p1[0], p2[0],), ('Agency', 'Competence'))

    plt.legend((p1[0], p2[0], p3[0]), ('PPO', 'Random', "DQL"))

    plt.xlabel('Agents')
    plt.ylabel('Value')

    # plt.legend()
    plt.savefig(saveDirectory + "/Agents_Similarity.png")

    plt.clf()


def calculateIntegratedGameStatistics(statisticsToCalculate, afterGameCSV, preGameCSV, saveDirectory):
    agencies = [[],[],[]]
    competences = [[],[],[]]
    communions = [[],[],[]]
    competitiveness = [[],[],[]]
    playAgain = [[],[],[]]

    with open(afterGameCSV) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count > 1:

                """Avery"""
                competitiveness[0].append(int(row[10][0]))

                ambitious = int(row[13][0])
                corageous = int(row[16][0])
                decisve = int(row[19][0])
                aggresive = int(row[22][0])
                agencies[0].append((ambitious + corageous + decisve + aggresive) / 4)

                creative = int(row[25][0])
                intelligent = int(row[28][0])
                innovative = int(row[31][0])
                organized = int(row[34][0])
                competences[0].append((creative + intelligent + innovative + organized) / 4)

                compassionate = int(row[37][0])
                affectionate = int(row[40][0])
                emotional = int(row[42][0])
                sensitive = int(row[45][0])
                communions[0].append((compassionate + affectionate + sensitive + emotional) / 4)

                # playAgain[0].append(int(row[48][0]))

                """Beck"""
                competitiveness[1].append(int(row[11][0]))

                ambitious = int(row[14][0])
                corageous = int(row[17][0])
                decisve = int(row[20][0])
                aggresive = int(row[23][0])
                agencies[1].append((ambitious + corageous + decisve + aggresive) / 4)

                creative = int(row[26][0])
                intelligent = int(row[29][0])
                innovative = int(row[32][0])
                organized = int(row[35][0])
                competences[1].append((creative + intelligent + innovative + organized) / 4)

                compassionate = int(row[38][0])
                affectionate = int(row[41][0])
                emotional = int(row[43][0])
                sensitive = int(row[46][0])
                communions[1].append((compassionate + affectionate + sensitive + emotional) / 4)

                # playAgain[1].append(int(row[49][0]))

                """Cass"""
                competitiveness[2].append(int(row[12][0]))

                ambitious = int(row[15][0])
                corageous = int(row[18][0])
                decisve = int(row[21][0])
                aggresive = int(row[24][0])
                agencies[2].append((ambitious + corageous + decisve + aggresive) / 4)

                creative = int(row[27][0])
                intelligent = int(row[30][0])
                innovative = int(row[33][0])
                organized = int(row[36][0])
                competences[2].append((creative + intelligent + innovative + organized) / 4)

                compassionate = int(row[39][0])
                affectionate = int(row[42][0])
                emotional = int(row[44][0])
                sensitive = int(row[47][0])

                communions[2].append((compassionate + affectionate + sensitive + emotional) / 4)

                # playAgain[2].append(int(row[50][0]))


            line_count = line_count + 1

    agenciesPlayer = []
    competencesPlayer = []
    communnionsPlayer = []
    competitivenessPlayer = []
    experiencePlayer = []

    with open(preGameCSV) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count > 1:
                # print ("Row:" + row[13])
                ambitious = int(row[13][0])
                corageous = int(row[14][0])
                decisve = int(row[15][0])
                aggresive = int(row[16][0])

                creative = int(row[17][0])
                intelligent = int(row[18][0])
                innovative = int(row[19][0])
                organized = int(row[20][0])

                compassionate = int(row[21][0])
                affectionate = int(row[22][0])
                sensitive = int(row[23][0])
                emotional = int(row[24][0])

                competitive = int(row[12][0])
                exp = int(row[25][0])

                agency = (ambitious + corageous + decisve + aggresive) / 4
                competence = (creative + intelligent + innovative + organized) / 4
                communion = (compassionate + affectionate + sensitive + emotional) / 4

                agenciesPlayer.append(agency)
                competencesPlayer.append(competence)
                communnionsPlayer.append(communion)


            line_count = line_count + 1
    if statisticsIntegrated["Similarity"] in statisticsToCalculate:
        print("Creating the " + str(statisticsIntegrated["Similarity"]) + " Plots.")
        plotSimilaritiesIntegrated(agencies, competences, communions,agenciesPlayer, competencesPlayer, communnionsPlayer, saveDirectory)


def calculateAfterGameStatistics(statisticsToCalculate, afterGameCSV, saveDirectory):
    agencies = [[],[],[]]
    competences = [[],[],[]]
    communions = [[],[],[]]
    competitiveness = [[],[],[]]
    playAgain = [[],[],[]]

    with open(afterGameCSV) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count > 1:

                """Avery"""
                competitiveness[0].append(int(row[10][0]))

                ambitious = int(row[13][0])
                corageous = int(row[16][0])
                decisve = int(row[19][0])
                aggresive = int(row[22][0])
                agencies[0].append((ambitious + corageous + decisve + aggresive) / 4)

                creative = int(row[25][0])
                intelligent = int(row[28][0])
                innovative = int(row[31][0])
                organized = int(row[34][0])
                competences[0].append((creative + intelligent + innovative + organized) / 4)

                compassionate = int(row[37][0])
                affectionate = int(row[40][0])
                emotional = int(row[42][0])
                sensitive = int(row[45][0])
                communions[0].append((compassionate + affectionate + sensitive + emotional) / 4)

                # playAgain[0].append(int(row[48][0]))

                """Beck"""
                competitiveness[1].append(int(row[11][0]))

                ambitious = int(row[14][0])
                corageous = int(row[17][0])
                decisve = int(row[20][0])
                aggresive = int(row[23][0])
                agencies[1].append((ambitious + corageous + decisve + aggresive) / 4)

                creative = int(row[26][0])
                intelligent = int(row[29][0])
                innovative = int(row[32][0])
                organized = int(row[35][0])
                competences[1].append((creative + intelligent + innovative + organized) / 4)

                compassionate = int(row[38][0])
                affectionate = int(row[41][0])
                emotional = int(row[43][0])
                sensitive = int(row[46][0])
                communions[1].append((compassionate + affectionate + sensitive + emotional) / 4)

                # playAgain[1].append(int(row[49][0]))

                """Cass"""
                competitiveness[2].append(int(row[12][0]))

                ambitious = int(row[15][0])
                corageous = int(row[18][0])
                decisve = int(row[21][0])
                aggresive = int(row[24][0])
                agencies[2].append((ambitious + corageous + decisve + aggresive) / 4)

                creative = int(row[27][0])
                intelligent = int(row[30][0])
                innovative = int(row[33][0])
                organized = int(row[36][0])
                competences[2].append((creative + intelligent + innovative + organized) / 4)

                compassionate = int(row[39][0])
                affectionate = int(row[42][0])
                emotional = int(row[44][0])
                sensitive = int(row[47][0])

                communions[2].append((compassionate + affectionate + sensitive + emotional) / 4)

                # playAgain[2].append(int(row[50][0]))


            line_count = line_count + 1

    if statisticsAfterGame["Personality"] in statisticsToCalculate:
        print("Creating the " + str(statisticsAfterGame["Personality"]) + " Plots.")
        plotPersonalitiesAfterGame(agencies, competences, communions, saveDirectory)

def calculatePreGameStatistics(statisticsToCalculate, preGameCSV, saveDirectory):

    agencies = []
    competences = []
    communnions = []
    competitiveness = []
    experience = []

    with open(preGameCSV) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count > 1:

                # print ("Row:" + row[13])
                ambitious = int(row[13][0])
                corageous = int(row[14][0])
                decisve = int(row[15][0])
                aggresive = int(row[16][0])

                creative = int(row[17][0])
                intelligent = int(row[18][0])
                innovative = int(row[19][0])
                organized = int(row[20][0])

                compassionate = int(row[21][0])
                affectionate = int(row[22][0])
                sensitive = int(row[23][0])
                emotional = int(row[24][0])

                competitive =  int(row[12][0])
                exp = int(row[25][0])

                agency = (ambitious + corageous + decisve + aggresive) / 4
                competence = (creative + intelligent + innovative + organized) / 4
                communion = (compassionate + affectionate + sensitive+emotional) / 4

                agencies.append(agency)
                competences.append(competence)
                communnions.append(communion)

                competitiveness.append(competitive)
                experience.append(exp)


            line_count = line_count+1




    if statisticsPreGame["Personality"] in statisticsToCalculate:
        print("Creating the " + str(statisticsPreGame["Personality"]) + " Plots.")
        plotPersonalitiesPreGame(agencies, competences, communnions, saveDirectory)

    if statisticsPreGame["Competitiveness"] in statisticsToCalculate:
        print("Creating the " + str(statisticsPreGame["Competitiveness"]) + " Plots.")
        plotCompetitiveness(competitiveness, saveDirectory)


    if statisticsPreGame["Experience"] in statisticsToCalculate:
        print("Creating the " + str(statisticsPreGame["Experience"]) + " Plots.")
        plotExperience(experience, saveDirectory)

def calculateGameStatistics(statisticsToCalculate, datasets, saveDirectory):


    playedTime = []
    numberGames = []
    roundNumbers = []
    playerPoints = []
    agregatedScore = []

    for dataset in datasets:
        readFile = pd.read_pickle(dataset)
        initialTime = ""
        currentGame = 0
        previousRoundNumber = 0
        previousScore = []
        currentScore = 0
        currentRounds = 0
        thisGameAgregatedScore = 0

        for lineCounter, row in readFile.iterrows():

            """Calculating game duration"""
            if initialTime == "":
                initialTime = datetime.datetime.strptime( row["Time"], '%Y-%m-%d_%H:%M:%S.%f')

            """If end of the current game"""
            if not (row["Game Number"] == "") and not currentGame == row["Game Number"]:

                """Calculating round number"""
                currentRounds += int(previousRoundNumber)
                # roundNumbers.append(int(previousRoundNumber))
                currentGame = int(row["Game Number"])

                """Calculating player score"""
                score = previousScore.index(0)
                currentScore += 3-score

                """Calculating Agregated Score"""
                thisGameAgregatedScore += (3-score) * int(previousRoundNumber)


            previousRoundNumber = row["Round Number"]
            previousScore = row["Scores"]


        playedTime.append((datetime.datetime.strptime( row["Time"], '%Y-%m-%d_%H:%M:%S.%f') - initialTime).total_seconds())
        numberGames.append(int(row["Game Number"])+1)
        # agregatedScore.append(thisGameAgregatedScore)


        """Information about the last game"""

        """Score"""
        score =  row["Scores"].index(0)
        currentScore += 3 - score
        playerPoints.append(currentScore)

        """Rounds"""
        currentRounds += int(row["Round Number"])
        roundNumbers.append(currentRounds)

        """Agregated Score"""
        agregatedScore.append(currentScore / currentRounds)


    # print ("Agregated score:" + str())
    if statisticsGame["GameDuration"] in statisticsToCalculate:
        print ("Creating the " + str(statisticsGame["GameDuration"]) + " Plots.")
        plotPlayedTime(playedTime,saveDirectory)

    if statisticsGame["NumberGames"] in statisticsToCalculate:
        print ("Creating the " + str(statisticsGame["NumberGames"]) + " Plots.")
        plotNumberGames(numberGames,saveDirectory)

    if statisticsGame["NumberRounds"] in statisticsToCalculate:
        print ("Creating the " + str(statisticsGame["NumberRounds"]) + " Plots.")
        plotNumberRounds(roundNumbers,saveDirectory)

    if statisticsGame["PlayerScore"] in statisticsToCalculate:
        print ("Creating the " + str(statisticsGame["PlayerScore"]) + " Plots.")
        plotPlayerScore(playerPoints,saveDirectory)

    if statisticsGame["AgregatedScore"] in statisticsToCalculate:
        print ("Creating the " + str(statisticsGame["AgregatedScore"]) + " Plots.")
        plotAgregatedScore(agregatedScore,saveDirectory)




