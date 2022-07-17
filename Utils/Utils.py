from multiprocessing import Process
from math import ceil, floor


class ConsoleLogger:
    @staticmethod
    def endgameOutput(gameStates: list, boardPlayers: list, AIThinkingTime: list, AIPositionCounter: list, AIMoveCounter: list, AIExists: bool):
        for i in range(2):
            print(f"Board {i + 1}:")
            print(gameStates[i].gameLog)
            if not boardPlayers[i * 2] and not boardPlayers[i * 2 + 1]:
                moveCount = len(gameStates[i].gameLog)
            else:
                moveCountCeil = ceil(len(gameStates[i].gameLog) / 2)
                moveCountFloor = floor(len(gameStates[i].gameLog) / 2)
                moveCount = moveCountCeil if not boardPlayers[i * 2] else moveCountFloor
            print(f"Moves: {moveCount}")
            print(f"Overall thinking time: {AIThinkingTime[i]}")
            print(f"Overall positions calculated: {AIPositionCounter[i]}")
            if moveCount != 0 and AIPositionCounter[i] != 0:
                print(f"Average time per move: {AIThinkingTime[i] / moveCount}")
                print(f"Average calculated positions per move: {AIPositionCounter[i] / moveCount}")
                print(f"Average time per position: {AIThinkingTime[i] / AIPositionCounter[i]}")
            if moveCount != 0 and AIExists:
                print(f"Average possible moves per move: {AIMoveCounter[i] / moveCount}")

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


def settingsCheck(settings: dict):
    """Checks SETTINGS dict for correctness"""
    if not isinstance(settings, dict):
        return False
    if len(settings) != 2:
        return False
    if not ("sounds" in settings and "language" in settings):
        return False
    if not (isinstance(settings["sounds"], bool) and isinstance(settings["language"], bool)):
        return False
    return True


def terminateAI(AIThinking: bool, AIProcess: Process):
    """Safely ends AI calculation"""
    if AIThinking:
        AIProcess.terminate()
        AIProcess.join()
        AIProcess.close()
        AIThinking = False
    return AIThinking


def updateUIObjects(screen, UIObjects: list):
    """Calls update method for every object in UIObjects"""
    for obj in UIObjects:
        obj.update(screen)


def changeColorOfUIObjects(mousePos: tuple, UIObjects: list):
    """Calls changeColor method for every object in UIObjects"""
    for obj in UIObjects:
        obj.changeColor(mousePos)


def playSound(sound, soundPlayed: bool, setting: bool):
    """Plays a sound if it is not played and settings allow it"""
    if not soundPlayed and setting:
        sound.play()
        soundPlayed = True
    return soundPlayed


def getCurrentPlayer(gameStates: list, activeBoard: int):
    """Gets number of a player who is now to move"""
    if gameStates[activeBoard].whiteTurn:
        return activeBoard * 2
    return activeBoard * 2 + 1


def getPlayerName(gameStates: list, activeBoard: int, names: list):
    """Gets name of a player who is now to move"""
    return names[getCurrentPlayer(gameStates, activeBoard)]


def getPlayersTeammate(playerNum: int):
    """Gets number of a player's teammate"""
    if playerNum == 0:
        return 3
    if playerNum == 3:
        return 0
    if playerNum == 1:
        return 2
    return 1
