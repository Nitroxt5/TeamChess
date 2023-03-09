import pygame as pg
from multiprocessing import freeze_support
from UI.Menus.DialogWindow import DialogWindowMenu
from UI.Menus.GamePlayMenu import GamePlayMenu
from UI.Menus.MainMenu import MainMenu
from UI.Menus.NewGameMenu import NewGameMenu
from UI.Menus.SettingsMenu import SettingsMenu
from UI.Menus.ConnectMenu import ConnectMenu
from UI.Menus.WaitingMenu import WaitingMenu
from UI.WindowSizeConsts import SCREEN_WIDTH, SCREEN_HEIGHT
from Utils.ResourceManager import ResourceLoader

if __name__ == "__main__":
    freeze_support()
    pg.init()
    RL = ResourceLoader()
    RL.loadResources()
    if RL.SETTINGS["language"]:
        from Localization.lang_en import *
    else:
        from Localization.lang_ru import *
    mainScreen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pg.display.set_caption("SwiChess")
    pg.display.set_icon(RL.IMAGES["icon"])
    DIALOG_WINDOW = DialogWindowMenu(mainScreen, RL)
    SETTINGS = SettingsMenu(mainScreen, RL, settingsMenuContent)
    NEW_GAME = NewGameMenu(mainScreen, RL, newGameMenuContent, playerNames)
    GAME_PLAY = GamePlayMenu(mainScreen, RL, gamePlayMenuContent)
    CONNECT_MENU = ConnectMenu(mainScreen, RL, connectionMenuContent)
    WAITING_MENU = WaitingMenu(mainScreen, RL, waitingMenuContent)
    MAIN_MENU = MainMenu(mainScreen, RL, mainMenuContent)
    MAIN_MENU.create(NEW_GAME, CONNECT_MENU, SETTINGS, WAITING_MENU, GAME_PLAY, DIALOG_WINDOW)
    pg.quit()
