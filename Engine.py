import ctypes
import random
from copy import deepcopy

MAX_INT = 18446744073709551615
ONE = 0b1000000000000000000000000000000000000000000000000000000000000000
COLORS = ("w", "b")
PIECES = ("K", "Q", "R", "B", "N", "p")
pieceScores = {"K": 0, "Q": 1200, "R": 600, "B": 400, "N": 400, "p": 100}
COLORED_PIECES = [color + piece for color in COLORS for piece in PIECES]
COLORED_PIECES_CODES = {COLORED_PIECES[i]: i for i in range(len(COLORED_PIECES))}
CASTLE_SIDES = {"wKs": 8, "wQs": 4, "bKs": 2, "bQs": 1}
DIMENSION = 8
bbOfPawnStarts = {"w": 0b0000000000000000000000000000000000000000000000001111111100000000,
                  "b": 0b0000000011111111000000000000000000000000000000000000000000000000}
bbOfColumns = {"a": 0b1000000010000000100000001000000010000000100000001000000010000000,
               "b": 0b0100000001000000010000000100000001000000010000000100000001000000,
               "c": 0b0010000000100000001000000010000000100000001000000010000000100000,
               "d": 0b0001000000010000000100000001000000010000000100000001000000010000,
               "e": 0b0000100000001000000010000000100000001000000010000000100000001000,
               "f": 0b0000010000000100000001000000010000000100000001000000010000000100,
               "g": 0b0000001000000010000000100000001000000010000000100000001000000010,
               "h": 0b0000000100000001000000010000000100000001000000010000000100000001}
bbOfRows = {"1": 0b0000000000000000000000000000000000000000000000000000000011111111,
            "2": 0b0000000000000000000000000000000000000000000000001111111100000000,
            "3": 0b0000000000000000000000000000000000000000111111110000000000000000,
            "4": 0b0000000000000000000000000000000011111111000000000000000000000000,
            "5": 0b0000000000000000000000001111111100000000000000000000000000000000,
            "6": 0b0000000000000000111111110000000000000000000000000000000000000000,
            "7": 0b0000000011111111000000000000000000000000000000000000000000000000,
            "8": 0b1111111100000000000000000000000000000000000000000000000000000000}
bbOfCenter = 0b0000000000000000000000000001100000011000000000000000000000000000
bbOfCorrections = {"a": 0b0111111101111111011111110111111101111111011111110111111101111111,
                   "ab": 0b0011111100111111001111110011111100111111001111110011111100111111,
                   "h": 0b1111111011111110111111101111111011111110111111101111111011111110,
                   "gh": 0b1111110011111100111111001111110011111100111111001111110011111100,
                   "1": 0b1111111111111111111111111111111111111111111111111111111100000000,
                   "12": 0b1111111111111111111111111111111111111111111111110000000000000000,
                   "8": 0b0000000011111111111111111111111111111111111111111111111111111111,
                   "78": 0b0000000000000000111111111111111111111111111111111111111111111111}


def powTo(x: int, n: int):
    y = 1
    while n > 0:
        if n % 2 == 1:
            y *= x
        x *= x
        n >>= 1
    return y


def numSplit(number: int):
    num1 = number
    num2 = num1
    result = []
    counter = 0
    while num1:
        if num2 % 2 == 1:
            num2 = num1 - powTo(2, counter)
            num1 = num2
            result.append(powTo(2, counter))
            counter = 0
        num2 >>= 1
        counter += 1
    return result


def getPower(number: int):
    num = number
    counter = 0
    while num:
        num >>= 1
        counter += 1
    return 64 - counter


def getBitsCount(number: int):
    num = number
    counter = 0
    while num:
        if num & 1:
            counter += 1
        num >>= 1
    return counter


class GameState:
    def __init__(self):
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
        # self.bbOfPieces = {"wK": 0b0000000000000000000000010000000000000000000000000000000000000000,
        #                    "wQ": 0b0000000000000000000000000000000000000000000000000000000000000000,
        #                    "wR": 0b0000000000000000000000000000000000000000000000000000000010000001,
        #                    "wB": 0b0000000000000000000000000100000000000001000000000000000000000000,
        #                    "wN": 0b0000000000000000000000000000000000000000000000010000000001000000,
        #                    "wp": 0b0000000000000000000000000001000000000000001000001000001100000000,
        #                    "bK": 0b0000001000000000000000000000000000000000000000000000000000000000,
        #                    "bQ": 0b0000000000000100000000000000000000000000000000000000000000000000,
        #                    "bR": 0b1000010000000000000000000000000000000000000000000000000000000000,
        #                    "bB": 0b0010000000000000000000000010000000000000000000000000000000000000,
        #                    "bN": 0b0000000000000000000000000000000000000000000000000100000000000000,
        #                    "bp": 0b0000000011110001000001000000000000000000000000000000000000000000}
        # self.bbOfOccupiedSquares = {"w": self.bbOfPieces["wK"] | self.bbOfPieces["wQ"] | self.bbOfPieces["wR"] | self.bbOfPieces["wB"] | self.bbOfPieces["wN"] | self.bbOfPieces["wp"],
        #                             "b": self.bbOfPieces["bK"] | self.bbOfPieces["bQ"] | self.bbOfPieces["bR"] | self.bbOfPieces["bB"] | self.bbOfPieces["bN"] | self.bbOfPieces["bp"],
        #                             "a": self.bbOfPieces["wK"] | self.bbOfPieces["wQ"] | self.bbOfPieces["wR"] | self.bbOfPieces["wB"] | self.bbOfPieces["wN"] | self.bbOfPieces["wp"] | self.bbOfPieces["bK"] | self.bbOfPieces["bQ"] | self.bbOfPieces["bR"] | self.bbOfPieces["bB"] | self.bbOfPieces["bN"] | self.bbOfPieces["bp"]}
        self.bbOfThreats = {"w": 0, "b": 0}
        self.bbOfThreatsLog = []
        self.moveFunc = {"p": self.getPawnMoves, "R": self.getRookMoves, "N": self.getKnightMoves,
                         "B": self.getBishopMoves, "Q": self.getQueenMoves, "K": self.getKingMoves}
        self.threatTableFunc = {"p": self.createPawnThreatTable, "R": self.createRookThreatTable,
                                "N": self.createKnightThreatTable, "B": self.createBishopThreatTable,
                                "Q": self.createQueenThreatTable, "K": self.createKingThreatTable}
        self.whiteTurn = True
        self.gameLog = []
        self.checkmate = False
        self.stalemate = False
        self.enpassantSq = 0
        self.enpassantSqLog = [self.enpassantSq]
        self.currentCastlingRight = 0b1111
        self.castleRightsLog = [self.currentCastlingRight]
        self.isWhiteCastled = False
        self.isBlackCastled = False
        self.isWhiteInCheck = False
        self.isBlackInCheck = False
        self.pieceScoreDiff = 0
        self.zobristTable = []
        self.boardHashLog = []
        self.boardHash = 0
        self.hashBoard()

    def hashBoard(self):
        for i in range(64):
            newList = []
            for j in range(12):
                newList.append(random.randint(0, MAX_INT))
            self.zobristTable.append(newList)
        for piece in COLORED_PIECES:
            splitPositions = numSplit(self.bbOfPieces[piece])
            for position in splitPositions:
                pos = getPower(position)
                self.boardHash ^= self.zobristTable[pos][COLORED_PIECES_CODES[piece]]

    def updateHash(self, move):
        self.boardHashLog.append(self.boardHash)
        if move.capturedPiece is not None and not move.isEnpassant:
            self.boardHash ^= self.zobristTable[move.endLoc][COLORED_PIECES_CODES[move.capturedPiece]]
        if move.capturedPiece is not None and move.isEnpassant:
            self.boardHash ^= self.zobristTable[self.enpassantSqLog[-1]][COLORED_PIECES_CODES[move.capturedPiece]]
        if not move.isPawnPromotion:
            self.boardHash ^= self.zobristTable[move.endLoc][COLORED_PIECES_CODES[move.movedPiece]]
        else:
            self.boardHash ^= self.zobristTable[move.endLoc][COLORED_PIECES_CODES[f"{move.movedPiece[0]}Q"]]
        self.boardHash ^= self.zobristTable[move.startLoc][COLORED_PIECES_CODES[move.movedPiece]]
        if move.isCastle:
            if move.endSquare & move.bbOfCastle["wKs"] or move.endSquare & move.bbOfCastle["bKs"]:
                self.boardHash ^= self.zobristTable[move.endLoc - 1][COLORED_PIECES_CODES[f"{move.movedPiece[0]}R"]]
                self.boardHash ^= self.zobristTable[move.endLoc + 1][COLORED_PIECES_CODES[f"{move.movedPiece[0]}R"]]
            elif move.endSquare & move.bbOfCastle["wQs"] or move.endSquare & move.bbOfCastle["bQs"]:
                self.boardHash ^= self.zobristTable[move.endLoc + 1][COLORED_PIECES_CODES[f"{move.movedPiece[0]}R"]]
                self.boardHash ^= self.zobristTable[move.endLoc - 2][COLORED_PIECES_CODES[f"{move.movedPiece[0]}R"]]

    def createThreatTable(self):
        self.bbOfThreats["w"] = 0
        self.bbOfThreats["b"] = 0
        self.createWhiteThreatTable()
        self.createBlackThreatTable()

    def createWhiteThreatTable(self):
        for piece in PIECES:
            self.threatTableFunc[piece]("w")

    def createBlackThreatTable(self):
        for piece in PIECES:
            self.threatTableFunc[piece]("b")

    def createPawnThreatTable(self, color: str):
        piece = color + "p"
        if color == "w":
            self.bbOfThreats[color] |= ((self.bbOfPieces[piece] & bbOfCorrections["h"]) << 7)
            self.bbOfThreats[color] |= ((self.bbOfPieces[piece] & bbOfCorrections["a"]) << 9)
        elif color == "b":
            self.bbOfThreats[color] |= ((self.bbOfPieces[piece] & bbOfCorrections["h"]) >> 9)
            self.bbOfThreats[color] |= ((self.bbOfPieces[piece] & bbOfCorrections["a"]) >> 7)

    def createKnightThreatTable(self, color: str):
        piece = color + "N"
        self.bbOfThreats[color] |= ((self.bbOfPieces[piece] & bbOfCorrections["h"] & bbOfCorrections["78"]) << 15)
        self.bbOfThreats[color] |= ((self.bbOfPieces[piece] & bbOfCorrections["gh"] & bbOfCorrections["8"]) << 6)
        self.bbOfThreats[color] |= ((self.bbOfPieces[piece] & bbOfCorrections["gh"] & bbOfCorrections["1"]) >> 10)
        self.bbOfThreats[color] |= ((self.bbOfPieces[piece] & bbOfCorrections["h"] & bbOfCorrections["12"]) >> 17)
        self.bbOfThreats[color] |= ((self.bbOfPieces[piece] & bbOfCorrections["a"] & bbOfCorrections["12"]) >> 15)
        self.bbOfThreats[color] |= ((self.bbOfPieces[piece] & bbOfCorrections["ab"] & bbOfCorrections["1"]) >> 6)
        self.bbOfThreats[color] |= ((self.bbOfPieces[piece] & bbOfCorrections["ab"] & bbOfCorrections["8"]) << 10)
        self.bbOfThreats[color] |= ((self.bbOfPieces[piece] & bbOfCorrections["a"] & bbOfCorrections["78"]) << 17)

    def createKingThreatTable(self, color: str):
        piece = color + "K"
        self.bbOfThreats[color] |= ((self.bbOfPieces[piece] & bbOfCorrections["8"]) << 8)
        self.bbOfThreats[color] |= ((self.bbOfPieces[piece] & bbOfCorrections["h"] & bbOfCorrections["8"]) << 7)
        self.bbOfThreats[color] |= ((self.bbOfPieces[piece] & bbOfCorrections["h"]) >> 1)
        self.bbOfThreats[color] |= ((self.bbOfPieces[piece] & bbOfCorrections["h"] & bbOfCorrections["1"]) >> 9)
        self.bbOfThreats[color] |= ((self.bbOfPieces[piece] & bbOfCorrections["1"]) >> 8)
        self.bbOfThreats[color] |= ((self.bbOfPieces[piece] & bbOfCorrections["a"] & bbOfCorrections["1"]) >> 7)
        self.bbOfThreats[color] |= ((self.bbOfPieces[piece] & bbOfCorrections["a"]) << 1)
        self.bbOfThreats[color] |= ((self.bbOfPieces[piece] & bbOfCorrections["a"] & bbOfCorrections["8"]) << 9)

    def createBishopThreatTable(self, color: str, isQueen=False):
        if isQueen:
            piece = color + "Q"
        else:
            piece = color + "B"
        splitPositions = numSplit(self.bbOfPieces[piece])
        for splitPosition in splitPositions:
            checkingSq = splitPosition
            while checkingSq & bbOfCorrections["h"] & bbOfCorrections["8"]:
                checkingSq <<= 7
                self.bbOfThreats[color] |= checkingSq
                if checkingSq & self.bbOfOccupiedSquares["a"]:
                    break
            checkingSq = splitPosition
            while checkingSq & bbOfCorrections["h"] & bbOfCorrections["1"]:
                checkingSq >>= 9
                self.bbOfThreats[color] |= checkingSq
                if checkingSq & self.bbOfOccupiedSquares["a"]:
                    break
            checkingSq = splitPosition
            while checkingSq & bbOfCorrections["a"] & bbOfCorrections["1"]:
                checkingSq >>= 7
                self.bbOfThreats[color] |= checkingSq
                if checkingSq & self.bbOfOccupiedSquares["a"]:
                    break
            checkingSq = splitPosition
            while checkingSq & bbOfCorrections["a"] & bbOfCorrections["8"]:
                checkingSq <<= 9
                self.bbOfThreats[color] |= checkingSq
                if checkingSq & self.bbOfOccupiedSquares["a"]:
                    break

    def createRookThreatTable(self, color: str, isQueen=False):
        if isQueen:
            piece = color + "Q"
        else:
            piece = color + "R"
        splitPositions = numSplit(self.bbOfPieces[piece])
        for splitPosition in splitPositions:
            checkingSq = splitPosition
            while checkingSq & bbOfCorrections["8"]:
                checkingSq <<= 8
                self.bbOfThreats[color] |= checkingSq
                if checkingSq & self.bbOfOccupiedSquares["a"]:
                    break
            checkingSq = splitPosition
            while checkingSq & bbOfCorrections["h"]:
                checkingSq >>= 1
                self.bbOfThreats[color] |= checkingSq
                if checkingSq & self.bbOfOccupiedSquares["a"]:
                    break
            checkingSq = splitPosition
            while checkingSq & bbOfCorrections["1"]:
                checkingSq >>= 8
                self.bbOfThreats[color] |= checkingSq
                if checkingSq & self.bbOfOccupiedSquares["a"]:
                    break
            checkingSq = splitPosition
            while checkingSq & bbOfCorrections["a"]:
                checkingSq <<= 1
                self.bbOfThreats[color] |= checkingSq
                if checkingSq & self.bbOfOccupiedSquares["a"]:
                    break

    def createQueenThreatTable(self, color: str):
        self.createBishopThreatTable(color, True)
        self.createRookThreatTable(color, True)

    def makeMove(self, move):
        if move.capturedPiece is not None:
            color = 1 if self.whiteTurn else -1
            self.pieceScoreDiff += color * pieceScores[move.capturedPiece[1]]
        self.unsetSqState(move.capturedPiece, move.endSquare)
        self.unsetSqState(move.movedPiece, move.startSquare)
        self.gameLog.append(move)
        if move.isEnpassant:
            if self.whiteTurn:
                self.unsetSqState(move.capturedPiece, move.endSquare >> 8)
            else:
                self.unsetSqState(move.capturedPiece, move.endSquare << 8)
        if move.movedPiece[0] == "w" and move.isFirst:
            self.enpassantSq = move.endSquare >> 8
        elif move.movedPiece[0] == "b" and move.isFirst:
            self.enpassantSq = move.startSquare >> 8
        else:
            self.enpassantSq = 0
        self.enpassantSqLog.append(self.enpassantSq)
        if move.isCastle:
            if self.whiteTurn:
                if move.endSquare & move.bbOfCastle["wKs"]:
                    self.unsetSqState(f"{move.movedPiece[0]}R", move.endSquare >> 1)
                    self.setSqState(f"{move.movedPiece[0]}R", move.endSquare << 1)
                elif move.endSquare & move.bbOfCastle["wQs"]:
                    self.unsetSqState(f"{move.movedPiece[0]}R", move.endSquare << 2)
                    self.setSqState(f"{move.movedPiece[0]}R", move.endSquare >> 1)
                self.isWhiteCastled = True
            else:
                if move.endSquare & move.bbOfCastle["bKs"]:
                    self.unsetSqState(f"{move.movedPiece[0]}R", move.endSquare >> 1)
                    self.setSqState(f"{move.movedPiece[0]}R", move.endSquare << 1)
                elif move.endSquare & move.bbOfCastle["bQs"]:
                    self.unsetSqState(f"{move.movedPiece[0]}R", move.endSquare << 2)
                    self.setSqState(f"{move.movedPiece[0]}R", move.endSquare >> 1)
                self.isBlackCastled = True
        if not move.isPawnPromotion:
            self.setSqState(move.movedPiece, move.endSquare)
        else:
            self.setSqState(f"{move.movedPiece[0]}Q", move.endSquare)
        self.updateCastleRights(move)
        self.updateHash(move)
        self.castleRightsLog.append(self.currentCastlingRight)
        self.whiteTurn = not self.whiteTurn
        self.createThreatTable()
        self.bbOfThreatsLog.append(deepcopy(self.bbOfThreats))
        self.inCheck()

    def undoMove(self):
        if len(self.gameLog) != 0:
            move = self.gameLog.pop()
            if move.capturedPiece is not None:
                color = 1 if self.whiteTurn else -1
                self.pieceScoreDiff += color * pieceScores[move.capturedPiece[1]]
            self.boardHash = self.boardHashLog.pop()
            if move.isPawnPromotion:
                self.unsetSqState(f"{move.movedPiece[0]}Q", move.endSquare)
            else:
                self.unsetSqState(move.movedPiece, move.endSquare)
            if not move.isEnpassant:
                self.setSqState(move.capturedPiece, move.endSquare)
            else:
                if self.whiteTurn:
                    self.setSqState(move.capturedPiece, move.endSquare << 8)
                else:
                    self.setSqState(move.capturedPiece, move.endSquare >> 8)
            self.enpassantSqLog.pop()
            self.enpassantSq = self.enpassantSqLog[-1]
            self.castleRightsLog.pop()
            self.currentCastlingRight = self.castleRightsLog[-1]
            if move.isCastle:
                if not self.whiteTurn:
                    if move.endSquare & move.bbOfCastle["wKs"]:
                        self.unsetSqState(f"{move.movedPiece[0]}R", move.endSquare << 1)
                        self.setSqState(f"{move.movedPiece[0]}R", move.endSquare >> 1)
                    elif move.endSquare & move.bbOfCastle["wQs"]:
                        self.unsetSqState(f"{move.movedPiece[0]}R", move.endSquare >> 1)
                        self.setSqState(f"{move.movedPiece[0]}R", move.endSquare << 2)
                    self.isWhiteCastled = False
                else:
                    if move.endSquare & move.bbOfCastle["bKs"]:
                        self.unsetSqState(f"{move.movedPiece[0]}R", move.endSquare << 1)
                        self.setSqState(f"{move.movedPiece[0]}R", move.endSquare >> 1)
                    elif move.endSquare & move.bbOfCastle["bQs"]:
                        self.unsetSqState(f"{move.movedPiece[0]}R", move.endSquare >> 1)
                        self.setSqState(f"{move.movedPiece[0]}R", move.endSquare << 2)
                    self.isBlackCastled = False
            self.setSqState(move.movedPiece, move.startSquare)
            self.checkmate = False
            self.stalemate = False
            self.whiteTurn = not self.whiteTurn
            self.bbOfThreats = self.bbOfThreatsLog.pop()
            self.inCheck()

    def updateCastleRights(self, move):
        if move.movedPiece == "wK":
            self.unsetCastleRight(CASTLE_SIDES["wKs"])
            self.unsetCastleRight(CASTLE_SIDES["wQs"])
        elif move.movedPiece == "bK":
            self.unsetCastleRight(CASTLE_SIDES["bKs"])
            self.unsetCastleRight(CASTLE_SIDES["bQs"])
        elif move.movedPiece == "wR":
            if not (move.startSquare & bbOfCorrections["1"]):
                if not (move.startSquare & bbOfCorrections["a"]):
                    self.unsetCastleRight(CASTLE_SIDES["wQs"])
                elif not (move.startSquare & bbOfCorrections["h"]):
                    self.unsetCastleRight(CASTLE_SIDES["wKs"])
        elif move.movedPiece == "bR":
            if not (move.startSquare & bbOfCorrections["8"]):
                if not (move.startSquare & bbOfCorrections["a"]):
                    self.unsetCastleRight(CASTLE_SIDES["bQs"])
                elif not (move.startSquare & bbOfCorrections["h"]):
                    self.unsetCastleRight(CASTLE_SIDES["bKs"])
        if move.capturedPiece == "wR":
            if not (move.endSquare & bbOfCorrections["1"]):
                if not (move.endSquare & bbOfCorrections["a"]):
                    self.unsetCastleRight(CASTLE_SIDES["wQs"])
                elif not (move.endSquare & bbOfCorrections["h"]):
                    self.unsetCastleRight(CASTLE_SIDES["wKs"])
        elif move.capturedPiece == "bR":
            if not (move.endSquare & bbOfCorrections["8"]):
                if not (move.endSquare & bbOfCorrections["a"]):
                    self.unsetCastleRight(CASTLE_SIDES["bQs"])
                elif not (move.endSquare & bbOfCorrections["h"]):
                    self.unsetCastleRight(CASTLE_SIDES["bKs"])

    def getPossibleMoves(self):
        moves = []
        for piece in COLORED_PIECES:
            if (piece[0] == "w" and self.whiteTurn) or (piece[0] == "b" and not self.whiteTurn):
                splitPositions = numSplit(self.bbOfPieces[piece])
                for position in splitPositions:
                    self.moveFunc[piece[1]](position, moves)
        return moves

    def getPawnMoves(self, square: int, moves: list):
        if self.whiteTurn:
            if not self.getSqState(square << 8):
                moves.append(Move(square, square << 8, self, movedPiece="wp"))
                if (square & bbOfPawnStarts["w"]) and not self.getSqState(square << 16):
                    moves.append(Move(square, square << 16, self, movedPiece="wp", isFirst=True))
            if square & bbOfCorrections["a"]:
                if self.getSqStateByColor("b", square << 9):
                    moves.append(Move(square, square << 9, self, movedPiece="wp"))
                elif square << 9 == self.enpassantSq:
                    moves.append(Move(square, square << 9, self, movedPiece="wp", isEnpassant=True))
            if square & bbOfCorrections["h"]:
                if self.getSqStateByColor("b", square << 7):
                    moves.append(Move(square, square << 7, self, movedPiece="wp"))
                elif square << 7 == self.enpassantSq:
                    moves.append(Move(square, square << 7, self, movedPiece="wp", isEnpassant=True))
        if not self.whiteTurn:
            if not self.getSqState(square >> 8):
                moves.append(Move(square, square >> 8, self, movedPiece="bp"))
                if (square & bbOfPawnStarts["b"]) and not self.getSqState(square >> 16):
                    moves.append(Move(square, square >> 16, self, movedPiece="bp", isFirst=True))
            if square & bbOfCorrections["a"]:
                if self.getSqStateByColor("w", square >> 7):
                    moves.append(Move(square, square >> 7, self, movedPiece="bp"))
                elif square >> 7 == self.enpassantSq:
                    moves.append(Move(square, square >> 7, self, movedPiece="bp", isEnpassant=True))
            if square & bbOfCorrections["h"]:
                if self.getSqStateByColor("w", square >> 9):
                    moves.append(Move(square, square >> 9, self, movedPiece="bp"))
                elif square >> 9 == self.enpassantSq:
                    moves.append(Move(square, square >> 9, self, movedPiece="bp", isEnpassant=True))

    def getRookMoves(self, square: int, moves: list, isQueen=False):
        allyColor = "w" if self.whiteTurn else "b"
        enemyColor = "b" if self.whiteTurn else "w"
        if isQueen:
            piece = f"{allyColor}Q"
        else:
            piece = f"{allyColor}R"
        tempSquare = square
        while tempSquare & bbOfCorrections["8"]:
            tempSquare <<= 8
            if not self.getSqState(tempSquare):
                moves.append(Move(square, tempSquare, self, movedPiece=piece))
            elif self.getSqStateByColor(enemyColor, tempSquare):
                moves.append(Move(square, tempSquare, self, movedPiece=piece))
                break
            else:
                break
        tempSquare = square
        while tempSquare & bbOfCorrections["1"]:
            tempSquare >>= 8
            if not self.getSqState(tempSquare):
                moves.append(Move(square, tempSquare, self, movedPiece=piece))
            elif self.getSqStateByColor(enemyColor, tempSquare):
                moves.append(Move(square, tempSquare, self, movedPiece=piece))
                break
            else:
                break
        tempSquare = square
        while tempSquare & bbOfCorrections["a"]:
            tempSquare <<= 1
            if not self.getSqState(tempSquare):
                moves.append(Move(square, tempSquare, self, movedPiece=piece))
            elif self.getSqStateByColor(enemyColor, tempSquare):
                moves.append(Move(square, tempSquare, self, movedPiece=piece))
                break
            else:
                break
        tempSquare = square
        while tempSquare & bbOfCorrections["h"]:
            tempSquare >>= 1
            if not self.getSqState(tempSquare):
                moves.append(Move(square, tempSquare, self, movedPiece=piece))
            elif self.getSqStateByColor(enemyColor, tempSquare):
                moves.append(Move(square, tempSquare, self, movedPiece=piece))
                break
            else:
                break

    def getKnightMoves(self, square: int, moves: list):
        enemyColor = "b" if self.whiteTurn else "w"
        allyColor = "w" if self.whiteTurn else "b"
        piece = f"{allyColor}N"
        if square & bbOfCorrections["h"] & bbOfCorrections["78"]:
            tempSquare = square << 15
            if not self.getSqState(tempSquare) or self.getSqStateByColor(enemyColor, tempSquare):
                moves.append(Move(square, tempSquare, self, movedPiece=piece))
        if square & bbOfCorrections["a"] & bbOfCorrections["78"]:
            tempSquare = square << 17
            if not self.getSqState(tempSquare) or self.getSqStateByColor(enemyColor, tempSquare):
                moves.append(Move(square, tempSquare, self, movedPiece=piece))
        if square & bbOfCorrections["gh"] & bbOfCorrections["8"]:
            tempSquare = square << 6
            if not self.getSqState(tempSquare) or self.getSqStateByColor(enemyColor, tempSquare):
                moves.append(Move(square, tempSquare, self, movedPiece=piece))
        if square & bbOfCorrections["gh"] & bbOfCorrections["1"]:
            tempSquare = square >> 10
            if not self.getSqState(tempSquare) or self.getSqStateByColor(enemyColor, tempSquare):
                moves.append(Move(square, tempSquare, self, movedPiece=piece))
        if square & bbOfCorrections["h"] & bbOfCorrections["12"]:
            tempSquare = square >> 17
            if not self.getSqState(tempSquare) or self.getSqStateByColor(enemyColor, tempSquare):
                moves.append(Move(square, tempSquare, self, movedPiece=piece))
        if square & bbOfCorrections["a"] & bbOfCorrections["12"]:
            tempSquare = square >> 15
            if not self.getSqState(tempSquare) or self.getSqStateByColor(enemyColor, tempSquare):
                moves.append(Move(square, tempSquare, self, movedPiece=piece))
        if square & bbOfCorrections["ab"] & bbOfCorrections["1"]:
            tempSquare = square >> 6
            if not self.getSqState(tempSquare) or self.getSqStateByColor(enemyColor, tempSquare):
                moves.append(Move(square, tempSquare, self, movedPiece=piece))

        if square & bbOfCorrections["ab"] & bbOfCorrections["8"]:
            tempSquare = square << 10
            if not self.getSqState(tempSquare) or self.getSqStateByColor(enemyColor, tempSquare):
                moves.append(Move(square, tempSquare, self, movedPiece=piece))

    def getBishopMoves(self, square: int, moves: list, isQueen=False):
        enemyColor = "b" if self.whiteTurn else "w"
        allyColor = "w" if self.whiteTurn else "b"
        if isQueen:
            piece = f"{allyColor}Q"
        else:
            piece = f"{allyColor}B"
        tempSquare = square
        while tempSquare & bbOfCorrections["h"] & bbOfCorrections["8"]:
            tempSquare <<= 7
            if not self.getSqState(tempSquare):
                moves.append(Move(square, tempSquare, self, movedPiece=piece))
            elif self.getSqStateByColor(enemyColor, tempSquare):
                moves.append(Move(square, tempSquare, self, movedPiece=piece))
                break
            else:
                break
        tempSquare = square
        while tempSquare & bbOfCorrections["a"] & bbOfCorrections["8"]:
            tempSquare <<= 9
            if not self.getSqState(tempSquare):
                moves.append(Move(square, tempSquare, self, movedPiece=piece))
            elif self.getSqStateByColor(enemyColor, tempSquare):
                moves.append(Move(square, tempSquare, self, movedPiece=piece))
                break
            else:
                break
        tempSquare = square
        while tempSquare & bbOfCorrections["h"] & bbOfCorrections["1"]:
            tempSquare >>= 9
            if not self.getSqState(tempSquare):
                moves.append(Move(square, tempSquare, self, movedPiece=piece))
            elif self.getSqStateByColor(enemyColor, tempSquare):
                moves.append(Move(square, tempSquare, self, movedPiece=piece))
                break
            else:
                break
        tempSquare = square
        while tempSquare & bbOfCorrections["a"] & bbOfCorrections["1"]:
            tempSquare >>= 7
            if not self.getSqState(tempSquare):
                moves.append(Move(square, tempSquare, self, movedPiece=piece))
            elif self.getSqStateByColor(enemyColor, tempSquare):
                moves.append(Move(square, tempSquare, self, movedPiece=piece))
                break
            else:
                break

    def getQueenMoves(self, square: int, moves: list):
        self.getRookMoves(square, moves, True)
        self.getBishopMoves(square, moves, True)

    def getKingMoves(self, square: int, moves: list):
        enemyColor = "b" if self.whiteTurn else "w"
        allyColor = "w" if self.whiteTurn else "b"
        piece = f"{allyColor}K"
        if square & bbOfCorrections["8"]:
            tempSquare = square << 8
            if not self.getSqState(tempSquare) or self.getSqStateByColor(enemyColor, tempSquare):
                moves.append(Move(square, tempSquare, self, movedPiece=piece))
        if square & bbOfCorrections["h"] & bbOfCorrections["8"]:
            tempSquare = square << 7
            if not self.getSqState(tempSquare) or self.getSqStateByColor(enemyColor, tempSquare):
                moves.append(Move(square, tempSquare, self, movedPiece=piece))
        if square & bbOfCorrections["h"]:
            tempSquare = square >> 1
            if not self.getSqState(tempSquare) or self.getSqStateByColor(enemyColor, tempSquare):
                moves.append(Move(square, tempSquare, self, movedPiece=piece))
        if square & bbOfCorrections["h"] & bbOfCorrections["1"]:
            tempSquare = square >> 9
            if not self.getSqState(tempSquare) or self.getSqStateByColor(enemyColor, tempSquare):
                moves.append(Move(square, tempSquare, self, movedPiece=piece))
        if square & bbOfCorrections["1"]:
            tempSquare = square >> 8
            if not self.getSqState(tempSquare) or self.getSqStateByColor(enemyColor, tempSquare):
                moves.append(Move(square, tempSquare, self, movedPiece=piece))
        if square & bbOfCorrections["a"] & bbOfCorrections["1"]:
            tempSquare = square >> 7
            if not self.getSqState(tempSquare) or self.getSqStateByColor(enemyColor, tempSquare):
                moves.append(Move(square, tempSquare, self, movedPiece=piece))
        if square & bbOfCorrections["a"]:
            tempSquare = square << 1
            if not self.getSqState(tempSquare) or self.getSqStateByColor(enemyColor, tempSquare):
                moves.append(Move(square, tempSquare, self, movedPiece=piece))
        if square & bbOfCorrections["a"] & bbOfCorrections["8"]:
            tempSquare = square << 9
            if not self.getSqState(tempSquare) or self.getSqStateByColor(enemyColor, tempSquare):
                moves.append(Move(square, tempSquare, self, movedPiece=piece))

    def getCastleMoves(self, square: int, moves: list):
        if self.isSquareAttacked(square):
            return
        if (self.whiteTurn and self.getCastleRight(CASTLE_SIDES["wKs"])) or (
                not self.whiteTurn and self.getCastleRight(CASTLE_SIDES["bKs"])):
            self.getKingSideCastle(square, moves)
        if (self.whiteTurn and self.getCastleRight(CASTLE_SIDES["wQs"])) or (
                not self.whiteTurn and self.getCastleRight(CASTLE_SIDES["bQs"])):
            self.getQueenSideCastle(square, moves)

    def getKingSideCastle(self, square: int, moves: list):
        if self.whiteTurn:
            piece = "wK"
        else:
            piece = "bK"
        if not self.getSqState(square >> 1) and not self.getSqState(square >> 2):
            if not self.isSquareAttacked(square >> 1) and not self.isSquareAttacked(square >> 2):
                moves.append(Move(square, square >> 2, self, movedPiece=piece, isCastle=True))

    def getQueenSideCastle(self, square: int, moves: list):
        if self.whiteTurn:
            piece = "wK"
        else:
            piece = "bK"
        if not self.getSqState(square << 1) and not self.getSqState(square << 2) and not self.getSqState(square << 3):
            if not self.isSquareAttacked(square << 1) and not self.isSquareAttacked(square << 2):
                moves.append(Move(square, square << 2, self, movedPiece=piece, isCastle=True))

    def getValidMoves(self):
        enpassantSq = self.enpassantSq
        currentCastlingRight = self.currentCastlingRight
        moves = self.getPossibleMoves()
        if self.whiteTurn:
            self.getCastleMoves(self.bbOfPieces["wK"], moves)
        else:
            self.getCastleMoves(self.bbOfPieces["bK"], moves)
        for i in range(len(moves) - 1, -1, -1):
            self.makeMove(moves[i])
            self.whiteTurn = not self.whiteTurn
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteTurn = not self.whiteTurn
            self.undoMove()
        if len(moves) == 0:
            if self.inCheck():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False
        if len(self.gameLog) >= 12:
            pos1 = self.gameLog[-4:]
            pos2 = self.gameLog[-8:-4]
            if pos1 == pos2:
                self.stalemate = True
            else:
                self.stalemate = False
        self.enpassantSq = enpassantSq
        self.currentCastlingRight = currentCastlingRight
        return moves

    def inCheck(self):
        if self.whiteTurn:
            self.isWhiteInCheck = self.isSquareAttacked(self.bbOfPieces["wK"])
            return self.isWhiteInCheck
        else:
            self.isBlackInCheck = self.isSquareAttacked(self.bbOfPieces["bK"])
            return self.isBlackInCheck

    def isSquareAttacked(self, square: int):
        if self.whiteTurn and (self.bbOfThreats["b"] & square):
            return True
        if not self.whiteTurn and (self.bbOfThreats["w"] & square):
            return True
        return False

    def setSqState(self, piece: str, piecePosition: int):
        if piece is not None:
            self.bbOfPieces[piece] |= piecePosition
            self.bbOfOccupiedSquares[piece[0]] |= piecePosition
            self.bbOfOccupiedSquares["a"] |= piecePosition

    def unsetSqState(self, piece: str, piecePosition: int):
        if piece is not None:
            newBit = ctypes.c_uint64(piecePosition)
            newBit.value = ~newBit.value
            self.bbOfPieces[piece] &= newBit.value
            self.bbOfOccupiedSquares[piece[0]] &= newBit.value
            self.bbOfOccupiedSquares["a"] &= newBit.value

    def getSqStateByPiece(self, piece: str, piecePosition: int):
        if piece is not None:
            return (self.bbOfPieces[piece] & piecePosition) != 0
        return False

    def getSqStateByColor(self, color: str, piecePosition: int):
        return (self.bbOfOccupiedSquares[color] & piecePosition) != 0

    def getSqState(self, piecePosition: int):
        return (self.bbOfOccupiedSquares["a"] & piecePosition) != 0

    def getPieceBySquare(self, piecePosition: int):
        if self.getSqState(piecePosition):
            for piece in COLORED_PIECES:
                if self.getSqStateByPiece(piece, piecePosition):
                    return piece
        return None

    def unsetCastleRight(self, right: int):
        newBit = ctypes.c_uint(right)
        newBit.value = ~newBit.value
        self.currentCastlingRight &= newBit.value

    def getCastleRight(self, right: int):
        return (self.currentCastlingRight & right) != 0


class Move:
    rowToNumber = {0: "8", 1: "7", 2: "6", 3: "5", 4: "4", 5: "3", 6: "2", 7: "1"}
    columnToLetter = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7: "h"}
    bbOfCastle = {"wKs": 0b0000000000000000000000000000000000000000000000000000000000000010,
                  "wQs": 0b0000000000000000000000000000000000000000000000000000000000100000,
                  "bKs": 0b0000001000000000000000000000000000000000000000000000000000000000,
                  "bQs": 0b0010000000000000000000000000000000000000000000000000000000000000}

    def __init__(self, startSq=0, endSq=0, gameState: GameState = None, movedPiece: str = None, isEnpassant=False,
                 isCastle=False, isFirst=False):
        if gameState is not None:
            self.startSquare = startSq
            self.endSquare = endSq
            self.startLoc = getPower(self.startSquare)
            self.endLoc = getPower(self.endSquare)
            self.movedPiece = movedPiece
            if self.movedPiece is None:
                self.movedPiece = gameState.getPieceBySquare(self.startSquare)
            self.isEnpassant = isEnpassant
            if not self.isEnpassant:
                self.capturedPiece = gameState.getPieceBySquare(self.endSquare)
            else:
                self.capturedPiece = "bp" if self.movedPiece == "wp" else "wp"
            self.moveID = self.startLoc * 100 + self.endLoc
            self.isPawnPromotion = (self.movedPiece == "wp" and not self.endSquare & bbOfCorrections["8"]) or (
                    self.movedPiece == "bp" and not self.endSquare & bbOfCorrections["1"])
            self.isCapture = False
            if self.capturedPiece is not None and self.movedPiece is not None:
                if self.capturedPiece[0] != self.movedPiece[0]:
                    self.isCapture = True
            self.isCastle = isCastle
            self.isFirst = isFirst
            self.estimatedScore = 0
            self.exactScore = 0
            self.goodScore = False
            self.isKiller = False

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def __repr__(self):
        return self.getMoveNotation()

    def __str__(self):
        return self.getMoveNotation()

    def getSquareNotation(self, square: int):
        location = getPower(square)
        return self.columnToLetter[location % 8] + self.rowToNumber[location // 8]

    def getMoveNotation(self):
        if self.isCastle:
            if (self.endSquare & self.bbOfCastle["wKs"]) or (self.endSquare & self.bbOfCastle["bKs"]):
                return "0-0"
            elif (self.endSquare & self.bbOfCastle["wQs"]) or (self.endSquare & self.bbOfCastle["bQs"]):
                return "0-0-0"
        if self.isPawnPromotion:
            return f"{self.getSquareNotation(self.endSquare)}Q"
        moveNotation = ""
        if self.movedPiece[1] != "p":
            moveNotation = self.movedPiece[1]
        moveNotation += self.getSquareNotation(self.startSquare)
        if self.isCapture:
            moveNotation += "x"
        else:
            moveNotation += "-"
        moveNotation += self.getSquareNotation(self.endSquare)
        return moveNotation
