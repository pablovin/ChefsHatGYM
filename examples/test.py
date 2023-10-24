import numpy as np

positions = {}


playerNames = ["a", "b", "c", "d"]
amountOfCardsByPlayer= [13, 13, 10, 13]

for a, count in zip(playerNames,amountOfCardsByPlayer) :
    positions[a] = count    

sortedPositions = dict(sorted(positions.items(), key=lambda x:x[1]))

playerIndex = [playerNames.index(a) for a in sortedPositions.keys()]

print (positions)
print (sortedPositions)
print (playerIndex)
# orderedAmount = sorted(amountOfCardsByPlayer)

# indicesPlayerbefore = [amountOfCardsByPlayer.index(a) for a in orderedAmount]

# positionPerPlayer = [amountOfCardsByPlayer.index(a) for a in orderedAmount]
# unique, counts = np.unique(positionPerPlayer, return_counts=True)

# print (f" Final position per player: {positionPerPlayer}")

# counts = dict(zip(unique, counts))
# finishingPosition = []
