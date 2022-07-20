import pygame as pg
from copy import deepcopy
from sys import exit as sys_exit
from TestDLL import numSplit, getPower
from AI.AIHandler import AIHandler
from Engine.Engine import GameState
from Engine.Move import Move
from Generators.PossiblePromotions import PossiblePromotionsGen
from UI.Highlighter import Highlighter
from UI.Menus.Menu import Menu
from UI.UIObjects import Label, Hourglass, Timer, Image, RadioButton, ImgDropDownMenu
from UI.WindowSizeConsts import FONT_SIZE, MARGIN, MARGIN_LEFT, RESERVE_MARGIN, SCREEN_HEIGHT, SCREEN_WIDTH, BOARD_SIZE, SQ_SIZE, FPS
from Utils.Logger import ConsoleLogger
from Utils.MagicConsts import COLORED_PIECES, DIM, RESERVE_PIECES, GAME_MODES, PIECES, SQUARES
from Utils.ResourceManager import SettingsSaver


class GamePlayMenu(Menu):
    def __init__(self, screen, resourceLoader, textContent):
        self._smallFont = pg.font.SysFont("Helvetica", FONT_SIZE, True, False)
        self._font = pg.font.SysFont("Helvetica", FONT_SIZE * 7 // 4, True, False)
        self._textContent = textContent
        super().__init__(screen, resourceLoader, Label("", (0, 0), self._font))
        self._gameStates = [GameState(), GameState()]
        self._validMoves = [self._gameStates[0].getValidMoves(), self._gameStates[1].getValidMoves()]

        self._backGround_img = Image(self._RL.IMAGES["BG"], (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        boardPositions = self._generateBoardPositionsInPixels()
        self._board_imgs = [Image(self._RL.IMAGES["board"], pos) for pos in boardPositions]
        self._player_lbls = []
        self._timers = []
        self._requiredPiece_ddms = []
        reqPiecePos = self._generateRequiredPiecesPositionsInPixels()
        colors = ("w", "b", "w", "b")
        for i in range(4):
            bodyImages = [self._RL.IMAGES[f"{colors[i]}{piece}Sq"] for piece in PIECES if piece != "K"]
            headImages = [self._RL.IMAGES[f"{colors[i]}{piece}SqH"] for piece in PIECES if piece != "K"]
            botPositioning = True if i == 0 or i == 3 else False
            self._requiredPiece_ddms.append(ImgDropDownMenu(reqPiecePos[i], bodyImages, headImages, botPositioning, True))
        self._hourglass = Hourglass(0, self._RL.IMAGES["hourglass"])
        buttonPositions = self._generateButtonPositions()
        self._toMenu_btn = RadioButton(buttonPositions[0], self._RL.IMAGES["home_button_on"], self._RL.IMAGES["home_button_off"])
        self._restart_btn = RadioButton(buttonPositions[1], self._RL.IMAGES["restart_button_on"], self._RL.IMAGES["restart_button_off"])
        self._soundPlayed = False

        self._highlighter = Highlighter(self._screen, self._gameStates, self._RL)
        self._promotionsGen = PossiblePromotionsGen(self._gameStates)
        self._possiblePromotions = {}
        self._isPromoting = False
        self._potentialScores = [0, 0, 0, 0]
        self._requiredPieces = ["wQ", "bQ", "wQ", "bQ"]
        self._AI = AIHandler(self._gameStates, self._potentialScores, self._requiredPieces)
        self._selectedSq = [(), ()]
        self._clicks = [[], []]
        self._moveMade = [False, False]
        self._activeBoard = 0
        self._gameOver = False

    @staticmethod
    def _generateBoardPositionsInPixels():
        xBoard1 = MARGIN + BOARD_SIZE // 2
        xBoard2 = MARGIN_LEFT + BOARD_SIZE // 2
        yBoard = MARGIN + BOARD_SIZE // 2
        return (xBoard1, yBoard), (xBoard2, yBoard)

    @staticmethod
    def _generateRequiredPiecesPositionsInPixels():
        xBoard1 = SCREEN_WIDTH // 2 - SQ_SIZE * 3 // 2
        xBoard2 = SCREEN_WIDTH // 2 + SQ_SIZE // 2
        yTop = SQ_SIZE
        yBot = SCREEN_HEIGHT - SQ_SIZE * 2
        return (xBoard1, yBot), (xBoard1, yTop), (xBoard2, yTop), (xBoard2, yBot)

    @staticmethod
    def _generateButtonPositions():
        xButton = SCREEN_WIDTH - SQ_SIZE
        yTop = SQ_SIZE
        yBot = int(SQ_SIZE * 2.5)
        return (xButton, yTop), (xButton, yBot)

    def _isPlayerTurn(self, difficulties: list):
        """Figures out who is to move: AI or player"""
        return difficulties[self._getCurrentPlayer()] == 1

    def create(self, dialogWindowMenu, difficulties: list, playerNames: list, gameMode: int):
        working = True
        self._gameOver = False
        clock = pg.time.Clock()
        playerNamesPositions = self._generateNamesPositionsInPixels()
        self._player_lbls = [Label(playerNames[i], playerNamesPositions[i], self._font, shift=2) for i in range(4)]
        timerPositions = self._generateTimerPositionsInPixels()
        self._timers = [Timer(timerPositions[i], GAME_MODES[gameMode][i], self._RL.IMAGES["timer"], self._font) for i in range(4)]
        for i in range(len(difficulties)):
            if difficulties[i] == 1:
                self._potentialScores[i] = 400
            if difficulties[i] != 1:
                self._requiredPiece_ddms[i].turnOff()
        self._timers[0].switch()
        while working:
            clock.tick(FPS)
            mousePos = pg.mouse.get_pos()
            self._changeColorOfUIObjects(mousePos, [self._toMenu_btn, self._restart_btn])
            self.drawGameState()
            for e in pg.event.get():
                if e.type == pg.KEYDOWN:
                    if e.key == pg.K_F4 and bool(e.mod & pg.KMOD_ALT):
                        SettingsSaver.saveResources(self._RL.SETTINGS)
                        pg.quit()
                        sys_exit()
                elif e.type == pg.QUIT:
                    self._AI.terminate()
                    ConsoleLogger.endgameOutput(self._gameStates, difficulties, self._AI)
                    self._setBoardsToDefault(difficulties)
                    self._gameOver = True
                    working = False
                elif e.type == pg.MOUSEBUTTONDOWN:
                    if e.button != 1:
                        continue
                    self._handleToMenuBtn(dialogWindowMenu, mousePos)
                    self._handleRestartBtn(dialogWindowMenu, mousePos, difficulties)
                    if not self._gameOver:
                        self._handleDDMs(mousePos)
                        boardNum, reserveBoardNum = self._getClickPlace(mousePos)
                        if self._activeBoard == boardNum:
                            column, row = self._getBoardSqByPixels(mousePos)
                            self._validateClick((column, row))
                            if self._playerTriedToMakeMove(difficulties):
                                move = self._configurateMove()
                                self._makeMoveIfValid(move, playerNames)
                                if not self._moveMade[boardNum]:
                                    self._resetFirstClick()
                        elif self._activeBoard == reserveBoardNum:
                            column, row = self._getReserveSqByPixels(mousePos)
                            self._validateClick((column, row))
                            if self._triedToMakeIllegalMove():
                                self._resetFirstClick()
                        else:
                            self._resetSelectAndClicks()
                        pg.display.flip()
            self._gameOverCheck()
            if self._gameOver:
                self._AI.terminate()
            if not self._gameOver and not self._isPlayerTurn(difficulties) and not self._AI.cameUpWithMove:
                player = self._getCurrentPlayer()
                self._AI.start(self._timers[player].value, difficulties[player], self._activeBoard, self._getPlayerName(playerNames))
            if self._AI.cameUpWithMove:
                player = self._getCurrentPlayer()
                self._requiredPiece_ddms[player].changeHead(RESERVE_PIECES[self._requiredPieces[player][1]] + 1)
                self._handleNonPromotionMove(self._AI.move)
                self._AI.cameUpWithMove = False
            for i in range(2):
                if self._moveMade[i]:
                    self._resetActiveBoardSelectAndClicks()
                    self._soundPlayed = False
                    self._moveMade[i] = False
            pg.display.flip()

    @staticmethod
    def _generateNamesPositionsInPixels():
        xBoard1 = MARGIN + BOARD_SIZE // 2
        xBoard2 = MARGIN_LEFT + BOARD_SIZE // 2
        yTop = MARGIN // 2
        yBot = SCREEN_HEIGHT - MARGIN // 2
        return (xBoard1, yBot), (xBoard1, yTop), (xBoard2, yTop), (xBoard2, yBot)

    @staticmethod
    def _generateTimerPositionsInPixels():
        xBoard1 = MARGIN // 2
        xBoard2 = SCREEN_WIDTH - MARGIN // 2
        yTop = (SCREEN_HEIGHT - BOARD_SIZE + SQ_SIZE) // 2
        yBot = (SCREEN_HEIGHT + BOARD_SIZE - SQ_SIZE) // 2
        return (xBoard1, yBot), (xBoard1, yTop), (xBoard2, yTop), (xBoard2, yBot)

    def drawGameState(self):
        self._drawBackGround()
        self._drawEndGameText()
        self._drawPlayerNames()
        self._drawBoards()
        self._drawRequiredPieces()
        if self._isPromoting:
            self._highlighter.highlightPossiblePromotions(self._possiblePromotions, self._activeBoard)
        else:
            self._highlighter.highlightLastMove(self._selectedSq)
            self._highlighter.highlightSelectedSq(self._selectedSq)
            self._highlighter.highlightPossibleMoves(self._validMoves, self._selectedSq)
        self._drawBoardPieces()
        self._drawReservePiecesWithCount()
        if not self._gameOver:
            self._drawHourglass()
        self._drawButtons()
        self._drawTimers()

    def _drawBackGround(self):
        self._updateUIObjects([self._backGround_img])

    def _drawEndGameText(self):
        if self._isWhiteWonOnLeftBoard() or self._isBlackWonOnRightBoard():
            self._drawTopText(self._textContent["T1"])
            return
        if self._gameStates[0].stalemate or self._gameStates[1].stalemate:
            self._drawTopText(self._textContent["D"])
            return
        if self._isBlackWonOnLeftBoard() or self._isWhiteWonOnRightBoard():
            self._drawTopText(self._textContent["T2"])
            return
        if self._timers[1].countdownEnd() or self._timers[2].countdownEnd():
            self._drawTopText(self._textContent["T1"])
            return
        if self._timers[0].countdownEnd() or self._timers[3].countdownEnd():
            self._drawTopText(self._textContent["T2"])

    def _drawTopText(self, text: str):
        topText_lbl = Label(text, (SCREEN_WIDTH // 2, FONT_SIZE), self._font)
        self._updateUIObjects([topText_lbl])

    def _isWhiteWonOnLeftBoard(self):
        return self._gameStates[0].checkmate and not self._gameStates[0].whiteTurn

    def _isBlackWonOnLeftBoard(self):
        return self._gameStates[0].checkmate and self._gameStates[0].whiteTurn

    def _isWhiteWonOnRightBoard(self):
        return self._gameStates[1].checkmate and not self._gameStates[1].whiteTurn

    def _isBlackWonOnRightBoard(self):
        return self._gameStates[1].checkmate and self._gameStates[1].whiteTurn

    def _drawPlayerNames(self):
        self._updateUIObjects(self._player_lbls)

    def _drawBoards(self):
        self._updateUIObjects(self._board_imgs)

    def _drawRequiredPieces(self):
        self._updateUIObjects(self._requiredPiece_ddms)

    def _drawBoardPieces(self):
        for i in range(2):
            for piece in COLORED_PIECES:
                splitPositions = numSplit(self._gameStates[i].bbOfPieces[piece])
                for position in splitPositions:
                    location = getPower(position)
                    positionInPixels = self._getPiecePositionInPixelsByBoard(i, location)
                    piece_img = Image(self._RL.IMAGES[piece], positionInPixels)
                    self._updateUIObjects([piece_img])

    def _getPiecePositionInPixelsByBoard(self, boardNum: int, location: int):
        if boardNum == 0:
            return self._convertSquareToPixelsOnLeftBoard((location % DIM, location // DIM))
        else:
            return self._convertSquareToPixelsOnRightBoard((location % DIM, location // DIM))

    @staticmethod
    def _convertSquareToPixelsOnLeftBoard(pos: tuple):
        return MARGIN + SQ_SIZE * pos[0] + SQ_SIZE // 2, MARGIN + SQ_SIZE * pos[1] + SQ_SIZE // 2

    @staticmethod
    def _convertSquareToPixelsOnRightBoard(pos: tuple):
        newPos = GamePlayMenu._invertPos(pos)
        return MARGIN_LEFT + SQ_SIZE * newPos[0] + SQ_SIZE // 2, MARGIN + SQ_SIZE * newPos[1] + SQ_SIZE // 2

    @staticmethod
    def _invertPos(pos: tuple):
        return GamePlayMenu._invertCoord(pos[0]), GamePlayMenu._invertCoord(pos[1])

    @staticmethod
    def _invertCoord(coord: int):
        return DIM - 1 - coord

    def _drawReservePiecesWithCount(self):
        for i in range(2):
            for piece in COLORED_PIECES:
                if piece[1] == "K":
                    continue
                imgPositionInPixels = self._getReservePiecePositionInPixelsByBoard(i, piece)
                if self._gameStates[i].reserve[piece[0]][piece[1]] > 0:
                    piece_img = Image(self._RL.IMAGES[piece], imgPositionInPixels)
                    lblPositionInPixels = self._getReservePieceCounterPosInPixelsByBoardAndImgPos(i, piece, imgPositionInPixels)
                    count_lbl = Label(f"{self._gameStates[i].reserve[piece[0]][piece[1]]}", lblPositionInPixels, self._smallFont, shift=1)
                    self._updateUIObjects([piece_img, count_lbl])
                else:
                    piece_img = Image(self._RL.IMAGES[f"e{piece[1]}"], imgPositionInPixels)
                    self._updateUIObjects([piece_img])

    def _getReservePiecePositionInPixelsByBoard(self, boardNum: int, piece: str):
        if boardNum == 0 and piece[0] == "w":
            return self._convertReserveSquareToPixelsAtBottomOfLeftBoard(piece[1])
        elif boardNum == 0 and piece[0] == "b":
            return self._convertReserveSquareToPixelsAtTopOfLeftBoard(piece[1])
        elif boardNum == 1 and piece[0] == "w":
            return self._convertReserveSquareToPixelsAtTopOfRightBoard(piece[1])
        return self._convertReserveSquareToPixelsAtBottomOfRightBoard(piece[1])

    @staticmethod
    def _convertReserveSquareToPixelsAtTopOfLeftBoard(piece: str):
        return MARGIN + RESERVE_MARGIN + SQ_SIZE * RESERVE_PIECES[piece] + SQ_SIZE // 2, MARGIN - SQ_SIZE // 2

    @staticmethod
    def _convertReserveSquareToPixelsAtBottomOfLeftBoard(piece: str):
        return MARGIN + RESERVE_MARGIN + SQ_SIZE * RESERVE_PIECES[piece] + SQ_SIZE // 2, MARGIN + BOARD_SIZE + SQ_SIZE // 2

    @staticmethod
    def _convertReserveSquareToPixelsAtTopOfRightBoard(piece: str):
        return MARGIN_LEFT + RESERVE_MARGIN + SQ_SIZE * RESERVE_PIECES[piece] + SQ_SIZE // 2, MARGIN - SQ_SIZE // 2

    @staticmethod
    def _convertReserveSquareToPixelsAtBottomOfRightBoard(piece: str):
        return MARGIN_LEFT + RESERVE_MARGIN + SQ_SIZE * RESERVE_PIECES[piece] + SQ_SIZE // 2, MARGIN + BOARD_SIZE + SQ_SIZE // 2

    def _getReservePieceCounterPosInPixelsByBoardAndImgPos(self, boardNum: int, piece: str, imgPos: tuple):
        if (piece[0] == "b" and boardNum == 0) or (piece[0] == "w" and boardNum == 1):
            return self._getReservePieceCounterPosInPixelsAtTop(imgPos)
        return self._getReservePieceCounterPosInPixelsAtBottom(imgPos)

    @staticmethod
    def _getReservePieceCounterPosInPixelsAtTop(pos: tuple):
        return pos[0], pos[1] - SQ_SIZE // 2 - 5

    @staticmethod
    def _getReservePieceCounterPosInPixelsAtBottom(pos: tuple):
        return pos[0], pos[1] + SQ_SIZE // 2 + 5

    def _drawHourglass(self):
        self._updateUIObjects([self._hourglass])

    def _drawButtons(self):
        self._updateUIObjects([self._toMenu_btn, self._restart_btn])

    def _drawTimers(self):
        self._updateUIObjects(self._timers)

    def _setBoardsToDefault(self, difficulties: list):
        self._gameStates = [GameState(), GameState()]
        self._validMoves = [self._gameStates[0].getValidMoves(), self._gameStates[1].getValidMoves()]
        self._activeBoard = 0
        self._gameOver = False
        self._resetSelectAndClicks()
        self._moveMade = [False, False]
        self._potentialScores = [0, 0, 0, 0]
        self._requiredPieces = ["wQ", "bQ", "wQ", "bQ"]
        self._possiblePromotions = {}
        self._isPromoting = False
        self._soundPlayed = False
        for i in range(len(difficulties)):
            if difficulties[i] == 1:
                self._potentialScores[i] = 400
        self._highlighter = Highlighter(self._screen, self._gameStates, self._RL)
        self._promotionsGen = PossiblePromotionsGen(self._gameStates)
        self._AI = AIHandler(self._gameStates, self._potentialScores, self._requiredPieces)
        self._hourglass = Hourglass(0, self._RL.IMAGES["hourglass"])
        for i in range(len(self._timers)):
            self._timers[i].reset()
            self._requiredPiece_ddms[i].hide()

    def _handleToMenuBtn(self, dialogWindowMenu, mousePos: tuple):
        if self._toMenu_btn.checkForInput(mousePos):
            self._timers[self._getCurrentPlayer()].switch()
            if dialogWindowMenu.create(self._textContent["DW1"], self):
                pg.event.post(pg.event.Event(pg.QUIT))
            self._timers[self._getCurrentPlayer()].switch()

    def _handleRestartBtn(self, dialogWindowMenu, mousePos: tuple, difficulties: list):
        if self._restart_btn.checkForInput(mousePos):
            self._timers[self._getCurrentPlayer()].switch()
            if dialogWindowMenu.create(self._textContent["DW2"], self):
                self._AI.terminate()
                ConsoleLogger.endgameOutput(self._gameStates, difficulties, self._AI)
                self._setBoardsToDefault(difficulties)
                self.drawGameState()
                self._timers[0].switch()
                pg.display.flip()
            self._timers[self._getCurrentPlayer()].switch()

    def _handleDDMs(self, mousePos: tuple):
        for i, ddm in enumerate(self._requiredPiece_ddms):
            if ddm.checkForInput(mousePos):
                ddm.switch()
            choice = ddm.checkForChoice(mousePos)
            if choice is not None:
                color = "w" if i == 0 or i == 2 else "b"
                self._requiredPieces[i] = color + PIECES[choice]

    def _getClickPlace(self, mousePos: tuple):
        boardNum = -1
        reserveBoardNum = -1
        if self._clickedOnLeftBoard(mousePos):
            boardNum = 0
        if self._clickedOnRightBoard(mousePos):
            boardNum = 1
        if self._clickedOnBottomLeftReserveField(mousePos) or self._clickedOnTopLeftReserveField(mousePos):
            reserveBoardNum = 0
        if self._clickedOnBottomRightReserveField(mousePos) or self._clickedOnTopRightReserveField(mousePos):
            reserveBoardNum = 1
        return boardNum, reserveBoardNum

    @staticmethod
    def _clickedOnLeftBoard(pos: tuple):
        leftBorder = MARGIN
        rightBorder = MARGIN + BOARD_SIZE
        topBorder = MARGIN
        botBorder = MARGIN + BOARD_SIZE
        return leftBorder < pos[0] < rightBorder and topBorder < pos[1] < botBorder

    @staticmethod
    def _clickedOnRightBoard(pos: tuple):
        leftBorder = MARGIN_LEFT
        rightBorder = MARGIN_LEFT + BOARD_SIZE
        topBorder = MARGIN
        botBorder = MARGIN + BOARD_SIZE
        return leftBorder < pos[0] < rightBorder and topBorder < pos[1] < botBorder

    @staticmethod
    def _clickedOnTopLeftReserveField(pos: tuple):
        leftBorder = MARGIN + RESERVE_MARGIN
        rightBorder = MARGIN + RESERVE_MARGIN + 5 * SQ_SIZE
        topBorder = MARGIN - SQ_SIZE
        botBorder = MARGIN
        return leftBorder < pos[0] < rightBorder and topBorder < pos[1] < botBorder

    @staticmethod
    def _clickedOnBottomLeftReserveField(pos: tuple):
        leftBorder = MARGIN + RESERVE_MARGIN
        rightBorder = MARGIN + RESERVE_MARGIN + 5 * SQ_SIZE
        topBorder = MARGIN + BOARD_SIZE
        botBorder = MARGIN + BOARD_SIZE + SQ_SIZE
        return leftBorder < pos[0] < rightBorder and topBorder < pos[1] < botBorder

    @staticmethod
    def _clickedOnTopRightReserveField(pos: tuple):
        leftBorder = MARGIN_LEFT + RESERVE_MARGIN
        rightBorder = MARGIN_LEFT + RESERVE_MARGIN + 5 * SQ_SIZE
        topBorder = MARGIN - SQ_SIZE
        botBorder = MARGIN
        return leftBorder < pos[0] < rightBorder and topBorder < pos[1] < botBorder

    @staticmethod
    def _clickedOnBottomRightReserveField(pos: tuple):
        leftBorder = MARGIN_LEFT + RESERVE_MARGIN
        rightBorder = MARGIN_LEFT + RESERVE_MARGIN + 5 * SQ_SIZE
        topBorder = MARGIN + BOARD_SIZE
        botBorder = MARGIN + BOARD_SIZE + SQ_SIZE
        return leftBorder < pos[0] < rightBorder and topBorder < pos[1] < botBorder

    def _getBoardSqByPixels(self, pos: tuple):
        if self._activeBoard == 0:
            return self._getBoardSqOnLeftBoardByPixels(pos)
        else:
            return self._getBoardSqOnRightBoardByPixels(pos)

    @staticmethod
    def _getBoardSqOnLeftBoardByPixels(pos: tuple):
        column = (pos[0] - MARGIN) // SQ_SIZE
        row = (pos[1] - MARGIN) // SQ_SIZE
        return column, row

    @staticmethod
    def _getBoardSqOnRightBoardByPixels(pos: tuple):
        column = (pos[0] - MARGIN_LEFT) // SQ_SIZE
        row = (pos[1] - MARGIN) // SQ_SIZE
        column, row = GamePlayMenu._invertPos((column, row))
        return column, row

    def _getReserveSqByPixels(self, pos: tuple):
        if self._activeBoard == 0:
            return self._getReserveSqOnLeftBoardByPixels(pos)
        else:
            return self._getReserveSqOnRightBoardByPixels(pos)

    @staticmethod
    def _getReserveSqOnLeftBoardByPixels(pos: tuple):
        column = (pos[0] - MARGIN - RESERVE_MARGIN) // SQ_SIZE
        row = (pos[1] - MARGIN) // SQ_SIZE
        return column, row

    @staticmethod
    def _getReserveSqOnRightBoardByPixels(pos: tuple):
        column = (pos[0] - MARGIN_LEFT - RESERVE_MARGIN) // SQ_SIZE
        row = (pos[1] - MARGIN) // SQ_SIZE
        row = GamePlayMenu._invertCoord(row)
        return column, row

    def _validateClick(self, pos: tuple):
        if self._clickedSameSqTwice(pos):
            self._resetActiveBoardSelectAndClicks()
        else:
            self._saveClick(pos)

    def _clickedSameSqTwice(self, pos):
        return self._selectedSq[self._activeBoard] == pos

    def _resetActiveBoardSelectAndClicks(self):
        self._selectedSq[self._activeBoard] = ()
        self._clicks[self._activeBoard] = []

    def _saveClick(self, pos):
        self._selectedSq[self._activeBoard] = pos
        self._clicks[self._activeBoard].append(deepcopy(self._selectedSq[self._activeBoard]))

    def _playerTriedToMakeMove(self, difficulties: list):
        return len(self._clicks[self._activeBoard]) == 2 and self._isPlayerTurn(difficulties)

    def _configurateMove(self):
        isReserve = False
        movedPiece = None
        color = "w" if self._clicks[self._activeBoard][0][1] == 8 else "b"
        if self._firstClickOnReserveField():
            startSq = 0
            isReserve = True
            movedPiece = color + PIECES[self._clicks[self._activeBoard][0][0] + 1]
        else:
            startSq = SQUARES[self._clicks[self._activeBoard][0][1]][self._clicks[self._activeBoard][0][0]]
        endSq = SQUARES[self._clicks[self._activeBoard][1][1]][self._clicks[self._activeBoard][1][0]]
        return Move(startSq, endSq, self._gameStates[self._activeBoard], movedPiece=movedPiece, isReserve=isReserve)

    def _firstClickOnReserveField(self):
        return self._clicks[self._activeBoard][0][1] == -1 or self._clicks[self._activeBoard][0][1] == 8

    def _makeMoveIfValid(self, move, playerNames: list):
        for movesPart in self._validMoves[self._activeBoard]:
            for validMove in movesPart:
                if self._isSimilarMove(move, validMove):
                    if move.isPawnPromotion:
                        self._handlePromotionMove(validMove, playerNames)
                    if not (validMove.isPawnPromotion and validMove.promotedTo is None):
                        self._handleNonPromotionMove(validMove)
                        break

    def _isSimilarMove(self, move, validMove):
        return move == validMove or self._isPossiblePromotionMove(move, validMove)

    def _isPossiblePromotionMove(self, move, validMove):
        return move.moveID == validMove.moveID and move.isPawnPromotion and len(self._validMoves[self._activeBoard][2]) > 0

    def _handlePromotionMove(self, validMove, playerNames: list):
        pos, piece = self._getPromotion(self._getPlayerName(playerNames))
        validMove.promotedTo = None if piece is None else piece[1]
        validMove.promotedPiecePosition = pos

    def _getPromotion(self, name: str):
        """Lets the player choose exact piece, he wants to promote into. Returns a bitboard of a position of a piece and that exact piece"""
        self._isPromoting = True
        self._possiblePromotions = self._promotionsGen.calculatePossiblePromotions(self._activeBoard)
        if self._possiblePromotions == {}:
            return 0, None
        working = True
        while working:
            self._gameOverCheck()
            if self._gameOver:
                pg.event.post(pg.event.Event(pg.QUIT))
            self.drawGameState()
            self._drawTopText(f"{name} {self._textContent['promText']}")
            for e in pg.event.get():
                if e.type == pg.QUIT:
                    self._isPromoting = False
                    return 0, None
                if e.type == pg.MOUSEBUTTONDOWN:
                    if e.button != 1:
                        continue
                    mousePos = pg.mouse.get_pos()
                    if self._activeBoard == 1 and self._clickedOnLeftBoard(mousePos):
                        column, row = self._getBoardSqOnLeftBoardByPixels(mousePos)
                        if (column, row) in self._possiblePromotions:
                            self._isPromoting = False
                            return SQUARES[row][column], self._possiblePromotions[(column, row)]
                    if self._activeBoard == 0 and self._clickedOnRightBoard(mousePos):
                        column, row = self._getBoardSqOnRightBoardByPixels(mousePos)
                        if (column, row) in self._possiblePromotions:
                            self._isPromoting = False
                            return SQUARES[row][column], self._possiblePromotions[(column, row)]
            pg.display.flip()

    def _handleNonPromotionMove(self, move):
        self._timers[self._getCurrentPlayer()].switch()
        self._gameStates[self._activeBoard].makeMove(move, self._gameStates[1 - self._activeBoard])
        for i in range(2):
            self._validMoves[i] = self._gameStates[i].getValidMoves()
            self._gameStates[i].updatePawnPromotionMoves(self._validMoves[i], self._gameStates[1 - i])
        self._moveMade[self._activeBoard] = True
        self._activeBoard = 1 - self._activeBoard
        self._gameOverCheck()
        if not self._gameOver:
            self._timers[self._getCurrentPlayer()].switch()
        self.drawGameState()
        self._hourglass = Hourglass(self._getCurrentPlayer(), self._RL.IMAGES["hourglass"])
        self._playSoundIfAllowed()

    def _triedToMakeIllegalMove(self):
        return not self._moveMade[self._activeBoard] and len(self._clicks[self._activeBoard]) == 2

    def _resetFirstClick(self):
        self._clicks[self._activeBoard] = [deepcopy(self._selectedSq[self._activeBoard])]

    def _resetSelectAndClicks(self):
        self._selectedSq = [(), ()]
        self._clicks = [[], []]

    def _playSoundIfAllowed(self):
        if not self._soundPlayed and self._RL.SETTINGS["sounds"]:
            self._RL.SOUNDS["move"].play()
            self._soundPlayed = True

    def _getCurrentPlayer(self):
        """Gets number of a player who is now to move"""
        if self._gameStates[self._activeBoard].whiteTurn:
            return self._activeBoard * 2
        return self._activeBoard * 2 + 1

    def _getPlayerName(self, playerNames: list):
        """Gets name of a player who is now to move"""
        return playerNames[self._getCurrentPlayer()]

    def _gameOverCheck(self):
        if self._gameStates[0].checkmate or self._gameStates[1].checkmate:
            self._gameOver = True
        if self._gameStates[0].stalemate or self._gameStates[1].stalemate:
            self._gameOver = True
        for timer in self._timers:
            if timer.countdownEnd():
                self._gameOver = True
        # if len(self._gameStates[1].gameLog) == 30:
        #     self._gameOver = True
        # if len(self._gameStates[0].gameLog) == 1:
        #     self._gameOver = True
