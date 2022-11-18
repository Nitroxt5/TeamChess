from math import exp
from PositionRecorder import PositionRecorder


K = 200
lam = 10


def main():
    weights = [15, 20, 30, 20, 3, 4, 50, 20, 70, 30, 10, 20, 30, 20, 30]
    with PositionRecorder() as pr:
        positions = pr.getPositions()
    estimatedResults = []
    realResults = []
    movesLeftCounts = []
    for position in positions:
        featuresStr, res, board, moves = position
        features = list(map(int, featuresStr.split(sep=" ")))
        estimatedResults.append(estimateResult(weights, features))
        realResults.append(res / 2)
        movesLeftCounts.append(moves - features[-2])
    print(evaluateAverageError(estimatedResults, realResults, movesLeftCounts))
    newWeights = coordinateDecentMethod(weights, realResults, movesLeftCounts, numIters=3)
    print(newWeights)
    print(list(map(int, newWeights)))
    print(newWeights)
    print(evaluateAverageError(evaluateEstimatedResults(newWeights), realResults, movesLeftCounts))


def scoreBoard(weights: list[int], features: list[int]):
    return sum([weights[i] * features[i] for i in range(len(weights))])


def estimateResult(weights: list[int], features: list[int]):
    return 1 / (1 + exp(-scoreBoard(weights, features) / K))


def evaluateError(estimatedResult: float, realResult: float, movesLeft: int):
    return (estimatedResult - realResult) * (estimatedResult - realResult) * exp(-movesLeft / lam)


def evaluateAverageError(estimatedResults: list, realResults: list, movesLeftCounts: list):
    return sum(map(evaluateError, estimatedResults, realResults, movesLeftCounts)) / len(estimatedResults)


def coordinateDecentMethod(weights: list, realResults: list, movesLeftCounts: list, numIters=10):
    weights0 = weights.copy()
    y0 = evaluateAverageError(evaluateEstimatedResults(weights0), realResults, movesLeftCounts)
    for it in range(numIters):
        for param in range(len(weights0)):
            if weights0[param] == 0:
                continue
            step = 4 if (it == 0 and numIters > 1) else 1
            while step >= 1:
                weights1 = weights0.copy()
                if weights1[param] + step < 70:
                    weights1[param] += step
                    if weights1[param] != weights0[param]:
                        y1 = evaluateAverageError(evaluateEstimatedResults(weights1), realResults, movesLeftCounts)
                        if y1 < y0:
                            weights0 = weights1.copy()
                            y0 = y1
                            continue
                weights2 = weights0.copy()
                if weights2[param] - step > 0:
                    weights2[param] -= step
                    if weights2[param] != weights0[param]:
                        y2 = evaluateAverageError(evaluateEstimatedResults(weights2), realResults, movesLeftCounts)
                        if y2 < y0:
                            weights0 = weights2.copy()
                            y0 = y2
                            continue
                step /= 2
            print(f"Passed param {param}")
        print(f"Passed iteration {it}")
    return weights0


def evaluateEstimatedResults(weights: list):
    with PositionRecorder() as pr:
        positions = pr.getPositions()
    estimatedResults = []
    for position in positions:
        featuresStr, _, _, _ = position
        features = list(map(int, featuresStr.split(sep=" ")))
        estimatedResults.append(estimateResult(weights, features))
    return estimatedResults


if __name__ == "__main__":
    main()
