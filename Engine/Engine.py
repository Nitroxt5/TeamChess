import ctypes
from TestDLL import getPower
from Generators.GSHasher import GSHasher
from Generators.MoveGen import MoveGenerator
from Generators.ThreatTables import ThreatTableGenerator
from Utils.Asserter import Asserter
from Utils.FENConverter import FENAndGSConverter
from Utils.MagicConsts import CASTLE_SQUARES, CASTLE_SIDES, ROWS, COLUMNS, COLORED_PIECES


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
        self.whiteTurn = True
        self.gameLog = []
        self.lastPieceMoved = "-"
        self.gameLogLen = 0
        self.checkmate = False
        self.stalemate = False
        self.enpassantSq = 0
        self.enpassantSqLog = []
        self.currentCastlingRight = 0b1111
        self.castleRightsLog = []
        self.reserve = {"w": {"Q": 0, "R": 0, "B": 0, "N": 0, "p": 0}, "b": {"Q": 0, "R": 0, "B": 0, "N": 0, "p": 0}}
        # self.reserve = {"w": {"Q": 16, "R": 16, "B": 16, "N": 16, "p": 16}, "b": {"Q": 16, "R": 16, "B": 16, "N": 16, "p": 16}}
        # FENAndGSConverter.FENtoGameState("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1", self)
        # print(self)
        self._hasher = GSHasher(self)
        self._threatTableGenerator = ThreatTableGenerator(self)
        self._moveGenerator = MoveGenerator(self)
        self.isWhiteCastled = False
        self.isBlackCastled = False
        self.isWhiteInCheck = False
        self.isBlackInCheck = False
        self.currentValidMovesCount = 0

    def __repr__(self):
        return FENAndGSConverter.gameStateToFEN(self)

    def makeMove(self, move, other=None):
        """Makes provided move. Switches turn. Updates hash. Rebuilds threat tables"""
        Asserter.assertionStartCheck(self, move=move)
        self._appendToGameStateLogs(move)
        if move.isCapture and isinstance(other, GameState):
            other._updateGameStateReserve(move.capturedPiece, 1)
        if move.isReserve:
            self._updateGameStateReserve(move.movedPiece, -1)
        else:
            self.unsetSqState(move.capturedPiece, move.endSquare)
            self.unsetSqState(move.movedPiece, move.startSquare)
        if move.isEnpassant:
            self._unsetEnpassantCapture(move)
        if move.isCastle:
            self._moveRookOnCastle(move)
        if not move.isPawnPromotion:
            self.setSqState(move.movedPiece, move.endSquare)
        else:
            self.setSqState(f"{move.movedPiece[0] + move.promotedTo}", move.endSquare)
            if isinstance(other, GameState):
                other._unsetPromotedPiece(move)
        self.whiteTurn = not self.whiteTurn
        self._generateEnpassantSquare(move)
        self._hasher.updateBoardHash(move)
        self._updateCastleRights(move)
        self._threatTableGenerator.createThreatTable()
        self.inCheck()
        Asserter.assertionEndCheck(self)

    def _appendToGameStateLogs(self, move):
        self._hasher.appendHashToLog()
        self.gameLog.append(move)
        self.lastPieceMoved = self.gameLog[-1].movedPiece[1]
        self.gameLogLen += 1
        self.enpassantSqLog.append(self.enpassantSq)
        self.castleRightsLog.append(self.currentCastlingRight)
        self._threatTableGenerator.appendThreatTableToLog()

    def _updateGameStateReserve(self, piece: str, amount: int):
        self.reserve[piece[0]][piece[1]] += amount
        self._hasher.updateReserveHash(piece, self.reserve[piece[0]][piece[1]] - amount)

    def _unsetEnpassantCapture(self, move):
        if self.whiteTurn:
            self.unsetSqState(move.capturedPiece, move.endSquare >> 8)
        else:
            self.unsetSqState(move.capturedPiece, move.endSquare << 8)

    def _moveRookOnCastle(self, move):
        color = self._getAllyColor()
        if move.endSquare & CASTLE_SQUARES[f"{color}Ks"]:
            self._moveKingSideRookOnCastle(move)
        elif move.endSquare & CASTLE_SQUARES[f"{color}Qs"]:
            self._moveQueenSideRookOnCastle(move)
        if self.whiteTurn:
            self.isWhiteCastled = True
        else:
            self.isBlackCastled = True

    def _getAllyColor(self):
        return "w" if self.whiteTurn else "b"

    def _moveKingSideRookOnCastle(self, move):
        self.unsetSqState(f"{move.movedPiece[0]}R", move.endSquare >> 1)
        self.setSqState(f"{move.movedPiece[0]}R", move.endSquare << 1)

    def _moveQueenSideRookOnCastle(self, move):
        self.unsetSqState(f"{move.movedPiece[0]}R", move.endSquare << 2)
        self.setSqState(f"{move.movedPiece[0]}R", move.endSquare >> 1)

    def _unsetPromotedPiece(self, move):
        self.unsetSqState(f"{move.movedPiece[0] + move.promotedTo}", move.promotedPiecePosition)
        self._hasher.switchBoardHash(getPower(move.promotedPiecePosition), move.movedPiece[0] + move.promotedTo)
        self._updateGameStateReserve(move.movedPiece, 1)

    def _generateEnpassantSquare(self, move):
        if move.movedPiece == "wp" and move.isFirst:
            self.enpassantSq = move.endSquare >> 8
        elif move.movedPiece == "bp" and move.isFirst:
            self.enpassantSq = move.startSquare >> 8
        else:
            self.enpassantSq = 0

    def undoMove(self):
        """Undoes last move. Switches turn. Undoes hash. Undoes threat tables"""
        Asserter.assertionStartCheck(self)
        if len(self.gameLog) == 0:
            return
        move = self._popFromLogs()
        self.whiteTurn = not self.whiteTurn
        if move.isReserve:
            self._updateGameStateReserve(move.movedPiece, 1)
        if move.isPawnPromotion:
            self.unsetSqState(f"{move.movedPiece[0] + move.promotedTo}", move.endSquare)
        else:
            self.unsetSqState(move.movedPiece, move.endSquare)
        if not move.isEnpassant:
            self.setSqState(move.capturedPiece, move.endSquare)
        else:
            self._setEnpassantCapture(move)
        if move.isCastle:
            self._undoRookOnCastle(move)
        if not move.isReserve:
            self.setSqState(move.movedPiece, move.startSquare)
        self.checkmate = False
        self.stalemate = False
        self.inCheck()
        Asserter.assertionEndCheck(self)

    def _popFromLogs(self):
        self._hasher.popHashFromLog()
        self.enpassantSq = self.enpassantSqLog.pop()
        self.currentCastlingRight = self.castleRightsLog.pop()
        self._threatTableGenerator.popThreatTableFromLog()
        move = self.gameLog.pop()
        if len(self.gameLog) == 0:
            self.lastPieceMoved = "-"
            self.gameLogLen = 0
        else:
            self.lastPieceMoved = self.gameLog[-1].movedPiece[1]
            self.gameLogLen -= 1
        return move

    def _setEnpassantCapture(self, move):
        if self.whiteTurn:
            self.setSqState(move.capturedPiece, move.endSquare >> 8)
        else:
            self.setSqState(move.capturedPiece, move.endSquare << 8)

    def _undoRookOnCastle(self, move):
        color = self._getAllyColor()
        if move.endSquare & CASTLE_SQUARES[f"{color}Ks"]:
            self._undoKingSideRookOnCastle(move)
        elif move.endSquare & CASTLE_SQUARES[f"{color}Qs"]:
            self._undoQueenSideRookOnCastle(move)
        if self.whiteTurn:
            self.isWhiteCastled = True
        else:
            self.isBlackCastled = True

    def _undoKingSideRookOnCastle(self, move):
        self.unsetSqState(f"{move.movedPiece[0]}R", move.endSquare << 1)
        self.setSqState(f"{move.movedPiece[0]}R", move.endSquare >> 1)

    def _undoQueenSideRookOnCastle(self, move):
        self.unsetSqState(f"{move.movedPiece[0]}R", move.endSquare >> 1)
        self.setSqState(f"{move.movedPiece[0]}R", move.endSquare << 2)

    def _updateCastleRights(self, move):
        """Checks whether any king or rook were moved. Checks whether any rook was captured. Updates castle rights according to this"""
        Asserter.assertionStartCheck(self, move=move)
        if move.isReserve:
            return
        if move.movedPiece == "wK":
            self.unsetCastleRight(CASTLE_SIDES["wKs"])
            self.unsetCastleRight(CASTLE_SIDES["wQs"])
        if move.movedPiece == "bK":
            self.unsetCastleRight(CASTLE_SIDES["bKs"])
            self.unsetCastleRight(CASTLE_SIDES["bQs"])
        if move.movedPiece == "wR":
            self._unsetCastleRightOnRookAbsence(move.startSquare, "w")
        if move.movedPiece == "bR":
            self._unsetCastleRightOnRookAbsence(move.startSquare, "b")
        if move.capturedPiece == "wR":
            self._unsetCastleRightOnRookAbsence(move.endSquare, "w")
        if move.capturedPiece == "bR":
            self._unsetCastleRightOnRookAbsence(move.endSquare, "b")

    def _unsetCastleRightOnRookAbsence(self, square: int, color: str):
        row = "1" if color == "w" else "8"
        if square & COLUMNS["a"] & ROWS[row]:
            self.unsetCastleRight(CASTLE_SIDES[f"{color}Qs"])
        if square & COLUMNS["h"] & ROWS[row]:
            self.unsetCastleRight(CASTLE_SIDES[f"{color}Ks"])

    def inCheck(self):
        """Checks whether current player is in check. Updates both inCheck flags"""
        Asserter.assertionStartCheck(self)
        if self.whiteTurn:
            self.isWhiteInCheck = self.isSquareAttackedByOpponent(self.bbOfPieces["wK"])
            self.whiteTurn = not self.whiteTurn
            self.isBlackInCheck = self.isSquareAttackedByOpponent(self.bbOfPieces["bK"])
            self.whiteTurn = not self.whiteTurn
            return self.isWhiteInCheck
        else:
            self.isBlackInCheck = self.isSquareAttackedByOpponent(self.bbOfPieces["bK"])
            self.whiteTurn = not self.whiteTurn
            self.isWhiteInCheck = self.isSquareAttackedByOpponent(self.bbOfPieces["wK"])
            self.whiteTurn = not self.whiteTurn
            return self.isBlackInCheck

    def isSquareAttackedByOpponent(self, square: int):
        if self.whiteTurn and (self._threatTableGenerator.bbOfThreats["b"] & square):
            return True
        if not self.whiteTurn and (self._threatTableGenerator.bbOfThreats["w"] & square):
            return True
        return False

    def canBeRemoved(self, square: int, otherColor: str):
        """Checks whether a piece on a specified square can be removed for a promotion on the other board"""
        Asserter.assertionStartCheck(self, square=square)
        piece = self.getPieceBySquare(square)
        assert piece is not None
        if piece[0] != otherColor or piece[1] == "p" or piece[1] == "K":
            return False
        canBeRemoved = False
        whiteInCheck, blackInCheck = self.isWhiteInCheck, self.isBlackInCheck
        self.unsetSqState(piece, square)
        self._threatTableGenerator.createThreatTable()
        self.inCheck()
        self.setSqState(piece, square)
        if whiteInCheck == self.isWhiteInCheck and blackInCheck == self.isBlackInCheck:
            canBeRemoved = True
        self.isWhiteInCheck, self.isBlackInCheck = whiteInCheck, blackInCheck
        self._threatTableGenerator.createThreatTable()
        return canBeRemoved

    def getValidMoves(self):
        return self._moveGenerator.getValidMoves()

    def updatePawnPromotionMoves(self, moves: list, other):
        self._moveGenerator.updatePawnPromotionMoves(moves, other)

    def getUnavailableReserveMoves(self):
        return self._moveGenerator.getUnavailableReserveMoves()

    def setSqState(self, piece: str, piecePosition: int):
        """Sets specified piece into specified position. Does nothing if piece is None or square is already occupied with that exact piece"""
        if piece is None:
            return
        self.bbOfPieces[piece] |= piecePosition
        self.bbOfOccupiedSquares[piece[0]] |= piecePosition
        self.bbOfOccupiedSquares["a"] |= piecePosition

    def unsetSqState(self, piece: str, piecePosition: int):
        """Unsets specified piece from specified position. Does nothing if piece is None or square is already empty"""
        if piece is None:
            return
        newBit = ctypes.c_uint64(piecePosition)
        newBit.value = ~newBit.value
        self.bbOfPieces[piece] &= newBit.value
        self.bbOfOccupiedSquares[piece[0]] &= newBit.value
        self.bbOfOccupiedSquares["a"] &= newBit.value

    def getSqStateByPiece(self, piece: str, piecePosition: int):
        """Returns True or False whether specified piece occupies specified square or not. Does nothing if piece is None"""
        if piece is None:
            return False
        return (self.bbOfPieces[piece] & piecePosition) != 0

    def getSqStateByColor(self, color: str, piecePosition: int):
        """Returns True or False whether piece of specified color occupies specified square or not"""
        return (self.bbOfOccupiedSquares[color] & piecePosition) != 0

    def getSqState(self, piecePosition: int):
        """Returns True or False whether any piece occupies specified square or not"""
        return (self.bbOfOccupiedSquares["a"] & piecePosition) != 0

    def getPieceBySquare(self, piecePosition: int):
        """If specified square is occupied by any piece returns it. If square is empty returns None"""
        if self.getSqState(piecePosition):
            for piece in COLORED_PIECES:
                if self.getSqStateByPiece(piece, piecePosition):
                    return piece

    def unsetCastleRight(self, right: int):
        """Unsets specified castle right"""
        newBit = ctypes.c_uint(right)
        newBit.value = ~newBit.value
        self.currentCastlingRight &= newBit.value

    def setCastleRight(self, right: int):
        """Sets specified castle right"""
        self.currentCastlingRight |= right

    def getCastleRight(self, right: int):
        """Returns True or False whether castling to the specified side is available or not"""
        return (self.currentCastlingRight & right) != 0

    @property
    def boardHash(self):
        return self._hasher.boardHash
