import random
import time
import Engine
from multiprocessing import Queue

pieceScores = {"K": 0, "Q": 900, "R": 500, "B": 300, "N": 300, "p": 100}
CHECKMATE = 100000
STALEMATE = 0
DEPTH = 3
nextMove = None
counter = 0
threatCost = 2
protectionCost = 3

knightPositionScore = [[1, 2, 1, 1, 1, 1, 2, 1],
                       [1, 2, 2, 2, 2, 2, 2, 1],
                       [1, 2, 3, 3, 3, 3, 2, 1],
                       [1, 2, 3, 4, 4, 3, 2, 1],
                       [1, 2, 3, 4, 4, 3, 2, 1],
                       [1, 2, 3, 3, 3, 3, 2, 1],
                       [1, 2, 2, 2, 2, 2, 2, 1],
                       [1, 2, 1, 1, 1, 1, 2, 1]]
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
rookPositionScore = [[3, 3, 3, 3, 3, 3, 3, 3],
                     [2, 2, 2, 2, 2, 2, 2, 2],
                     [2, 2, 2, 2, 2, 2, 2, 2],
                     [1, 2, 2, 2, 2, 2, 2, 1],
                     [1, 2, 2, 2, 2, 2, 2, 1],
                     [2, 2, 2, 2, 2, 2, 2, 2],
                     [2, 2, 2, 2, 2, 2, 2, 2],
                     [3, 3, 3, 3, 3, 3, 3, 3]]
whitePawnPositionScore = [[6, 6, 6, 6, 6, 6, 6, 6],
                          [5, 5, 5, 5, 5, 5, 5, 5],
                          [4, 4, 4, 4, 4, 4, 4, 4],
                          [3, 3, 4, 4, 4, 4, 3, 3],
                          [2, 2, 3, 4, 4, 3, 2, 2],
                          [2, 2, 3, 3, 3, 1, 2, 2],
                          [1, 1, 1, 0, 0, 1, 1, 1],
                          [0, 0, 0, 0, 0, 0, 0, 0]]
blackPawnPositionScore = [[0, 0, 0, 0, 0, 0, 0, 0],
                          [1, 1, 1, 0, 0, 1, 1, 1],
                          [2, 2, 3, 3, 3, 1, 2, 2],
                          [2, 2, 3, 4, 4, 3, 2, 2],
                          [3, 3, 4, 4, 4, 4, 3, 3],
                          [4, 4, 4, 4, 4, 4, 4, 4],
                          [5, 5, 5, 5, 5, 5, 5, 5],
                          [6, 6, 6, 6, 6, 6, 6, 6]]

piecePositionScores = {"Q": queenPositionScore, "R": rookPositionScore, "B": bishopPositionScore,
                       "N": knightPositionScore, "bp": blackPawnPositionScore, "wp": whitePawnPositionScore}


def randomMoveAI(validMoves: list) -> Engine.Move:
    return validMoves[random.randint(0, len(validMoves) - 1)]


def negaMaxWithPruningMoveAI(gameState: Engine.GameState, validMoves: list, returnQ: Queue):
    global nextMove, counter
    nextMove = None
    # random.shuffle(validMoves)
    # validMoves.sort(key=lambda move: move.isCapture, reverse=True)
    # validMoves.sort(key=lambda move: move.isCastle, reverse=True)
    counter = 0
    start = time.perf_counter()
    if validMoves is not None:
        negaMaxWithPruningAI(gameState, validMoves, -CHECKMATE - 1, CHECKMATE + 1, 1 if gameState.whiteTurn else -1, DEPTH)
    thinkingTime = time.perf_counter() - start
    returnQ.put((nextMove, thinkingTime, counter))


def oneDepthSearch(gameState: Engine.GameState, validMoves: list, turn: int):
    for move in validMoves:
        gameState.makeMove(move)
        move.estimatedScore = turn * scoreBoard(gameState, validMoves)
        gameState.undoMove()


def negaMaxWithPruningAI(gameState: Engine.GameState, validMoves: list, alpha: int, beta: int, turn: int, depth: int):
    global nextMove, counter
    counter += 1
    if gameState.checkmate:
        return turn * CHECKMATE
    elif gameState.stalemate:
        return STALEMATE
    if depth == 0:
        return turn * scoreBoard(gameState, validMoves)
    # random.shuffle(validMoves)
    # validMoves.sort(key=lambda mov: mov.isCapture, reverse=True)
    # validMoves.sort(key=lambda mov: mov.isCastle, reverse=True)
    oneDepthSearch(gameState, validMoves, turn)
    validMoves.sort(key=lambda mov: mov.estimatedScore, reverse=True)
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
                move.exactScore = score
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


def scoreRookPositioning(gameState: Engine.GameState):
    score = 0
    for key, value in Engine.bbOfColumns.items():
        whiteRookPos = value & gameState.bbOfPieces["wR"]
        blackRookPos = value & gameState.bbOfPieces["bR"]
        if whiteRookPos | blackRookPos:
            whitePawnsPos = value & gameState.bbOfPieces["wp"]
            blackPawnsPos = value & gameState.bbOfPieces["bp"]
            whitePawnsCount = Engine.getBitsCount(whitePawnsPos)
            blackPawnsCount = Engine.getBitsCount(blackPawnsPos)
            if whiteRookPos:
                if whitePawnsCount + blackPawnsCount == 1:
                    if whitePawnsCount == 1:
                        score += 8
                    if blackPawnsCount == 1:
                        score += 10
                if whitePawnsCount + blackPawnsCount == 0:
                    score += 15
            if blackRookPos:
                if whitePawnsCount + blackPawnsCount == 1:
                    if whitePawnsCount == 1:
                        score -= 10
                    if blackPawnsCount == 1:
                        score -= 8
                if whitePawnsCount + blackPawnsCount == 0:
                    score += 15
            whiteRooksCount = Engine.getBitsCount(whiteRookPos)
            blackRooksCount = Engine.getBitsCount(blackRookPos)
            if whiteRooksCount > 1:
                score += 10
            if blackRooksCount > 1:
                score -= 10
    whiteRookRowPos = Engine.bbOfRows["7"] & gameState.bbOfPieces["wR"]
    blackRookRowPos = Engine.bbOfRows["2"] & gameState.bbOfPieces["bR"]
    if blackRookRowPos:
        rooksCount = Engine.getBitsCount(blackRookRowPos)
        score -= rooksCount * 20
    if whiteRookRowPos:
        rooksCount = Engine.getBitsCount(whiteRookRowPos)
        score += rooksCount * 20
    for key, value in Engine.bbOfRows.items():
        whiteRookPos = value & gameState.bbOfPieces["wR"]
        blackRookPos = value & gameState.bbOfPieces["bR"]
        whiteRooksCount = Engine.getBitsCount(whiteRookPos)
        blackRooksCount = Engine.getBitsCount(blackRookPos)
        if whiteRooksCount > 1:
            score += 10
        if blackRooksCount > 1:
            score -= 10
    return score


def scoreKnightPositioning(gameState: Engine.GameState):
    knightMoves = {"w": 0, "b": 0}
    for color in Engine.COLORS:
        piece = color + "N"
        knightMoves[color] |= ((gameState.bbOfPieces[piece] & Engine.bbOfCorrections["h"]
                                                            & Engine.bbOfCorrections["78"]) << 15)
        knightMoves[color] |= ((gameState.bbOfPieces[piece] & Engine.bbOfCorrections["gh"]
                                                            & Engine.bbOfCorrections["8"]) << 6)
        knightMoves[color] |= ((gameState.bbOfPieces[piece] & Engine.bbOfCorrections["gh"]
                                                            & Engine.bbOfCorrections["1"]) >> 10)
        knightMoves[color] |= ((gameState.bbOfPieces[piece] & Engine.bbOfCorrections["h"]
                                                            & Engine.bbOfCorrections["12"]) >> 17)
        knightMoves[color] |= ((gameState.bbOfPieces[piece] & Engine.bbOfCorrections["a"]
                                                            & Engine.bbOfCorrections["12"]) >> 15)
        knightMoves[color] |= ((gameState.bbOfPieces[piece] & Engine.bbOfCorrections["ab"]
                                                            & Engine.bbOfCorrections["1"]) >> 6)
        knightMoves[color] |= ((gameState.bbOfPieces[piece] & Engine.bbOfCorrections["ab"]
                                                            & Engine.bbOfCorrections["8"]) << 10)
        knightMoves[color] |= ((gameState.bbOfPieces[piece] & Engine.bbOfCorrections["a"]
                                                            & Engine.bbOfCorrections["78"]) << 17)
    return (Engine.getBitsCount(knightMoves["w"]) - Engine.getBitsCount(knightMoves["b"])) * 2


def scoreBishopPositioning(gameState: Engine.GameState):
    score = 0
    for color in Engine.COLORS:
        piece = color + "B"
        enemyColor = "w" if color == "b" else "b"
        diffCount = 1 if color == "w" else -1
        splitPositions = Engine.numSplit(gameState.bbOfPieces[piece])
        for splitPosition in splitPositions:
            checkingSq = splitPosition
            while checkingSq & Engine.bbOfCorrections["h"] & Engine.bbOfCorrections["8"]:
                checkingSq <<= 7
                if checkingSq & gameState.bbOfPieces[f"{color}p"]:
                    break
                if checkingSq & gameState.bbOfPieces[f"{enemyColor}p"]:
                    score += diffCount
                    break
                score += diffCount
            checkingSq = splitPosition
            while checkingSq & Engine.bbOfCorrections["h"] & Engine.bbOfCorrections["1"]:
                checkingSq >>= 9
                if checkingSq & gameState.bbOfPieces[f"{color}p"]:
                    break
                if checkingSq & gameState.bbOfPieces[f"{enemyColor}p"]:
                    score += diffCount
                    break
                score += diffCount
            checkingSq = splitPosition
            while checkingSq & Engine.bbOfCorrections["a"] & Engine.bbOfCorrections["1"]:
                checkingSq >>= 7
                if checkingSq & gameState.bbOfPieces[f"{color}p"]:
                    break
                if checkingSq & gameState.bbOfPieces[f"{enemyColor}p"]:
                    score += diffCount
                    break
                score += diffCount
            checkingSq = splitPosition
            while checkingSq & Engine.bbOfCorrections["a"] & Engine.bbOfCorrections["8"]:
                checkingSq <<= 9
                if checkingSq & gameState.bbOfPieces[f"{color}p"]:
                    break
                if checkingSq & gameState.bbOfPieces[f"{enemyColor}p"]:
                    score += diffCount
                    break
                score += diffCount
    return score * 2


def scoreKingSafety(gameState: Engine.GameState):
    score = 0
    if gameState.isWhiteCastled:
        score += 40
    if gameState.isBlackCastled:
        score -= 40
    if gameState.isWhiteInCheck:
        score -= 20
    if gameState.isBlackInCheck:
        score += 20
    for key, value in Engine.bbOfColumns.items():
        whiteKingPos = value & gameState.bbOfPieces["wK"]
        blackKingPos = value & gameState.bbOfPieces["bK"]
        if whiteKingPos:
            whitePawnsPos = value & gameState.bbOfPieces["wp"]
            whitePawnsCount = Engine.getBitsCount(whitePawnsPos)
            if whitePawnsCount == 0:
                score -= 30
        if blackKingPos:
            blackPawnsPos = value & gameState.bbOfPieces["bp"]
            blackPawnsCount = Engine.getBitsCount(blackPawnsPos)
            if blackPawnsCount == 0:
                score += 30
    return score


def scorePawnPositioning(gameState: Engine.GameState):
    score = 0
    for key, value in Engine.bbOfColumns.items():
        whitePawnsColumn = value & gameState.bbOfPieces["wp"]
        blackPawnsColumn = value & gameState.bbOfPieces["bp"]
        whitePawnsCount = Engine.getBitsCount(whitePawnsColumn)
        blackPawnsCount = Engine.getBitsCount(blackPawnsColumn)
        if whitePawnsCount == 2:
            score -= 10
        if whitePawnsCount >= 3:
            score -= 20
        if blackPawnsCount == 2:
            score += 10
        if blackPawnsCount >= 3:
            score += 20
    return score


pieceAdditionalPositionScores = {"Ks": scoreKingSafety, "R": scoreRookPositioning, "K": scoreKnightPositioning,
                                 "B": scoreBishopPositioning, "p": scorePawnPositioning}


def scoreBoard(gameState: Engine.GameState, validMoves: list):
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
    for key in pieceAdditionalPositionScores.keys():
        score += pieceAdditionalPositionScores[key](gameState)
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
