from TeamChess.Utils.MagicConsts import COLORED_PIECES, bbOfCorrections, POSSIBLE_PIECES_TO_PROMOTE, bbOfPawnStarts, CASTLE_SIDES, bbOfRows
from TestDLL import numSplit
from TeamChess.Engine.Move import Move
import ctypes


class MoveGenerator:
    def __init__(self, gameState):
        self._gameState = gameState
        self._moveFunc = {"p": self._getPawnMoves, "R": self._getVerticalAndHorizontalMoves, "N": self._getKnightMoves,
                          "B": self._getDiagonalMoves, "Q": self._getQueenMoves, "K": self._getKingMoves}

    def getValidMoves(self):
        """Generates all valid moves (checks for threats to kings)"""
        self._gameState.assertionStartCheck()
        moves = self._getPossibleMoves()
        self._getCastleMoves(self._gameState.bbOfPieces[f"{self._getAllyColor()}K"], moves)
        self._getReserveMoves(moves)
        for movesPart in moves:
            if len(movesPart) == 0:
                continue
            for i in range(len(movesPart) - 1, -1, -1):
                if not self._isValid(movesPart[i]):
                    movesPart.remove(movesPart[i])
        self._gameEndCheck(moves)
        self._drawOnRepeatCheck()
        self._gameState.assertionEndCheck()
        return moves

    def _getPossibleMoves(self):
        """Generates all possible moves (ignores their validity in terms of king safety)"""
        self._gameState.assertionStartCheck()
        moves = [[], [], []]
        for piece in COLORED_PIECES:
            if (piece[0] == "w" and self._gameState.whiteTurn) or (piece[0] == "b" and not self._gameState.whiteTurn):
                splitPositions = numSplit(self._gameState.bbOfPieces[piece])
                for position in splitPositions:
                    self._moveFunc[piece[1]](position, moves)
        self._gameState.assertionEndCheck()
        return moves

    def _getPawnMoves(self, square: int, moves: list):
        self._gameState.assertionStartCheck(square)
        if self._gameState.whiteTurn:
            self._getWhitePawnMoves(square, moves)
        if not self._gameState.whiteTurn:
            self._getBlackPawnMoves(square, moves)

    def _getWhitePawnMoves(self, square, moves):
        if not self._gameState.getSqState(square << 8):
            self._getWhitePawnForwardMoves(square, moves)
        if square & bbOfCorrections["a"]:
            self._getWhitePawnLeftCaptureMoves(square, moves)
        if square & bbOfCorrections["h"]:
            self._getWhitePawnRightCaptureMoves(square, moves)

    def _getWhitePawnForwardMoves(self, square, moves):
        move = Move(square, square << 8, self._gameState, movedPiece="wp")
        if move.isPawnPromotion:
            for piece in POSSIBLE_PIECES_TO_PROMOTE:
                moves[2].append(Move(square, square << 8, self._gameState, movedPiece="wp", promotedTo=piece))
        else:
            moves[0].append(move)
        if (square & bbOfPawnStarts["w"]) and not self._gameState.getSqState(square << 16):
            moves[0].append(Move(square, square << 16, self._gameState, movedPiece="wp", isFirst=True))

    def _getWhitePawnLeftCaptureMoves(self, square, moves):
        if self._gameState.getSqStateByColor("b", square << 9):
            move = Move(square, square << 9, self._gameState, movedPiece="wp")
            if move.isPawnPromotion:
                for piece in POSSIBLE_PIECES_TO_PROMOTE:
                    moves[2].append(Move(square, square << 9, self._gameState, movedPiece="wp", promotedTo=piece))
            else:
                moves[0].append(move)
        elif square << 9 == self._gameState.enpassantSq:
            moves[0].append(Move(square, square << 9, self._gameState, movedPiece="wp", isEnpassant=True))

    def _getWhitePawnRightCaptureMoves(self, square, moves):
        if self._gameState.getSqStateByColor("b", square << 7):
            move = Move(square, square << 7, self._gameState, movedPiece="wp")
            if move.isPawnPromotion:
                for piece in POSSIBLE_PIECES_TO_PROMOTE:
                    moves[2].append(Move(square, square << 7, self._gameState, movedPiece="wp", promotedTo=piece))
            else:
                moves[0].append(move)
        elif square << 7 == self._gameState.enpassantSq:
            moves[0].append(Move(square, square << 7, self._gameState, movedPiece="wp", isEnpassant=True))

    def _getBlackPawnMoves(self, square, moves):
        if not self._gameState.getSqState(square >> 8):
            self._getBlackPawnForwardMoves(square, moves)
        if square & bbOfCorrections["a"]:
            self._getBlackPawnLeftCaptureMoves(square, moves)
        if square & bbOfCorrections["h"]:
            self._getBlackPawnRightCaptureMoves(square, moves)

    def _getBlackPawnForwardMoves(self, square, moves):
        move = Move(square, square >> 8, self._gameState, movedPiece="bp")
        if move.isPawnPromotion:
            for piece in POSSIBLE_PIECES_TO_PROMOTE:
                moves[2].append(Move(square, square >> 8, self._gameState, movedPiece="bp", promotedTo=piece))
        else:
            moves[0].append(move)
        if (square & bbOfPawnStarts["b"]) and not self._gameState.getSqState(square >> 16):
            moves[0].append(Move(square, square >> 16, self._gameState, movedPiece="bp", isFirst=True))

    def _getBlackPawnLeftCaptureMoves(self, square, moves):
        if self._gameState.getSqStateByColor("w", square >> 7):
            move = Move(square, square >> 7, self._gameState, movedPiece="bp")
            if move.isPawnPromotion:
                for piece in POSSIBLE_PIECES_TO_PROMOTE:
                    moves[2].append(Move(square, square >> 7, self._gameState, movedPiece="bp", promotedTo=piece))
            else:
                moves[0].append(move)
        elif square >> 7 == self._gameState.enpassantSq:
            moves[0].append(Move(square, square >> 7, self._gameState, movedPiece="bp", isEnpassant=True))

    def _getBlackPawnRightCaptureMoves(self, square, moves):
        if self._gameState.getSqStateByColor("w", square >> 9):
            move = Move(square, square >> 9, self._gameState, movedPiece="bp")
            if move.isPawnPromotion:
                for piece in POSSIBLE_PIECES_TO_PROMOTE:
                    moves[2].append(Move(square, square >> 9, self._gameState, movedPiece="bp", promotedTo=piece))
            else:
                moves[0].append(move)
        elif square >> 9 == self._gameState.enpassantSq:
            moves[0].append(Move(square, square >> 9, self._gameState, movedPiece="bp", isEnpassant=True))

    def _getKnightMoves(self, square: int, moves: list):
        self._gameState.assertionStartCheck(square)
        piece = f"{self._getAllyColor()}N"
        if square & bbOfCorrections["h"] & bbOfCorrections["78"]:
            tempSquare = square << 15
            self._appendMoveIfPossible(square, tempSquare, piece, moves)
        if square & bbOfCorrections["a"] & bbOfCorrections["78"]:
            tempSquare = square << 17
            self._appendMoveIfPossible(square, tempSquare, piece, moves)
        if square & bbOfCorrections["gh"] & bbOfCorrections["8"]:
            tempSquare = square << 6
            self._appendMoveIfPossible(square, tempSquare, piece, moves)
        if square & bbOfCorrections["gh"] & bbOfCorrections["1"]:
            tempSquare = square >> 10
            self._appendMoveIfPossible(square, tempSquare, piece, moves)
        if square & bbOfCorrections["h"] & bbOfCorrections["12"]:
            tempSquare = square >> 17
            self._appendMoveIfPossible(square, tempSquare, piece, moves)
        if square & bbOfCorrections["a"] & bbOfCorrections["12"]:
            tempSquare = square >> 15
            self._appendMoveIfPossible(square, tempSquare, piece, moves)
        if square & bbOfCorrections["ab"] & bbOfCorrections["1"]:
            tempSquare = square >> 6
            self._appendMoveIfPossible(square, tempSquare, piece, moves)
        if square & bbOfCorrections["ab"] & bbOfCorrections["8"]:
            tempSquare = square << 10
            self._appendMoveIfPossible(square, tempSquare, piece, moves)

    def _getAllyColor(self):
        return "w" if self._gameState.whiteTurn else "b"

    def _appendMoveIfPossible(self, startSquare: int, endSquare: int, movedPiece: str, moves: list):
        if not self._gameState.getSqState(endSquare) or self._gameState.getSqStateByColor(self._getEnemyColor(), endSquare):
            moves[0].append(Move(startSquare, endSquare, self._gameState, movedPiece=movedPiece))

    def _getEnemyColor(self):
        return "b" if self._gameState.whiteTurn else "w"

    def _getKingMoves(self, square: int, moves: list):
        self._gameState.assertionStartCheck(square)
        piece = f"{self._getAllyColor()}K"
        if square & bbOfCorrections["8"]:
            tempSquare = square << 8
            self._appendMoveIfPossible(square, tempSquare, piece, moves)
        if square & bbOfCorrections["h"] & bbOfCorrections["8"]:
            tempSquare = square << 7
            self._appendMoveIfPossible(square, tempSquare, piece, moves)
        if square & bbOfCorrections["h"]:
            tempSquare = square >> 1
            self._appendMoveIfPossible(square, tempSquare, piece, moves)
        if square & bbOfCorrections["h"] & bbOfCorrections["1"]:
            tempSquare = square >> 9
            self._appendMoveIfPossible(square, tempSquare, piece, moves)
        if square & bbOfCorrections["1"]:
            tempSquare = square >> 8
            self._appendMoveIfPossible(square, tempSquare, piece, moves)
        if square & bbOfCorrections["a"] & bbOfCorrections["1"]:
            tempSquare = square >> 7
            self._appendMoveIfPossible(square, tempSquare, piece, moves)
        if square & bbOfCorrections["a"]:
            tempSquare = square << 1
            self._appendMoveIfPossible(square, tempSquare, piece, moves)
        if square & bbOfCorrections["a"] & bbOfCorrections["8"]:
            tempSquare = square << 9
            self._appendMoveIfPossible(square, tempSquare, piece, moves)
        self._gameState.assertionEndCheck()

    def _getVerticalAndHorizontalMoves(self, square: int, moves: list, piece="R"):
        self._gameState.assertionStartCheck(square)
        enemyColor = self._getEnemyColor()
        coloredPiece = f"{self._getAllyColor()}{piece}"
        tempSquare = square
        while tempSquare & bbOfCorrections["8"]:
            tempSquare <<= 8
            if not self._gameState.getSqState(tempSquare):
                moves[0].append(Move(square, tempSquare, self._gameState, movedPiece=coloredPiece))
            elif self._gameState.getSqStateByColor(enemyColor, tempSquare):
                moves[0].append(Move(square, tempSquare, self._gameState, movedPiece=coloredPiece))
                break
            else:
                break
        tempSquare = square
        while tempSquare & bbOfCorrections["1"]:
            tempSquare >>= 8
            if not self._gameState.getSqState(tempSquare):
                moves[0].append(Move(square, tempSquare, self._gameState, movedPiece=coloredPiece))
            elif self._gameState.getSqStateByColor(enemyColor, tempSquare):
                moves[0].append(Move(square, tempSquare, self._gameState, movedPiece=coloredPiece))
                break
            else:
                break
        tempSquare = square
        while tempSquare & bbOfCorrections["a"]:
            tempSquare <<= 1
            if not self._gameState.getSqState(tempSquare):
                moves[0].append(Move(square, tempSquare, self._gameState, movedPiece=coloredPiece))
            elif self._gameState.getSqStateByColor(enemyColor, tempSquare):
                moves[0].append(Move(square, tempSquare, self._gameState, movedPiece=coloredPiece))
                break
            else:
                break
        tempSquare = square
        while tempSquare & bbOfCorrections["h"]:
            tempSquare >>= 1
            if not self._gameState.getSqState(tempSquare):
                moves[0].append(Move(square, tempSquare, self._gameState, movedPiece=coloredPiece))
            elif self._gameState.getSqStateByColor(enemyColor, tempSquare):
                moves[0].append(Move(square, tempSquare, self._gameState, movedPiece=coloredPiece))
                break
            else:
                break

    def _getDiagonalMoves(self, square: int, moves: list, piece="B"):
        self._gameState.assertionStartCheck(square)
        enemyColor = self._getEnemyColor()
        coloredPiece = f"{self._getAllyColor()}{piece}"
        tempSquare = square
        while tempSquare & bbOfCorrections["h"] & bbOfCorrections["8"]:
            tempSquare <<= 7
            if not self._gameState.getSqState(tempSquare):
                moves[0].append(Move(square, tempSquare, self._gameState, movedPiece=coloredPiece))
            elif self._gameState.getSqStateByColor(enemyColor, tempSquare):
                moves[0].append(Move(square, tempSquare, self._gameState, movedPiece=coloredPiece))
                break
            else:
                break
        tempSquare = square
        while tempSquare & bbOfCorrections["a"] & bbOfCorrections["8"]:
            tempSquare <<= 9
            if not self._gameState.getSqState(tempSquare):
                moves[0].append(Move(square, tempSquare, self._gameState, movedPiece=coloredPiece))
            elif self._gameState.getSqStateByColor(enemyColor, tempSquare):
                moves[0].append(Move(square, tempSquare, self._gameState, movedPiece=coloredPiece))
                break
            else:
                break
        tempSquare = square
        while tempSquare & bbOfCorrections["h"] & bbOfCorrections["1"]:
            tempSquare >>= 9
            if not self._gameState.getSqState(tempSquare):
                moves[0].append(Move(square, tempSquare, self._gameState, movedPiece=coloredPiece))
            elif self._gameState.getSqStateByColor(enemyColor, tempSquare):
                moves[0].append(Move(square, tempSquare, self._gameState, movedPiece=coloredPiece))
                break
            else:
                break
        tempSquare = square
        while tempSquare & bbOfCorrections["a"] & bbOfCorrections["1"]:
            tempSquare >>= 7
            if not self._gameState.getSqState(tempSquare):
                moves[0].append(Move(square, tempSquare, self._gameState, movedPiece=coloredPiece))
            elif self._gameState.getSqStateByColor(enemyColor, tempSquare):
                moves[0].append(Move(square, tempSquare, self._gameState, movedPiece=coloredPiece))
                break
            else:
                break

    def _getQueenMoves(self, square: int, moves: list):
        self._getVerticalAndHorizontalMoves(square, moves, "Q")
        self._getDiagonalMoves(square, moves, "Q")

    def _getCastleMoves(self, square: int, moves: list):
        self._gameState.assertionStartCheck(square)
        if self._gameState.isSquareAttackedByOpponent(square):
            return
        if self._isCastleAvailableForWhite("wKs") or self._isCastleAvailableForBlack("bKs"):
            self._getKingSideCastle(square, moves)
        if self._isCastleAvailableForWhite("wQs") or self._isCastleAvailableForBlack("bQs"):
            self._getQueenSideCastle(square, moves)

    def _isCastleAvailableForWhite(self, castleSide: str):
        return self._gameState.whiteTurn and self._gameState.getCastleRight(CASTLE_SIDES[castleSide])

    def _isCastleAvailableForBlack(self, castleSide: str):
        return not self._gameState.whiteTurn and self._gameState.getCastleRight(CASTLE_SIDES[castleSide])

    def _getKingSideCastle(self, square: int, moves: list):
        if self._areKingSideSquaresEmpty(square) and not self._areKingSideSquaresUnderEnemyAttack(square):
            moves[0].append(Move(square, square >> 2, self._gameState, movedPiece=f"{self._getAllyColor()}K", isCastle=True))
        self._gameState.assertionEndCheck()

    def _areKingSideSquaresEmpty(self, square):
        return not (self._gameState.getSqState(square >> 1) or self._gameState.getSqState(square >> 2))

    def _areKingSideSquaresUnderEnemyAttack(self, square):
        return self._gameState.isSquareAttackedByOpponent(square >> 1) or \
               self._gameState.isSquareAttackedByOpponent(square >> 2)

    def _getQueenSideCastle(self, square: int, moves: list):
        if self._areQueenSideSquaresEmpty(square) and not self._areQueenSideSquaresUnderEnemyAttack(square):
            moves[0].append(Move(square, square << 2, self._gameState, movedPiece=f"{self._getAllyColor()}K", isCastle=True))
        self._gameState.assertionEndCheck()

    def _areQueenSideSquaresEmpty(self, square):
        return not (self._gameState.getSqState(square << 1) or self._gameState.getSqState(square << 2) or
                    self._gameState.getSqState(square << 3))

    def _areQueenSideSquaresUnderEnemyAttack(self, square):
        return self._gameState.isSquareAttackedByOpponent(square << 1) or \
               self._gameState.isSquareAttackedByOpponent(square << 2)

    def _getReserveMoves(self, moves):
        self._gameState.assertionStartCheck()
        reserveMoves = []
        allyColor = self._getAllyColor()
        freeSquares = numSplit(~ctypes.c_uint64(self._gameState.bbOfOccupiedSquares["a"]).value)
        for sq in freeSquares:
            for piece, count in self._gameState.reserve[allyColor].items():
                if count < 1:
                    continue
                if not ((sq & bbOfRows["1"] or sq & bbOfRows["8"]) and piece == "p"):
                    reserveMoves.append(Move(0, sq, self._gameState, movedPiece=allyColor + piece, isReserve=True))
        moves[1] = reserveMoves
        self._gameState.assertionEndCheck()

    def _isValid(self, move):
        self._gameState.makeMove(move)
        self._gameState.whiteTurn = not self._gameState.whiteTurn
        isValid = not self._gameState.inCheck()
        self._gameState.whiteTurn = not self._gameState.whiteTurn
        self._gameState.undoMove()
        return isValid

    def updatePawnPromotionMoves(self, moves: list, other):
        """Updates pawn promotion moves. Checks if a piece to promote can be removed from the other board

        Mostly, this method should be called right after getValidMoves()
        """
        self._gameState.assertionStartCheck()
        badPieces = self._getPiecesUnavailableToPromoteTo(other)
        for i in range(len(moves[2]) - 1, -1, -1):
            if moves[2][i].promotedTo in badPieces:
                moves[2].remove(moves[2][i])
        self._gameState.assertionEndCheck()

    def _getPiecesUnavailableToPromoteTo(self, other):
        color = self._getAllyColor()
        badPieces = []
        for piece in POSSIBLE_PIECES_TO_PROMOTE:
            canBeRemoved = False
            splitPositions = numSplit(other.bbOfPieces[color + piece])
            for position in splitPositions:
                if other.canBeRemoved(position, color):
                    canBeRemoved = True
                    break
            if not canBeRemoved:
                badPieces.append(piece)
        return badPieces

    def _gameEndCheck(self, moves):
        if len(moves[0]) + len(moves[1]) + len(moves[2]) == 0:
            if self._gameState.inCheck():
                self._gameState.checkmate = True
            else:
                self._gameState.stalemate = True
        else:
            self._gameState.checkmate = False
            self._gameState.stalemate = False

    def _drawOnRepeatCheck(self):
        if len(self._gameState.gameLog) >= 12:
            pos1 = self._gameState.gameLog[-4:]
            pos2 = self._gameState.gameLog[-8:-4]
            if pos1 == pos2:
                self._gameState.stalemate = True

    def getUnavailableReserveMoves(self):
        """Generates and validates reserve moves which are not available due to absence of some pieces"""
        self._gameState.assertionStartCheck()
        reserveMoves = []
        allyColor = self._getAllyColor()
        freeSquares = numSplit(~ctypes.c_uint64(self._gameState.bbOfOccupiedSquares["a"]).value)
        for sq in freeSquares:
            for piece, count in self._gameState.reserve[allyColor].items():
                if count != 0:
                    continue
                if not ((sq & bbOfRows["1"] or sq & bbOfRows["8"]) and piece == "p"):
                    move = Move(0, sq, self._gameState, movedPiece=allyColor + piece, isReserve=True)
                    if self._isValid(move):
                        reserveMoves.append(move)
        self._gameState.assertionEndCheck()
        return reserveMoves
