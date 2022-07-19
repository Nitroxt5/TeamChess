from math import ceil, floor


class ConsoleLogger:
    @staticmethod
    def endgameOutput(gameStates: list, difficulties: list, AI):
        for i in range(2):
            print(f"Board {i + 1}:")
            print(gameStates[i].gameLog)
            if difficulties[i * 2] != 1 and difficulties[i * 2 + 1] != 1:
                moveCount = len(gameStates[i].gameLog)
            else:
                moveCountCeil = ceil(len(gameStates[i].gameLog) / 2)
                moveCountFloor = floor(len(gameStates[i].gameLog) / 2)
                moveCount = moveCountCeil if difficulties[i * 2] != 1 else moveCountFloor
            print(f"Moves: {moveCount}")
            print(f"Overall thinking time: {AI.thinkingTime[i]}")
            print(f"Overall positions calculated: {AI.positionCounter[i]}")
            if moveCount != 0 and AI.positionCounter[i] != 0:
                print(f"Average time per move: {AI.thinkingTime[i] / moveCount}")
                print(f"Average calculated positions per move: {AI.positionCounter[i] / moveCount}")
                print(f"Average time per position: {AI.thinkingTime[i] / AI.positionCounter[i]}")

    @staticmethod
    def thinkingStart(playerName: str):
        print(f"{playerName} is thinking...")

    @staticmethod
    def thinkingEnd(playerName: str, thinkingTime: float, positionCounter: int, potentialScore: int, requiredPiece: str):
        print(f"{playerName} came up with a move")
        print(f"{playerName} needs {requiredPiece}, its score = {potentialScore}")
        print(f"{playerName} thinking time: {thinkingTime} s")
        print(f"{playerName} positions calculated: {positionCounter}")

    @staticmethod
    def madeRandomMove(playerName: str):
        print(f"{playerName} made a random move")
