from math import ceil, floor
from Engine.Move import Move


class ConsoleLogger:
    @classmethod
    def endgameOutput(cls, gameStates: list, difficulties: list, AI):
        for i in range(2):
            print(f"Board {i + 1}:")
            print(gameStates[i].gameLog)
            moveCount = cls._evaluateMoveCount(gameStates, difficulties, i)
            print(f"Moves: {moveCount}")
            print(f"Overall thinking time: {AI.thinkingTime[i]}")
            print(f"Overall positions calculated: {AI.positionCounter[i]}")
            if moveCount != 0 and AI.positionCounter[i] != 0:
                print(f"Average time per move: {AI.thinkingTime[i] / moveCount}")
                print(f"Average calculated positions per move: {AI.positionCounter[i] / moveCount}")
                print(f"Average time per position: {AI.thinkingTime[i] / AI.positionCounter[i]}")

    @classmethod
    def _evaluateMoveCount(cls, gameStates: list, difficulties: list, boardNum: int):
        if difficulties[boardNum * 2] != 1 and difficulties[boardNum * 2 + 1] != 1:
            moveCount = len(gameStates[boardNum].gameLog)
        else:
            moveCountCeil = ceil(len(gameStates[boardNum].gameLog) / 2)
            moveCountFloor = floor(len(gameStates[boardNum].gameLog) / 2)
            moveCount = moveCountCeil if difficulties[boardNum * 2] != 1 else moveCountFloor
        return moveCount

    @classmethod
    def thinkingStart(cls, playerName: str):
        print(f"{playerName} is thinking...")

    @classmethod
    def thinkingEnd(cls, playerName: str, thinkingTime: float, positionCounter: int, potentialScore: int, requiredPiece: str):
        print(f"{playerName} came up with a move")
        print(f"{playerName} needs {requiredPiece}, its score = {potentialScore}")
        print(f"{playerName} thinking time: {thinkingTime} s")
        print(f"{playerName} positions calculated: {positionCounter}")

    @classmethod
    def madeRandomMove(cls, playerName: str):
        print(f"{playerName} made a random move")

    @classmethod
    def foundBetterMove(cls, move, score: int):
        print(move, score)

    @classmethod
    def foundBetterPromotionAtSq(cls, square: int, score: int):
        print(f"Found better promotion at square {Move.getSquareNotation(square)} with score {score}")
