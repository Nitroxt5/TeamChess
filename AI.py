import random
import time
import Engine

pieceScores = {"K": 0, "Q": 900, "R": 500, "B": 300, "N": 300, "p": 100}
CHECKMATE = 100000
STALEMATE = 0
DEPTH = 3
nextMove = None
counter = 0
threatCost = 2
protectionCost = 2

knightPositionScore = [[1, 1, 1, 1, 1, 1, 1, 1],
                       [1, 2, 2, 2, 2, 2, 2, 1],
                       [1, 2, 3, 3, 3, 3, 2, 1],
                       [1, 2, 3, 4, 4, 3, 2, 1],
                       [1, 2, 3, 4, 4, 3, 2, 1],
                       [1, 2, 3, 3, 3, 3, 2, 1],
                       [1, 2, 2, 2, 2, 2, 2, 1],
                       [1, 1, 1, 1, 1, 1, 1, 1]]
bishopPositionScore = [[2, 2, 2, 1, 1, 2, 2, 2],
                       [2, 4, 3, 3, 3, 3, 4, 2],
                       [2, 3, 3, 3, 3, 3, 3, 2],
                       [2, 3, 3, 3, 3, 3, 3, 2],
                       [2, 3, 3, 3, 3, 3, 3, 2],
                       [2, 3, 3, 3, 3, 3, 3, 2],
                       [2, 4, 3, 3, 3, 3, 4, 2],
                       [2, 2, 2, 1, 1, 2, 2, 2]]
queenPositionScore = [[1, 2, 1, 3, 1, 1, 1, 1],
                      [1, 2, 4, 3, 3, 1, 1, 1],
                      [1, 4, 2, 2, 2, 2, 3, 1],
                      [3, 2, 2, 3, 3, 2, 2, 3],
                      [3, 2, 2, 3, 3, 2, 2, 3],
                      [1, 4, 2, 2, 2, 2, 3, 1],
                      [1, 2, 4, 3, 3, 1, 1, 1],
                      [1, 2, 1, 3, 1, 1, 1, 1]]
rookPositionScore = [[4, 3, 4, 4, 4, 4, 3, 4],
                     [4, 4, 4, 4, 4, 4, 4, 4],
                     [2, 2, 2, 2, 2, 2, 2, 2],
                     [1, 2, 2, 2, 2, 2, 2, 1],
                     [1, 2, 2, 2, 2, 2, 2, 1],
                     [2, 2, 2, 2, 2, 2, 2, 2],
                     [4, 4, 4, 4, 4, 4, 4, 4],
                     [4, 3, 4, 4, 4, 4, 3, 4]]
whitePawnPositionScore = [[4, 4, 4, 4, 4, 4, 4, 4],
                          [4, 4, 4, 4, 4, 4, 4, 4],
                          [4, 4, 4, 4, 4, 4, 4, 4],
                          [3, 3, 4, 4, 4, 4, 3, 3],
                          [2, 2, 3, 3, 3, 3, 2, 2],
                          [2, 2, 3, 3, 3, 3, 2, 2],
                          [1, 1, 1, 1, 0, 1, 1, 1],
                          [0, 0, 0, 0, 0, 0, 0, 0]]
blackPawnPositionScore = [[0, 0, 0, 0, 0, 0, 0, 0],
                          [1, 1, 1, 1, 0, 1, 1, 1],
                          [2, 2, 3, 3, 3, 3, 2, 2],
                          [2, 2, 3, 3, 3, 3, 2, 2],
                          [3, 3, 4, 4, 4, 4, 3, 3],
                          [4, 4, 4, 4, 4, 4, 4, 4],
                          [4, 4, 4, 4, 4, 4, 4, 4],
                          [4, 4, 4, 4, 4, 4, 4, 4]]

piecePositionScores = {"Q": queenPositionScore, "R": rookPositionScore, "B": bishopPositionScore,
                       "N": knightPositionScore, "bp": blackPawnPositionScore, "wp": whitePawnPositionScore}


def randomMoveAI(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]


def negaMaxWithPruningMoveAI(gameState, validMoves, returnQ):
    global nextMove, counter
    nextMove = None
    # random.shuffle(validMoves)
    # validMoves.sort(key=lambda move: move.isCapture, reverse=True)
    # validMoves.sort(key=lambda move: move.isCastle, reverse=True)
    print(validMoves)
    counter = 0
    start = time.perf_counter()
    negaMaxWithPruningAI(gameState, validMoves, -CHECKMATE - 1, CHECKMATE + 1, 1 if gameState.whiteTurn else -1, DEPTH)
    thinkingTime = time.perf_counter() - start
    print(f"Thinking time: {thinkingTime} s")
    print(f"Positions calculated: {counter}")
    returnQ.put((nextMove, thinkingTime, counter))


def negaMaxWithPruningAI(gameState, validMoves, alpha, beta, turn, depth):
    global nextMove, counter
    counter += 1
    if gameState.checkmate:
        return turn * CHECKMATE
    elif gameState.stalemate:
        return STALEMATE
    if depth == 0:
        return turn * scoreBoard(gameState, validMoves)
    random.shuffle(validMoves)
    validMoves.sort(key=lambda mov: mov.isCapture, reverse=True)
    validMoves.sort(key=lambda mov: mov.isCastle, reverse=True)
    for move in validMoves:
        gameState.makeMove(move)
        nextMoves = gameState.getValidMoves()
        score = -negaMaxWithPruningAI(gameState, nextMoves, -beta, -alpha, -turn, depth - 1)
        gameState.undoMove()
        if score >= beta:
            return beta
        if score > alpha:
            alpha = score
            if depth == DEPTH:
                nextMove = move
                print(move, score)
    return alpha


def scoreProtectionsAndThreats(gameState: Engine.GameState):
    whiteThreats = gameState.bbOfThreats["w"] & gameState.bbOfOccupiedSquares["b"]
    whiteProtections = gameState.bbOfThreats["w"] & gameState.bbOfOccupiedSquares["w"]
    blackThreats = gameState.bbOfThreats["b"] & gameState.bbOfOccupiedSquares["w"]
    blackProtections = gameState.bbOfThreats["b"] & gameState.bbOfOccupiedSquares["b"]
    threatsDifference = Engine.getBitsCount(whiteThreats) - Engine.getBitsCount(blackThreats)
    protectionsDifference = Engine.getBitsCount(whiteProtections) - Engine.getBitsCount(blackProtections)
    return threatsDifference, protectionsDifference


def scoreBoard(gameState, validMoves):
    if gameState.checkmate:
        if gameState.whiteTurn:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif gameState.stalemate:
        return STALEMATE
    threatsDifference, protectionsDifference = scoreProtectionsAndThreats(gameState)
    score = threatsDifference * threatCost + protectionsDifference * protectionCost
    if gameState.whiteTurn:
        score += len(validMoves)
    else:
        score -= len(validMoves)
    if gameState.isWhiteCastled:
        score += 50
    if gameState.isBlackCastled:
        score -= 50
    if gameState.isWhiteInCheck:
        score -= 20
    if gameState.isBlackInCheck:
        score += 20
    for piece in Engine.COLORED_PIECES:
        splitPositions = Engine.numSplit(gameState.bbOfPieces[piece])
        for position in splitPositions:
            pos = Engine.getPower(position)
            piecePositionScore = 0
            if piece[1] != "K":
                if piece[1] == "p":
                    piecePositionScore = piecePositionScores[piece][pos // 8][pos % 8] * 10
                else:
                    piecePositionScore = piecePositionScores[piece[1]][pos // 8][pos % 8] * 10
            if piece[0] == "w":
                score += pieceScores[piece[1]] + piecePositionScore
            elif piece[0] == "b":
                score -= pieceScores[piece[1]] + piecePositionScore
    return score
