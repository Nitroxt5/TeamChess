from TeamChess.UI.WindowSizeConsts import FONT_SIZE, SCREEN_HEIGHT, SCREEN_WIDTH, SQ_SIZE, FPS
from TeamChess.UI.Menus.Menu import Menu
from TeamChess.UI.UIObjects import Button, Label, RadioLabel, RadioButton, Image
import pygame as pg


class SettingsMenu(Menu):
    def __init__(self, screen, resourceLoader, textContent):
        self._font = pg.font.SysFont("Helvetica", FONT_SIZE * 3, True, False)
        self._bigFont = pg.font.SysFont("Helvetica", FONT_SIZE * 7, True, False)
        self._textContent = textContent
        menuName_lbl = Label(self._textContent["Name"], (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 10), self._bigFont, shift=5)
        super().__init__(screen, resourceLoader, menuName_lbl)

        backBtnPos, soundBtnPos, langBtnPos, soundLblPos, langLblPos, soundImgPos, langImgPos = self._generatePositionsInPixels()
        self._back_btn = Button(self._RL.IMAGES["button"], backBtnPos, self._textContent["Back_btn"], self._font)
        self._sound_btn = RadioButton(soundBtnPos, self._RL.IMAGES["radio_button_on"], self._RL.IMAGES["radio_button_off"], self._RL.SETTINGS["sounds"])
        self._lang_btn = RadioButton(langBtnPos, self._RL.IMAGES["en_flag"], self._RL.IMAGES["ru_flag"], self._RL.SETTINGS["language"])
        self._sound_lbl = RadioLabel(soundLblPos, self._textContent["Sound_btn"][0], self._textContent["Sound_btn"][1], self._font, self._RL.SETTINGS["sounds"])
        self._lang_lbl = RadioLabel(langLblPos, self._textContent["Lang_btn"], self._textContent["Lang_btn"], self._font, self._RL.SETTINGS["language"])
        self._lang_img = Image(self._RL.IMAGES["settingsBG"], langImgPos)
        self._sound_img = Image(self._RL.IMAGES["settingsBG"], soundImgPos)
        self._UIObjects = [self._lang_img, self._sound_img, self._back_btn, self._sound_btn, self._sound_lbl, self._lang_btn, self._lang_lbl]

    def _generatePositionsInPixels(self):
        return self._generateBtnPositionsInPixels() + self._generateLblPositionsInPixels() + self._generateImgPositionsInPixels()

    @staticmethod
    def _generateBtnPositionsInPixels():
        backBtnPos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - SQ_SIZE * 2)
        soundBtnPos = (SCREEN_WIDTH // 4 + SQ_SIZE, SCREEN_HEIGHT // 4 + SQ_SIZE // 2)
        langBtnPos = (SCREEN_WIDTH // 4 + SQ_SIZE, SCREEN_HEIGHT // 4 + int(SQ_SIZE * 2.5))
        return backBtnPos, soundBtnPos, langBtnPos

    @staticmethod
    def _generateLblPositionsInPixels():
        soundLblPos = (SCREEN_WIDTH // 4 + int(SQ_SIZE * 1.5), SCREEN_HEIGHT // 4)
        langLblPos = (SCREEN_WIDTH // 4 + int(SQ_SIZE * 1.5), SCREEN_HEIGHT // 4 + SQ_SIZE * 2)
        return soundLblPos, langLblPos

    @staticmethod
    def _generateImgPositionsInPixels():
        soundImgPos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 + SQ_SIZE // 2)
        langImgPos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 + int(SQ_SIZE * 2.5))
        return soundImgPos, langImgPos

    def create(self, dialogWindowMenu):
        working = True
        clock = pg.time.Clock()
        while working:
            mousePos = pg.mouse.get_pos()
            clock.tick(FPS)
            self._drawMenu()
            self._changeColorOfUIObjects(mousePos, [self._back_btn])
            self._updateUIObjects(self._UIObjects)
            for e in pg.event.get():
                if e.type == pg.QUIT:
                    working = False
                elif e.type == pg.MOUSEBUTTONDOWN:
                    if e.button != 1:
                        continue
                    if self._back_btn.checkForInput(mousePos):
                        working = False
                    if self._sound_btn.checkForInput(mousePos):
                        self._sound_btn.switch()
                        self._sound_lbl.switch()
                        self._RL.SETTINGS["sounds"] = self._sound_btn.state
                    if self._lang_btn.checkForInput(mousePos):
                        if dialogWindowMenu.create(self._textContent["DW"]):
                            working = False
                            self._RL.SETTINGS["language"] = not self._RL.SETTINGS["language"]
                            pg.event.post(pg.event.Event(pg.QUIT))
            pg.display.flip()
