import pygame as pg
from threading import Thread, Event
from Networking.NetHelpers import getIP, GameParams
from Networking.Network import Network
from Networking.Server import Server
from UI.Menus.Menu import Menu
from UI.UIObjects import Label, Button, Image, DropDownMenu
from UI.WindowSizeConsts import FONT_SIZE, FPS, SCREEN_HEIGHT, SCREEN_WIDTH, SQ_SIZE, BOARD_SIZE


class NewGameMenu(Menu):
    def __init__(self, screen, resourceLoader, textContent, playerNames: list):
        self._smallFont = pg.font.SysFont("Helvetica", int(FONT_SIZE * 1.5), True, False)
        self._font = pg.font.SysFont("Helvetica", FONT_SIZE * 3, True, False)
        self._bigFont = pg.font.SysFont("Helvetica", FONT_SIZE * 7, True, False)
        self._textContent = textContent
        menuName_lbl = Label(self._textContent["Name"], (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 10), self._bigFont, shift=5)
        super().__init__(screen, resourceLoader, menuName_lbl)
        self._NAMES = playerNames.copy()
        self._names = self._NAMES.copy()

        backBtnPos, playBtnPos = self._generateBtnPositionsInPixels()
        self._back_btn = Button(self._RL.IMAGES["button"], backBtnPos, self._textContent["Back_btn"], self._font)
        self._play_btn = Button(self._RL.IMAGES["button"], playBtnPos, self._textContent["Play_btn"], self._font)
        board1ImgPos, board2ImgPos = self._generateImgPositionsInPixels()
        self._board1_img = Image(self._RL.IMAGES["board_with_pieces1"], board1ImgPos, (BOARD_SIZE // 2, BOARD_SIZE // 2))
        self._board2_img = Image(self._RL.IMAGES["board_with_pieces2"], board2ImgPos, (BOARD_SIZE // 2, BOARD_SIZE // 2))
        gameModeDDMPos, ddm1pos, ddm2pos, ddm3pos, ddm4pos = self._generateDDMPositionsInPixels()
        positions = (ddm1pos, ddm2pos, ddm3pos, ddm4pos)
        self._player_ddms = [DropDownMenu(positions[i], self._textContent[f"DDM{i + 1}"], self._smallFont,
                                          self._RL.IMAGES["ddm_head"], self._RL.IMAGES["ddm_body"]) for i in range(4)]
        self._gameMode_ddm = DropDownMenu(gameModeDDMPos, self._textContent["DDM5"], self._smallFont,
                                          self._RL.IMAGES["ddm_head"], self._RL.IMAGES["ddm_body"])
        gameModeLblPos = (SCREEN_WIDTH * 3 // 4, SCREEN_HEIGHT // 2 - self._gameMode_ddm.height)
        self._gameMode_lbl = Label(self._textContent["gameMode"], gameModeLblPos, self._smallFont, shift=2)
        self._UIObjects = [self._board1_img, self._board2_img, self._back_btn, self._play_btn, self._gameMode_ddm,
                           self._gameMode_lbl] + self._player_ddms

        self._difficulties = [1, 1, 1, 1]  # 1 = player, 2 = EasyAI, 3 = NormalAI, 4 = HardAI
        self._currentGameMode = 0

    @staticmethod
    def _generateBtnPositionsInPixels():
        backBtnPos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - SQ_SIZE * 2)
        playBtnPos = (SCREEN_WIDTH * 4 // 5, SCREEN_HEIGHT - SQ_SIZE * 2)
        return backBtnPos, playBtnPos

    @staticmethod
    def _generateImgPositionsInPixels():
        xBoard1 = SCREEN_WIDTH // 4
        xBoard2 = SCREEN_WIDTH // 4 + BOARD_SIZE // 2 + SQ_SIZE
        yBoard = SCREEN_HEIGHT // 3 + SQ_SIZE
        board1ImgPos = (xBoard1, yBoard)
        board2ImgPos = (xBoard2, yBoard)
        return board1ImgPos, board2ImgPos

    @staticmethod
    def _generateDDMPositionsInPixels():
        xBoard1 = SCREEN_WIDTH // 4
        xBoard2 = SCREEN_WIDTH // 4 + BOARD_SIZE // 2 + SQ_SIZE
        yBoard = SCREEN_HEIGHT // 3 + SQ_SIZE
        gameModeDDMPos = (SCREEN_WIDTH * 3 // 4, SCREEN_HEIGHT // 2)
        ddm1pos = (xBoard1, yBoard + BOARD_SIZE // 4 + SQ_SIZE // 2)
        ddm2pos = (xBoard1, yBoard - BOARD_SIZE // 4 - SQ_SIZE // 2)
        ddm3pos = (xBoard2, yBoard - BOARD_SIZE // 4 - SQ_SIZE // 2)
        ddm4pos = (xBoard2, yBoard + BOARD_SIZE // 4 + SQ_SIZE // 2)
        return gameModeDDMPos, ddm1pos, ddm2pos, ddm3pos, ddm4pos

    def create(self, waitingMenu, gamePlayMenu, dialogWindowMenu):
        working = True
        clock = pg.time.Clock()
        self._configureStartingNamesAccordingToChosenDifficulties()
        while working:
            mousePos = pg.mouse.get_pos()
            clock.tick(FPS)
            self._drawMenu()
            self._updateUIObjects(self._UIObjects)
            self._changeColorOfUIObjects(mousePos, self._player_ddms + [self._back_btn, self._play_btn, self._gameMode_ddm])
            for e in pg.event.get():
                if e.type == pg.QUIT:
                    working = False
                elif e.type == pg.MOUSEBUTTONDOWN:
                    if e.button != 1:
                        continue
                    if self._back_btn.checkForInput(mousePos):
                        working = False
                    if self._play_btn.checkForInput(mousePos):
                        self._initiateGame(waitingMenu, gamePlayMenu, dialogWindowMenu)
                        working = False
                    if self._gameMode_ddm.checkForInput(mousePos):
                        self._gameMode_ddm.switch()
                    choice = self._gameMode_ddm.checkForChoice(mousePos)
                    if choice is not None:
                        self._currentGameMode = choice - 1
                    for i, ddm in enumerate(self._player_ddms):
                        if ddm.checkForInput(mousePos):
                            ddm.switch()
                        choice = ddm.checkForChoice(mousePos)
                        if choice is not None:
                            self._difficulties[i] = choice
                            self._configureNameByDifficulty(i, choice)
            pg.display.flip()

    def _configureStartingNamesAccordingToChosenDifficulties(self):
        for i, ddm_lst in enumerate([self._textContent["DDM1"], self._textContent["DDM2"], self._textContent["DDM3"], self._textContent["DDM4"]]):
            ddm_lst[0] = ddm_lst[self._difficulties[i]]
            if self._difficulties[i] in (2, 3, 4):
                self._names[i] = f"{self._NAMES[i]} {self._textContent['AItxt']} ({self._textContent['diffNames'][self._difficulties[i]]})"
        self._textContent["DDM5"][0] = self._textContent["DDM5"][self._currentGameMode + 1]

    def _initiateGame(self, waitingMenu, gamePlayMenu, dialogWindowMenu):
        acceptionEvent = Event()
        Thread(target=Server, args=([player for player, difficulty in enumerate(self._difficulties) if difficulty == 1], acceptionEvent)).start()
        acceptionEvent.wait()
        network = Network(getIP())
        gameParams = GameParams(difficulties=self._difficulties, playerNames=self._names, gameMode=self._currentGameMode)
        network.send(gameParams)
        waitingMenu.create(network, gamePlayMenu, dialogWindowMenu, True)
        network.close()

    def _configureNameByDifficulty(self, nameNum: int, choice: int):
        if choice == 1:
            self._names[nameNum] = self._NAMES[nameNum]
        elif choice in (2, 3, 4):
            self._names[nameNum] = f"{self._NAMES[nameNum]} {self._textContent['AItxt']} ({self._textContent['diffNames'][choice]})"
