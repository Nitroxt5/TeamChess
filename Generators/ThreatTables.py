from TestDLL import numSplit
from Utils.MagicConsts import PIECES, COLORS, CORRECTIONS


class ThreatTableGenerator:
    def __init__(self, gameState):
        self._gameState = gameState
        self._bbOfThreats = {"w": 0, "b": 0}
        self._bbOfThreatsLog = []
        self._threatTableFunc = {"p": self._createPawnThreatTable, "R": self._createVerticalAndHorizontalMovesThreatTable,
                                 "N": self._createKnightThreatTable, "B": self._createDiagonalMovesThreatTable,
                                 "Q": self._createQueenThreatTable, "K": self._createKingThreatTable}

    def createThreatTable(self):
        self._bbOfThreats["w"] = 0
        self._bbOfThreats["b"] = 0
        for piece in PIECES:
            for color in COLORS:
                self._threatTableFunc[piece](color)

    def _createPawnThreatTable(self, color: str):
        if color == "w":
            self._createWhitePawnThreatTable()
        else:
            self._createBlackPawnThreatTable()

    def _createWhitePawnThreatTable(self):
        self._bbOfThreats["w"] |= ((self._gameState.bbOfPieces["wp"] & CORRECTIONS["h"]) << 7)
        self._bbOfThreats["w"] |= ((self._gameState.bbOfPieces["wp"] & CORRECTIONS["a"]) << 9)

    def _createBlackPawnThreatTable(self):
        self._bbOfThreats["b"] |= ((self._gameState.bbOfPieces["bp"] & CORRECTIONS["h"]) >> 9)
        self._bbOfThreats["b"] |= ((self._gameState.bbOfPieces["bp"] & CORRECTIONS["a"]) >> 7)

    def _createKnightThreatTable(self, color: str):
        piece = color + "N"
        self._bbOfThreats[color] |= ((self._gameState.bbOfPieces[piece] & CORRECTIONS["h"] & CORRECTIONS["78"]) << 15)
        self._bbOfThreats[color] |= ((self._gameState.bbOfPieces[piece] & CORRECTIONS["gh"] & CORRECTIONS["8"]) << 6)
        self._bbOfThreats[color] |= ((self._gameState.bbOfPieces[piece] & CORRECTIONS["gh"] & CORRECTIONS["1"]) >> 10)
        self._bbOfThreats[color] |= ((self._gameState.bbOfPieces[piece] & CORRECTIONS["h"] & CORRECTIONS["12"]) >> 17)
        self._bbOfThreats[color] |= ((self._gameState.bbOfPieces[piece] & CORRECTIONS["a"] & CORRECTIONS["12"]) >> 15)
        self._bbOfThreats[color] |= ((self._gameState.bbOfPieces[piece] & CORRECTIONS["ab"] & CORRECTIONS["1"]) >> 6)
        self._bbOfThreats[color] |= ((self._gameState.bbOfPieces[piece] & CORRECTIONS["ab"] & CORRECTIONS["8"]) << 10)
        self._bbOfThreats[color] |= ((self._gameState.bbOfPieces[piece] & CORRECTIONS["a"] & CORRECTIONS["78"]) << 17)

    def _createKingThreatTable(self, color: str):
        piece = color + "K"
        self._bbOfThreats[color] |= ((self._gameState.bbOfPieces[piece] & CORRECTIONS["8"]) << 8)
        self._bbOfThreats[color] |= ((self._gameState.bbOfPieces[piece] & CORRECTIONS["h"] & CORRECTIONS["8"]) << 7)
        self._bbOfThreats[color] |= ((self._gameState.bbOfPieces[piece] & CORRECTIONS["h"]) >> 1)
        self._bbOfThreats[color] |= ((self._gameState.bbOfPieces[piece] & CORRECTIONS["h"] & CORRECTIONS["1"]) >> 9)
        self._bbOfThreats[color] |= ((self._gameState.bbOfPieces[piece] & CORRECTIONS["1"]) >> 8)
        self._bbOfThreats[color] |= ((self._gameState.bbOfPieces[piece] & CORRECTIONS["a"] & CORRECTIONS["1"]) >> 7)
        self._bbOfThreats[color] |= ((self._gameState.bbOfPieces[piece] & CORRECTIONS["a"]) << 1)
        self._bbOfThreats[color] |= ((self._gameState.bbOfPieces[piece] & CORRECTIONS["a"] & CORRECTIONS["8"]) << 9)

    def _createDiagonalMovesThreatTable(self, color: str, piece="B"):
        splitPositions = numSplit(self._gameState.bbOfPieces[color + piece])
        for splitPosition in splitPositions:
            checkingSq = splitPosition
            while checkingSq & CORRECTIONS["h"] & CORRECTIONS["8"]:
                checkingSq <<= 7
                self._bbOfThreats[color] |= checkingSq
                if checkingSq & self._gameState.bbOfOccupiedSquares["a"]:
                    break
            checkingSq = splitPosition
            while checkingSq & CORRECTIONS["h"] & CORRECTIONS["1"]:
                checkingSq >>= 9
                self._bbOfThreats[color] |= checkingSq
                if checkingSq & self._gameState.bbOfOccupiedSquares["a"]:
                    break
            checkingSq = splitPosition
            while checkingSq & CORRECTIONS["a"] & CORRECTIONS["1"]:
                checkingSq >>= 7
                self._bbOfThreats[color] |= checkingSq
                if checkingSq & self._gameState.bbOfOccupiedSquares["a"]:
                    break
            checkingSq = splitPosition
            while checkingSq & CORRECTIONS["a"] & CORRECTIONS["8"]:
                checkingSq <<= 9
                self._bbOfThreats[color] |= checkingSq
                if checkingSq & self._gameState.bbOfOccupiedSquares["a"]:
                    break

    def _createVerticalAndHorizontalMovesThreatTable(self, color: str, piece="R"):
        splitPositions = numSplit(self._gameState.bbOfPieces[color + piece])
        for splitPosition in splitPositions:
            checkingSq = splitPosition
            while checkingSq & CORRECTIONS["8"]:
                checkingSq <<= 8
                self._bbOfThreats[color] |= checkingSq
                if checkingSq & self._gameState.bbOfOccupiedSquares["a"]:
                    break
            checkingSq = splitPosition
            while checkingSq & CORRECTIONS["h"]:
                checkingSq >>= 1
                self._bbOfThreats[color] |= checkingSq
                if checkingSq & self._gameState.bbOfOccupiedSquares["a"]:
                    break
            checkingSq = splitPosition
            while checkingSq & CORRECTIONS["1"]:
                checkingSq >>= 8
                self._bbOfThreats[color] |= checkingSq
                if checkingSq & self._gameState.bbOfOccupiedSquares["a"]:
                    break
            checkingSq = splitPosition
            while checkingSq & CORRECTIONS["a"]:
                checkingSq <<= 1
                self._bbOfThreats[color] |= checkingSq
                if checkingSq & self._gameState.bbOfOccupiedSquares["a"]:
                    break

    def _createQueenThreatTable(self, color: str):
        self._createDiagonalMovesThreatTable(color, "Q")
        self._createVerticalAndHorizontalMovesThreatTable(color, "Q")

    def appendThreatTableToLog(self):
        self._bbOfThreatsLog.append(self._bbOfThreats.copy())

    def popThreatTableFromLog(self):
        self._bbOfThreats = self._bbOfThreatsLog.pop()

    @property
    def bbOfThreats(self):
        return self._bbOfThreats
