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

    @classmethod
    def gameStatesToFEN2(cls, gameState1, gameState2, activeBoard):
        """Converts game states into a FEN2 likewise gameStateToFEN. Returns an active board."""
        FEN = f"{cls._bitBoardToFEN(gameState1)} {cls._bitBoardToFEN(gameState2)} "
        FEN += f"{cls._reserveToFEN(gameState1)} {cls._reserveToFEN(gameState2)} "
        FEN += f"{cls._turnToFEN(gameState1).upper() if activeBoard == 0 else cls._turnToFEN(gameState2)} "
        FEN += f"{cls._castlingRightToFEN(gameState1)} {cls._castlingRightToFEN(gameState2)} "
        FEN += f"{cls._enpassantSquareToFEN(gameState1)} {cls._enpassantSquareToFEN(gameState2)} "
        FEN += f"{gameState1.lastPieceMoved} {gameState2.lastPieceMoved} "
        FEN += f"{gameState1.gameLogLen} {gameState2.gameLogLen}"
        return FEN

    @classmethod
    def _reserveToFEN(cls, gs):
        return "/".join(map(str, gs.reserve["w"].values())) + "/" + "/".join(map(str, gs.reserve["b"].values()))

    @classmethod
    def FEN2toGameStates(cls, FEN: str, gameState1, gameState2):
        """Transfers information from FEN2 into game states likewise FENtoGameState. Returns an active board."""
        FENParts = FEN.split(" ")
        errorMsg = "Given FEN string is incorrect"
        assert len(FENParts) == 13, errorMsg
        FENEnpassant1 = int(FENParts[7])
        FENEnpassant2 = int(FENParts[8])
        assert 0 <= FENEnpassant1 <= 64, errorMsg
        assert 0 <= FENEnpassant2 <= 64, errorMsg
        cls._FENtobbOfPieces(FENParts[0], gameState1)
        cls._FENtobbOfPieces(FENParts[1], gameState2)
        cls._generatebbOfOccupiedSquares(gameState1)
        cls._generatebbOfOccupiedSquares(gameState2)
        cls._FENtoReserve(FENParts[2], gameState1)
        cls._FENtoReserve(FENParts[3], gameState2)
        cls._FENtoCastleRight(FENParts[5], gameState1)
        cls._FENtoCastleRight(FENParts[6], gameState2)
        cls._FENtoEnpassantSquare(FENEnpassant1, gameState1)
        cls._FENtoEnpassantSquare(FENEnpassant2, gameState2)
        cls._FENtoLastPieceMoved(FENParts[9], gameState1)
        cls._FENtoLastPieceMoved(FENParts[10], gameState2)
        cls._FENtoGameLogLen(FENParts[11], gameState1)
        cls._FENtoGameLogLen(FENParts[12], gameState2)
        return cls._FENtoTurnWithUpperCase(FENParts[4], gameState1, gameState2)

    @classmethod
    def _FENtoReserve(cls, FENPart, gs):
        gs.reserve = {"w": {PIECES[i + 1]: int(FENPart.split("/")[:5][i]) for i in range(5)},
                      "b": {PIECES[i + 1]: int(FENPart.split("/")[5:][i]) for i in range(5)}}

    @classmethod
    def _FENtoTurnWithUpperCase(cls, FENPart, gs1, gs2):
        """Sets turn order. Returns an active board."""
        if FENPart == "W":
            gs1.whiteTurn = True
            gs2.whiteTurn = True
            return 0
        if FENPart == "B":
            gs1.whiteTurn = False
            gs2.whiteTurn = False
            return 0
        if FENPart == "w":
            gs1.whiteTurn = False
            gs2.whiteTurn = True
            return 1
        gs1.whiteTurn = True
        gs2.whiteTurn = False
        return 1

    @classmethod
    def _FENtoLastPieceMoved(cls, FENPart, gs):
        gs.lastPieceMoved = FENPart

    @classmethod
    def _FENtoGameLogLen(cls, FENPart, gs):
        gs.gameLogLen = int(FENPart)
