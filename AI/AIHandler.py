from multiprocessing import Process, Queue
from random import randint
from AI.AI import AI
from Engine.Move import Move
from Generators.PossiblePromotions import PossiblePromotionsGen
from Utils.Logger import ConsoleLogger
from Utils.MagicConsts import SQUARES


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
            self._updateStats(potentialScore, requiredPiece, thinkingTime, positionCounter, activeBoard)
            if self.move is None:  # this section should never be entered
                self._getRandomMove(activeBoard)
                ConsoleLogger.madeRandomMove(playerName)
            if self.move.isPawnPromotion:
                self._updateMoveWithPromotionPos(activeBoard)
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

    def _updateStats(self, potentialScore: int, requiredPiece: str, thinkingTime: int, positionCounter: int, activeBoard: int):
        playerNum = self._getCurrentPlayer(activeBoard)
        self._potentialScores[playerNum] = potentialScore
        if requiredPiece is not None:
            self._requiredPieces[playerNum] = requiredPiece
        self.thinkingTime[activeBoard] += thinkingTime
        self.positionCounter[activeBoard] += positionCounter

    def _getRandomMove(self, activeBoard):
        AIPlayer = AI(self._gameStates[activeBoard], self._gameStates[1 - activeBoard])
        self._move = AIPlayer.randomMoveAI()

    def _updateMoveWithPromotionPos(self, activeBoard):
        promotions = self._promotionsGen.calculatePossiblePromotions(activeBoard)
        requiredPromotions = [SQUARES[loc[1]][loc[0]] for loc, piece in promotions.items() if piece[1] == self.move.promotedTo]
        promotionPos = requiredPromotions[randint(0, len(requiredPromotions) - 1)]
        self.move = Move(self.move.startSquare, self.move.endSquare, self._gameStates[activeBoard],
                         movedPiece=self.move.movedPiece, promotedTo=self.move.promotedTo,
                         promotedPiecePosition=promotionPos)

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
