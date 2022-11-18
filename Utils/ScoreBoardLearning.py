from math import exp
from PositionRecorder import PositionRecorder


K = 200
lam = 10
eps = 0.00001
a = 0
b = 100
phi = 1.61803398874989


def main():
    weights = [15, 20, 20, 3, 4, 50, 20, 70, 30, 10, 20, 30, 20, 30]
    with PositionRecorder() as pr:
        positions = pr.getPositions()
    estimatedResults = []
    realResults = []
    movesLeftCounts = []
    for position in positions:
        featuresStr, res, board, moves = position
        features = list(map(int, " ".split(featuresStr)))
        estimatedResults.append(estimateResult(weights, features, K))
        realResults.append(res / 2)
        movesLeftCounts.append(moves - features[-2])
        # print(estimateResult(gameStates[board], K))
        # print(FEN, res, board, moves)
    print(evaluateAverageError(estimatedResults, realResults, movesLeftCounts))


def scoreBoard(weights: list[int], features: list[int]):
    return features[-1] + sum([weights[i] * features[i] for i in range(len(weights))])


def estimateResult(weights: list[int], features: list[int], k: int):
    return 1 / (1 + exp(-scoreBoard(weights, features) / k))


def evaluateError(estimatedResult: float, realResult: float, movesLeft: int):
    return (estimatedResult - realResult) * (estimatedResult - realResult) * exp(-movesLeft / lam)


def evaluateAverageError(estimatedResults: list, realResults: list, movesLeftCounts: list):
    return sum(map(evaluateError, estimatedResults, realResults, movesLeftCounts)) / len(estimatedResults)


def goldenRatioMethod():
    pass


if __name__ == "__main__":
    main()
