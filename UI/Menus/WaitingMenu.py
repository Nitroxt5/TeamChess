import pygame as pg
from threading import Thread
from queue import Queue
from Networking.Network import Network
from UI.Menus.Menu import Menu
from UI.UIObjects import Label
from UI.WindowSizeConsts import FONT_SIZE, FPS, SCREEN_HEIGHT, SCREEN_WIDTH


class WaitingMenu(Menu):
    def __init__(self, screen, resourceLoader, textContent):
        self._bigFont = pg.font.SysFont("Helvetica", FONT_SIZE * 7, True, False)
        self._textContent = textContent
        super().__init__(screen, resourceLoader, Label(self._textContent["Name"], (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 10), self._bigFont, shift=5))
        self._msgs = Queue()

    def create(self, network: Network, gamePlayMenu, dialogWindowMenu):
        code_lbl = Label(network.ip, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), self._bigFont)
        working = True
        clock = pg.time.Clock()
        Thread(target=self._listenerFunc, args=(network,)).start()
        while working:
            # mousePos = pg.mouse.get_pos()
            clock.tick(FPS)
            self._drawMenu()
            self._updateUIObjects([code_lbl])
            for e in pg.event.get():
                if e.type == pg.QUIT:
                    working = False
            gameParams = self._getFirstMsg()
            if gameParams is not None:
                gamePlayMenu.create(network, dialogWindowMenu, gameParams["difficulties"], gameParams["playerNames"],
                                    gameParams["gameMode"], gameParams["playerNum"])
                working = False
            pg.display.flip()
        return False

    def _listenerFunc(self, network: Network):
        gameParams = network.recv()
        self._msgs.put(gameParams)

    def _getFirstMsg(self):
        try:
            return self._msgs.queue[0]
        except IndexError:
            return
