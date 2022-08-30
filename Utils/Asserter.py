from Engine.Move import Move


class Asserter:
    @classmethod
    def assertionStartCheck(cls, gs, square=None, move=None):
        msg = ""
        if isinstance(move, Move):
            msg = f"move = {move.movedPiece}, {bin(move.startSquare)}, {bin(move.endSquare)}, {gs.isWhiteInCheck}, {gs.isBlackInCheck}"
            assert move.endSquare != 0, msg
        assert square != 0
        assert gs.bbOfPieces["wK"] != 0, msg
        assert gs.bbOfPieces["bK"] != 0, msg

    @classmethod
    def assertionEndCheck(cls, gs):
        assert gs.bbOfPieces["wK"] != 0
        assert gs.bbOfPieces["bK"] != 0
