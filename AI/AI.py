from dataclasses import dataclass, field
from math import sqrt
from random import randint
from ScoreBoard import scoreBoard
from time import perf_counter
from Engine.Move import Move
from Utils.Logger import ConsoleLogger
from Utils.MagicConsts import CHECKMATE


@dataclass
class ValidMovesObj:
    checkmate: bool = field(default=False)
    stalemate: bool = field(default=False)
    moves: list[list[Move]] = field(default_factory=list)


class AI:
    def __init__(self, gameState, otherGameState):
        self._gameState = gameState
        self._otherGameState = otherGameState
        self._DEPTH = 4
        self._LOW_TIME_DEPTH = 3
        self._VERY_LOW_TIME_DEPTH = 2
        self._EXTREMELY_LOW_TIME_DEPTH = 1
        self._R = 1 if self._DEPTH <= 3 else 2
        self._posMargin = {1: 350, 2: 800}
        self._nextMove = None
        self._counter = 0
        self._hashTableForBestMoves = {}
        self._hashTableForValidMoves = {}
        self._killerMoves = {}
        self._globalValidMovesCount = 0
        self._teammatePotentialScore = 0
        self._teammateBestUnavailableReservePiece = None

    def randomMoveAI(self) -> Move:
        validMoves = self._gameState.getValidMoves()
        self._gameState.updatePawnPromotionMoves(validMoves, self._otherGameState)
        return validMoves[randint(0, len(validMoves) - 1)]

    def negaScoutMoveAI(self, requiredDepth: int, timeLeft: float, potentialScore: int, bestUnavailableReservePiece: [str, None], returnQ):
        """This method is an entry point of the new process which calculates AI next move"""
        self._initializeAI(requiredDepth, timeLeft, potentialScore, bestUnavailableReservePiece)
        validMoves = self._gameState.getValidMoves()
        self._gameState.updatePawnPromotionMoves(validMoves, self._otherGameState)
        self._globalValidMovesCount = len(validMoves[0]) + len(validMoves[1]) + len(validMoves[2])
        start = perf_counter()
        score = self._calculatePosition(-CHECKMATE - 1, validMoves, self._DEPTH)
        move = self._nextMove
        self._nextMove = None
        if score < CHECKMATE:
            myBestUnavailableReservePiece, myPotentialScore = self._getMyBestUnavailableReservePieceAndScore(score)
        else:
            myBestUnavailableReservePiece, myPotentialScore = None, 0
        thinkingTime = perf_counter() - start
        returnQ.put((move, myPotentialScore - score, myBestUnavailableReservePiece, thinkingTime, self._counter))

    def _initializeAI(self, requiredDepth: int, timeLeft: float, potentialScore: int, bestUnavailableReservePiece: [str, None]):
        self._configureSearchDepthByTimeLeft(timeLeft, requiredDepth)
        self._R = 1 if self._DEPTH <= 3 else 2
        self._nextMove = None
        self._counter = 0
        self._teammatePotentialScore = potentialScore
        self._teammateBestUnavailableReservePiece = bestUnavailableReservePiece

    def _configureSearchDepthByTimeLeft(self, timeLeft: float, requiredDepth: int):
        self._DEPTH = requiredDepth
        if timeLeft > 0:
            if timeLeft < 60:
                self._DEPTH = min(requiredDepth, self._LOW_TIME_DEPTH)
            if timeLeft < 20:
                self._DEPTH = min(requiredDepth, self._VERY_LOW_TIME_DEPTH)
            if timeLeft < 10:
                self._DEPTH = min(requiredDepth, self._EXTREMELY_LOW_TIME_DEPTH)

    def _getMyBestUnavailableReservePieceAndScore(self, alpha: int):
        validMoves = [[], self._gameState.getUnavailableReserveMoves(), []]
        score = self._calculatePosition(alpha, validMoves, self._DEPTH // 2, False)
        myBestUnavailableReservePiece = None
        if isinstance(self._nextMove, Move):
            myBestUnavailableReservePiece = self._nextMove.movedPiece
        return myBestUnavailableReservePiece, score

    def _resetTablesCounterMove(self):
        self._hashTableForBestMoves = {}
        self._hashTableForValidMoves = {}
        self._killerMoves = {}
        self._counter = 0
        self._nextMove = None

    def _calculatePosition(self, alpha: int, validMoves: list, requiredDepth: int, log=True) -> int:
        turn = 1 if self._gameState.whiteTurn else -1
        score = 0
        if self._globalValidMovesCount < 9:
            score = self._negaScoutAI(validMoves, alpha, CHECKMATE + 1, turn, requiredDepth, requiredDepth, log)
        else:
            for currentDepth in range(1, requiredDepth + 1):
                score = self._negaScoutAI(validMoves, alpha, CHECKMATE + 1, turn, currentDepth, currentDepth, log)
                if score >= CHECKMATE:
                    break
        return score

    def _negaScoutAI(self, validMoves: list, alpha: int, beta: int, turn: int, currentDepth: int, searchDepth: int, log=True):
        """Algorithm for searching the best move"""
        self._counter += 1
        moves = validMoves[0] + validMoves[1] + validMoves[2]
        if self._isSearchStopped(currentDepth):
            self._gameState.currentValidMovesCount = len(moves)
            return turn * scoreBoard(self._gameState)
        self._oneDepthSearch(moves, turn, currentDepth)
        self._sortMoves(moves)
        silentMoveCounter = 19 + int(2 * sqrt(max(len(validMoves[1]), 100)))
        for move in moves:
            if not silentMoveCounter:
                break
            self._gameState.makeMove(move)
            score = self._extractBestMoveFromHashTable(currentDepth)
            if score is None:
                silentMoveCounter, score = self._calculateScore(move, alpha, beta, turn, currentDepth, searchDepth, silentMoveCounter)
            self._gameState.undoMove()
            score = self._updateScoreWithTeammatesPotentialScore(move, score)
            prevAlpha = alpha
            if score > alpha:
                alpha = score
                self._updateBestMoveHashTable(currentDepth, score)
                if currentDepth == searchDepth:
                    self._updateNextMove(currentDepth, score, move, log)
            if alpha >= beta:
                self._killerMoves[currentDepth] = move.moveID
                break
            if currentDepth <= 2 and self._globalValidMovesCount > 8:
                if score <= prevAlpha - self._posMargin[currentDepth] and self._isSilentMove(move) and searchDepth >= 4:
                    break
        return alpha

    def _isSearchStopped(self, depth):
        return depth <= 0 or self._gameState.checkmate or self._gameState.stalemate

    def _oneDepthSearch(self, validMoves: list, turn: int, currentDepth: int):
        """Lightweight algorithm for searching the best move. Goes only for a depth of 1. Does not use any heuristics."""
        self._gameState.currentValidMovesCount = len(validMoves)
        for move in validMoves:
            if currentDepth in self._killerMoves:
                if move.moveID == self._killerMoves[currentDepth]:
                    move.isKiller = True
            if not move.goodScore:
                self._gameState.makeMove(move)
                move.estimatedScore = turn * scoreBoard(self._gameState)
                self._gameState.undoMove()
            if move.capturedPiece == self._teammateBestUnavailableReservePiece and self._teammatePotentialScore > 0:
                move.estimatedScore += self._teammatePotentialScore // 10

    @staticmethod
    def _sortMoves(moves):
        moves.sort(key=lambda mov: mov.estimatedScore, reverse=True)
        moves.sort(key=lambda mov: mov.isKiller, reverse=True)

    def _extractBestMoveFromHashTable(self, currentDepth: int):
        if self._gameState.boardHash in self._hashTableForBestMoves:
            if self._hashTableForBestMoves[self._gameState.boardHash][0] >= currentDepth:
                return self._hashTableForBestMoves[self._gameState.boardHash][1]

    def _calculateScore(self, move, alpha: int, beta: int, turn: int, currentDepth: int, searchDepth: int, silentMoveCounter: int):
        """Calculates score in case it was not found in the hash table.

        Returns silentMoveCounter and calculated score
        """
        validMovesObj = self._extractValidMovesFromHashTable()
        if validMovesObj is None:
            validMovesObj = self._generateValidMovesObj()
            self._hashTableForValidMoves[self._gameState.boardHash] = validMovesObj
        if currentDepth == self._DEPTH or not self._isSilentMove(move):
            score = -self._negaScoutAI(validMovesObj.moves, -beta, -alpha, -turn, currentDepth - 1, searchDepth)
        else:
            silentMoveCounter -= 1
            score = -self._negaScoutAI(validMovesObj.moves, -alpha - 1, -alpha, -turn, currentDepth - self._R, searchDepth)
            if alpha < score < beta:
                score = -self._negaScoutAI(validMovesObj.moves, -beta, -score, -turn, currentDepth - 1, searchDepth)
        return silentMoveCounter, score

    def _extractValidMovesFromHashTable(self):
        if self._gameState.boardHash in self._hashTableForValidMoves:
            validMovesObj = self._hashTableForValidMoves[self._gameState.boardHash]
            self._gameState.updatePawnPromotionMoves(validMovesObj.moves, self._otherGameState)
            self._gameState.checkmate = validMovesObj.checkmate
            self._gameState.stalemate = validMovesObj.stalemate
            return validMovesObj

    def _generateValidMovesObj(self):
        validMovesObj = ValidMovesObj(moves=self._gameState.getValidMoves())
        self._gameState.updatePawnPromotionMoves(validMovesObj.moves, self._otherGameState)
        validMovesObj.checkmate = self._gameState.checkmate
        validMovesObj.stalemate = self._gameState.stalemate
        return validMovesObj

    def _isSilentMove(self, move):
        return not (move.isCapture or self._gameState.isWhiteInCheck or self._gameState.isBlackInCheck)

    def _updateScoreWithTeammatesPotentialScore(self, move, score: int):
        if move.capturedPiece == self._teammateBestUnavailableReservePiece and self._teammatePotentialScore > 0:
            score += self._teammatePotentialScore // 10
        return score

    def _updateBestMoveHashTable(self, currentDepth: int, score: int):
        if self._gameState.boardHash in self._hashTableForBestMoves:
            if self._isNewScoreBetter(currentDepth, score):
                self._hashTableForBestMoves[self._gameState.boardHash] = (currentDepth, score)
        else:
            self._hashTableForBestMoves[self._gameState.boardHash] = (currentDepth, score)

    def _isNewScoreBetter(self, currentDepth: int, score: int):
        return currentDepth > self._hashTableForBestMoves[self._gameState.boardHash][0] or \
               (currentDepth == self._hashTableForBestMoves[self._gameState.boardHash][0] and
                score > self._hashTableForBestMoves[self._gameState.boardHash][1])

    def _updateNextMove(self, currentDepth: int, score: int, move, log=True):
        move.exactScore = score
        move.estimatedScore = score
        move.goodScore = True
        self._nextMove = move
        if currentDepth == self._DEPTH and log:
            ConsoleLogger.foundBetterMove(move, score)

    def scoreBoardWithRemovedPieceAtPos(self, piece: str, position: int):
        self._gameState.unsetSqState(piece, position)
        validMoves = self._gameState.getValidMoves()
        self._gameState.updatePawnPromotionMoves(validMoves, self._otherGameState)
        score = self._calculatePosition(-CHECKMATE - 1, validMoves, self._DEPTH // 2, False)
        self._gameState.setSqState(piece, position)
        self._resetTablesCounterMove()
        return score
