from TeamChess.Utils.MagicConsts import SQUARES
from TeamChess.Engine.Move import Move
from TeamChess.Generators.PossiblePromotions import PossiblePromotionsGen
from TeamChess.AI.AIpy import AI
from TeamChess.Utils.Logger import ConsoleLogger
from multiprocessing import Process, Queue
from random import randint


class AIHandler:
    def __init__(self, gameStates: list, potentialScores: list, requiredPieces: list):
        self._gameStates = gameStates
        self._potentialScores = potentialScores
        self._requiredPieces = requiredPieces
        self._promotionsGen = PossiblePromotionsGen(self._gameStates)
        self._process = Process()
        self._returnQ = Queue()
        self._thinking = False
        self.move = None
        self.cameUpWithMove = False
        self.thinkingTime = [0, 0]
        self.positionCounter = [0, 0]

    def start(self, timeLeft: float, depth: int, activeBoard: int, playerName: str):
        playerNum = self._getCurrentPlayer(activeBoard)
        if not self._thinking:
            ConsoleLogger.thinkingStart(playerName)
            AIPlayer = AI(self._gameStates[activeBoard], self._gameStates[1 - activeBoard])
            self._thinking = True
            teammateNum = self._getPlayersTeammate(playerNum)
            self._process = Process(target=AIPlayer.negaScoutMoveAI,
                                    args=(depth, timeLeft, self._potentialScores[teammateNum],
                                          self._requiredPieces[teammateNum], self._returnQ))
            self._process.start()
        if not self._process.is_alive():
            self.move, potentialScore, requiredPiece, thinkingTime, positionCounter = self._returnQ.get()
            ConsoleLogger.thinkingEnd(playerName, thinkingTime, positionCounter, potentialScore, requiredPiece)
            self._potentialScores[playerNum] = potentialScore
            self._requiredPieces[playerNum] = requiredPiece
            self.thinkingTime[activeBoard] += thinkingTime
            self.positionCounter[activeBoard] += positionCounter
            if self.move is None:
                AIPlayer = AI(self._gameStates[activeBoard], self._gameStates[1 - activeBoard])
                self.move = AIPlayer.randomMoveAI()
                ConsoleLogger.madeRandomMove(playerName)
            if self.move.isPawnPromotion:
                possiblePromotions = self._promotionsGen.calculatePossiblePromotions(activeBoard)
                requiredPromotions = [SQUARES[key[1]][key[0]] for key, value in possiblePromotions.items() if value[1] == self.move.promotedTo]
                promotion = requiredPromotions[randint(0, len(requiredPromotions) - 1)]
                self.move = Move(self.move.startSquare, self.move.endSquare, self._gameStates[activeBoard],
                                 movedPiece=self.move.movedPiece, promotedTo=self.move.promotedTo, promotedPiecePosition=promotion)
            self._thinking = False
            self.cameUpWithMove = True

    def _getCurrentPlayer(self, activeBoard: int):
        """Gets number of a player who is now to move"""
        if self._gameStates[activeBoard].whiteTurn:
            return activeBoard * 2
        return activeBoard * 2 + 1

    @staticmethod
    def _getPlayersTeammate(playerNum: int):
        """Gets number of a current player's teammate"""
        if playerNum == 0:
            return 3
        if playerNum == 3:
            return 0
        if playerNum == 1:
            return 2
        return 1

    def terminate(self):
        """Safely ends AI calculation"""
        if self._thinking:
            self._process.terminate()
            self._process.join()
            self._process.close()
            self._thinking = False
            self.cameUpWithMove = False

    @property
    def thinking(self):
        return self._thinking
