from random import randint
from time import perf_counter
import Engine
from multiprocessing import Queue

CHECKMATE = 100000
STALEMATE = 0
DEPTH = 4
R = 1 if DEPTH <= 3 else 2
nextMove = None
counter = 0
threatCost = 2
protectionCost = 2
hashTableForBestMoves = {}
hashTableForValidMoves = {}
killerMoves = {}


knightPositionScore = [[1, 2, 1, 1, 1, 1, 2, 1],
                       [1, 2, 2, 2, 2, 2, 2, 1],
                       [1, 2, 3, 3, 3, 3, 2, 1],
                       [1, 2, 3, 4, 4, 3, 2, 1],
                       [1, 2, 3, 4, 4, 3, 2, 1],
                       [1, 2, 3, 3, 3, 3, 2, 1],
                       [1, 2, 2, 2, 2, 2, 2, 1],
                       [1, 2, 1, 1, 1, 1, 2, 1]]
bishopPositionScore = [[3, 2, 2, 1, 1, 2, 2, 3],
                       [2, 4, 3, 3, 3, 3, 4, 2],
                       [2, 3, 3, 3, 3, 3, 3, 2],
                       [2, 3, 3, 3, 3, 3, 3, 2],
                       [2, 3, 3, 3, 3, 3, 3, 2],
                       [2, 3, 3, 3, 3, 3, 3, 2],
                       [2, 4, 3, 3, 3, 3, 4, 2],
                       [3, 2, 2, 1, 1, 2, 2, 3]]
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
    return validMoves[randint(0, len(validMoves) - 1)]


def predictionAI(gameState: Engine.GameState, otherGameState: Engine.GameState, validMoves: list, returnQ: Queue):
    if validMoves is not None:
        if len(validMoves[0]) + len(validMoves[1]) + len(validMoves[2]) > 8:
            for d in range(DEPTH):
                currentDepth = d + 1
                score = negaScoutAI(gameState, otherGameState, validMoves, -CHECKMATE - 1, CHECKMATE + 1, 1 if gameState.whiteTurn else -1, currentDepth, currentDepth)
                if score == CHECKMATE:
                    break
        else:
            negaScoutAI(gameState, otherGameState, validMoves, -CHECKMATE - 1, CHECKMATE + 1, 1 if gameState.whiteTurn else -1, DEPTH, DEPTH)
    returnQ.put(hashTableForBestMoves)


def negaScoutMoveAI(gameState: Engine.GameState, otherGameState: Engine.GameState, validMoves: list, returnQ: Queue, hashTable=None):
    if hashTable is None:
        hashTable = {}
    global nextMove, counter, hashTableForBestMoves
    hashTableForBestMoves = hashTable
    nextMove = None
    counter = 0
    start = perf_counter()
    if validMoves is not None:
        if len(validMoves[0]) + len(validMoves[1]) + len(validMoves[2]) > 8:
            for d in range(DEPTH):
                currentDepth = d + 1
                score = negaScoutAI(gameState, otherGameState, validMoves, -CHECKMATE - 1, CHECKMATE + 1, 1 if gameState.whiteTurn else -1, currentDepth, currentDepth)
                if score == CHECKMATE:
                    break
        else:
            negaScoutAI(gameState, otherGameState, validMoves, -CHECKMATE - 1, CHECKMATE + 1, 1 if gameState.whiteTurn else -1, DEPTH, DEPTH)
    thinkingTime = perf_counter() - start
    returnQ.put((nextMove, thinkingTime, counter))


def oneDepthSearch(gameState: Engine.GameState, validMoves: list, turn: int, depth: int):
    for move in validMoves:
        if depth in killerMoves:
            if move.moveID == killerMoves[depth]:
                move.isKiller = True
        if not move.goodScore:
            gameState.makeMove(move)
            move.estimatedScore = turn * scoreBoard(gameState, validMoves)
            gameState.undoMove()


def negaScoutAI(gameState: Engine.GameState, otherGameState: Engine.GameState, validMoves: list, alpha: int, beta: int, turn: int, depth: int, globalDepth: int):
    global nextMove, counter
    counter += 1
    moves = validMoves[0] + validMoves[1] + validMoves[2]
    if depth <= 0 or gameState.checkmate or gameState.stalemate:
        return turn * scoreBoard(gameState, moves)
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
        if (gameState.boardHash, gameState.boardReserveHash, gameState.whiteTurn) in hashTableForBestMoves:
            if hashTableForBestMoves[(gameState.boardHash, gameState.boardReserveHash, gameState.whiteTurn)][0] >= depth:
                score = hashTableForBestMoves[(gameState.boardHash, gameState.boardReserveHash, gameState.whiteTurn)][1]
                inTable = True
        if not inTable:
            if (gameState.boardHash, gameState.boardReserveHash, gameState.whiteTurn) in hashTableForValidMoves:
                nextMoves, gameState.checkmate, gameState.stalemate = hashTableForValidMoves[(gameState.boardHash, gameState.boardReserveHash, gameState.whiteTurn)]
                gameState.updatePawnPromotionMoves(nextMoves, otherGameState)
            else:
                nextMoves = gameState.getValidMoves()
                gameState.updatePawnPromotionMoves(nextMoves, otherGameState)
                hashTableForValidMoves[(gameState.boardHash, gameState.boardReserveHash, gameState.whiteTurn)] = (nextMoves, gameState.checkmate, gameState.stalemate)
            if depth == DEPTH or move.isCapture or gameState.isWhiteInCheck or gameState.isBlackInCheck:
                score = -negaScoutAI(gameState, otherGameState, nextMoves, -beta, -alpha, -turn, depth - 1, globalDepth)
            else:
                silentMoveCounter -= 1
                score = -negaScoutAI(gameState, otherGameState, nextMoves, -alpha - 1, -alpha, -turn, depth - R, globalDepth)
                if alpha < score < beta:
                    score = -negaScoutAI(gameState, otherGameState, nextMoves, -beta, -score, -turn, depth - 1, globalDepth)
        gameState.undoMove()
        if score > alpha:
            alpha = score
            if (gameState.boardHash, gameState.boardReserveHash, gameState.whiteTurn) in hashTableForBestMoves:
                if depth > hashTableForBestMoves[(gameState.boardHash, gameState.boardReserveHash, gameState.whiteTurn)][0]:
                    hashTableForBestMoves[(gameState.boardHash, gameState.boardReserveHash, gameState.whiteTurn)] = (depth, score)
                if depth == hashTableForBestMoves[(gameState.boardHash, gameState.boardReserveHash, gameState.whiteTurn)][0] and score > hashTableForBestMoves[(gameState.boardHash, gameState.boardReserveHash, gameState.whiteTurn)][1]:
                    hashTableForBestMoves[(gameState.boardHash, gameState.boardReserveHash, gameState.whiteTurn)] = (depth, score)
            else:
                hashTableForBestMoves[(gameState.boardHash, gameState.boardReserveHash, gameState.whiteTurn)] = (depth, score)
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
    return alpha


def scoreProtectionsAndThreats(gameState: Engine.GameState):
    whiteThreats = gameState.bbOfThreats["w"] & gameState.bbOfOccupiedSquares["b"]
    whiteProtections = gameState.bbOfThreats["w"] & gameState.bbOfOccupiedSquares["w"]
    blackThreats = gameState.bbOfThreats["b"] & gameState.bbOfOccupiedSquares["w"]
    blackProtections = gameState.bbOfThreats["b"] & gameState.bbOfOccupiedSquares["b"]
    threatsDifference = Engine.getBitsCount(whiteThreats) - Engine.getBitsCount(blackThreats)
    protectionsDifference = Engine.getBitsCount(whiteProtections) - Engine.getBitsCount(blackProtections)
    return threatsDifference * threatCost + protectionsDifference * protectionCost


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
                if blackPawnsCount == 0 and whitePawnsCount == 1:
                    score += 15
                elif whitePawnsCount == 0 and blackPawnsCount >= 1:
                    score += 20
                elif whitePawnsCount + blackPawnsCount == 0:
                    score += 30
            if blackRookPos:
                if whitePawnsCount == 0 and blackPawnsCount == 1:
                    score -= 15
                elif blackPawnsCount == 0 and whitePawnsCount >= 1:
                    score -= 20
                elif whitePawnsCount + blackPawnsCount == 0:
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
    score += (len(whiteSplitPositions) - len(blackSplitPositions)) * Engine.pieceScores["R"]
    score += int((gameState.reserve["w"]["R"] - gameState.reserve["b"]["R"]) * Engine.pieceScores["R"] * 0.8)
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
    score += (len(whiteSplitPositions) - len(blackSplitPositions)) * Engine.pieceScores["N"]
    score += int((gameState.reserve["w"]["N"] - gameState.reserve["b"]["N"]) * Engine.pieceScores["N"] * 0.8)
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
    score += (len(whiteSplitPositions) - len(blackSplitPositions)) * Engine.pieceScores["B"]
    score += int((gameState.reserve["w"]["B"] - gameState.reserve["b"]["B"]) * Engine.pieceScores["B"] * 0.8)
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
    score += (len(whiteSplitPositions) - len(blackSplitPositions)) * Engine.pieceScores["p"]
    score += int((gameState.reserve["w"]["p"] - gameState.reserve["b"]["p"]) * Engine.pieceScores["p"] * 0.8)
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
    score += (len(whiteSplitPositions) - len(blackSplitPositions)) * Engine.pieceScores["Q"]
    score += int((gameState.reserve["w"]["Q"] - gameState.reserve["b"]["Q"]) * Engine.pieceScores["Q"] * 0.8)
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
                                 "Cs": scoreCenterControl, "PT": scoreProtectionsAndThreats}


def scoreBoard(gameState: Engine.GameState, validMoves: list):
    if gameState.checkmate:
        if gameState.whiteTurn:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif gameState.stalemate:
        return STALEMATE
    score = 0
    if gameState.whiteTurn:
        score += len(validMoves)
    else:
        score -= len(validMoves)
    for value in pieceAdditionalPositionScores.values():
        score += value(gameState)
    return score
