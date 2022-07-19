from TeamChess.Utils.MagicConsts import MAX_INT, COLORED_PIECES, COLORED_PIECES_CODES, CASTLE_SQUARES
from TestDLL import numSplit, getPower
from random import randint, seed


class GSHasher:
    def __init__(self, gameState):
        self._gameState = gameState
        self._zobristTable = []
        self._zobristReserveTable = []
        self._zobristWhiteTurn = 0
        self._zobristBlackTurn = 0
        self._boardHashLog = []
        self._boardHash = 0
        self._generateZobristTables()
        self._hashBoard()

    def _generateZobristTables(self):
        seed(1)
        for _ in range(64):
            newList = []
            for _ in range(12):
                newList.append(randint(0, MAX_INT))
            self._zobristTable.append(newList)
        for _ in range(18):
            newList = []
            for _ in range(12):
                newList.append(randint(0, MAX_INT))
            self._zobristReserveTable.append(newList)
        self._zobristWhiteTurn = randint(0, MAX_INT)
        self._zobristBlackTurn = randint(0, MAX_INT)

    def _hashBoard(self):
        for piece in COLORED_PIECES:
            splitPositions = numSplit(self._gameState.bbOfPieces[piece])
            for position in splitPositions:
                pos = getPower(position)
                self.switchBoardHash(pos, piece)
        for color, value in self._gameState.reserve.items():
            for piece, count in value.items():
                self.switchReserveHash(count, color + piece)
        self._boardHash ^= self._zobristWhiteTurn

    def switchBoardHash(self, location: int, piece: str):
        self._boardHash ^= self._zobristTable[location][COLORED_PIECES_CODES[piece]]

    def switchReserveHash(self, count: int, piece: str):
        self._boardHash ^= self._zobristReserveTable[count][COLORED_PIECES_CODES[piece]]

    def updateBoardHash(self, move):
        startLoc = getPower(move.startSquare)
        endLoc = getPower(move.endSquare)
        moveInfo = f"move = {move.startSquare}, {move.endSquare}, {move.movedPiece}"
        assert 0 <= startLoc <= 64, f"startLoc = {startLoc}, {moveInfo}"
        assert 0 <= endLoc <= 63, f"endLoc = {endLoc}, {moveInfo}"
        if move.capturedPiece is not None and not move.isEnpassant:
            self.switchBoardHash(endLoc, move.capturedPiece)
        if move.isEnpassant:
            self._updateHashOnEnpassant(endLoc, move)
        if not move.isPawnPromotion:
            self.switchBoardHash(endLoc, move.movedPiece)
        else:
            self.switchBoardHash(endLoc, move.movedPiece[0] + move.promotedTo)
        if not move.isReserve:
            self.switchBoardHash(startLoc, move.movedPiece)
        if move.isCastle:
            self._updateHashOnCastle(endLoc, move)
        self._updateTurnHash()

    def _updateHashOnEnpassant(self, endLoc: int, move):
        if move.movedPiece == "wp":
            self.switchBoardHash(endLoc - 8, move.capturedPiece)
        elif move.movedPiece == "bp":
            self.switchBoardHash(endLoc + 8, move.capturedPiece)

    def _updateHashOnCastle(self, endLoc: int, move):
        if move.endSquare & CASTLE_SQUARES["wKs"] or move.endSquare & CASTLE_SQUARES["bKs"]:
            self._updateHashOnKingSideCastle(endLoc, move)
        elif move.endSquare & CASTLE_SQUARES["wQs"] or move.endSquare & CASTLE_SQUARES["bQs"]:
            self._updateHashOnQueenSideCastle(endLoc, move)

    def _updateHashOnKingSideCastle(self, endLoc: int, move):
        self.switchBoardHash(endLoc - 1, f"{move.movedPiece[0]}R")
        self.switchBoardHash(endLoc + 1, f"{move.movedPiece[0]}R")

    def _updateHashOnQueenSideCastle(self, endLoc: int, move):
        self.switchBoardHash(endLoc + 1, f"{move.movedPiece[0]}R")
        self.switchBoardHash(endLoc - 2, f"{move.movedPiece[0]}R")

    def _updateTurnHash(self):
        self._boardHash ^= self._zobristWhiteTurn
        self._boardHash ^= self._zobristBlackTurn

    def updateReserveHash(self, piece: str, prevCount: int):
        self.switchReserveHash(prevCount, piece)
        self.switchReserveHash(self._gameState.reserve[piece[0]][piece[1]], piece)

    def appendHashToLog(self):
        self._boardHashLog.append(self._boardHash)

    def popHashFromLog(self):
        self._boardHash = self._boardHashLog.pop()

    @property
    def boardHash(self):
        return self._boardHash
