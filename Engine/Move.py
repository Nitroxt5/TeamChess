from TeamChess.Utils.MagicConsts import CORRECTIONS, CASTLE_SQUARES, COLUMN_TO_LETTER, ROW_TO_NUMBER
from TestDLL import getPower


class Move:
    def __init__(self, startSq, endSq, gameState, movedPiece: str = None, isEnpassant=False,
                 isCastle=False, isFirst=False, isReserve=False, promotedTo="", promotedPiecePosition=0):
        self.isReserve = isReserve
        self.startSquare = startSq
        self.endSquare = endSq
        self.movedPiece = movedPiece
        self.isEnpassant = isEnpassant
        self.isCastle = isCastle
        self.isFirst = isFirst
        if self.isReserve:
            self.capturedPiece = None
            self.isPawnPromotion = False
            self.isCapture = False
            self.moveID = self.endSquare
            self.promotedTo = ""
            self.promotedPiecePosition = 0
        else:
            if self.movedPiece is None:
                self.movedPiece = gameState.getPieceBySquare(self.startSquare)
            if not self.isEnpassant:
                self.capturedPiece = gameState.getPieceBySquare(self.endSquare)
            else:
                self.capturedPiece = "bp" if self.movedPiece == "wp" else "wp"
            self.moveID = self.startSquare ^ self.endSquare
            self.isPawnPromotion = (self.movedPiece == "wp" and not self.endSquare & CORRECTIONS["8"]) or (
                    self.movedPiece == "bp" and not self.endSquare & CORRECTIONS["1"])
            self.promotedTo = promotedTo
            self.promotedPiecePosition = promotedPiecePosition
            self.isCapture = False
            if self.capturedPiece is not None and self.movedPiece is not None:
                if self.capturedPiece[0] != self.movedPiece[0]:
                    self.isCapture = True
        self.estimatedScore = 0
        self.exactScore = 0
        self.goodScore = False
        self.isKiller = False

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID and self.promotedTo == other.promotedTo and self.movedPiece == other.movedPiece
        return False

    def __repr__(self):
        return self._getMoveNotation()

    def _getMoveNotation(self):
        if self.isReserve:
            return self._getReserveMoveNotation()
        if self.isCastle:
            return self._getCastleMoveNotation()
        if self.isPawnPromotion:
            return self._getPawnPromotionMoveNotation()
        moveNotation = "" if self.movedPiece[1] == "p" else self.movedPiece[1]
        moveNotation += self._getSquareNotation(self.startSquare)
        moveNotation += "x" if self.isCapture else "-"
        moveNotation += self._getSquareNotation(self.endSquare)
        return moveNotation

    def _getReserveMoveNotation(self):
        if self.movedPiece[1] == "p":
            return f"&{self._getSquareNotation(self.endSquare)}"
        else:
            return f"&{self.movedPiece[1]}{self._getSquareNotation(self.endSquare)}"

    def _getCastleMoveNotation(self):
        if (self.endSquare & CASTLE_SQUARES["wKs"]) or (self.endSquare & CASTLE_SQUARES["bKs"]):
            return "0-0"
        if (self.endSquare & CASTLE_SQUARES["wQs"]) or (self.endSquare & CASTLE_SQUARES["bQs"]):
            return "0-0-0"

    def _getPawnPromotionMoveNotation(self):
        moveNotation = self._getSquareNotation(self.startSquare)
        moveNotation += "x" if self.isCapture else "-"
        moveNotation += self._getSquareNotation(self.endSquare) + self.promotedTo
        return moveNotation

    @staticmethod
    def _getSquareNotation(square: int):
        location = getPower(square)
        return COLUMN_TO_LETTER[location % 8] + ROW_TO_NUMBER[location // 8]
