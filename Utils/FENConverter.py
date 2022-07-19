from TeamChess.Utils.MagicConsts import CASTLE_SIDES, COLORED_PIECES, COLORS, PIECES, SQUARES
from TestDLL import getPower


class FENAndGSConverter:
    @staticmethod
    def FENtoGameState(FEN: str, gameState):
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
        FENAndGSConverter._FENtobbOfPieces(FENParts[0], gameState)
        FENAndGSConverter._generatebbOfOccupiedSquares(gameState)
        FENAndGSConverter._FENtoTurn(FENParts[1], gameState)
        FENAndGSConverter._FENtoCastleRight(FENParts[2], gameState)
        FENAndGSConverter._FENtoEnpassantSquare(FENEnpassant, gameState)

    @staticmethod
    def _FENtobbOfPieces(FENPart: str, gs):
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

    @staticmethod
    def _generatebbOfOccupiedSquares(gs):
        gs.bbOfOccupiedSquares = {"w": 0, "b": 0}
        for color in COLORS:
            for piece in PIECES:
                gs.bbOfOccupiedSquares[color] |= gs.bbOfPieces[f"{color}{piece}"]
        gs.bbOfOccupiedSquares["a"] = gs.bbOfOccupiedSquares["w"] | gs.bbOfOccupiedSquares["b"]

    @staticmethod
    def _FENtoTurn(FENPart, gs):
        gs.whiteTurn = True if FENPart == "w" else False

    @staticmethod
    def _FENtoCastleRight(FENPart: str, gs):
        FENRuleToStr = {"K": "wKs", "Q": "wQs", "k": "bKs", "q": "bQs"}
        gs.currentCastlingRight = 0
        if FENPart == "-":
            gs.currentCastlingRight = 0
        else:
            for rule in FENPart:
                gs.setCastleRight(CASTLE_SIDES[FENRuleToStr[rule]])

    @staticmethod
    def _FENtoEnpassantSquare(FENEnpassant: int, gs):
        if FENEnpassant == 0:
            gs.enpassantSq = 0
        else:
            gs.enpassantSq = 1 << (64 - FENEnpassant)

    @staticmethod
    def gameStateToFEN(gameState):
        """Turns a bitboard representation, used in program, into a FEN string.

        FEN string will not contain halfmove and fullmove counters.
        Enpassant square will be a number (a8 is 1; h8 is 8; a1 is 56; h1 is 64)
        If enpassant square is absent, it will be a 0
        """
        FEN = FENAndGSConverter._bitBoardToFEN(gameState)
        FEN += f" {FENAndGSConverter._turnToFEN(gameState)} "
        FEN += FENAndGSConverter._castlingRightToFEN(gameState)
        FEN += f" {FENAndGSConverter._enpassantSquareToFEN(gameState)}"
        return FEN

    @staticmethod
    def _bitBoardToFEN(gs):
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
                if emptySquaresCounter > 0:
                    FEN += str(emptySquaresCounter)
                    emptySquaresCounter = 0
                FEN += StrPieceToFEN[piece]
            if emptySquaresCounter > 0:
                FEN += str(emptySquaresCounter)
                emptySquaresCounter = 0
            if i != len(SQUARES) - 1:
                FEN += "/"
        return FEN

    @staticmethod
    def _turnToFEN(gs):
        return "w" if gs.whiteTurn else "b"

    @staticmethod
    def _castlingRightToFEN(gs):
        FEN = ""
        StrRuleToFEN = {"wKs": "K", "wQs": "Q", "bKs": "k", "bQs": "q"}
        if gs.currentCastlingRight == 0:
            FEN += "-"
        else:
            for strRule, FENRule in StrRuleToFEN.items():
                if gs.getCastleRight(CASTLE_SIDES[strRule]):
                    FEN += FENRule
        return FEN

    @staticmethod
    def _enpassantSquareToFEN(gs):
        return "0" if gs.enpassantSq == 0 else f"{getPower(gs.enpassantSq)}"
