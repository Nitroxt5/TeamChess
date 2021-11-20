ONE = 0b1000000000000000000000000000000000000000000000000000000000000000
COLORS = ("w", "b")
PIECES = ("K", "Q", "R", "B", "N", "p")
COLORED_PIECES = [color + piece for color in COLORS for piece in PIECES]


def reverse(number):
    rev = 0
    counter = 64
    while number:
        counter -= 1
        rev <<= 1
        rev += number & 1
        number >>= 1
    rev <<= counter
    return rev


class GameState:
    def __init__(self, side):
        self.bbOfPieces = {"wK": 0b0000000000000000000000000000000000000000000000000000000000001000,
                           "wQ": 0b0000000000000000000000000000000000000000000000000000000000010000,
                           "wR": 0b0000000000000000000000000000000000000000000000000000000010000001,
                           "wB": 0b0000000000000000000000000000000000000000000000000000000000100100,
                           "wN": 0b0000000000000000000000000000000000000000000000000000000001000010,
                           "wp": 0b0000000000000000000000000000000000000000000000001111111100000000,
                           "bK": 0b0000100000000000000000000000000000000000000000000000000000000000,
                           "bQ": 0b0001000000000000000000000000000000000000000000000000000000000000,
                           "bR": 0b1000000100000000000000000000000000000000000000000000000000000000,
                           "bB": 0b0010010000000000000000000000000000000000000000000000000000000000,
                           "bN": 0b0100001000000000000000000000000000000000000000000000000000000000,
                           "bp": 0b0000000011111111000000000000000000000000000000000000000000000000}
        self.bbOfOccupiedSquares = {"w": 0b0000000000000000000000000000000000000000000000001111111111111111,
                                    "b": 0b1111111111111111000000000000000000000000000000000000000000000000,
                                    "a": 0b1111111111111111000000000000000000000000000000001111111111111111}
        if not side:
            self.bbOfPieces = {key: reverse(value) for key, value in self.bbOfPieces.items()}
            self.bbOfOccupiedSquares = {key: reverse(value) for key, value in self.bbOfOccupiedSquares.items()}
        self.whiteTurn = True
        self.gameLog = []

    def makeMove(self, move):
        self.setSqState(move.movedPiece, move.endColumn, move.endRow)
        self.unsetSqState(move.movedPiece, move.startColumn, move.startRow)
        self.unsetSqState(move.capturedPiece, move.endColumn, move.endRow)
        self.gameLog.append(move)
        self.whiteTurn = not self.whiteTurn

    def undoMove(self):
        if len(self.gameLog) != 0:
            move = self.gameLog.pop()
            self.setSqState(move.movedPiece, move.startColumn, move.startRow)
            self.unsetSqState(move.movedPiece, move.endColumn, move.endRow)
            self.setSqState(move.capturedPiece, move.endColumn, move.endRow)
            self.whiteTurn = not self.whiteTurn

    def setSqState(self, piece, column, row):
        if piece is not None:
            newBit = ONE >> (row * 8 + column)
            self.bbOfPieces[piece] |= newBit
            self.bbOfOccupiedSquares[piece[0]] |= newBit
            self.bbOfOccupiedSquares["a"] |= newBit

    def unsetSqState(self, piece, column, row):
        if piece is not None:
            newBit = ONE >> (row * 8 + column)
            newBit = ~newBit
            self.bbOfPieces[piece] &= newBit
            self.bbOfOccupiedSquares[piece[0]] &= newBit
            self.bbOfOccupiedSquares["a"] &= newBit

    def getSqState(self, piece, column, row):
        if piece is not None:
            mask = ONE >> (row * 8 + column)
            return (self.bbOfPieces[piece] & mask) != 0

    def getPieceBySquare(self, column, row):
        for piece in COLORED_PIECES:
            if self.getSqState(piece, column, row):
                return piece
        return None


class Move:
    rowToNumber = {0: "8", 1: "7", 2: "6", 3: "5", 4: "4", 5: "3", 6: "2", 7: "1"}
    columnToLetter = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7: "h"}

    def __init__(self, startSq, endSq, gameState, isEnpassant=False, isCastle=False):
        self.startColumn = startSq[0]
        self.startRow = startSq[1]
        self.endColumn = endSq[0]
        self.endRow = endSq[1]
        self.movedPiece = gameState.getPieceBySquare(self.startColumn, self.startRow)
        self.capturedPiece = gameState.getPieceBySquare(self.endColumn, self.endRow)
        self.isCapture = False
        if self.capturedPiece is not None:
            if self.capturedPiece[0] != self.movedPiece[0]:
                self.isCapture = True
        self.moveID = self.startColumn * 1000 + self.startRow * 100 + self.endColumn * 10 + self.endRow
        self.isPawnPromotion = (self.movedPiece == "wp" and self.endRow == 0) or (
                self.movedPiece == "bp" and self.endRow == 7)
        self.isEnpassant = isEnpassant
        if self.isEnpassant:
            self.capturedPiece = "bp" if self.movedPiece == "wp" else "wp"
        self.isCastle = isCastle

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def __repr__(self):
        return self.getMoveNotation()

    def __str__(self):
        return self.getMoveNotation()

    def getSquareNotation(self, row, column):
        return self.columnToLetter[column] + self.rowToNumber[row]

    def getMoveNotation(self):
        if self.isCastle:
            if self.endColumn == 6:
                return "0-0"
            elif self.endColumn == 2:
                return "0-0-0"
        moveNotation = ""
        if self.movedPiece[1] != "p":
            moveNotation = self.movedPiece[1]
        moveNotation += self.getSquareNotation(self.startRow, self.startColumn)
        if self.capturedPiece != "--":
            moveNotation += "x"
        else:
            moveNotation += "-"
        moveNotation += self.getSquareNotation(self.endRow, self.endColumn)
        return moveNotation
