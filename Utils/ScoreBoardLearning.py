from math import exp
from Engine.Engine import GameState
from ScoreBoard import scoreBoard
from PositionRecorder import PositionRecorder
from FENConverter import FENAndGSConverter


K = 200
lam = 10


def main():
    with PositionRecorder() as pr:
        positions = pr.getPositions()
    estimatedResults = []
    realResults = []
    movesLeftCounts = []
    for position in positions:
        FEN, res, board, moves = position
        gameStates = [GameState(), GameState()]
        FENAndGSConverter.FEN2toGameStates(FEN, gameStates[0], gameStates[1])
        estimatedResults.append(estimateResult(gameStates[board], K))
        realResults.append(res / 2)
        movesLeftCounts.append(moves - gameStates[board].gameLogLen)
        # print(estimateResult(gameStates[board], K))
        # print(FEN, res, board, moves)
    print(evaluateAverageError(estimatedResults, realResults, movesLeftCounts))


def estimateResult(gs: GameState, k: int):
    return 1 / (1 + exp(-scoreBoard(gs) / k))


def evaluateError(estimatedResult: float, realResult: float, movesLeft: int):
    return (estimatedResult - realResult) * (estimatedResult - realResult) * exp(-movesLeft / lam)


def evaluateAverageError(estimatedResults: list, realResults: list, movesLeftCounts: list):
    return sum(map(evaluateError, estimatedResults, realResults, movesLeftCounts))


if __name__ == "__main__":
    main()
