from TeamChess.Utils.MagicConsts import PIECES, SQUARES, DIMENSION, RESERVE_PIECES
from TeamChess.UI.WindowSizeConsts import SQ_SIZE, MARGIN, MARGIN_LEFT, RESERVE_MARGIN, BOARD_SIZE
from TeamChess.UI.UIObjects import Image
from TestDLL import getPower
import pygame as pg


class Highlighter:
    def __init__(self, screen, gameStates: list, resourceLoader):
        self._screen = screen
        self._gameStates = gameStates
        self._RL = resourceLoader
        self._DARK_GREEN = pg.Surface((SQ_SIZE, SQ_SIZE))
        self._DARK_GREEN.fill((110, 90, 0))
        self._BLUE = pg.Surface((SQ_SIZE, SQ_SIZE))
        self._BLUE.set_alpha(100)
        self._BLUE.fill((0, 0, 255))
        self._YELLOW = pg.Surface((SQ_SIZE, SQ_SIZE))
        self._YELLOW.set_alpha(100)
        self._YELLOW.fill("yellow")

    def highlightSelectedSq(self, selectedSq: list):
        for i in range(2):
            if selectedSq[i] == ():
                continue
            color = "w" if selectedSq[i][1] == 8 else "b"
            isReserve = True if selectedSq[i][1] == -1 or selectedSq[i][1] == 8 else False
            square = SQUARES[selectedSq[i][1]][selectedSq[i][0]] if not isReserve else 0
            piece = self._gameStates[i].getPieceBySquare(square) if not isReserve else color + PIECES[selectedSq[i][0] + 1]
            if piece is None:
                continue
            highlightPosition = self._getSelectedSqHighlightPositionInPixelsByBoard(i, selectedSq[i], isReserve)
            highlighting = Image(self._DARK_GREEN, highlightPosition)
            highlighting.update(self._screen)

    def _getSelectedSqHighlightPositionInPixelsByBoard(self, boardNum: int, pos: tuple, isReserve: bool):
        if isReserve:
            return self._getSelectedSqReserveHighlightPositionInPixelsByBoard(boardNum, pos)
        else:
            return self._getBoardHighlightPositionInPixelsByBoard(boardNum, pos)

    def _getSelectedSqReserveHighlightPositionInPixelsByBoard(self, boardNum: int, pos: tuple):
        if boardNum == 0:
            return self._convertSelectedSqReserveSqToPixelsOnLeftBoard(pos)
        else:
            return self._convertSelectedSqReserveSqToPixelsOnRightBoard(pos)

    @staticmethod
    def _convertSelectedSqReserveSqToPixelsOnLeftBoard(pos: tuple):
        return MARGIN + RESERVE_MARGIN + pos[0] * SQ_SIZE + SQ_SIZE // 2, MARGIN + pos[1] * SQ_SIZE + SQ_SIZE // 2

    @staticmethod
    def _convertSelectedSqReserveSqToPixelsOnRightBoard(pos: tuple):
        newPos = (pos[0], Highlighter._invertCoord(pos[1]))
        return MARGIN_LEFT + RESERVE_MARGIN + newPos[0] * SQ_SIZE + SQ_SIZE // 2, MARGIN + newPos[1] * SQ_SIZE + SQ_SIZE // 2

    @staticmethod
    def _invertCoord(coord: int):
        return DIMENSION - 1 - coord

    def _getBoardHighlightPositionInPixelsByBoard(self, boardNum: int, pos: tuple):
        if boardNum == 0:
            return self._convertBoardSqToPixelsOnLeftBoard(pos)
        else:
            return self._convertBoardSqToPixelsOnRightBoard(pos)

    @staticmethod
    def _convertBoardSqToPixelsOnLeftBoard(pos: tuple):
        return MARGIN + pos[0] * SQ_SIZE + SQ_SIZE // 2, MARGIN + pos[1] * SQ_SIZE + SQ_SIZE // 2

    @staticmethod
    def _convertBoardSqToPixelsOnRightBoard(pos: tuple):
        newPos = Highlighter._invertPos(pos)
        return MARGIN_LEFT + newPos[0] * SQ_SIZE + SQ_SIZE // 2, MARGIN + newPos[1] * SQ_SIZE + SQ_SIZE // 2

    @staticmethod
    def _invertPos(pos: tuple):
        return Highlighter._invertCoord(pos[0]), Highlighter._invertCoord(pos[1])

    def highlightPossibleMoves(self, validMoves: list, selectedSq: list):
        for i in range(2):
            if selectedSq[i] == ():
                continue
            isReserve = True if selectedSq[i][1] == -1 or selectedSq[i][1] == 8 else False
            square = SQUARES[selectedSq[i][1]][selectedSq[i][0]] if not isReserve else 0
            color = "w" if selectedSq[i][1] == 8 else "b"
            piece = self._gameStates[i].getPieceBySquare(square) if not isReserve else color + PIECES[selectedSq[i][0] + 1]
            if not self._needHighlightPossibleMoves(i, isReserve, color, piece):
                continue
            endSquares = []
            for movesPart in validMoves[i]:
                for move in movesPart:
                    if move.startSquare == square and move.endSquare not in endSquares and move.movedPiece == piece:
                        endLoc = getPower(move.endSquare)
                        endSquares.append(move.endSquare)
                        highlightPosition = self._getBoardHighlightPositionInPixelsByBoard(i, (endLoc % 8, endLoc // 8))
                        highlighting = Image(self._YELLOW, highlightPosition)
                        highlighting.update(self._screen)

    def _needHighlightPossibleMoves(self, boardNum: int, isReserve: bool, color: str, piece: str):
        if piece is None:
            return False
        if isReserve and self._gameStates[boardNum].reserve[color][piece[1]] < 1:
            return False
        if piece[0] != ("w" if self._gameStates[boardNum].whiteTurn else "b"):
            return False
        return True

    def highlightLastMove(self, selectedSq: list):
        for i in range(2):
            if len(self._gameStates[i].gameLog) == 0 or not self._needHighlightLastMove(i, selectedSq[i]):
                continue
            lastMove = self._gameStates[i].gameLog[-1]
            startLoc = getPower(lastMove.startSquare)
            endLoc = getPower(lastMove.endSquare)
            if lastMove.isReserve:
                highlightStartPosition = self._getLastMoveReserveHighlightPositionInPixelsByBoard(i, lastMove)
            else:
                highlightStartPosition = self._getBoardHighlightPositionInPixelsByBoard(i, (startLoc % 8, startLoc // 8))
            highlightEndPosition = self._getBoardHighlightPositionInPixelsByBoard(i, (endLoc % 8, endLoc // 8))
            startHighlighting = Image(self._BLUE, highlightStartPosition)
            endHighlighting = Image(self._BLUE, highlightEndPosition)
            startHighlighting.update(self._screen)
            endHighlighting.update(self._screen)

    def _needHighlightLastMove(self, boardNum: int, pos: tuple):
        if pos == ():
            return True
        isReserve = True if pos[1] == -1 or pos[1] == 8 else False
        square = SQUARES[pos[1]][pos[0]] if not isReserve else 0
        color = "w" if pos[1] == 8 else "b"
        piece = self._gameStates[boardNum].getPieceBySquare(square) if not isReserve else color + PIECES[pos[0] + 1]
        if piece is None:
            return True
        if isReserve and self._clickedOnAbsentReservePieceOrEnemyReservePiece(boardNum, color, pos):
            return True
        return False

    def _clickedOnAbsentReservePieceOrEnemyReservePiece(self, boardNum: int, color: str, pos: tuple):
        turn = "w" if self._gameStates[boardNum].whiteTurn else "b"
        return self._gameStates[boardNum].reserve[color][PIECES[pos[0] + 1]] == 0 or color != turn

    def _getLastMoveReserveHighlightPositionInPixelsByBoard(self, boardNum: int, move):
        if boardNum == 0:
            return self._convertLastMoveReserveSqToPixelsOnLeftBoard(move)
        else:
            return self._convertLastMoveReserveSqToPixelsOnRightBoard(move)

    @staticmethod
    def _convertLastMoveReserveSqToPixelsOnLeftBoard(move):
        marginTop = MARGIN - SQ_SIZE // 2 if move.movedPiece[0] == "b" else MARGIN + BOARD_SIZE + SQ_SIZE // 2
        return MARGIN + RESERVE_MARGIN + RESERVE_PIECES[move.movedPiece[1]] * SQ_SIZE + SQ_SIZE // 2, marginTop

    @staticmethod
    def _convertLastMoveReserveSqToPixelsOnRightBoard(move):
        marginTop = MARGIN - SQ_SIZE // 2 if move.movedPiece[0] == "w" else MARGIN + BOARD_SIZE + SQ_SIZE // 2
        return MARGIN_LEFT + RESERVE_MARGIN + RESERVE_PIECES[move.movedPiece[1]] * SQ_SIZE + SQ_SIZE // 2, marginTop

    def highlightPossiblePromotions(self, possiblePromotions: dict, boardNum: int):
        if possiblePromotions == {} or boardNum == -1:
            return
        for pos in possiblePromotions.keys():
            highlightPosition = self._getBoardHighlightPositionInPixelsByBoard(1 - boardNum, pos)
            highlighting = Image(self._RL.IMAGES["frame"], highlightPosition)
            highlighting.update(self._screen)
