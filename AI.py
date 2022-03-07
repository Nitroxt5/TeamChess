from ScoreBoard import scoreBoard
from random import randint
from time import perf_counter
from Engine import GameState, Move
from multiprocessing import Queue

CHECKMATE = 100000
STALEMATE = 0
DEPTH = 4
R = 1 if DEPTH <= 3 else 2
nextMove = None
counter = 0
hashTableForBestMoves = {}
hashTableForValidMoves = {}
killerMoves = {}
posMargin = {1: 350, 2: 800}


def randomMoveAI(validMoves: list) -> Move:
    return validMoves[randint(0, len(validMoves) - 1)]


def negaScoutMoveAI(gameState: GameState, otherGameState: GameState, validMoves: list, requiredDepth: int, returnQ: Queue):
    global nextMove, counter, DEPTH
    DEPTH = requiredDepth
    nextMove = None
    counter = 0
    start = perf_counter()
    if validMoves is not None:
        globalLength = len(validMoves[0]) + len(validMoves[1]) + len(validMoves[2])
        if globalLength > 8:
            for d in range(DEPTH):
                currentDepth = d + 1
                score = negaScoutAI(gameState, otherGameState, validMoves, -CHECKMATE - 1, CHECKMATE + 1, 1 if gameState.whiteTurn else -1, currentDepth, currentDepth, globalLength)
                if score == CHECKMATE:
                    break
        else:
            negaScoutAI(gameState, otherGameState, validMoves, -CHECKMATE - 1, CHECKMATE + 1, 1 if gameState.whiteTurn else -1, DEPTH, DEPTH, globalLength)
    thinkingTime = perf_counter() - start
    returnQ.put((nextMove, thinkingTime, counter))


def oneDepthSearch(gameState: GameState, validMoves: list, turn: int, depth: int):
    gameState.currentValidMovesCount = len(validMoves)
    for move in validMoves:
        if depth in killerMoves:
            if move.moveID == killerMoves[depth]:
                move.isKiller = True
        if not move.goodScore:
            gameState.makeMove(move)
            move.estimatedScore = turn * scoreBoard(gameState)
            gameState.undoMove()


def negaScoutAI(gameState: GameState, otherGameState: GameState, validMoves: list, alpha: int, beta: int, turn: int, depth: int, globalDepth: int, globalLength: int):
    global nextMove, counter
    counter += 1
    moves = validMoves[0] + validMoves[1] + validMoves[2]
    if depth <= 0 or gameState.checkmate or gameState.stalemate:
        gameState.currentValidMovesCount = len(moves)
        return turn * scoreBoard(gameState)
    oneDepthSearch(gameState, moves, turn, depth)
    moves.sort(key=lambda mov: mov.estimatedScore, reverse=True)
    moves.sort(key=lambda mov: mov.isKiller, reverse=True)
    silentMoveCounter = 19 + len(validMoves[1]) * 2 // 3
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
                score = -negaScoutAI(gameState, otherGameState, nextMoves, -beta, -alpha, -turn, depth - 1, globalDepth, globalLength)
            else:
                silentMoveCounter -= 1
                score = -negaScoutAI(gameState, otherGameState, nextMoves, -alpha - 1, -alpha, -turn, depth - R, globalDepth, globalLength)
                if alpha < score < beta:
                    score = -negaScoutAI(gameState, otherGameState, nextMoves, -beta, -score, -turn, depth - 1, globalDepth, globalLength)
        gameState.undoMove()
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
