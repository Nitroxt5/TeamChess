from TeamChess.Utils.MagicConsts import POSSIBLE_PIECES_TO_PROMOTE
from TestDLL import numSplit, getPower


class PossiblePromotionsGen:
    def __init__(self, gameStates: list):
        self._gameStates = gameStates

    def calculatePossiblePromotions(self, boardNum: int):
        """Creates a dict where:

        key = tuple which represents coordinates of a piece that can be removed from the other board;
        value = that exact piece
        """
        possiblePromotions = {}
        color = "w" if self._gameStates[boardNum].whiteTurn else "b"
        for piece in POSSIBLE_PIECES_TO_PROMOTE:
            splitPositions = numSplit(self._gameStates[1 - boardNum].bbOfPieces[color + piece])
            for position in splitPositions:
                if self._gameStates[1 - boardNum].canBeRemoved(position, color):
                    pos = getPower(position)
                    possiblePromotions[(pos % 8, pos // 8)] = color + piece
        return possiblePromotions
