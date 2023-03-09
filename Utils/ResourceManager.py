import json
from os.path import isfile, join
from os import getcwd
import pygame as pg
import sys
from UI.WindowSizeConsts import SQ_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, BOARD_SIZE
from Utils.MagicConsts import EMPTY_PIECES, COLORED_PIECES


class ResourceLoader:
    def __init__(self):
        self.IMAGES = {}
        self.SOUNDS = {}
        self.SETTINGS = {"sounds": True, "language": True}
        # required for correct convertation into .exe file
        try:
            self._WD = sys._MEIPASS  # working directory
        except AttributeError:
            self._WD = getcwd()

    def loadResources(self):
        """Loads all textures, sounds and SETTINGS file if it exists"""
        self._loadImages()
        self._loadSounds()
        self._loadSettings()

    def _loadImages(self):
        IMAGE_SIZES = self._generateImageSizes()
        for img, size in IMAGE_SIZES.items():
            self.IMAGES[img] = pg.transform.scale(pg.image.load(join(self._WD, f"images/{img}.png")), size)
        self.IMAGES["icon"] = pg.image.load(join(self._WD, "images/icon.png"))

    @staticmethod
    def _generateImageSizes():
        IMAGE_SIZES = {}
        SQ_SIZE_IMAGES = ["frame", "weSq", "beSq", "hourglass", "home_button_on", "home_button_off",
                          "radio_button_on", "radio_button_off", "restart_button_on", "restart_button_off",
                          "ru_flag", "en_flag"]
        SQUARED_PIECES = [f"{piece}Sq" for piece in COLORED_PIECES if piece != "wK" and piece != "bK"] + \
                         [f"{piece}SqH" for piece in COLORED_PIECES if piece != "wK" and piece != "bK"]
        for img in COLORED_PIECES + EMPTY_PIECES + SQUARED_PIECES + SQ_SIZE_IMAGES:
            IMAGE_SIZES[img] = (SQ_SIZE, SQ_SIZE)
        IMAGE_SIZES["settingsBG"] = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 9)
        IMAGE_SIZES["board"] = (BOARD_SIZE, BOARD_SIZE)
        IMAGE_SIZES["board_with_pieces1"] = (BOARD_SIZE // 2, BOARD_SIZE // 2)
        IMAGE_SIZES["board_with_pieces2"] = (BOARD_SIZE // 2, BOARD_SIZE // 2)
        IMAGE_SIZES["button"] = (SCREEN_WIDTH // 4, int(SQ_SIZE * 1.5))
        IMAGE_SIZES["header"] = (SCREEN_WIDTH // 4 * 3, SCREEN_HEIGHT // 5)
        IMAGE_SIZES["ddm_head"] = (BOARD_SIZE * 5 // 12, SQ_SIZE * 2 // 3)
        IMAGE_SIZES["ddm_body"] = (BOARD_SIZE * 5 // 12, SQ_SIZE * 2 // 3)
        IMAGE_SIZES["dialogWindow"] = (SCREEN_WIDTH // 3, SCREEN_HEIGHT // 4)
        IMAGE_SIZES["BG"] = (SCREEN_WIDTH, SCREEN_HEIGHT)
        IMAGE_SIZES["timer"] = (SQ_SIZE * 2, SQ_SIZE)
        return IMAGE_SIZES

    def _loadSounds(self):
        self.SOUNDS["move"] = pg.mixer.Sound(join(self._WD, "sounds/move.wav"))

    def _loadSettings(self):
        if not isfile("SETTINGS.json"):
            return
        with open("SETTINGS.json", "r", encoding="utf-8") as f:
            try:
                self.SETTINGS = json.load(f)
            except json.decoder.JSONDecodeError:
                self.SETTINGS = {"sounds": True, "language": True}
            if not self._settingsCheck():
                self.SETTINGS = {"sounds": True, "language": True}

    def _settingsCheck(self):
        if not isinstance(self.SETTINGS, dict):
            return False
        if len(self.SETTINGS) != 2:
            return False
        if not ("sounds" in self.SETTINGS and "language" in self.SETTINGS):
            return False
        if not (isinstance(self.SETTINGS["sounds"], bool) and isinstance(self.SETTINGS["language"], bool)):
            return False
        return True


class SettingsSaver:
    @classmethod
    def saveResources(cls, settings: dict):
        """Saves SETTINGS in a json file"""
        with open("SETTINGS.json", "w", encoding="utf-8") as f:
            json.dump(settings, f)
