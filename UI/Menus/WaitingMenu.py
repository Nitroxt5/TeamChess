import pygame as pg
from threading import Thread, Barrier
from queue import Queue
from Networking.NetHelpers import GameParams
from Networking.Network import Network
from UI.Menus.Menu import Menu
from UI.UIObjects import Label, Button
from UI.WindowSizeConsts import FONT_SIZE, FPS, SCREEN_HEIGHT, SCREEN_WIDTH, SQ_SIZE


class WaitingMenu(Menu):
    def __init__(self, screen, resourceLoader, textContent):
        self._font = pg.font.SysFont("Helvetica", FONT_SIZE * 3, True, False)
        self._bigFont = pg.font.SysFont("Helvetica", FONT_SIZE * 7, True, False)
        self._textContent = textContent
        super().__init__(screen, resourceLoader, Label(self._textContent["Name"], (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 10), self._bigFont, shift=5))
        backBtnPos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - SQ_SIZE * 2)
        self._back_btn = Button(self._RL.IMAGES["button"], backBtnPos, self._textContent["Back_btn"], self._font)
        self._msgs = Queue()

    def create(self, network: Network, gamePlayMenu, dialogWindowMenu, barrier: [Barrier, None]):
        code_lbl = Label(network.ip, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), self._bigFont)
        working = True
        clock = pg.time.Clock()
        Thread(target=self._listenerFunc, args=(network,)).start()
        while working:
            mousePos = pg.mouse.get_pos()
            clock.tick(FPS)
            self._drawMenu()
            self._updateUIObjects([code_lbl, self._back_btn])
            self._changeColorOfUIObjects(mousePos, [self._back_btn])
            working = self._handleMessages(network, gamePlayMenu, dialogWindowMenu)
            for e in pg.event.get():
                if e.type == pg.QUIT:
                    working = False
                elif e.type == pg.MOUSEBUTTONDOWN:
                    if e.button != 1:
                        continue
                    if self._back_btn.checkForInput(mousePos):
                        if barrier is None:
                            network.close()
                        else:
                            barrier.abort()
                        working = False
            pg.display.flip()
        return False

    def _listenerFunc(self, network: Network):
        try:
            msg = network.recv()
        except (EOFError, ConnectionAbortedError):
            return
        self._msgs.put(msg)

    def _getFirstMsg(self):
        try:
            return self._msgs.queue[0]
        except IndexError:
            return

    def _handleMessages(self, network: Network, gamePlayMenu, dialogWindowMenu):
        msg = self._getFirstMsg()
        if isinstance(msg, GameParams):
            self._msgs.get()
            gamePlayMenu.create(network, dialogWindowMenu, msg.difficulties, msg.playerNames.copy(), msg.gameMode,
                                msg.playerNum)
            return False
        if msg == "quit":
            return False
        return True
