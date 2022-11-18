import psycopg2 as pg
from Utils.MagicConsts import COLUMNS, ROWS, COLORS, CORRECTIONS, CASTLE_SIDES, CENTER
from TestDLL import getBitsCount, numSplit, getPower


class PositionRecorder:
    def __init__(self):
        self._user = "postgres"
        self._password = "1qaz2wsx"
        self._host = "localhost"
        self._port = "5432"
        self._db = "postgres"
        self._connection = pg.connect(user=self._user, password=self._password,
                                      host=self._host, port=self._port, database=self._db)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._connection.close()

    def addPosition(self, position: str, board: int, game: int):
        with self._connection.cursor() as curs:
            curs.execute("INSERT INTO positions(position, board, game) VALUES (%s, %s, %s)", (position, board, game))
        self._connection.commit()

    def updateResultAndMoves(self, result: int, movesCount: int):
        with self._connection.cursor() as curs:
            curs.execute("UPDATE positions SET result=%s, moves=%s WHERE result IS NULL", (result, movesCount))
        self._connection.commit()

    def deleteHalfPositionsOfGame(self, board: int, game: int):
        with self._connection.cursor() as curs:
            curs.execute("DELETE FROM positions WHERE board=%s AND game=%s", (board, game))
        self._connection.commit()

    def deleteLastPositions(self, count: int):
        with self._connection.cursor() as curs:
            for i in range(count):
                curs.execute("DELETE FROM positions WHERE id=(SELECT MAX(id) FROM positions)")
        self._connection.commit()

    def getPositions(self):
        with self._connection.cursor() as curs:
            curs.execute("SELECT position, result, board, moves FROM positions")
            result = curs.fetchall()
        return result


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


pieceScores = {"K": 0, "Q": 1200, "R": 600, "B": 400, "N": 400, "p": 100}


def scoreRookPositioning(gameState, features: list[int]):
    score = 0
    for value in COLUMNS.values():
        whiteRookPos = value & gameState.bbOfPieces["wR"]
        blackRookPos = value & gameState.bbOfPieces["bR"]
        if whiteRookPos | blackRookPos:
            whitePawnsPos = value & gameState.bbOfPieces["wp"]
            blackPawnsPos = value & gameState.bbOfPieces["bp"]
            whitePawnsCount = getBitsCount(whitePawnsPos)
            blackPawnsCount = getBitsCount(blackPawnsPos)
            if whiteRookPos:
                if blackPawnsCount == 0 and whitePawnsCount == 1:
                    features[0] += 1
                elif whitePawnsCount == 0 and blackPawnsCount >= 1:
                    features[1] += 1
                elif whitePawnsCount + blackPawnsCount == 0:
                    features[2] += 1
            if blackRookPos:
                if whitePawnsCount == 0 and blackPawnsCount == 1:
                    features[0] -= 1
                elif blackPawnsCount == 0 and whitePawnsCount >= 1:
                    features[1] -= 1
                elif whitePawnsCount + blackPawnsCount == 0:
                    features[2] -= 1
    whiteRookRowPos = ROWS["7"] & gameState.bbOfPieces["wR"]
    blackRookRowPos = ROWS["2"] & gameState.bbOfPieces["bR"]
    if blackRookRowPos:
        rooksCount = getBitsCount(blackRookRowPos)
        features[3] -= rooksCount
    if whiteRookRowPos:
        rooksCount = getBitsCount(whiteRookRowPos)
        features[3] += rooksCount
    whiteSplitPositions = numSplit(gameState.bbOfPieces["wR"])
    blackSplitPositions = numSplit(gameState.bbOfPieces["bR"])
    score += (len(whiteSplitPositions) - len(blackSplitPositions)) * pieceScores["R"]
    score += int((gameState.reserve["w"]["R"] - gameState.reserve["b"]["R"]) * pieceScores["R"] * 0.8)
    for position in whiteSplitPositions:
        pos = getPower(position)
        score += piecePositionScores["R"][pos // 8][pos % 8] * 10
    for position in blackSplitPositions:
        pos = getPower(position)
        score -= piecePositionScores["R"][pos // 8][pos % 8] * 10
    return score


def scoreKnightPositioning(gameState, features: list[int]):
    knightMoves = {"w": 0, "b": 0}
    for color in COLORS:
        piece = color + "N"
        knightMoves[color] |= ((gameState.bbOfPieces[piece] & CORRECTIONS["h"]
                                                            & CORRECTIONS["78"]) << 15)
        knightMoves[color] |= ((gameState.bbOfPieces[piece] & CORRECTIONS["gh"]
                                                            & CORRECTIONS["8"]) << 6)
        knightMoves[color] |= ((gameState.bbOfPieces[piece] & CORRECTIONS["gh"]
                                                            & CORRECTIONS["1"]) >> 10)
        knightMoves[color] |= ((gameState.bbOfPieces[piece] & CORRECTIONS["h"]
                                                            & CORRECTIONS["12"]) >> 17)
        knightMoves[color] |= ((gameState.bbOfPieces[piece] & CORRECTIONS["a"]
                                                            & CORRECTIONS["12"]) >> 15)
        knightMoves[color] |= ((gameState.bbOfPieces[piece] & CORRECTIONS["ab"]
                                                            & CORRECTIONS["1"]) >> 6)
        knightMoves[color] |= ((gameState.bbOfPieces[piece] & CORRECTIONS["ab"]
                                                            & CORRECTIONS["8"]) << 10)
        knightMoves[color] |= ((gameState.bbOfPieces[piece] & CORRECTIONS["a"]
                                                            & CORRECTIONS["78"]) << 17)
    features[4] = getBitsCount(knightMoves["w"]) - getBitsCount(knightMoves["b"])
    score = 0
    whiteSplitPositions = numSplit(gameState.bbOfPieces["wN"])
    blackSplitPositions = numSplit(gameState.bbOfPieces["bN"])
    score += (len(whiteSplitPositions) - len(blackSplitPositions)) * pieceScores["N"]
    score += int((gameState.reserve["w"]["N"] - gameState.reserve["b"]["N"]) * pieceScores["N"] * 0.8)
    for position in whiteSplitPositions:
        pos = getPower(position)
        score += piecePositionScores["N"][pos // 8][pos % 8] * 10
    for position in blackSplitPositions:
        pos = getPower(position)
        score -= piecePositionScores["N"][pos // 8][pos % 8] * 10
    return score


def scoreBishopPositioning(gameState, features: list[int]):
    score = 0
    for color in COLORS:
        piece = color + "B"
        enemyColor = "w" if color == "b" else "b"
        diffCount = 1 if color == "w" else -1
        splitPositions = numSplit(gameState.bbOfPieces[piece])
        for splitPosition in splitPositions:
            checkingSq = splitPosition
            while checkingSq & CORRECTIONS["h"] & CORRECTIONS["8"]:
                checkingSq <<= 7
                if checkingSq & gameState.bbOfPieces[f"{color}p"]:
                    break
                if checkingSq & gameState.bbOfPieces[f"{enemyColor}p"]:
                    features[5] += diffCount
                    break
                features[5] += diffCount
            checkingSq = splitPosition
            while checkingSq & CORRECTIONS["h"] & CORRECTIONS["1"]:
                checkingSq >>= 9
                if checkingSq & gameState.bbOfPieces[f"{color}p"]:
                    break
                if checkingSq & gameState.bbOfPieces[f"{enemyColor}p"]:
                    features[5] += diffCount
                    break
                features[5] += diffCount
            checkingSq = splitPosition
            while checkingSq & CORRECTIONS["a"] & CORRECTIONS["1"]:
                checkingSq >>= 7
                if checkingSq & gameState.bbOfPieces[f"{color}p"]:
                    break
                if checkingSq & gameState.bbOfPieces[f"{enemyColor}p"]:
                    features[5] += diffCount
                    break
                features[5] += diffCount
            checkingSq = splitPosition
            while checkingSq & CORRECTIONS["a"] & CORRECTIONS["8"]:
                checkingSq <<= 9
                if checkingSq & gameState.bbOfPieces[f"{color}p"]:
                    break
                if checkingSq & gameState.bbOfPieces[f"{enemyColor}p"]:
                    features[5] += diffCount
                    break
                features[5] += diffCount
    whiteSplitPositions = numSplit(gameState.bbOfPieces["wB"])
    blackSplitPositions = numSplit(gameState.bbOfPieces["bB"])
    score += (len(whiteSplitPositions) - len(blackSplitPositions)) * pieceScores["B"]
    score += int((gameState.reserve["w"]["B"] - gameState.reserve["b"]["B"]) * pieceScores["B"] * 0.8)
    for position in whiteSplitPositions:
        pos = getPower(position)
        score += piecePositionScores["B"][pos // 8][pos % 8] * 10
    for position in blackSplitPositions:
        pos = getPower(position)
        score -= piecePositionScores["B"][pos // 8][pos % 8] * 10
    return score


def scoreKingSafety(gameState, features: list[int]):
    score = 0
    if gameState.isWhiteCastled:
        features[6] += 1
    if gameState.isBlackCastled:
        features[6] -= 1
    if gameState.isWhiteInCheck:
        features[7] -= 1
    if gameState.isBlackInCheck:
        features[7] += 1
    for key, value in CASTLE_SIDES.items():
        if not gameState.getCastleRight(value):
            if key[0] == "w" and not gameState.isWhiteCastled:
                features[8] -= 1
            elif key[0] == "b" and not gameState.isBlackCastled:
                features[8] += 1
    for value in COLUMNS.values():
        whiteKingPos = value & gameState.bbOfPieces["wK"]
        blackKingPos = value & gameState.bbOfPieces["bK"]
        if whiteKingPos:
            whitePawnsPos = value & gameState.bbOfPieces["wp"]
            whitePawnsCount = getBitsCount(whitePawnsPos)
            if whitePawnsCount == 0:
                features[9] -= 1
        if blackKingPos:
            blackPawnsPos = value & gameState.bbOfPieces["bp"]
            blackPawnsCount = getBitsCount(blackPawnsPos)
            if blackPawnsCount == 0:
                features[9] += 1
    return score


def scorePawnPositioning(gameState, features: list[int]):
    score = 0
    for value in COLUMNS.values():
        whitePawnsColumn = value & gameState.bbOfPieces["wp"]
        blackPawnsColumn = value & gameState.bbOfPieces["bp"]
        if (whitePawnsColumn | blackPawnsColumn) - whitePawnsColumn == 0:
            features[10] += 1
        if (whitePawnsColumn | blackPawnsColumn) - blackPawnsColumn == 0:
            features[10] -= 1
        whitePawnsCount = getBitsCount(whitePawnsColumn)
        blackPawnsCount = getBitsCount(blackPawnsColumn)
        if whitePawnsCount == 2:
            features[11] -= 1
        if whitePawnsCount >= 3:
            features[12] -= 1
        if blackPawnsCount == 2:
            features[11] += 1
        if blackPawnsCount >= 3:
            features[12] += 1
    whiteSplitPositions = numSplit(gameState.bbOfPieces["wp"])
    blackSplitPositions = numSplit(gameState.bbOfPieces["bp"])
    score += (len(whiteSplitPositions) - len(blackSplitPositions)) * pieceScores["p"]
    score += int((gameState.reserve["w"]["p"] - gameState.reserve["b"]["p"]) * pieceScores["p"] * 0.8)
    for position in whiteSplitPositions:
        pos = getPower(position)
        score += piecePositionScores["wp"][pos // 8][pos % 8] * 10
    for position in blackSplitPositions:
        pos = getPower(position)
        score -= piecePositionScores["bp"][pos // 8][pos % 8] * 10
    return score


def scoreQueenPositioning(gameState, features: list[int]):
    score = 0
    if gameState.gameLogLen < 20 and gameState.lastPieceMoved == "Q":
        if gameState.whiteTurn:
            features[13] += 1
        else:
            features[13] -= 1
    whiteSplitPositions = numSplit(gameState.bbOfPieces["wQ"])
    blackSplitPositions = numSplit(gameState.bbOfPieces["bQ"])
    score += (len(whiteSplitPositions) - len(blackSplitPositions)) * pieceScores["Q"]
    score += int((gameState.reserve["w"]["Q"] - gameState.reserve["b"]["Q"]) * pieceScores["Q"] * 0.8)
    for position in whiteSplitPositions:
        pos = getPower(position)
        score += piecePositionScores["Q"][pos // 8][pos % 8] * 10
    for position in blackSplitPositions:
        pos = getPower(position)
        score -= piecePositionScores["Q"][pos // 8][pos % 8] * 10
    return score


def scoreCenterControl(gameState, features: list[int]):
    whiteCenterControl = CENTER & gameState.bbOfOccupiedSquares["w"]
    blackCenterControl = CENTER & gameState.bbOfOccupiedSquares["b"]
    features[14] += getBitsCount(whiteCenterControl) - getBitsCount(blackCenterControl)
    return 0


pieceAdditionalPositionScores = {"Ks": scoreKingSafety, "Q": scoreQueenPositioning, "R": scoreRookPositioning,
                                 "K": scoreKnightPositioning, "B": scoreBishopPositioning, "p": scorePawnPositioning,
                                 "CC": scoreCenterControl}


def getFeatures(gameState):
    features = [0] * 15
    features.append(gameState.gameLogLen)
    if gameState.checkmate:
        if gameState.whiteTurn:
            features.append(-100000)
        else:
            features.append(100000)
        return features
    elif gameState.stalemate:
        features.append(0)
        return features
    score = 0
    if gameState.whiteTurn:
        score += gameState.currentValidMovesCount
    else:
        score -= gameState.currentValidMovesCount
    for value in pieceAdditionalPositionScores.values():
        score += value(gameState, features)
    features.append(score)
    return features
