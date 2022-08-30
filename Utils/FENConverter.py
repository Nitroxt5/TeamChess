from TestDLL import getPower
from Utils.MagicConsts import CASTLE_SIDES, COLORED_PIECES, COLORS, PIECES, SQUARES


class FENAndGSConverter:
    @classmethod
    def FENtoGameState(cls, FEN: str, gameState):
        """Turns a FEN string into a bitboard representation, used in program.

        FEN string must be correct, otherwise behaviour of this method is unpredictable.
        FEN string must not contain halfmove and fullmove counters.
        Enpassant square must be a number (a8 is 1; h8 is 8; a1 is 56; h1 is 64)
        If enpassant square is absent, it must be a 0
        """
        FENParts = FEN.split(" ")
        assert len(FENParts) == 4, "Given FEN string is incorrect"
        FENEnpassant = int(FENParts[3])
        assert 0 <= FENEnpassant <= 64, "Given FEN string is incorrect"
        cls._FENtobbOfPieces(FENParts[0], gameState)
        cls._generatebbOfOccupiedSquares(gameState)
        cls._FENtoTurn(FENParts[1], gameState)
        cls._FENtoCastleRight(FENParts[2], gameState)
        cls._FENtoEnpassantSquare(FENEnpassant, gameState)

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
                gs.setCastleRight(CASTLE_SIDES[FENRuleToStr[rule]])

    @classmethod
    def _FENtoEnpassantSquare(cls, FENEnpassant: int, gs):
        if FENEnpassant == 0:
            gs.enpassantSq = 0
        else:
            gs.enpassantSq = 1 << (64 - FENEnpassant)

    @classmethod
    def gameStateToFEN(cls, gameState):
        """Turns a bitboard representation, used in program, into a FEN string.

        FEN string will not contain halfmove and fullmove counters.
        Enpassant square will be a number (a8 is 1; h8 is 8; a1 is 56; h1 is 64)
        If enpassant square is absent, it will be a 0
        """
        FEN = cls._bitBoardToFEN(gameState)
        FEN += f" {cls._turnToFEN(gameState)} "
        FEN += cls._castlingRightToFEN(gameState)
        FEN += f" {cls._enpassantSquareToFEN(gameState)}"
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
        return "0" if gs.enpassantSq == 0 else f"{getPower(gs.enpassantSq)}"
