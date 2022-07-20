import pygame as pg
from UI.Menus.Menu import Menu
from UI.UIObjects import Label, DialogWindow
from UI.WindowSizeConsts import FONT_SIZE, FPS


class DialogWindowMenu(Menu):
    def __init__(self, screen, resourceLoader):
        self._font = pg.font.SysFont("Helvetica", FONT_SIZE * 2, True, False)
        super().__init__(screen, resourceLoader, Label("", (0, 0), self._font))

    def create(self, text: str, gamePlayMenu=None):
        """Creates dialog window"""
        working = True
        clock = pg.time.Clock()
        dW = DialogWindow(text, self._font, self._RL.IMAGES["dialogWindow"], self._RL.SETTINGS["language"])
        while working:
            mousePos = pg.mouse.get_pos()
            clock.tick(FPS)
            if gamePlayMenu is not None:
                gamePlayMenu.drawGameState()
            dW.update(self._screen)
            dW.changeColor(mousePos)
            for e in pg.event.get():
                if e.type == pg.QUIT:
                    working = False
                elif e.type == pg.MOUSEBUTTONDOWN:
                    if e.button != 1:
                        continue
                    if dW.checkYesForInput(mousePos):
                        return True
                    if dW.checkNoForInput(mousePos):
                        return False
            pg.display.flip()
        return False
