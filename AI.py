import random
import time
import Engine
from multiprocessing import Queue

pieceScores = {"K": 0, "Q": 1200, "R": 600, "B": 400, "N": 400, "p": 100}
CHECKMATE = 100000
STALEMATE = 0
DEPTH = 4
R = 1 if DEPTH <= 3 else 2
nextMove = None
counter = 0
threatCost = 2
protectionCost = 2
hashTable = {}

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
queenPositionScore = [[1, 1, 1, 2, 1, 1, 1, 1],
                      [1, 1, 2, 2, 1, 1, 1, 1],
                      [1, 2, 1, 2, 1, 1, 1, 1],
                      [1, 1, 1, 2, 1, 1, 1, 1],
                      [1, 1, 1, 2, 1, 1, 1, 1],
                      [1, 2, 1, 2, 1, 1, 1, 1],
                      [1, 1, 2, 2, 1, 1, 1, 1],
                      [1, 1, 1, 2, 1, 1, 1, 1]]
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
                          [3, 3, 3, 4, 4, 3, 3, 3],
                          [1, 2, 2, 4, 4, 2, 2, 1],
                          [2, 1, 2, 3, 3, 1, 1, 2],
                          [1, 1, 1, 0, 0, 1, 1, 1],
                          [0, 0, 0, 0, 0, 0, 0, 0]]
blackPawnPositionScore = [[0, 0, 0, 0, 0, 0, 0, 0],
                          [1, 1, 1, 0, 0, 1, 1, 1],
                          [2, 1, 2, 3, 3, 1, 1, 2],
                          [1, 2, 2, 4, 4, 2, 2, 1],
                          [3, 3, 3, 4, 4, 3, 3, 3],
                          [4, 4, 4, 4, 4, 4, 4, 4],
                          [5, 5, 5, 5, 5, 5, 5, 5],
                          [6, 6, 6, 6, 6, 6, 6, 6]]

piecePositionScores = {"Q": queenPositionScore, "R": rookPositionScore, "B": bishopPositionScore,
                       "N": knightPositionScore, "bp": blackPawnPositionScore, "wp": whitePawnPositionScore}


def randomMoveAI(validMoves: list) -> Engine.Move:
    return validMoves[random.randint(0, len(validMoves) - 1)]


def negaScoutMoveAI(gameState: Engine.GameState, validMoves: list, returnQ: Queue):
    global nextMove, counter
    nextMove = None
    counter = 0
    start = time.perf_counter()
    if validMoves is not None:
        if len(validMoves) > 8:
            for d in range(DEPTH):
                currentDepth = d + 1
                score = negaScoutAI(gameState, validMoves, -CHECKMATE - 1, CHECKMATE + 1, 1 if gameState.whiteTurn else -1, currentDepth, currentDepth)
                if score == CHECKMATE:
                    break
        else:
            negaScoutAI(gameState, validMoves, -CHECKMATE - 1, CHECKMATE + 1, 1 if gameState.whiteTurn else -1, DEPTH, DEPTH)
    thinkingTime = time.perf_counter() - start
    returnQ.put((nextMove, thinkingTime, counter))


def oneDepthSearch(gameState: Engine.GameState, validMoves: list, turn: int):
    for move in validMoves:
        if not move.goodScore:
            gameState.makeMove(move)
            move.estimatedScore = turn * scoreBoard(gameState, validMoves)
            gameState.undoMove()


def negaScoutAI(gameState: Engine.GameState, validMoves: list, alpha: int, beta: int, turn: int, depth: int, globalDepth: int):
    global nextMove, counter
    counter += 1
    if depth <= 0 or gameState.checkmate:
        return turn * scoreBoard(gameState, validMoves)
    oneDepthSearch(gameState, validMoves, turn)
    validMoves.sort(key=lambda mov: mov.estimatedScore, reverse=True)
    silentMoveCounter = 19
    for move in validMoves:
        if not silentMoveCounter:
            break
        gameState.makeMove(move)
        inTable = False
        score = 0
        if gameState.boardHash in hashTable:
            if hashTable[gameState.boardHash][0] >= depth:
                score = hashTable[gameState.boardHash][1]
                inTable = True
        if not inTable:
            nextMoves = gameState.getValidMoves()
            if depth == DEPTH or move.isCapture or gameState.isWhiteInCheck or gameState.isBlackInCheck:
                score = -negaScoutAI(gameState, nextMoves, -beta, -alpha, -turn, depth - 1, globalDepth)
            else:
                silentMoveCounter -= 1
                score = -negaScoutAI(gameState, nextMoves, -alpha - 1, -alpha, -turn, depth - R, globalDepth)
                if alpha < score < beta:
                    score = -negaScoutAI(gameState, nextMoves, -beta, -score, -turn, depth - 1, globalDepth)
        gameState.undoMove()
        if score > alpha:
            alpha = score
            if gameState.boardHash in hashTable:
                if depth > hashTable[gameState.boardHash][0]:
                    hashTable[gameState.boardHash] = (depth, score)
                if depth == hashTable[gameState.boardHash][0] and score > hashTable[gameState.boardHash][1]:
                    hashTable[gameState.boardHash] = (depth, score)
            else:
                hashTable[gameState.boardHash] = (depth, score)
            if depth == globalDepth:
                move.exactScore = score
                move.estimatedScore = score
                move.goodScore = True
                nextMove = move
                if depth == DEPTH:
                    print(move, score)
        if alpha >= beta:
            break
    return alpha


# def negaScoutAI(gameState: Engine.GameState, validMoves: list, alpha: int, beta: int, turn: int, depth: int):
#     global nextMove, counter
#     counter += 1
#     if depth <= 0 or gameState.checkmate:
#         return turn * scoreBoard(gameState, validMoves)
#     oneDepthSearch(gameState, validMoves, turn)
#     validMoves.sort(key=lambda mov: mov.estimatedScore, reverse=True)
#     for move in validMoves:
#         gameState.makeMove(move)
#         nextMoves = gameState.getValidMoves()
#         if depth == DEPTH or move.isCapture or gameState.isWhiteInCheck or gameState.isBlackInCheck:
#             score = -negaScoutAI(gameState, nextMoves, -beta, -alpha, -turn, depth - 1)
#         else:
#             score = -negaScoutAI(gameState, nextMoves, -alpha - 1, -alpha, -turn, depth - R)
#             if alpha < score < beta:
#                 score = -negaScoutAI(gameState, nextMoves, -beta, -score, -turn, depth - 1)
#         gameState.undoMove()
#         if score > alpha:
#             alpha = score
#             if depth == DEPTH:
#                 move.exactScore = score
#                 nextMove = move
#                 print(move, score)
#         if alpha >= beta:
#             break
#     return alpha


# def negaMaxWithPruningAI(gameState: Engine.GameState, validMoves: list, alpha: int, beta: int, turn: int, depth: int):
#     global nextMove, counter
#     counter += 1
#     if depth == 0:
#         return turn * scoreBoard(gameState, validMoves)
#     maxScore = -CHECKMATE
#     oneDepthSearch(gameState, validMoves, turn)
#     validMoves.sort(key=lambda mov: mov.estimatedScore, reverse=True)
#     for move in validMoves:
#         gameState.makeMove(move)
#         nextMoves = gameState.getValidMoves()
#         score = -negaMaxWithPruningAI(gameState, nextMoves, -beta, -alpha, -turn, depth - 1)
#         gameState.undoMove()
#         if score > maxScore:
#             maxScore = score
#             if depth == DEPTH:
#                 move.exactScore = score
#                 nextMove = move
#                 print(move, score)
#         if maxScore > alpha:
#             alpha = maxScore
#         if alpha >= beta:
#             break
#     return maxScore


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
    for value in Engine.bbOfColumns.values():
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
                        score += 15
                    if blackPawnsCount == 1:
                        score += 20
                if whitePawnsCount + blackPawnsCount == 0:
                    score += 30
            if blackRookPos:
                if whitePawnsCount + blackPawnsCount == 1:
                    if whitePawnsCount == 1:
                        score -= 20
                    if blackPawnsCount == 1:
                        score -= 15
                if whitePawnsCount + blackPawnsCount == 0:
                    score -= 30
    whiteRookRowPos = Engine.bbOfRows["7"] & gameState.bbOfPieces["wR"]
    blackRookRowPos = Engine.bbOfRows["2"] & gameState.bbOfPieces["bR"]
    if blackRookRowPos:
        rooksCount = Engine.getBitsCount(blackRookRowPos)
        score -= rooksCount * 20
    if whiteRookRowPos:
        rooksCount = Engine.getBitsCount(whiteRookRowPos)
        score += rooksCount * 20
    whiteSplitPositions = Engine.numSplit(gameState.bbOfPieces["wR"])
    blackSplitPositions = Engine.numSplit(gameState.bbOfPieces["bR"])
    for position in whiteSplitPositions:
        pos = Engine.getPower(position)
        score += piecePositionScores["R"][pos // 8][pos % 8] * 10
    for position in blackSplitPositions:
        pos = Engine.getPower(position)
        score -= piecePositionScores["R"][pos // 8][pos % 8] * 10
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
    score = (Engine.getBitsCount(knightMoves["w"]) - Engine.getBitsCount(knightMoves["b"])) * 3
    whiteSplitPositions = Engine.numSplit(gameState.bbOfPieces["wN"])
    blackSplitPositions = Engine.numSplit(gameState.bbOfPieces["bN"])
    for position in whiteSplitPositions:
        pos = Engine.getPower(position)
        score += piecePositionScores["N"][pos // 8][pos % 8] * 10
    for position in blackSplitPositions:
        pos = Engine.getPower(position)
        score -= piecePositionScores["N"][pos // 8][pos % 8] * 10
    return score


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
    whiteSplitPositions = Engine.numSplit(gameState.bbOfPieces["wB"])
    blackSplitPositions = Engine.numSplit(gameState.bbOfPieces["bB"])
    score *= 4
    for position in whiteSplitPositions:
        pos = Engine.getPower(position)
        score += piecePositionScores["B"][pos // 8][pos % 8] * 10
    for position in blackSplitPositions:
        pos = Engine.getPower(position)
        score -= piecePositionScores["B"][pos // 8][pos % 8] * 10
    return score


def scoreKingSafety(gameState: Engine.GameState):
    score = 0
    if gameState.isWhiteCastled:
        score += 50
    if gameState.isBlackCastled:
        score -= 50
    if gameState.isWhiteInCheck:
        score -= 20
    if gameState.isBlackInCheck:
        score += 20
    for key, value in Engine.CASTLE_SIDES.items():
        if not gameState.getCastleRight(value):
            if key[0] == "w" and not gameState.isWhiteCastled:
                score -= 70
            elif key[0] == "b" and not gameState.isBlackCastled:
                score += 70
    for value in Engine.bbOfColumns.values():
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
    for value in Engine.bbOfColumns.values():
        whitePawnsColumn = value & gameState.bbOfPieces["wp"]
        blackPawnsColumn = value & gameState.bbOfPieces["bp"]
        if (whitePawnsColumn | blackPawnsColumn) - whitePawnsColumn == 0:
            score += 10
        if (whitePawnsColumn | blackPawnsColumn) - blackPawnsColumn == 0:
            score -= 10
        whitePawnsCount = Engine.getBitsCount(whitePawnsColumn)
        blackPawnsCount = Engine.getBitsCount(blackPawnsColumn)
        if whitePawnsCount == 2:
            score -= 20
        if whitePawnsCount >= 3:
            score -= 30
        if blackPawnsCount == 2:
            score += 20
        if blackPawnsCount >= 3:
            score += 30
    whiteSplitPositions = Engine.numSplit(gameState.bbOfPieces["wp"])
    blackSplitPositions = Engine.numSplit(gameState.bbOfPieces["bp"])
    for position in whiteSplitPositions:
        pos = Engine.getPower(position)
        score += piecePositionScores["wp"][pos // 8][pos % 8] * 10
    for position in blackSplitPositions:
        pos = Engine.getPower(position)
        score -= piecePositionScores["bp"][pos // 8][pos % 8] * 10
    return score


def scoreQueenPositioning(gameState: Engine.GameState):
    score = 0
    if len(gameState.gameLog) < 20 and gameState.gameLog[-1].movedPiece[1] == "Q":
        if gameState.whiteTurn:
            score += 20
        else:
            score -= 20
    whiteSplitPositions = Engine.numSplit(gameState.bbOfPieces["wQ"])
    blackSplitPositions = Engine.numSplit(gameState.bbOfPieces["bQ"])
    for position in whiteSplitPositions:
        pos = Engine.getPower(position)
        score += piecePositionScores["Q"][pos // 8][pos % 8] * 10
    for position in blackSplitPositions:
        pos = Engine.getPower(position)
        score -= piecePositionScores["Q"][pos // 8][pos % 8] * 10
    return score


def scoreCenterControl(gameState: Engine.GameState):
    whiteCenterControl = Engine.bbOfCenter & gameState.bbOfOccupiedSquares["w"]
    blackCenterControl = Engine.bbOfCenter & gameState.bbOfOccupiedSquares["b"]
    return (Engine.getBitsCount(whiteCenterControl) - Engine.getBitsCount(blackCenterControl)) * 30


pieceAdditionalPositionScores = {"Ks": scoreKingSafety, "Q": scoreQueenPositioning, "R": scoreRookPositioning,
                                 "K": scoreKnightPositioning, "B": scoreBishopPositioning, "p": scorePawnPositioning,
                                 "Cs": scoreCenterControl}


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
    for value in pieceAdditionalPositionScores.values():
        score += value(gameState)
    score += gameState.pieceScoreDiff
    return score
