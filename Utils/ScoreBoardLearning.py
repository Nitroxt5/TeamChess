from math import exp
from time import perf_counter
from random import seed, shuffle
from Engine.Engine import GameState
from FENConverter import FENAndGSConverter
from PositionRecorder import PositionRecorder, getFeatures


K = 200
lam = 20
eps = 0.00001


def trainScoreBoard():
    seed(1)
    weights = [15, 20, 30, 20, 3, 4, 50, 20, 70, 30, 10, 20, 30, 20, 30]
    with PositionRecorder() as pr:
        positions = pr.getPositions()
    shuffle(positions)
    positionTypes = {"train": positions[:100000], "validation": positions[100000:]}
    estimatedResults = []
    realResults = []
    movesLeftCounts = []
    for position in positionTypes["train"]:
        featuresStr, res, moves = position
        features = list(map(int, featuresStr.split(sep=" ")))
        estimatedResults.append(estimateResult(weights, features))
        realResults.append(res / 2)
        movesLeftCounts.append(moves - features[-2])
    print(evaluateAverageError(estimatedResults, realResults, movesLeftCounts))
    newWeights = coordinateDecentMethod(weights, realResults, movesLeftCounts, positionTypes["train"], numIters=10)
    # newWeights = [73, 107, 154, 113, 10, 16, 28, 199, 1, 96, 26, 1, 1, 20, 15]
    print(list(map(int, newWeights)))
    print(evaluateAverageError(evaluateEstimatedResults(newWeights, positionTypes["train"]), realResults, movesLeftCounts))
    oldGuessesCount = 0
    newGuessesCount = 0
    positionsCount = len(positionTypes["validation"])
    for position in positionTypes["validation"]:
        featuresStr, res, moves = position
        features = list(map(int, featuresStr.split(sep=" ")))
        res /= 2
        oldPrediction = estimateResult(weights, features)
        newPrediction = estimateResult(newWeights, features)
        if abs(res - 0.5) < eps:
            if abs(res - oldPrediction) < 0.17:
                oldGuessesCount += 1
            if abs(res - newPrediction) < 0.17:
                newGuessesCount += 1
        else:
            if abs(res - oldPrediction) < 0.33:
                oldGuessesCount += 1
            if abs(res - newPrediction) < 0.33:
                newGuessesCount += 1
    print(f"Old weights guesses: {oldGuessesCount} out of {positionsCount}; percentage: {oldGuessesCount / positionsCount * 100:.2f}%")
    print(f"New weights guesses: {newGuessesCount} out of {positionsCount}; percentage: {newGuessesCount / positionsCount * 100:.2f}%")


def scoreBoard(weights: list[int], features: list[int]):
    return sum([weights[i] * features[i] for i in range(len(weights))]) + features[-1]


def estimateResult(weights: list[int], features: list[int]):
    return 1 / (1 + exp(-scoreBoard(weights, features) / K))


def evaluateError(estimatedResult: float, realResult: float, movesLeft: int):
    return (estimatedResult - realResult) * (estimatedResult - realResult) * exp(-movesLeft / lam)


def evaluateAverageError(estimatedResults: list, realResults: list, movesLeftCounts: list):
    return sum(map(evaluateError, estimatedResults, realResults, movesLeftCounts)) / len(estimatedResults)


def coordinateDecentMethod(weights: list, realResults: list, movesLeftCounts: list, positions: list, numIters=10):
    weights0 = weights.copy()
    y0 = evaluateAverageError(evaluateEstimatedResults(weights0, positions), realResults, movesLeftCounts)
    timeStart = perf_counter()
    exclusions = (7, 12, 13)
    for it in range(numIters):
        itStart = perf_counter()
        paramOrder = list(range(len(weights0)))
        shuffle(paramOrder)
        for param in paramOrder:
            if weights0[param] == 0 or param in exclusions:
                continue
            step = 4 if (it == 0 and numIters > 1) else 1
            while step >= 1:
                weights1 = weights0.copy()
                if weights1[param] + step < 200:
                    weights1[param] += step
                    if weights1[param] != weights0[param]:
                        y1 = evaluateAverageError(evaluateEstimatedResults(weights1, positions), realResults, movesLeftCounts)
                        if y1 < y0:
                            weights0 = weights1.copy()
                            y0 = y1
                            continue
                weights2 = weights0.copy()
                if weights2[param] - step > 0:
                    weights2[param] -= step
                    if weights2[param] != weights0[param]:
                        y2 = evaluateAverageError(evaluateEstimatedResults(weights2, positions), realResults, movesLeftCounts)
                        if y2 < y0:
                            weights0 = weights2.copy()
                            y0 = y2
                            continue
                step /= 2
            print(f"Passed param {param}")
        print(f"Passed iteration {it} in {perf_counter() - itStart}")
        print(f"Got weights: {weights0}")
        print(f"Error: {evaluateAverageError(evaluateEstimatedResults(weights0, positions), realResults, movesLeftCounts)}")
    print(f"Overall time: {perf_counter() - timeStart}")
    return weights0


def evaluateEstimatedResults(weights: list, positions: list):
    estimatedResults = []
    for position in positions:
        featuresStr, _, _ = position
        features = list(map(int, featuresStr.split(sep=" ")))
        estimatedResults.append(estimateResult(weights, features))
    return estimatedResults


def parseFENFile(filename: str):
    print(f"Got file with {countRows(filename)} rows")
    k = 0
    with open(filename, "r") as f:
        while line := f.readline():
            k += 1
            lineParts = line.split(sep=";")
            gameState = GameState()
            FENAndGSConverter.FENtoGameState(lineParts[0], gameState)
            with PositionRecorder() as pr:
                pr.addPosition2(" ".join(map(str, getFeatures(gameState))), int(float(lineParts[1]) * 2), int(lineParts[3]) * 2)
            if k % 100 == 0:
                print(f"Processed {k} rows")


def countRows(filename):
    return sum(1 for _ in open(filename, "r"))


if __name__ == "__main__":
    trainScoreBoard()
    # parseFENFile("fen.txt")
