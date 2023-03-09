import pygame as pg
from threading import Event
from UI.Menus.Menu import Menu
from UI.UIObjects import Button, Label
from UI.WindowSizeConsts import FONT_SIZE, SCREEN_HEIGHT, SCREEN_WIDTH, FPS
from Utils.ResourceManager import SettingsSaver


class MainMenu(Menu):
    def __init__(self, screen, resourceLoader, textContent):
        self._font = pg.font.SysFont("Helvetica", FONT_SIZE * 3, True, False)
        self._bigFont = pg.font.SysFont("Helvetica", FONT_SIZE * 7, True, False)
        self._textContent = textContent
        menuName_lbl = Label("SwiChess", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 10), self._bigFont, shift=5)
        super().__init__(screen, resourceLoader, menuName_lbl)

        newGameBtnPos, connectBtnPos, settingsBtnPos, quitBtnPos = MainMenu._generateBtnPositionsInPixels()
        self._newGame_btn = Button(self._RL.IMAGES["button"], newGameBtnPos, self._textContent["NewGame_btn"], self._font)
        self._connect_btn = Button(self._RL.IMAGES["button"], connectBtnPos, self._textContent["Connect_btn"], self._font)
        self._settings_btn = Button(self._RL.IMAGES["button"], settingsBtnPos, self._textContent["Settings_btn"], self._font)
        self._quit_btn = Button(self._RL.IMAGES["button"], quitBtnPos, self._textContent["Quit_btn"], self._font)
        self._buttons = [self._newGame_btn, self._connect_btn, self._settings_btn, self._quit_btn]

        self._moveEvent = Event()

    @staticmethod
    def _generateBtnPositionsInPixels():
        return [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 6 * i) for i in range(2, 6)]

    def create(self, newGameMenu, connectMenu, settingsMenu, waitingMenu, gamePlayMenu, dialogWindowMenu):
        working = True
        clock = pg.time.Clock()
        while working:
            mousePos = pg.mouse.get_pos()
            clock.tick(FPS)
            self._drawMenu()
            self._changeColorOfUIObjects(mousePos, self._buttons)
            self._updateUIObjects(self._buttons)
            for e in pg.event.get():
                if e.type == pg.QUIT:
                    working = False
                elif e.type == pg.MOUSEBUTTONDOWN:
                    if e.button != 1:
                        continue
                    if self._newGame_btn.checkForInput(mousePos):
                        newGameMenu.create(waitingMenu, gamePlayMenu, dialogWindowMenu, self._moveEvent)
                    if self._connect_btn.checkForInput(mousePos):
                        connectMenu.create(waitingMenu, gamePlayMenu, dialogWindowMenu, self._moveEvent)
                    if self._settings_btn.checkForInput(mousePos):
                        settingsMenu.create(dialogWindowMenu)
                    if self._quit_btn.checkForInput(mousePos):
                        if dialogWindowMenu.create(self._textContent["DW"]):
                            working = False
            pg.display.flip()
        SettingsSaver.saveResources(self._RL.SETTINGS)
