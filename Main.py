from TestDLL import getPower, numSplit
from Engine import GameState, Move, PIECES, bbOfSquares, COLORED_PIECES, POSSIBLE_PIECES_TO_PROMOTE, RESERVE_PIECES
from AIpy import randomMoveAI, negaScoutMoveAI
from Utils import *
import pygame as pg
from multiprocessing import Queue, freeze_support
from copy import deepcopy
from random import randint
from UI import Button, Hourglass, DialogWindow, RadioButton, RadioLabel, Image, DropDownMenu, Label
import json
from os.path import isfile, join
from sys import exit as sys_exit
import sys
from os import getcwd
# required for correct convertation into .exe file
try:
    workingDirectory = sys._MEIPASS
except AttributeError:
    workingDirectory = getcwd()

if __name__ == "__main__":
    pg.init()
    # SCREEN_WIDTH, SCREEN_HEIGHT = pg.display.Info().current_w, pg.display.Info().current_h  # getting screen sizes
    SCREEN_WIDTH, SCREEN_HEIGHT = 960, 540
    DIMENSION = 8  # chessboard is 8x8
    BOARD_SIZE = 600 * SCREEN_HEIGHT // 1080  # approximate size of the board in pixels
    SQ_SIZE = BOARD_SIZE // DIMENSION  # size of one square of a board in pixels
    BOARD_SIZE = SQ_SIZE * DIMENSION  # exact size of the board in pixels
    MARGIN = (SCREEN_HEIGHT - BOARD_SIZE) // 2  # top and left margin for the left board in pixels
    MARGIN_LEFT = SCREEN_WIDTH - BOARD_SIZE - MARGIN  # left margin for the right board in pixels, top margin is the same as for the left board
    RESERVE_MARGIN = (BOARD_SIZE - 5 * SQ_SIZE) // 2  # distance between the edge of the board and the edge of the reserve pieces in pixels
    FONT_SIZE = 25 * SCREEN_HEIGHT // 1080  # standard font size; every label size in the game is a scale of this constant
    FPS = 30

    # surfaces used in highlighting
    DARK_GREEN = pg.Surface((SQ_SIZE, SQ_SIZE))
    DARK_GREEN.fill((110, 90, 0))
    BLUE = pg.Surface((SQ_SIZE, SQ_SIZE))
    BLUE.set_alpha(100)
    BLUE.fill((0, 0, 255))
    YELLOW = pg.Surface((SQ_SIZE, SQ_SIZE))
    YELLOW.set_alpha(100)
    YELLOW.fill("yellow")

IMAGES = {}  # loaded images are stored here
SOUNDS = {}  # loaded sounds are stored here


def loadResources():
    """Loads all textures, sounds and SETTINGS file if it exists"""
    SQ_SIZE_IMAGES = ["frame", "hourglass", "home_button_on", "home_button_off", "radio_button_on", "radio_button_off",
                      "restart_button_on", "restart_button_off", "ru_flag", "en_flag"]
    EMPTY_PIECES = ["e" + piece for piece in PIECES if piece != "K"]
    for img in COLORED_PIECES + EMPTY_PIECES + SQ_SIZE_IMAGES:
        IMAGES[img] = pg.transform.scale(pg.image.load(join(workingDirectory, f"images/{img}.png")), (SQ_SIZE, SQ_SIZE))
    IMAGES["icon"] = pg.image.load(join(workingDirectory, "images/icon.png"))
    IMAGES["settingsBG"] = pg.transform.scale(pg.image.load(join(workingDirectory, "images/settingsBG.png")), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 9))
    IMAGES["board"] = pg.transform.scale(pg.image.load(join(workingDirectory, "images/board.png")), (BOARD_SIZE, BOARD_SIZE))
    IMAGES["board_with_pieces1"] = pg.transform.scale(pg.image.load(join(workingDirectory, "images/board_with_pieces1.png")), (BOARD_SIZE // 2, BOARD_SIZE // 2))
    IMAGES["board_with_pieces2"] = pg.transform.scale(pg.image.load(join(workingDirectory, "images/board_with_pieces2.png")), (BOARD_SIZE // 2, BOARD_SIZE // 2))
    IMAGES["button"] = pg.transform.scale(pg.image.load(join(workingDirectory, "images/button.png")), (SCREEN_WIDTH // 5, int(SQ_SIZE * 1.5)))
    IMAGES["header"] = pg.transform.scale(pg.image.load(join(workingDirectory, "images/button.png")), (SCREEN_WIDTH // 4 * 3, SCREEN_HEIGHT // 5))
    IMAGES["ddm_head"] = pg.transform.scale(pg.image.load(join(workingDirectory, "images/button2.png")), (BOARD_SIZE * 5 // 12, SQ_SIZE * 2 // 3))
    IMAGES["ddm_body"] = pg.transform.scale(pg.image.load(join(workingDirectory, "images/button3.png")), (BOARD_SIZE * 5 // 12, SQ_SIZE * 2 // 3))
    IMAGES["dialogWindow"] = pg.transform.scale(pg.image.load(join(workingDirectory, "images/dialogWindow.png")), (SCREEN_WIDTH // 3, SCREEN_HEIGHT // 4))
    IMAGES["BG"] = pg.transform.scale(pg.image.load(join(workingDirectory, "images/BG.png")), (SCREEN_WIDTH, SCREEN_HEIGHT))
    SOUNDS["move"] = pg.mixer.Sound(join(workingDirectory, "sounds/move.wav"))
    global SETTINGS
    if isfile("SETTINGS.json"):
        with open("SETTINGS.json", "r", encoding="utf-8") as f:
            try:
                SETTINGS = json.load(f)
            except json.decoder.JSONDecodeError:
                SETTINGS = {"sounds": True, "language": True}
            if not settingsCheck(SETTINGS):
                SETTINGS = {"sounds": True, "language": True}


def saveResources():
    """Saves SETTINGS in a json file"""
    with open("SETTINGS.json", "w", encoding="utf-8") as f:
        json.dump(SETTINGS, f)


SETTINGS = {"sounds": True, "language": True}
if __name__ == "__main__":
    loadResources()
if SETTINGS["language"]:
    from lang_en import *
else:
    from lang_ru import *

boardPlayers = [True, True, True, True]  # there are 4 players in the game; True = player, False = AI
difficulties = [1, 1, 1, 1]  # 1 = player, 2 = EasyAI, 3 = NormalAI, 4 = HardAI
names = deepcopy(plyrNames)  # current names of every player (they are changing for AI)


def setGameStateToDefault():
    """Sets some game state variables to default state

    Order is: AIExists, gameStates, validMoves, AIProcess, returnQ, activeBoard, gameOver, selectedSq,
    clicks, moveMade, AIThinkingTime, AIPositionCounter, AIMoveCounter, hourglass
    """
    AIExists = not (boardPlayers[0] and boardPlayers[1] and boardPlayers[2] and boardPlayers[3])  # figures out if there is an AI in the game
    gameStates = [GameState(), GameState()]
    validMoves = [gameStates[0].getValidMoves(), gameStates[1].getValidMoves()]
    AIProcess = Process()
    returnQ = Queue()
    activeBoard = 0  # number of the board (0 or 1) which player is to move
    gameOver = False
    selectedSq = [(), ()]
    clicks = [[], []]
    moveMade = [False, False]
    AIThinkingTime = [0, 0]
    AIPositionCounter = [0, 0]
    AIMoveCounter = [len(validMoves[0][0]), 0]
    hourglass = Hourglass(0, IMAGES["hourglass"], MARGIN, MARGIN_LEFT, SQ_SIZE, SCREEN_HEIGHT)
    return AIExists, gameStates, validMoves, AIProcess, returnQ, activeBoard, gameOver, selectedSq, \
           clicks, moveMade, AIThinkingTime, AIPositionCounter, AIMoveCounter, hourglass


def gamePlay(screen: pg.Surface):
    """Contains main loop that handles game process"""
    global difficulties, boardPlayers, names
    clock = pg.time.Clock()
    AIExists, gameStates, validMoves, AIProcess, returnQ, activeBoard, gameOver, selectedSq, clicks, moveMade, AIThinkingTime, AIPositionCounter, AIMoveCounter, hourglass = setGameStateToDefault()
    working = True  # for game loop
    soundPlayed = False
    AIThinking = False
    toMenu_btn = RadioButton((SCREEN_WIDTH - SQ_SIZE, SQ_SIZE), True, IMAGES["home_button_on"], IMAGES["home_button_off"])
    restart_btn = RadioButton((SCREEN_WIDTH - SQ_SIZE, int(SQ_SIZE * 2.5)), True, IMAGES["restart_button_on"], IMAGES["restart_button_off"])
    while working:
        clock.tick(FPS)
        location = pg.mouse.get_pos()  # getting position of the cursor
        playerTurn = [(gameStates[0].whiteTurn and boardPlayers[0]) or (not gameStates[0].whiteTurn and boardPlayers[1]),  # calculates whether it is players turn or AI turn
                      (gameStates[1].whiteTurn and boardPlayers[2]) or (not gameStates[1].whiteTurn and boardPlayers[3])]
        changeColorOfUIObjects(location, [toMenu_btn, restart_btn])  # updating UI
        drawGameState(screen, gameStates, validMoves, selectedSq, toMenu_btn, restart_btn, AIExists)
        if not gameOver:
            updateUIObjects(screen, [hourglass])
        for e in pg.event.get():
            if e.type == pg.KEYDOWN:
                if e.key == pg.K_F4 and bool(e.mod & pg.KMOD_ALT):  # in case alt+f4 save settings and exit
                    saveResources()
                    pg.quit()
                    sys_exit()
            elif e.type == pg.QUIT:  # before exit: terminating an AI process and print log info
                gameOver = True
                AIThinking = terminateAI(AIThinking, AIProcess)
                ConsoleLog.endgameOutput(gameStates, boardPlayers, AIThinkingTime, AIPositionCounter, AIMoveCounter, AIExists)
                names = deepcopy(plyrNames)
                working = False
            elif e.type == pg.MOUSEBUTTONDOWN:
                if e.button == 1:  # in case LMB
                    if toMenu_btn.checkForInput(location):  # if menu button clicked, dialog window pops up
                        if createDialogWindow(screen, gameMenu["DW1"]):  # if player wants to exit - exit
                            pg.event.post(pg.event.Event(pg.QUIT))
                    if restart_btn.checkForInput(location):  # if restart button clicked, dialog window pops up
                        if createDialogWindow(screen, gameMenu["DW2"]):  # if player wants to restart - set game state to starting position
                            AIThinking = terminateAI(AIThinking, AIProcess)
                            ConsoleLog.endgameOutput(gameStates, boardPlayers, AIThinkingTime, AIPositionCounter, AIMoveCounter, AIExists)
                            AIExists, gameStates, validMoves, AIProcess, returnQ, activeBoard, gameOver, selectedSq, clicks, moveMade, AIThinkingTime, AIPositionCounter, AIMoveCounter, hourglass = setGameStateToDefault()
                            playerTurn = [(gameStates[0].whiteTurn and boardPlayers[0]) or (not gameStates[0].whiteTurn and boardPlayers[1]),
                                          (gameStates[1].whiteTurn and boardPlayers[2]) or (not gameStates[1].whiteTurn and boardPlayers[3])]
                            drawGameState(screen, gameStates, validMoves, selectedSq, toMenu_btn, restart_btn, AIExists)
                            pg.display.flip()
                    if not gameOver:  # if any other position was clicked
                        boardNum = -1  # -1 = clicked outside any board; 0 = clicked left board; 1 - clicked right board
                        reserveBoardNum = -1  # -1 = clicked outside any reserve field; 0 = clicked left board reserve field; 1 - clicked right board reserve field
                        if MARGIN < location[0] < MARGIN + BOARD_SIZE and MARGIN < location[1] < MARGIN + BOARD_SIZE:
                            boardNum = 0
                        elif MARGIN_LEFT < location[0] < SCREEN_WIDTH - MARGIN and MARGIN < location[1] < MARGIN + BOARD_SIZE:
                            boardNum = 1
                        elif MARGIN + RESERVE_MARGIN < location[0] < MARGIN + BOARD_SIZE - RESERVE_MARGIN and (MARGIN - SQ_SIZE < location[1] < MARGIN or MARGIN + BOARD_SIZE < location[1] < MARGIN + BOARD_SIZE + SQ_SIZE):
                            reserveBoardNum = 0
                        elif MARGIN_LEFT + RESERVE_MARGIN < location[0] < MARGIN_LEFT + BOARD_SIZE - RESERVE_MARGIN and (MARGIN - SQ_SIZE < location[1] < MARGIN or MARGIN + BOARD_SIZE < location[1] < MARGIN + BOARD_SIZE + SQ_SIZE):
                            reserveBoardNum = 1
                        if boardNum != -1:  # if clicked on any board or reserve field of any board
                            if activeBoard == boardNum:  # we can move pieces only on an active board
                                if boardNum == 0:
                                    column = (location[0] - MARGIN) // SQ_SIZE  # calculating exact square which was clicked
                                    row = (location[1] - MARGIN) // SQ_SIZE
                                else:
                                    column = (location[0] - MARGIN_LEFT) // SQ_SIZE
                                    row = (location[1] - MARGIN) // SQ_SIZE
                                    column = DIMENSION - column - 1  # right board is upside down, so we must invert coordinates of the square
                                    row = DIMENSION - row - 1
                                if selectedSq[boardNum] == (column, row):  # if clicked same square twice - reset clicks
                                    selectedSq[boardNum] = ()
                                    clicks[boardNum] = []
                                else:  # otherwise - remember clicks
                                    selectedSq[boardNum] = (column, row)
                                    clicks[boardNum].append(deepcopy(selectedSq[boardNum]))
                                if len(clicks[boardNum]) == 2 and playerTurn[boardNum]:  # if clicked 2 different squares on an active board - start generating a move
                                    isReserve = False
                                    movedPiece = None
                                    color = "w" if clicks[boardNum][0][1] == 8 else "b"  # bottom pieces color of an active board
                                    if clicks[boardNum][0][1] == -1 or clicks[boardNum][0][1] == 8:  # columns and rows change from 0 to 7, so if row is -1 or 8, player clicked on a reserve field
                                        startSq = 0
                                        isReserve = True
                                        movedPiece = color + PIECES[clicks[boardNum][0][0]]
                                    else:
                                        startSq = bbOfSquares[clicks[boardNum][0][1]][clicks[boardNum][0][0]]  # getting a bitboard of a starting square (0 - if it is a reserve move)
                                    if 0 <= clicks[boardNum][1][1] <= 7:
                                        endSq = bbOfSquares[clicks[boardNum][1][1]][clicks[boardNum][1][0]]  # getting a bitboard of an end square (0 - if second click of the player was on a reserve field)
                                    else:
                                        endSq = 0
                                    move = Move(startSq, endSq, gameStates[boardNum], movedPiece=movedPiece, isReserve=isReserve)  # generating a move
                                    for part in validMoves[boardNum]:  # searching for the same move in valid moves
                                        for validMove in part:  # if our move is a pawn promotion, it is not generated finally, so it may not match
                                            if move == validMove or (move.moveID == validMove.moveID and move.isPawnPromotion and len(validMoves[boardNum][2]) > 0):
                                                if move.isPawnPromotion:  # if move is a pawn promotion - allow player to choose a promotion
                                                    pos, piece = getPromotion(screen, gameStates, boardNum, toMenu_btn, restart_btn, AIExists)
                                                    validMove.promotedTo = None if piece is None else piece[1]
                                                    validMove.promotedPiecePosition = pos
                                                if not (validMove.isPawnPromotion and validMove.promotedTo is None):  # if it is a valid move - make it
                                                    gameStates[boardNum].makeMove(validMove, gameStates[1 - boardNum])
                                                    for i in range(2):
                                                        validMoves[i] = gameStates[i].getValidMoves()  # update valid moves
                                                        gameStates[i].updatePawnPromotionMoves(validMoves[i], gameStates[1 - i])
                                                    moveMade[boardNum] = True
                                                    selectedSq[boardNum] = ()  # reset clicks
                                                    clicks[boardNum] = []
                                                    activeBoard = 1 - activeBoard  # swap active board
                                                    # update hourglass sprite position
                                                    hourglass = Hourglass(getCurrentPlayer(gameStates, activeBoard), IMAGES["hourglass"], MARGIN, MARGIN_LEFT, SQ_SIZE, SCREEN_HEIGHT)
                                                    soundPlayed = playSound(SOUNDS["move"], soundPlayed, SETTINGS["sounds"])
                                                    break
                                    if not moveMade[boardNum]:  # if move was not made (was not a valid move) reset the first click
                                        clicks[boardNum] = [deepcopy(selectedSq[boardNum])]
                        elif reserveBoardNum != -1:  # if player clicked directly on a reserve field, just save this click
                            if activeBoard == reserveBoardNum:
                                if reserveBoardNum == 0:
                                    column = (location[0] - MARGIN - RESERVE_MARGIN) // SQ_SIZE + 1
                                    row = (location[1] - MARGIN) // SQ_SIZE
                                else:
                                    column = (location[0] - MARGIN_LEFT - RESERVE_MARGIN) // SQ_SIZE + 1
                                    row = (location[1] - MARGIN) // SQ_SIZE
                                    row = DIMENSION - row - 1
                                if selectedSq[reserveBoardNum] == (column, row):
                                    selectedSq[reserveBoardNum] = ()
                                    clicks[reserveBoardNum] = []
                                else:
                                    selectedSq[reserveBoardNum] = (column, row)
                                    clicks[reserveBoardNum].append(deepcopy(selectedSq[reserveBoardNum]))
                                if not moveMade[reserveBoardNum] and len(clicks[reserveBoardNum]) == 2:
                                    clicks[reserveBoardNum] = [deepcopy(selectedSq[reserveBoardNum])]
                        else:
                            selectedSq = [(), ()]
                            clicks = [[], []]
                        drawGameState(screen, gameStates, validMoves, selectedSq, toMenu_btn, restart_btn, AIExists)  # updating UI once more, to remove lags
                        pg.display.flip()
        if not gameOver:  # check for game end
            gameOver = gameOverCheck(gameStates, AIExists)
        for i in range(2):  # AI turn
            if not gameOver and not playerTurn[i] and activeBoard == i:
                playerNum = i * 2 + (0 if gameStates[i].whiteTurn else 1)  # get the difficulty to correctly start an algorithm
                playerName = getPlayerName(gameStates, activeBoard, names)  # get the name for log info
                if not AIThinking:
                    AIMoveCounter[1 - i] += len(validMoves[1 - i][0]) + len(validMoves[1 - i][1]) + len(validMoves[1 - i][2])
                    ConsoleLog.thinkingStart(playerName)
                    AIThinking = True
                    AIProcess = Process(target=negaScoutMoveAI, args=(gameStates[i], gameStates[1 - i], validMoves[i], difficulties[playerNum], returnQ))
                    AIProcess.start()  # starting an algorithm
                if not AIProcess.is_alive():  # when AI found a move
                    AIMove, thinkingTime, positionCounter = returnQ.get()  # get the move from the process
                    AIThinkingTime[i] += thinkingTime
                    AIPositionCounter[i] += positionCounter
                    ConsoleLog.thinkingEnd(playerName, thinkingTime, positionCounter)
                    if AIMove is None:  # if move was not found, make a random move (this case must never happen)
                        AIMove = randomMoveAI(validMoves)
                        ConsoleLog.madeRandomMove(playerName)
                    if AIMove.isPawnPromotion:  # if move is a pawn promotion, AI chooses a random piece to remove
                        possiblePromotions = calculatePossiblePromotions(gameStates, i)  # calculating positions of pieces, that can be removed
                        possibleRequiredPromotions = [bbOfSquares[key[1]][key[0]] for key, value in possiblePromotions.items() if value[1] == AIMove.promotedTo]  # leave those pieces, that AI wants to promote to
                        promotion = possibleRequiredPromotions[randint(0, len(possibleRequiredPromotions) - 1)]  # randomly choose a position of a piece
                        AIMove = Move(AIMove.startSquare, AIMove.endSquare, gameStates[i], movedPiece=AIMove.movedPiece, promotedTo=AIMove.promotedTo, promotedPiecePosition=promotion)
                    gameStates[i].makeMove(AIMove, gameStates[1 - i])  # make a move
                    for j in range(2):  # update valid moves
                        validMoves[j] = gameStates[j].getValidMoves()
                        gameStates[j].updatePawnPromotionMoves(validMoves[j], gameStates[1 - j])
                    if not gameOver:  # we should check for game end right here, not to start a new process when the game actually ended
                        gameOver = gameOverCheck(gameStates, AIExists)
                    moveMade[i] = True
                    activeBoard = 1 - activeBoard
                    hourglass = Hourglass(getCurrentPlayer(gameStates, activeBoard), IMAGES["hourglass"], MARGIN, MARGIN_LEFT, SQ_SIZE, SCREEN_HEIGHT)
                    AIThinking = False
                    selectedSq[i] = ()
                    clicks[i] = []
            if moveMade[i]:  # updating UI once more to remove lags
                drawGameState(screen, gameStates, validMoves, selectedSq, toMenu_btn, restart_btn, AIExists)
                playSound(SOUNDS["move"], soundPlayed, SETTINGS["sounds"])
                soundPlayed = False
                pg.display.flip()
                moveMade[i] = False
        pg.display.flip()


def drawEndGameText(screen: pg.Surface, gameStates: list, AIExists: bool):
    """Draws endgame text at the top of a screen (Team 1 wins, Team 2 wins or Draw)"""
    if (gameStates[0].checkmate and not gameStates[0].whiteTurn) or (gameStates[1].checkmate and gameStates[1].whiteTurn):
        drawTopText(screen, endGame["T1"])
    elif gameStates[0].stalemate and gameStates[1].stalemate:
        drawTopText(screen, endGame["D"])
    elif AIExists and (gameStates[0].stalemate or gameStates[1].stalemate):
        drawTopText(screen, endGame["D"])
    elif (gameStates[0].checkmate and gameStates[0].whiteTurn) or (gameStates[1].checkmate and not gameStates[1].whiteTurn):
        drawTopText(screen, endGame["T2"])


def gameOverCheck(gameStates: list, AIExists: bool):
    """Checks whether the game has ended"""
    if gameStates[0].checkmate or gameStates[1].checkmate:
        return True
    elif gameStates[0].stalemate and gameStates[1].stalemate:
        return True
    elif AIExists and (gameStates[0].stalemate or gameStates[1].stalemate):
        return True
    # if len(gameStates[1].gameLog) == 30:
    #     return True
    # if len(gameStates[0].gameLog) == 1:
    #     return True
    return False


def highlightSq(screen: pg.Surface, gameStates: list, validMoves: list, selectedSq: list):
    """Highlights square clicked last and all possible moves if a piece was clicked"""
    for i in range(2):
        if selectedSq[i] == ():
            continue
        color = "w" if selectedSq[i][1] == 8 else "b"  # bottom pieces color
        isReserve = True if selectedSq[i][1] == -1 or selectedSq[i][1] == 8 else False
        square = bbOfSquares[selectedSq[i][1]][selectedSq[i][0]] if not isReserve else 0  # bitboard of the clicked square
        piece = gameStates[i].getPieceBySquare(square) if not isReserve else color + PIECES[selectedSq[i][0]]  # piece, located on this square
        if piece is None:
            continue
        if not isReserve:  # highlighting selected square
            if i == 0:
                screen.blit(DARK_GREEN, (selectedSq[i][0] * SQ_SIZE + MARGIN, selectedSq[i][1] * SQ_SIZE + MARGIN))
            else:
                screen.blit(DARK_GREEN, ((DIMENSION - 1 - selectedSq[i][0]) * SQ_SIZE + MARGIN_LEFT,
                                         (DIMENSION - 1 - selectedSq[i][1]) * SQ_SIZE + MARGIN))
        else:
            if i == 0:
                screen.blit(DARK_GREEN, ((selectedSq[i][0] - 1) * SQ_SIZE + MARGIN + RESERVE_MARGIN, selectedSq[i][1] * SQ_SIZE + MARGIN))
            else:
                screen.blit(DARK_GREEN, ((selectedSq[i][0] - 1) * SQ_SIZE + MARGIN_LEFT + RESERVE_MARGIN,
                                         (DIMENSION - 1 - selectedSq[i][1]) * SQ_SIZE + MARGIN))
        if not isReserve or (isReserve and gameStates[i].reserve[color][piece[1]] > 0):  # highlighting possible moves
            if piece[0] == ("w" if gameStates[i].whiteTurn else "b"):
                endSquares = []
                for part in validMoves[i]:
                    for move in part:
                        if move.startSquare == square and move.endSquare not in endSquares:
                            endLoc = getPower(move.endSquare)
                            endSquares.append(move.endSquare)
                            if i == 0:
                                screen.blit(YELLOW, (endLoc % 8 * SQ_SIZE + MARGIN, endLoc // 8 * SQ_SIZE + MARGIN))
                            else:
                                r = DIMENSION - 1 - endLoc // 8
                                c = DIMENSION - 1 - endLoc % 8
                                screen.blit(YELLOW, (c * SQ_SIZE + MARGIN_LEFT, r * SQ_SIZE + MARGIN))


def highlightLastMove(screen: pg.Surface, gameStates: list, selectedSq: list):
    """Highlights last move"""
    for i in range(2):
        piece = None
        if selectedSq[i] != ():
            color = "w" if selectedSq[i][1] == 8 else "b"  # bottom pieces color
            isReserve = True if selectedSq[i][1] == -1 or selectedSq[i][1] == 8 else False
            square = bbOfSquares[selectedSq[i][1]][selectedSq[i][0]] if not isReserve else -1
            piece = gameStates[i].getPieceBySquare(square) if not isReserve else color + PIECES[selectedSq[i][0]]
            if isReserve and (gameStates[i].reserve[color][PIECES[selectedSq[i][0]]] == 0 or color == ("b" if gameStates[i].whiteTurn else "w")):
                piece = None  # do not highlight, if player tried to make a move with a reserve piece, which he does not have
        if piece is None or selectedSq[i] == ():
            if len(gameStates[i].gameLog) == 0:
                continue
            lastMove = gameStates[i].gameLog[-1]
            startLoc = getPower(lastMove.startSquare)  # number of a start square
            endLoc = getPower(lastMove.endSquare)  # number of an end square
            if not lastMove.isReserve:
                if i == 0:
                    screen.blit(BLUE, (startLoc % 8 * SQ_SIZE + MARGIN, startLoc // 8 * SQ_SIZE + MARGIN))
                    screen.blit(BLUE, (endLoc % 8 * SQ_SIZE + MARGIN, endLoc // 8 * SQ_SIZE + MARGIN))
                else:
                    screen.blit(BLUE, ((DIMENSION - 1 - startLoc % 8) * SQ_SIZE + MARGIN_LEFT,
                                       (DIMENSION - 1 - startLoc // 8) * SQ_SIZE + MARGIN))
                    screen.blit(BLUE, ((DIMENSION - 1 - endLoc % 8) * SQ_SIZE + MARGIN_LEFT,
                                       (DIMENSION - 1 - endLoc // 8) * SQ_SIZE + MARGIN))
            else:
                if i == 0:
                    marginTop = MARGIN - SQ_SIZE if lastMove.movedPiece[0] == "b" else MARGIN + BOARD_SIZE
                    screen.blit(BLUE, ((RESERVE_PIECES[lastMove.movedPiece[1]] - 1) * SQ_SIZE + MARGIN + RESERVE_MARGIN, marginTop))
                    screen.blit(BLUE, (endLoc % 8 * SQ_SIZE + MARGIN, endLoc // 8 * SQ_SIZE + MARGIN))
                else:
                    marginTop = MARGIN - SQ_SIZE if lastMove.movedPiece[0] == "w" else MARGIN + BOARD_SIZE
                    screen.blit(BLUE, ((RESERVE_PIECES[lastMove.movedPiece[1]] - 1) * SQ_SIZE + MARGIN_LEFT + RESERVE_MARGIN, marginTop))
                    screen.blit(BLUE, ((DIMENSION - 1 - endLoc % 8) * SQ_SIZE + MARGIN_LEFT,
                                       (DIMENSION - 1 - endLoc // 8) * SQ_SIZE + MARGIN))


def calculatePossiblePromotions(gameStates: list, board: int):
    """Creates a dict where: key = tuple which represents coordinates of a piece that can be removed; value = that exact piece"""
    possiblePromotions = {}
    color = "w" if gameStates[board].whiteTurn else "b"
    for piece in POSSIBLE_PIECES_TO_PROMOTE:
        splitPositions = numSplit(gameStates[1 - board].bbOfPieces[color + piece])  # get positions of every piece we can promote to on the other board
        for position in splitPositions:  # for every position check, if we can remove a piece from it
            if gameStates[1 - board].canBeRemoved(position, "w" if gameStates[board].whiteTurn else "b"):
                pos = getPower(position)
                possiblePromotions[(pos % 8, pos // 8)] = color + piece  # if we can - add to a possible promotion
    return possiblePromotions


def highlightPossiblePromotions(screen: pg.Surface, possiblePromotions: dict, board: int):
    """Highlights pieces on the other board that can be removed for a promotion"""
    if possiblePromotions == {}:
        return
    if board == 0:
        for column, row in possiblePromotions.keys():
            screen.blit(IMAGES["frame"], pg.Rect((DIMENSION - 1 - column) * SQ_SIZE + MARGIN_LEFT, (DIMENSION - 1 - row) * SQ_SIZE + MARGIN, SQ_SIZE, SQ_SIZE))
    elif board == 1:
        for column, row in possiblePromotions.keys():
            screen.blit(IMAGES["frame"], pg.Rect(column * SQ_SIZE + MARGIN, row * SQ_SIZE + MARGIN, SQ_SIZE, SQ_SIZE))


def drawGameState(screen: pg.Surface, gameStates: list, validMoves: list, selectedSq: list, toMenu_btn: RadioButton, restart_btn: RadioButton, AIExists: bool, promotion=-1, possiblePromotions=None):
    """Draws boards, pieces, buttons, highlights during the game"""
    screen.blit(IMAGES["BG"], (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
    drawEndGameText(screen, gameStates, AIExists)
    drawPlayersNames(screen)
    drawBoard(screen)
    updateUIObjects(screen, [toMenu_btn, restart_btn])
    highlightPossiblePromotions(screen, possiblePromotions, promotion)
    if promotion == -1:
        highlightLastMove(screen, gameStates, selectedSq)
        highlightSq(screen, gameStates, validMoves, selectedSq)
    drawPieces(screen, gameStates)


def drawBoard(screen: pg.Surface):
    """Draws both boards with a little shadow"""
    s2 = pg.Surface((BOARD_SIZE + 4, BOARD_SIZE + 4))
    s2.set_alpha(100)
    s2.fill(pg.Color("black"))
    screen.blit(s2, pg.Rect(MARGIN - 2, MARGIN - 2, BOARD_SIZE + 4, BOARD_SIZE + 4))
    screen.blit(IMAGES["board"], pg.Rect(MARGIN, MARGIN, BOARD_SIZE, BOARD_SIZE))
    screen.blit(s2, pg.Rect(MARGIN_LEFT - 2, MARGIN - 2, BOARD_SIZE + 4, BOARD_SIZE + 4))
    screen.blit(IMAGES["board"], pg.Rect(MARGIN_LEFT, MARGIN, BOARD_SIZE, BOARD_SIZE))


def drawPieces(screen: pg.Surface, gameStates: list):
    """Draws pieces on both boards"""
    marginTop1 = MARGIN - SQ_SIZE
    marginTop2 = MARGIN + BOARD_SIZE
    font = pg.font.SysFont("Helvetica", FONT_SIZE, True, False)
    for i in range(2):
        marginLeft = MARGIN if i == 0 else MARGIN_LEFT
        for piece in COLORED_PIECES:
            splitPositions = numSplit(gameStates[i].bbOfPieces[piece])  # gets positions of a piece
            for position in splitPositions:  # draw piece on every position
                pos = getPower(position) if i == 0 else 63 - getPower(position)
                screen.blit(IMAGES[piece], pg.Rect(pos % 8 * SQ_SIZE + marginLeft, pos // 8 * SQ_SIZE + MARGIN, SQ_SIZE, SQ_SIZE))
            if piece != "wK" and piece != "bK":  # for reserve pieces
                marginTop = marginTop1 if (piece[0] == "b" and i == 0) or (piece[0] == "w" and i == 1) else marginTop2  # top margin for a piece in pixels
                marginTextTop = -5 if (piece[0] == "b" and i == 0) or (piece[0] == "w" and i == 1) else SQ_SIZE + 5  # top margin for a number of pieces in pixels
                marg = marginLeft + (RESERVE_PIECES[piece[1]] - 1) * SQ_SIZE + RESERVE_MARGIN  # left margin, depending on a piece we draw
                if gameStates[i].reserve[piece[0]][piece[1]] > 0:  # if number of pieces is not 0, draw a piece and a number
                    screen.blit(IMAGES[piece], pg.Rect(marg, marginTop, SQ_SIZE, SQ_SIZE))
                    tmp_lbl = Label(f"{gameStates[i].reserve[piece[0]][piece[1]]}", (marg + SQ_SIZE // 2 - 1, marginTop + marginTextTop), font, shift=1)
                    updateUIObjects(screen, [tmp_lbl])
                elif gameStates[i].reserve[piece[0]][piece[1]] == 0:  # if number of pieces is 0, draw an empty piece
                    screen.blit(IMAGES[f"e{piece[1]}"], pg.Rect(marg, marginTop, SQ_SIZE, SQ_SIZE))


def getPromotion(screen: pg.Surface, gameStates: list, boardNum: int, toMenu_btn: RadioButton, restart_btn: RadioButton, AIExists: bool):
    """Lets the player choose exact piece, he wants to promote into. Returns a bitboard of a position of a piece and that exact piece"""
    possiblePromotions = calculatePossiblePromotions(gameStates, boardNum)
    if possiblePromotions == {}:
        return 0, None
    drawGameState(screen, gameStates, [], [], toMenu_btn, restart_btn, AIExists, promotion=boardNum, possiblePromotions=possiblePromotions)
    playerName = getPlayerName(gameStates, boardNum, names)
    drawTopText(screen, f"{playerName} {promText}")  # message, that current player chooses a piece to promote
    pg.display.flip()
    working = True
    while working:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.event.post(pg.event.Event(pg.QUIT))
                return 0, None
            if e.type == pg.MOUSEBUTTONDOWN:
                if e.button == 1:  # if LBM
                    location = pg.mouse.get_pos()
                    if boardNum == 1:
                        if MARGIN < location[0] < MARGIN + BOARD_SIZE and MARGIN < location[1] < MARGIN + BOARD_SIZE:
                            column = (location[0] - MARGIN) // SQ_SIZE
                            row = (location[1] - MARGIN) // SQ_SIZE
                            if (column, row) in possiblePromotions:
                                return bbOfSquares[row][column], possiblePromotions[(column, row)]
                    if boardNum == 0:
                        if MARGIN_LEFT < location[0] < MARGIN_LEFT + BOARD_SIZE and MARGIN < location[1] < MARGIN + BOARD_SIZE:
                            column = (location[0] - MARGIN_LEFT) // SQ_SIZE
                            row = (location[1] - MARGIN) // SQ_SIZE
                            column = DIMENSION - column - 1
                            row = DIMENSION - row - 1
                            if (column, row) in possiblePromotions:
                                return bbOfSquares[row][column], possiblePromotions[(column, row)]


def drawTopText(screen: pg.Surface, text: str):
    """Draws a text at a top of the screen"""
    font = pg.font.SysFont("Helvetica", FONT_SIZE * 2, True, False)
    topText_lbl = Label(text, (SCREEN_WIDTH // 2, SQ_SIZE), font)
    updateUIObjects(screen, [topText_lbl])


def drawPlayersNames(screen: pg.Surface):
    """Draws players names"""
    font = pg.font.SysFont("Helvetica", FONT_SIZE * 7 // 4, True, False)
    xBoard1 = MARGIN + BOARD_SIZE // 2
    xBoard2 = MARGIN_LEFT + BOARD_SIZE // 2
    yTop = MARGIN // 2
    yBot = SCREEN_HEIGHT - MARGIN // 2
    player1_lbl = Label(names[0], (xBoard1, yBot), font, shift=2)
    player2_lbl = Label(names[1], (xBoard1, yTop), font, shift=2)
    player3_lbl = Label(names[2], (xBoard2, yTop), font, shift=2)
    player4_lbl = Label(names[3], (xBoard2, yBot), font, shift=2)
    updateUIObjects(screen, [player1_lbl, player2_lbl, player3_lbl, player4_lbl])


def drawMenu(screen: pg.Surface, menuName_lbl: Label):
    """Draws background and a header for menus"""
    screen.blit(IMAGES["BG"], (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(IMAGES["header"], (SCREEN_WIDTH // 8, 0, SCREEN_WIDTH // 4 * 3, SCREEN_HEIGHT // 5))
    updateUIObjects(screen, [menuName_lbl])


def createMainMenu(screen: pg.Surface):
    """Creates main menu"""
    working = True
    clock = pg.time.Clock()
    font = pg.font.SysFont("Helvetica", FONT_SIZE * 3, True, False)
    settings_btn = Button(IMAGES["button"], (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), mainMenu["Settings_btn"], font)
    newGame_btn = Button(IMAGES["button"], (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - settings_btn.rect.height * 2), mainMenu["NewGame_btn"], font)
    quit_btn = Button(IMAGES["button"], (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + settings_btn.rect.height * 2), mainMenu["Quit_btn"], font)
    menuName_lbl = Label("SwiChess", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 10), pg.font.SysFont("Helvetica", FONT_SIZE * 7, True, False), shift=5)
    while working:
        mousePos = pg.mouse.get_pos()
        clock.tick(FPS)
        drawMenu(screen, menuName_lbl)
        changeColorOfUIObjects(mousePos, [newGame_btn, settings_btn, quit_btn])
        updateUIObjects(screen, [newGame_btn, settings_btn, quit_btn])
        for e in pg.event.get():
            if e.type == pg.QUIT:
                working = False
            elif e.type == pg.MOUSEBUTTONDOWN:
                if e.button == 1:
                    if newGame_btn.checkForInput(mousePos):
                        createNewGameMenu(screen)
                    if settings_btn.checkForInput(mousePos):
                        createSettingsMenu(screen)
                    if quit_btn.checkForInput(mousePos):
                        if createDialogWindow(screen, mainMenu["DW"]):
                            working = False
        pg.display.flip()
    saveResources()


def createSettingsMenu(screen: pg.Surface):
    """Creates settings menu"""
    working = True
    clock = pg.time.Clock()
    font = pg.font.SysFont("Helvetica", FONT_SIZE * 3, True, False)
    back_btn = Button(IMAGES["button"], (SCREEN_WIDTH // 2, SCREEN_HEIGHT - SQ_SIZE * 2), settingsMenu["Back_btn"], font)
    sound_btn = RadioButton((SCREEN_WIDTH // 4 + SQ_SIZE, SCREEN_HEIGHT // 4 + SQ_SIZE // 2), SETTINGS["sounds"], IMAGES["radio_button_on"], IMAGES["radio_button_off"])
    sound_lbl = RadioLabel(settingsMenu["Sound_btn"][0], settingsMenu["Sound_btn"][1], SETTINGS["sounds"], (SCREEN_WIDTH // 4 + int(SQ_SIZE * 1.5), SCREEN_HEIGHT // 4), font)
    lang_btn = RadioButton((SCREEN_WIDTH // 4 + SQ_SIZE, SCREEN_HEIGHT // 4 + int(SQ_SIZE * 2.5)), SETTINGS["language"], IMAGES["en_flag"], IMAGES["ru_flag"])
    lang_lbl = RadioLabel(settingsMenu["Lang_btn"], settingsMenu["Lang_btn"], SETTINGS["language"], (SCREEN_WIDTH // 4 + int(SQ_SIZE * 1.5), SCREEN_HEIGHT // 4 + SQ_SIZE * 2), font)
    menuName_lbl = Label(settingsMenu["Name"], (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 10), pg.font.SysFont("Helvetica", FONT_SIZE * 7, True, False), shift=5)
    lang_img = Image(IMAGES["settingsBG"], (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 + int(SQ_SIZE * 2.5)), None)
    sound_img = Image(IMAGES["settingsBG"], (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 + SQ_SIZE // 2), None)
    while working:
        mousePos = pg.mouse.get_pos()
        clock.tick(FPS)
        drawMenu(screen, menuName_lbl)
        changeColorOfUIObjects(mousePos, [back_btn])
        updateUIObjects(screen, [lang_img, sound_img, back_btn, sound_btn, sound_lbl, lang_btn, lang_lbl])
        for e in pg.event.get():
            if e.type == pg.QUIT:
                working = False
            elif e.type == pg.MOUSEBUTTONDOWN:
                if e.button == 1:
                    if back_btn.checkForInput(mousePos):
                        working = False
                    if sound_btn.checkForInput(mousePos):
                        sound_btn.switch()
                        sound_lbl.switch()
                        SETTINGS["sounds"] = sound_btn.state
                    if lang_btn.checkForInput(mousePos):
                        if createDialogWindow(screen, langChange):
                            working = False
                            SETTINGS["language"] = not SETTINGS["language"]
                            pg.event.post(pg.event.Event(pg.QUIT))
        pg.display.flip()


def createNewGameMenu(screen: pg.Surface):
    """Creates new game menu"""
    global names
    working = True
    clock = pg.time.Clock()
    font = pg.font.SysFont("Helvetica", FONT_SIZE * 3, True, False)
    smallFont = pg.font.SysFont("Helvetica", int(FONT_SIZE * 1.5), True, False)
    back_btn = Button(IMAGES["button"], (SCREEN_WIDTH // 2, SCREEN_HEIGHT - SQ_SIZE * 2), newGameMenu["Back_btn"], font)
    play_btn = Button(IMAGES["button"], (SCREEN_WIDTH * 4 // 5, SCREEN_HEIGHT - SQ_SIZE * 2), newGameMenu["Play_btn"], font)
    xBoard1 = SCREEN_WIDTH // 4
    xBoard2 = SCREEN_WIDTH // 4 + BOARD_SIZE // 2 + SQ_SIZE
    yBoard = SCREEN_HEIGHT // 3 + SQ_SIZE
    board1_img = Image(IMAGES["board_with_pieces1"], (xBoard1, yBoard), (BOARD_SIZE // 2, BOARD_SIZE // 2))
    board2_img = Image(IMAGES["board_with_pieces2"], (xBoard2, yBoard), (BOARD_SIZE // 2, BOARD_SIZE // 2))
    names = deepcopy(plyrNames)
    for i, ddm_lst in enumerate([newGameMenu["DDM1"], newGameMenu["DDM2"], newGameMenu["DDM3"], newGameMenu["DDM4"]]):
        ddm_lst[0] = ddm_lst[difficulties[i]]
        if difficulties[i] == 1:
            names[i] = plyrNames[i]
        elif difficulties[i] in [2, 3, 4]:
            names[i] = f"{plyrNames[i]} {AItxt} ({diffNames[difficulties[i]]})"
    player1_ddm = DropDownMenu((xBoard1, yBoard + BOARD_SIZE // 4 + SQ_SIZE // 2),
                               newGameMenu["DDM1"], smallFont, SQ_SIZE, IMAGES["ddm_head"], IMAGES["ddm_body"])
    player2_ddm = DropDownMenu((xBoard1, yBoard - BOARD_SIZE // 4 - SQ_SIZE // 2),
                               newGameMenu["DDM2"], smallFont, SQ_SIZE, IMAGES["ddm_head"], IMAGES["ddm_body"])
    player3_ddm = DropDownMenu((xBoard2, yBoard - BOARD_SIZE // 4 - SQ_SIZE // 2),
                               newGameMenu["DDM3"], smallFont, SQ_SIZE, IMAGES["ddm_head"], IMAGES["ddm_body"])
    player4_ddm = DropDownMenu((xBoard2, yBoard + BOARD_SIZE // 4 + SQ_SIZE // 2),
                               newGameMenu["DDM4"], smallFont, SQ_SIZE, IMAGES["ddm_head"], IMAGES["ddm_body"])
    menuName_lbl = Label(newGameMenu["Name"], (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 10), pg.font.SysFont("Helvetica", FONT_SIZE * 7, True, False), shift=5)
    while working:
        mousePos = pg.mouse.get_pos()
        clock.tick(FPS)
        drawMenu(screen, menuName_lbl)
        updateUIObjects(screen, [board1_img, board2_img, player1_ddm, player2_ddm, player3_ddm, player4_ddm, back_btn, play_btn])
        changeColorOfUIObjects(mousePos, player1_ddm.buttons + player2_ddm.buttons + player3_ddm.buttons + player4_ddm.buttons + [back_btn, play_btn])
        for e in pg.event.get():
            if e.type == pg.QUIT:
                working = False
            elif e.type == pg.MOUSEBUTTONDOWN:
                if e.button == 1:
                    if back_btn.checkForInput(mousePos):
                        working = False
                    if play_btn.checkForInput(mousePos):
                        gamePlay(screen)
                        working = False
                    for i, ddm in enumerate([player1_ddm, player2_ddm, player3_ddm, player4_ddm]):
                        if ddm.checkForInput(mousePos):
                            ddm.switch()
                        choice = ddm.checkForChoice(mousePos)
                        if choice == 1:
                            boardPlayers[i] = True
                            names[i] = plyrNames[i]
                        elif choice in [2, 3, 4]:
                            boardPlayers[i] = False
                            names[i] = f"{plyrNames[i]} {AItxt} ({diffNames[choice]})"
                        if choice is not None:
                            difficulties[i] = choice
        pg.display.flip()


def createDialogWindow(screen: pg.Surface, text: str):
    """Creates dialog window"""
    working = True
    clock = pg.time.Clock()
    dW = DialogWindow(text, SCREEN_HEIGHT, SCREEN_WIDTH, FONT_SIZE, IMAGES["dialogWindow"], SETTINGS["language"])
    while working:
        mousePos = pg.mouse.get_pos()
        clock.tick(FPS)
        dW.update(screen, mousePos)
        for e in pg.event.get():
            if e.type == pg.QUIT:
                working = False
            elif e.type == pg.MOUSEBUTTONDOWN:
                if e.button == 1:
                    if dW.yes_btn.checkForInput(mousePos):
                        return True
                    if dW.no_btn.checkForInput(mousePos):
                        return False
        pg.display.flip()
    return False


if __name__ == "__main__":
    freeze_support()
    mainScreen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pg.display.set_caption("SwiChess")
    pg.display.set_icon(IMAGES["icon"])
    createMainMenu(mainScreen)
    pg.quit()
