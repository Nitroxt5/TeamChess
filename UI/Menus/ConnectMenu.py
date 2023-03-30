import pygame as pg
from Networking.Network import Network
from Networking.NetHelpers import checkIP
from UI.Menus.Menu import Menu
from UI.UIObjects import Label, InputBox, Button
from UI.WindowSizeConsts import FONT_SIZE, FPS, SCREEN_HEIGHT, SCREEN_WIDTH, SQ_SIZE


class ConnectMenu(Menu):
    def __init__(self, screen, resourceLoader, textContent):
        self._font = pg.font.SysFont("Helvetica", FONT_SIZE * 3, True, False)
        self._bigFont = pg.font.SysFont("Helvetica", FONT_SIZE * 7, True, False)
        self._textContent = textContent
        super().__init__(screen, resourceLoader, Label(self._textContent["Name"], (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 10), self._bigFont, shift=5))
        self._inputBox = InputBox((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), self._font)
        connectBtnPos, backBtnPos = self._generateBtnPositions()
        self._connect_btn = Button(self._RL.IMAGES["button"], connectBtnPos, self._textContent["Connect_btn"], self._font)
        self._back_btn = Button(self._RL.IMAGES["button"], backBtnPos, self._textContent["Back_btn"], self._font)
        self._err_lbl = Label("", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4), self._font)

    @staticmethod
    def _generateBtnPositions():
        connectBtnPos = (SCREEN_WIDTH // 4 * 3, SCREEN_HEIGHT - SQ_SIZE * 2)
        backBtnPos = (SCREEN_WIDTH // 4, SCREEN_HEIGHT - SQ_SIZE * 2)
        return connectBtnPos, backBtnPos

    def create(self, waitingMenu, gamePlayMenu, dialogWindowMenu):
        working = True
        clock = pg.time.Clock()
        while working:
            mousePos = pg.mouse.get_pos()
            clock.tick(FPS)
            self._drawMenu()
            self._changeColorOfUIObjects(mousePos, [self._connect_btn, self._back_btn])
            self._updateUIObjects([self._inputBox, self._connect_btn, self._back_btn, self._err_lbl])
            for e in pg.event.get():
                self._inputBox.handle_event(e)
                if e.type == pg.QUIT:
                    working = False
                elif e.type == pg.MOUSEBUTTONDOWN:
                    if e.button != 1:
                        continue
                    if self._back_btn.checkForInput(mousePos):
                        self._err_lbl = Label("", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4), self._font)
                        working = False
                    if self._connect_btn.checkForInput(mousePos):
                        self._handleConnectButton(waitingMenu, gamePlayMenu, dialogWindowMenu)
                        working = False
                    if self._inputBox.checkForInput(mousePos):
                        self._err_lbl = Label("", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 * 2), self._font)
            pg.display.flip()
        return False

    def _handleConnectButton(self, waitingMenu, gamePlayMenu, dialogWindowMenu):
        if not checkIP(self._inputBox.text):
            self._showError()
            return
        network = self._tryNetwork()
        if network is None:
            self._showError()
            return
        waitingMenu.create(network, gamePlayMenu, dialogWindowMenu, None)

    def _showError(self):
        self._err_lbl = Label(self._textContent["Error"], (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4), self._font)
        self._inputBox.clear()
        self._inputBox.deactivate()

    def _tryNetwork(self):
        try:
            return Network(self._inputBox.text)
        except (ConnectionRefusedError, ValueError, TimeoutError):
            return None
