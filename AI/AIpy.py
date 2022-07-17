from math import sqrt
from ScoreBoard import scoreBoard
from random import randint
from time import perf_counter
from TeamChess.Engine.Engine import GameState, Move
from multiprocessing import Queue

CHECKMATE = 100000
DEPTH = 4
LOW_TIME_DEPTH = 3
VERY_LOW_TIME_DEPTH = 2
EXTREMELY_LOW_TIME_DEPTH = 1
R = 1 if DEPTH <= 3 else 2
nextMove = None
counter = 0
hashTableForBestMoves = {}
hashTableForValidMoves = {}
killerMoves = {}
posMargin = {1: 350, 2: 800}


def randomMoveAI(validMoves: list) -> Move:
    return validMoves[randint(0, len(validMoves) - 1)]


def negaScoutMoveAI(gameState: GameState, otherGameState: GameState, validMoves: list, requiredDepth: int, returnQ: Queue, potentialScore: int, bestUnavailableReservePiece: [str, None], timeLeft: float):
    """This method is an entry point of the new process which calculates AI next move"""
    global nextMove, counter, DEPTH, hashTableForBestMoves, hashTableForValidMoves, killerMoves, R
    DEPTH = requiredDepth
    if timeLeft is not None:
        if timeLeft < 60:
            DEPTH = min(requiredDepth, LOW_TIME_DEPTH)
        if timeLeft < 20:
            DEPTH = min(requiredDepth, VERY_LOW_TIME_DEPTH)
        if timeLeft < 10:
            DEPTH = min(requiredDepth, EXTREMELY_LOW_TIME_DEPTH)
    R = 1 if DEPTH <= 3 else 2
    nextMove = None
    counter = 0
    score = 0
    myPotentialScore = 0
    myBestUnavailableReservePiece = None
    start = perf_counter()
    if validMoves is not None:
        globalLength = len(validMoves[0]) + len(validMoves[1]) + len(validMoves[2])
        if globalLength > 8:
            for currentDepth in range(1, DEPTH // 2 + 1):
                myPotentialScore = negaScoutAI(gameState, otherGameState, [[], gameState.getUnavailableReserveMoves(), []],
                                               -CHECKMATE - 1, CHECKMATE + 1, 1 if gameState.whiteTurn else -1,
                                               currentDepth, currentDepth, globalLength, potentialScore,
                                               bestUnavailableReservePiece)
            hashTableForBestMoves = {}
            hashTableForValidMoves = {}
            killerMoves = {}
            counter = 0
            if isinstance(nextMove, Move):
                myBestUnavailableReservePiece = nextMove.movedPiece
            nextMove = None
            for currentDepth in range(1, DEPTH + 1):
                score = negaScoutAI(gameState, otherGameState, validMoves, -CHECKMATE - 1, CHECKMATE + 1,
                                    1 if gameState.whiteTurn else -1, currentDepth, currentDepth, globalLength,
                                    potentialScore, bestUnavailableReservePiece)
                if score == CHECKMATE:
                    break
        else:
            myPotentialScore = negaScoutAI(gameState, otherGameState, [[], gameState.getUnavailableReserveMoves(), []],
                                           -CHECKMATE - 1, CHECKMATE + 1, 1 if gameState.whiteTurn else -1,
                                           DEPTH, DEPTH, globalLength, potentialScore, bestUnavailableReservePiece)
            hashTableForBestMoves = {}
            hashTableForValidMoves = {}
            killerMoves = {}
            counter = 0
            if isinstance(nextMove, Move):
                myBestUnavailableReservePiece = nextMove.movedPiece
            nextMove = None
            score = negaScoutAI(gameState, otherGameState, validMoves, -CHECKMATE - 1, CHECKMATE + 1, 1 if gameState.whiteTurn else -1,
                                DEPTH, DEPTH, globalLength, potentialScore, bestUnavailableReservePiece)
    thinkingTime = perf_counter() - start
    returnQ.put((nextMove, myPotentialScore - score, myBestUnavailableReservePiece, thinkingTime, counter))


def oneDepthSearch(gameState: GameState, validMoves: list, turn: int, currentDepth: int, potentialScore: int, bestUnavailableReservePiece: [str, None]):
    """Lightweight algorithm for searching the best move. Goes only for a depth of 1. Does not use any heuristics."""
    gameState.currentValidMovesCount = len(validMoves)
    for move in validMoves:
        if currentDepth in killerMoves:
            if move.moveID == killerMoves[currentDepth]:
                move.isKiller = True
        if not move.goodScore:
            gameState.makeMove(move)
            move.estimatedScore = turn * scoreBoard(gameState)
            gameState.undoMove()
        if move.capturedPiece == bestUnavailableReservePiece and potentialScore > 0:
            move.estimatedScore += potentialScore // 10


def negaScoutAI(gameState: GameState, otherGameState: GameState, validMoves: list, alpha: int, beta: int, turn: int, depth: int, globalDepth: int, globalLength: int, potentialScore: int, bestUnavailableReservePiece: [str, None]):
    """Algorithm for searching the best move"""
    global nextMove, counter
    counter += 1
    moves = validMoves[0] + validMoves[1] + validMoves[2]
    if depth <= 0 or gameState.checkmate or gameState.stalemate:
        gameState.currentValidMovesCount = len(moves)
        return turn * scoreBoard(gameState)
    oneDepthSearch(gameState, moves, turn, depth, potentialScore, bestUnavailableReservePiece)
    moves.sort(key=lambda mov: mov.estimatedScore, reverse=True)
    moves.sort(key=lambda mov: mov.isKiller, reverse=True)
    silentMoveCounter = 19 + int(2 * sqrt(max(len(validMoves[1]), 100)))
    for move in moves:
        if not silentMoveCounter:
            break
        gameState.makeMove(move)
        inTable = False
        score = 0
        if gameState.boardHash in hashTableForBestMoves:
            if hashTableForBestMoves[gameState.boardHash][0] >= depth:
                score = hashTableForBestMoves[gameState.boardHash][1]
                inTable = True
        if not inTable:
            if gameState.boardHash in hashTableForValidMoves:
                nextMoves, gameState.checkmate, gameState.stalemate = hashTableForValidMoves[gameState.boardHash]
                gameState.updatePawnPromotionMoves(nextMoves, otherGameState)
            else:
                nextMoves = gameState.getValidMoves()
                gameState.updatePawnPromotionMoves(nextMoves, otherGameState)
                hashTableForValidMoves[gameState.boardHash] = (nextMoves, gameState.checkmate, gameState.stalemate)
            if depth == DEPTH or move.isCapture or gameState.isWhiteInCheck or gameState.isBlackInCheck:
                score = -negaScoutAI(gameState, otherGameState, nextMoves, -beta, -alpha, -turn, depth - 1, globalDepth,
                                     globalLength, potentialScore, bestUnavailableReservePiece)
            else:
                silentMoveCounter -= 1
                score = -negaScoutAI(gameState, otherGameState, nextMoves, -alpha - 1, -alpha, -turn, depth - R,
                                     globalDepth, globalLength, potentialScore, bestUnavailableReservePiece)
                if alpha < score < beta:
                    score = -negaScoutAI(gameState, otherGameState, nextMoves, -beta, -score, -turn, depth - 1,
                                         globalDepth, globalLength, potentialScore, bestUnavailableReservePiece)
        gameState.undoMove()
        if move.capturedPiece == bestUnavailableReservePiece and potentialScore > 0:
            score += potentialScore // 10
        prevAlpha = alpha
        if score > alpha:
            alpha = score
            if gameState.boardHash in hashTableForBestMoves:
                if depth > hashTableForBestMoves[gameState.boardHash][0]:
                    hashTableForBestMoves[gameState.boardHash] = (depth, score)
                if depth == hashTableForBestMoves[gameState.boardHash][0] and score > hashTableForBestMoves[gameState.boardHash][1]:
                    hashTableForBestMoves[gameState.boardHash] = (depth, score)
            else:
                hashTableForBestMoves[gameState.boardHash] = (depth, score)
            if depth == globalDepth:
                move.exactScore = score
                move.estimatedScore = score
                move.goodScore = True
                nextMove = move
                if depth == DEPTH:
                    print(move, score)
        if alpha >= beta:
            killerMoves[depth] = move.moveID
            break
        if depth <= 2 and globalLength > 8:
            if score <= prevAlpha - posMargin[depth] and not (move.isCapture or gameState.isWhiteInCheck or gameState.isBlackInCheck) and globalDepth >= 4:
                break
    return alpha
