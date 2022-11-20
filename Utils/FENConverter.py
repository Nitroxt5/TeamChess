from Engine.Move import Move
from Generators.GSHasher import GSHasher
from Generators.MoveGen import MoveGenerator
from Generators.ThreatTables import ThreatTableGenerator
from Utils.MagicConsts import CASTLE_SIDES, COLORED_PIECES, COLORS, PIECES, SQUARES, COLUMNS, ROWS


class FENAndGSConverter:
    @classmethod
    def FENtoGameState(cls, FEN: str, gameState):
        """Turns a FEN string into a bitboard representation, used in program.

        FEN string must be correct, otherwise behaviour of this method is unpredictable.
        """
        FENParts = FEN.split(" ")
        assert len(FENParts) == 6, "Given FEN string is incorrect"
        cls._FENtobbOfPieces(FENParts[0], gameState)
        cls._generatebbOfOccupiedSquares(gameState)
        cls._FENtoTurn(FENParts[1], gameState)
        cls._FENtoCastleRight(FENParts[2], gameState)
        cls._FENtoEnpassantSquare(FENParts[3], gameState)
        gameState.gameLogLen = (int(FENParts[5]) - 1) * 2
        if not gameState.whiteTurn:
            gameState.gameLogLen += 1
        gameState.hasher = GSHasher(gameState)
        gameState.threatTableGenerator = ThreatTableGenerator(gameState)
        gameState.moveGenerator = MoveGenerator(gameState)

    @classmethod
    def _FENtobbOfPieces(cls, FENPart: str, gs):
        FENPieceToStr = {"K": "wK", "Q": "wQ", "R": "wR", "B": "wB", "N": "wN", "P": "wp",
                         "k": "bK", "q": "bQ", "r": "bR", "b": "bB", "n": "bN", "p": "bp"}
        FENPart = "".join(FENPart.split("/"))
        for piece in COLORED_PIECES:
            gs.bbOfPieces[piece] = 0
        i = 0
        for letter in FENPart:
            if letter.isdigit():
                i += int(letter)
                continue
            gs.bbOfPieces[FENPieceToStr[letter]] ^= 1 << (63 - i)
            i += 1

    @classmethod
    def _generatebbOfOccupiedSquares(cls, gs):
        gs.bbOfOccupiedSquares = {"w": 0, "b": 0}
        for color in COLORS:
            for piece in PIECES:
                gs.bbOfOccupiedSquares[color] |= gs.bbOfPieces[f"{color}{piece}"]
        gs.bbOfOccupiedSquares["a"] = gs.bbOfOccupiedSquares["w"] | gs.bbOfOccupiedSquares["b"]

    @classmethod
    def _FENtoTurn(cls, FENPart, gs):
        gs.whiteTurn = True if FENPart == "w" else False

    @classmethod
    def _FENtoCastleRight(cls, FENPart: str, gs):
        FENRuleToStr = {"K": "wKs", "Q": "wQs", "k": "bKs", "q": "bQs"}
        gs.currentCastlingRight = 0
        if FENPart == "-":
            gs.currentCastlingRight = 0
        else:
            for rule in FENPart:
                if rule == "a":
                    gs.isBlackInCheck = True
                    continue
                if rule == "A":
                    gs.isWhiteInCheck = True
                    continue
                gs.setCastleRight(CASTLE_SIDES[FENRuleToStr[rule]])

    @classmethod
    def _FENtoEnpassantSquare(cls, FENPart: str, gs):
        if FENPart == "-":
            gs.enpassantSq = 0
        else:
            gs.enpassantSq = COLUMNS[FENPart[0]] & ROWS[FENPart[1]]

    @classmethod
    def gameStateToFEN(cls, gameState):
        """Turns a bitboard representation, used in program, into a FEN string.
        Draw move counters is not important for swedish chess, so it sets to 0"""
        FEN = cls._bitBoardToFEN(gameState)
        FEN += f" {cls._turnToFEN(gameState)} "
        FEN += cls._castlingRightToFEN(gameState)
        FEN += f" {cls._enpassantSquareToFEN(gameState)} 0 {gameState.gameLogLen // 2 + 1}"
        return FEN

    @classmethod
    def _bitBoardToFEN(cls, gs):
        FEN = ""
        StrPieceToFEN = {"wK": "K", "wQ": "Q", "wR": "R", "wB": "B", "wN": "N", "wp": "P",
                         "bK": "k", "bQ": "q", "bR": "r", "bB": "b", "bN": "n", "bp": "p"}
        emptySquaresCounter = 0
        for i in range(len(SQUARES)):
            for sq in SQUARES[i]:
                piece = gs.getPieceBySquare(sq)
                if piece is None:
                    emptySquaresCounter += 1
                    continue
                FEN, emptySquaresCounter = cls._appendEmptySquaresNumberIfPositive(FEN, emptySquaresCounter)
                FEN += StrPieceToFEN[piece]
            FEN, emptySquaresCounter = cls._appendEmptySquaresNumberIfPositive(FEN, emptySquaresCounter)
            FEN = cls._appendSlashIfNotEnd(FEN, i)
        return FEN

    @classmethod
    def _appendEmptySquaresNumberIfPositive(cls, FEN: str, emptySquaresCounter: int):
        if emptySquaresCounter > 0:
            FEN += str(emptySquaresCounter)
            emptySquaresCounter = 0
        return FEN, emptySquaresCounter

    @classmethod
    def _appendSlashIfNotEnd(cls, FEN: str, pos: int):
        if pos != len(SQUARES) - 1:
            FEN += "/"
        return FEN

    @classmethod
    def _turnToFEN(cls, gs):
        return "w" if gs.whiteTurn else "b"

    @classmethod
    def _castlingRightToFEN(cls, gs):
        FEN = ""
        StrRuleToFEN = {"wKs": "K", "wQs": "Q", "bKs": "k", "bQs": "q"}
        if gs.currentCastlingRight == 0:
            FEN += "-"
        else:
            for strRule, FENRule in StrRuleToFEN.items():
                if gs.getCastleRight(CASTLE_SIDES[strRule]):
                    FEN += FENRule
        return FEN

    @classmethod
    def _enpassantSquareToFEN(cls, gs):
        return "-" if gs.enpassantSq == 0 else Move.getSquareNotation(gs.enpassantSq)
