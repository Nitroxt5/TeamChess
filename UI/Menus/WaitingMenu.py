import pygame as pg
from Networking.NetHelpers import GameParams
from Networking.Network import Network
from UI.Menus.Menu import Menu
from UI.UIObjects import Label, Button, Image
from UI.WindowSizeConsts import FONT_SIZE, FPS, SCREEN_HEIGHT, SCREEN_WIDTH, SQ_SIZE, BOARD_SIZE, MARGIN, MARGIN_LEFT


class WaitingMenu(Menu):
    def __init__(self, screen, resourceLoader, textContent):
        self._smallFont = pg.font.SysFont("Helvetica", FONT_SIZE * 7 // 4, True, False)
        self._font = pg.font.SysFont("Helvetica", FONT_SIZE * 3, True, False)
        self._bigFont = pg.font.SysFont("Helvetica", FONT_SIZE * 7, True, False)
        self._textContent = textContent
        super().__init__(screen, resourceLoader, Label(self._textContent["Name"], (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 10), self._bigFont, shift=5))
        self._gameParams = GameParams()
        self._playerChoice = []
        self._choice_btns = []

        board1ImgPos, board2ImgPos = self._generateImgPositionsInPixels()
        self._board1_img = Image(self._RL.IMAGES["board_with_pieces1"], board1ImgPos, (BOARD_SIZE // 2, BOARD_SIZE // 2))
        self._board2_img = Image(self._RL.IMAGES["board_with_pieces2"], board2ImgPos, (BOARD_SIZE // 2, BOARD_SIZE // 2))
        backBtnPos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - SQ_SIZE * 2)
        self._back_btn = Button(self._RL.IMAGES["button"], backBtnPos, self._textContent["Back_btn"], self._font)

    @staticmethod
    def _generateImgPositionsInPixels():
        xBoard1 = MARGIN + 3 * BOARD_SIZE // 4
        xBoard2 = MARGIN_LEFT + BOARD_SIZE // 4
        yBoard = MARGIN + (BOARD_SIZE + SQ_SIZE) // 2
        return (xBoard1, yBoard), (xBoard2, yBoard)

    def create(self, network: Network, gamePlayMenu, dialogWindowMenu, isHost: bool):
        code_lbl = Label(f"{self._textContent['serv_addr']}: {network.ip}", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4), self._font)
        self._gameParams = network.request("params")
        self._playerChoice = network.request("choice")
        self._configureChoiceButtons()
        working = True
        clock = pg.time.Clock()
        while working:
            tryRequest = True
            mousePos = pg.mouse.get_pos()
            clock.tick(FPS)
            self._drawMenu()
            self._updateUIObjects([code_lbl, self._back_btn, self._board1_img, self._board2_img] + self._choice_btns)
            self._changeColorOfUIObjects(mousePos, [self._back_btn] + self._choice_btns)
            for e in pg.event.get():
                if e.type == pg.QUIT:
                    working = False
                elif e.type == pg.MOUSEBUTTONDOWN:
                    if e.button != 1:
                        continue
                    if self._back_btn.checkForInput(mousePos):
                        network.send("quit")
                        tryRequest = False
                        working = False
                    for player, button in enumerate(self._choice_btns):
                        if button.checkForInput(mousePos):
                            network.send(player)
                            tryRequest = False
                            self._gameParams.playerNum = player
                            self._gameParams.playerNames[player] += f" ({self._textContent['you']})"
                            self._deactivateChoiceButtons()
            if tryRequest:
                if not self._handleMessages(network, gamePlayMenu, dialogWindowMenu, isHost):
                    break
            pg.display.flip()
        return False

    def _configureChoiceButtons(self):
        namesPositions = self._generateNamesPositionsInPixels()
        self._choice_btns = []
        for i, difficulty in enumerate(self._gameParams.difficulties):
            if difficulty != 1 or i in self._playerChoice:
                self._choice_btns.append(Label(self._gameParams.playerNames[i], namesPositions[i], self._smallFont))
            else:
                self._choice_btns.append(Button(self._RL.IMAGES["ddm_body"], namesPositions[i], self._gameParams.playerNames[i], self._smallFont))

    def _deactivateChoiceButtons(self):
        namesPositions = self._generateNamesPositionsInPixels()
        self._choice_btns = []
        for i, difficulty in enumerate(self._gameParams.difficulties):
            self._choice_btns.append(Label(self._gameParams.playerNames[i], namesPositions[i], self._smallFont))

    @staticmethod
    def _generateNamesPositionsInPixels():
        xBoard1 = MARGIN + 3 * BOARD_SIZE // 4
        xBoard2 = MARGIN_LEFT + BOARD_SIZE // 4
        yTop = MARGIN + BOARD_SIZE // 4
        yBot = SCREEN_HEIGHT - MARGIN - SQ_SIZE
        return (xBoard1, yBot), (xBoard1, yTop), (xBoard2, yTop), (xBoard2, yBot)

    def _handleMessages(self, network: Network, gamePlayMenu, dialogWindowMenu, isHost: bool):
        try:
            msg = network.request()
            if isinstance(msg, list):
                self._playerChoice = msg
                if self._gameParams.playerNum == -1:
                    self._configureChoiceButtons()
            if msg == "start":
                assert self._gameParams.playerNum != -1
                gamePlayMenu.create(network, dialogWindowMenu, self._gameParams, isHost)
                return False
            if msg == "quit":
                return False
        except (ConnectionResetError, ConnectionAbortedError):
            return False
        return True
