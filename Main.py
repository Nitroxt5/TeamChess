from TeamChess.UI.WindowSizeConsts import SCREEN_WIDTH, SCREEN_HEIGHT
from TeamChess.Utils.ResourceManager import ResourceLoader
from TeamChess.UI.Menus.MainMenu import MainMenu
from TeamChess.UI.Menus.SettingsMenu import SettingsMenu
from TeamChess.UI.Menus.DialogWindow import DialogWindowMenu
from TeamChess.UI.Menus.NewGameMenu import NewGameMenu
from TeamChess.UI.Menus.GamePlayMenu import GamePlayMenu
import pygame as pg
from multiprocessing import freeze_support

if __name__ == "__main__":
    freeze_support()
    pg.init()
    RL = ResourceLoader()
    RL.loadResources()
    if RL.SETTINGS["language"]:
        from TeamChess.Localization.lang_en import *
    else:
        from TeamChess.Localization.lang_ru import *
    mainScreen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pg.display.set_caption("SwiChess")
    pg.display.set_icon(RL.IMAGES["icon"])
    DIALOG_WINDOW = DialogWindowMenu(mainScreen, RL)
    SETTINGS = SettingsMenu(mainScreen, RL, settingsMenu)
    NEW_GAME = NewGameMenu(mainScreen, RL, newGameMenu, playerNames)
    GAME_PLAY = GamePlayMenu(mainScreen, RL, gamePlayMenu)
    MAIN_MENU = MainMenu(mainScreen, RL, mainMenu)
    MAIN_MENU.create(NEW_GAME, SETTINGS, GAME_PLAY, DIALOG_WINDOW)
    pg.quit()
