from TestDLL import getPower, numSplit
from Engine import DIMENSION, GameState, Move, PIECES, bbOfSquares, COLORED_PIECES, POSSIBLE_PIECES_TO_PROMOTE
import pygame as pg
from AI import randomMoveAI, negaScoutMoveAI
from math import ceil, floor
from multiprocessing import Process, Queue
from copy import deepcopy
from random import randint
from UI import Button, Hourglass, DialogWindow, RadioButton, RadioLabel, Image, DropDownMenu, Label
import json
from os.path import isfile
from sys import exit as sys_exit

pg.init()
SCREEN_WIDTH, SCREEN_HEIGHT = pg.display.Info().current_w, pg.display.Info().current_h
# SCREEN_WIDTH, SCREEN_HEIGHT = 960, 540
if __name__ != "__main__":
    pg.quit()
BOARD_SIZE = 600 * SCREEN_HEIGHT // 1080
MARGIN = (SCREEN_HEIGHT - BOARD_SIZE) // 2
SQ_SIZE = BOARD_SIZE // DIMENSION
BOARD_SIZE = SQ_SIZE * DIMENSION
MARGIN_LEFT = SCREEN_WIDTH - BOARD_SIZE - MARGIN
RESERVE_MARGIN = (BOARD_SIZE - 5 * SQ_SIZE) // 2
FONT_SIZE = 25 * SCREEN_HEIGHT // 1080
EMPTY_PIECES = ["e" + piece for piece in PIECES if piece != "K"]
SKIN_PACK = 2
FPS = 60
# PALETTE = {"dark brown": (127, 97, 70), "brown": (181, 136, 99)}
IMAGES = {}
SOUNDS = {}


def settingsCheck(settings):
    if not isinstance(settings, dict):
        return False
    if not ("sounds" in settings and "language" in settings):
        return False
    if not (isinstance(settings["sounds"], bool) and isinstance(settings["language"], bool)):
        return False
    return True


def loadResources():
    SQ_SIZE_IMAGES = ("frame", "hourglass", "home_button_on", "home_button_off", "radio_button_on", "radio_button_off",
                      "restart_button_on", "restart_button_off", "ru_flag", "en_flag")
    for piece in COLORED_PIECES:
        IMAGES[piece] = pg.transform.scale(pg.image.load(f"images/{SKIN_PACK}/{piece}.png"), (SQ_SIZE, SQ_SIZE))
    for piece in EMPTY_PIECES:
        IMAGES[piece] = pg.transform.scale(pg.image.load(f"images/{SKIN_PACK}/{piece}.png"), (SQ_SIZE, SQ_SIZE))
    for img in SQ_SIZE_IMAGES:
        IMAGES[img] = pg.transform.scale(pg.image.load(f"images/{img}.png"), (SQ_SIZE, SQ_SIZE))
    IMAGES["icon"] = pg.image.load("images/icon.png")
    IMAGES["settingsBG"] = pg.transform.scale(pg.image.load("images/settingsBG.png"), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 9))
    IMAGES["board"] = pg.transform.scale(pg.image.load("images/board.png"), (BOARD_SIZE, BOARD_SIZE))
    IMAGES["board_with_pieces1"] = pg.transform.scale(pg.image.load("images/board_with_pieces1.png"), (BOARD_SIZE // 2, BOARD_SIZE // 2))
    IMAGES["board_with_pieces2"] = pg.transform.scale(pg.image.load("images/board_with_pieces2.png"), (BOARD_SIZE // 2, BOARD_SIZE // 2))
    IMAGES["button"] = pg.transform.scale(pg.image.load("images/button.png"), (SCREEN_WIDTH // 5, int(SQ_SIZE * 1.5)))
    IMAGES["header"] = pg.transform.scale(pg.image.load("images/button.png"), (SCREEN_WIDTH // 4 * 3, SCREEN_HEIGHT // 5))
    IMAGES["ddm_head"] = pg.transform.scale(pg.image.load("images/button2.png"), (BOARD_SIZE * 5 // 12, SQ_SIZE * 2 // 3))
    IMAGES["ddm_body"] = pg.transform.scale(pg.image.load("images/button3.png"), (BOARD_SIZE * 5 // 12, SQ_SIZE * 2 // 3))
    IMAGES["dialogWindow"] = pg.transform.scale(pg.image.load("images/dialogWindow.png"), (SCREEN_WIDTH // 3, SCREEN_HEIGHT // 4))
    SOUNDS["move"] = pg.mixer.Sound("sounds/move.wav")
    global SETTINGS
    if isfile("SETTINGS.json"):
        with open("SETTINGS.json", "r", encoding="utf-8") as f:
            try:
                SETTINGS = json.load(f)
            except json.decoder.JSONDecodeError:
                SETTINGS = {"sounds": True, "language": True}
            if not settingsCheck(SETTINGS):
                SETTINGS = {"sounds": True, "language": True}
    IMAGES["BG"] = pg.transform.scale(pg.image.load("images/BG.png"), (SCREEN_WIDTH, SCREEN_HEIGHT))


def saveResources():
    with open("SETTINGS.json", "w", encoding="utf-8") as f:
        json.dump(SETTINGS, f)


SETTINGS = {"sounds": True, "language": True}
if __name__ == "__main__":
    loadResources()
if SETTINGS["language"]:
    from lang_en import *
else:
    from lang_ru import *
boardPlayers = [True, True, True, True]
difficulties = [1, 1, 1, 1]
difficultiesNames = diffNames
constNames = deepcopy(plyrNames)
names = deepcopy(plyrNames)


def main(screen: pg.Surface):
    global difficulties, boardPlayers, names
    clock = pg.time.Clock()
    AIExists = not (boardPlayers[0] and boardPlayers[1] and boardPlayers[2] and boardPlayers[3])
    activeBoard = 0
    gameStates = [GameState(), GameState()]
    working = True
    validMoves = [gameStates[0].getValidMoves(), gameStates[1].getValidMoves()]
    moveMade = [False, False]
    soundPlayed = False
    gameOver = False
    AIThinking = False
    AIThinkingTime = [0, 0]
    AIPositionCounter = [0, 0]
    AIMoveCounter = [len(validMoves[0][0]), 0]
    AIProcess = Process()
    returnQ = Queue()
    selectedSq = [(), ()]
    clicks = [[], []]
    hourglass = Hourglass(0, IMAGES["hourglass"], MARGIN, MARGIN_LEFT, SQ_SIZE, SCREEN_HEIGHT)
    noAIActivePlayer = [0, 2]
    hourglasses = [Hourglass(noAIActivePlayer[0], IMAGES["hourglass"], MARGIN, MARGIN_LEFT, SQ_SIZE, SCREEN_HEIGHT),
                   Hourglass(noAIActivePlayer[1], IMAGES["hourglass"], MARGIN, MARGIN_LEFT, SQ_SIZE, SCREEN_HEIGHT)]
    toMenu_btn = RadioButton((SCREEN_WIDTH - SQ_SIZE, SQ_SIZE), True, IMAGES["home_button_on"], IMAGES["home_button_off"])
    restart_btn = RadioButton((SCREEN_WIDTH - SQ_SIZE, int(SQ_SIZE * 2.5)), True, IMAGES["restart_button_on"], IMAGES["restart_button_off"])
    while working:
        clock.tick(FPS)
        location = pg.mouse.get_pos()
        playerTurn = [(gameStates[0].whiteTurn and boardPlayers[0]) or (not gameStates[0].whiteTurn and boardPlayers[1]),
                      (gameStates[1].whiteTurn and boardPlayers[2]) or (not gameStates[1].whiteTurn and boardPlayers[3])]
        for btn in [toMenu_btn, restart_btn]:
            btn.changeColor(location)
        drawGameState(screen, gameStates, validMoves, selectedSq, toMenu_btn, restart_btn, AIExists)
        if not gameOver and AIExists:
            hourglass.update(screen)
        elif not gameOver and not AIExists:
            hourglasses[0].update(screen)
            hourglasses[1].update(screen)
        for e in pg.event.get():
            if e.type == pg.KEYDOWN:
                if e.key == pg.K_F4 and bool(e.mod & pg.KMOD_ALT):
                    saveResources()
                    pg.quit()
                    sys_exit()
            elif e.type == pg.QUIT:
                gameOver = True
                if AIThinking:
                    AIProcess.terminate()
                    AIProcess.join()
                    AIProcess.close()
                    AIThinking = False
                for i in range(2):
                    print(f"Board {i + 1}:")
                    print(gameStates[i].gameLog)
                    if not boardPlayers[i * 2] and not boardPlayers[i * 2 + 1]:
                        moveCount = len(gameStates[i].gameLog)
                    else:
                        moveCountCeil = ceil(len(gameStates[i].gameLog) / 2)
                        moveCountFloor = floor(len(gameStates[i].gameLog) / 2)
                        moveCount = moveCountCeil if not boardPlayers[i * 2] else moveCountFloor
                    print(f"Moves: {moveCount}")
                    print(f"Overall thinking time: {AIThinkingTime[i]}")
                    print(f"Overall positions calculated: {AIPositionCounter[i]}")
                    if moveCount != 0 and AIPositionCounter[i] != 0:
                        print(f"Average time per move: {AIThinkingTime[i] / moveCount}")
                        print(f"Average calculated positions per move: {AIPositionCounter[i] / moveCount}")
                        print(f"Average time per position: {AIThinkingTime[i] / AIPositionCounter[i]}")
                    if moveCount != 0 and AIExists:
                        print(f"Average possible moves per move: {AIMoveCounter[i] / moveCount}")
                names = plyrNames
                working = False
            elif e.type == pg.MOUSEBUTTONDOWN:
                if e.button == 1:
                    if toMenu_btn.checkForInput(location):
                        if createDialogWindow(screen, gameMenu["DW1"]):
                            pg.event.post(pg.event.Event(pg.QUIT))
                    if restart_btn.checkForInput(location):
                        if createDialogWindow(screen, gameMenu["DW2"]):
                            if AIThinking:
                                AIProcess.terminate()
                                AIProcess.join()
                                AIProcess.close()
                                AIThinking = False
                            gameStates = [GameState(), GameState()]
                            validMoves = [gameStates[0].getValidMoves(), gameStates[1].getValidMoves()]
                            AIThinkingTime = [0, 0]
                            AIPositionCounter = [0, 0]
                            AIMoveCounter = [len(validMoves[0][0]), 0]
                            returnQ = Queue()
                            activeBoard = 0
                            gameOver = False
                            selectedSq = [(), ()]
                            clicks = [[], []]
                            moveMade = [False, False]
                            hourglass = Hourglass(0, IMAGES["hourglass"], MARGIN, MARGIN_LEFT, SQ_SIZE, SCREEN_HEIGHT)
                            noAIActivePlayer = [0, 2]
                            hourglasses = [Hourglass(noAIActivePlayer[0], IMAGES["hourglass"], MARGIN, MARGIN_LEFT, SQ_SIZE, SCREEN_HEIGHT),
                                           Hourglass(noAIActivePlayer[1], IMAGES["hourglass"], MARGIN, MARGIN_LEFT, SQ_SIZE, SCREEN_HEIGHT)]
                            playerTurn = [(gameStates[0].whiteTurn and boardPlayers[0]) or (not gameStates[0].whiteTurn and boardPlayers[1]),
                                          (gameStates[1].whiteTurn and boardPlayers[2]) or (not gameStates[1].whiteTurn and boardPlayers[3])]
                            drawGameState(screen, gameStates, validMoves, selectedSq, toMenu_btn, restart_btn, AIExists)
                            pg.display.flip()
                    if not gameOver:
                        boardNum = -1
                        reserveBoardNum = -1
                        if MARGIN < location[0] < MARGIN + BOARD_SIZE and MARGIN < location[1] < MARGIN + BOARD_SIZE:
                            boardNum = 0
                        elif MARGIN_LEFT < location[0] < SCREEN_WIDTH - MARGIN and MARGIN < location[1] < MARGIN + BOARD_SIZE:
                            boardNum = 1
                        elif MARGIN + RESERVE_MARGIN < location[0] < MARGIN + BOARD_SIZE - RESERVE_MARGIN and (MARGIN - SQ_SIZE < location[1] < MARGIN or MARGIN + BOARD_SIZE < location[1] < MARGIN + BOARD_SIZE + SQ_SIZE):
                            reserveBoardNum = 0
                        elif MARGIN_LEFT + RESERVE_MARGIN < location[0] < MARGIN_LEFT + BOARD_SIZE - RESERVE_MARGIN and (MARGIN - SQ_SIZE < location[1] < MARGIN or MARGIN + BOARD_SIZE < location[1] < MARGIN + BOARD_SIZE + SQ_SIZE):
                            reserveBoardNum = 1
                        if boardNum != -1:
                            if not AIExists or (AIExists and activeBoard == boardNum):
                                if boardNum == 0:
                                    column = (location[0] - MARGIN) // SQ_SIZE
                                    row = (location[1] - MARGIN) // SQ_SIZE
                                else:
                                    column = (location[0] - MARGIN_LEFT) // SQ_SIZE
                                    row = (location[1] - MARGIN) // SQ_SIZE
                                    column = DIMENSION - column - 1
                                    row = DIMENSION - row - 1
                                if selectedSq[boardNum] == (column, row):
                                    selectedSq[boardNum] = ()
                                    clicks[boardNum] = []
                                else:
                                    selectedSq[boardNum] = (column, row)
                                    clicks[boardNum].append(deepcopy(selectedSq[boardNum]))
                                if len(clicks[boardNum]) == 2 and playerTurn[boardNum]:
                                    isReserve = False
                                    movedPiece = None
                                    color = "w" if clicks[boardNum][0][1] == 8 else "b"
                                    if clicks[boardNum][0][1] == -1 or clicks[boardNum][0][1] == 8:
                                        startSq = -clicks[boardNum][0][0] if clicks[boardNum][0][1] == -1 else clicks[boardNum][0][0]
                                        isReserve = True
                                        movedPiece = color + PIECES[clicks[boardNum][0][0]]
                                    else:
                                        startSq = bbOfSquares[clicks[boardNum][0][1]][clicks[boardNum][0][0]]
                                    if 0 <= clicks[boardNum][1][1] <= 7:
                                        endSq = bbOfSquares[clicks[boardNum][1][1]][clicks[boardNum][1][0]]
                                    elif clicks[boardNum][1][1] == -1 or clicks[boardNum][1][1] == 8:
                                        endSq = -1
                                    else:
                                        endSq = 0
                                    move = Move(startSq, endSq, gameStates[boardNum], movedPiece=movedPiece, isReserve=isReserve)
                                    for part in validMoves[boardNum]:
                                        for validMove in part:
                                            if move == validMove or (move.moveID == validMove.moveID and move.isPawnPromotion and len(validMoves[boardNum][2]) > 0):
                                                if move.isPawnPromotion:
                                                    pos, piece = getPromotion(screen, gameStates, names, boardNum, toMenu_btn, restart_btn, AIExists)
                                                    validMove.promotedTo = None if piece is None else piece[1]
                                                    validMove.promotedPiecePosition = pos
                                                if not (validMove.isPawnPromotion and validMove.promotedTo is None):
                                                    gameStates[boardNum].makeMove(validMove, gameStates[1 - boardNum])
                                                    for i in range(2):
                                                        validMoves[i] = gameStates[i].getValidMoves()
                                                        gameStates[i].updatePawnPromotionMoves(validMoves[i], gameStates[1 - i])
                                                    moveMade[boardNum] = True
                                                    selectedSq[boardNum] = ()
                                                    clicks[boardNum] = []
                                                    activeBoard = 1 - activeBoard
                                                    if AIExists:
                                                        hourglass = Hourglass(getCurrentPlayer(gameStates, activeBoard), IMAGES["hourglass"], MARGIN, MARGIN_LEFT, SQ_SIZE, SCREEN_HEIGHT)
                                                    else:
                                                        noAIActivePlayer[boardNum] = 5 - (1 - boardNum) * 4 - noAIActivePlayer[boardNum]
                                                        hourglasses[boardNum] = Hourglass(noAIActivePlayer[boardNum], IMAGES["hourglass"], MARGIN, MARGIN_LEFT, SQ_SIZE, SCREEN_HEIGHT)
                                                    if not soundPlayed and SETTINGS["sounds"]:
                                                        SOUNDS["move"].play()
                                                        soundPlayed = True
                                                break
                                    if not moveMade[boardNum]:
                                        clicks[boardNum] = [deepcopy(selectedSq[boardNum])]
                        elif reserveBoardNum != -1:
                            if not AIExists or (AIExists and activeBoard == reserveBoardNum):
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
                        drawGameState(screen, gameStates, validMoves, selectedSq, toMenu_btn, restart_btn, AIExists)
                        pg.display.flip()
        if not gameOver:
            gameOver = gameOverCheck(gameStates, AIExists)
        for i in range(2):
            if not gameOver and not playerTurn[i]:
                if AIExists and activeBoard == i:
                    playerNum = i * 2 + (0 if gameStates[i].whiteTurn else 1)
                    playerName = getPlayerName(gameStates[i], names[i * 2:(i + 1) * 2])
                    if not AIThinking:
                        AIMoveCounter[1 - i] += len(validMoves[1 - i][0]) + len(validMoves[1 - i][1]) + len(validMoves[1 - i][2])
                        print(f"{playerName} is thinking...")
                        AIThinking = True
                        AIProcess = Process(target=negaScoutMoveAI, args=(gameStates[i], gameStates[1 - i], validMoves[i], difficulties[playerNum], returnQ))
                        AIProcess.start()
                    if not AIProcess.is_alive():
                        AIMove, thinkingTime, positionCounter = returnQ.get()
                        AIThinkingTime[i] += thinkingTime
                        AIPositionCounter[i] += positionCounter
                        print(f"{playerName} came up with a move")
                        print(f"{playerName} thinking time: {thinkingTime} s")
                        print(f"{playerName} positions calculated: {positionCounter}")
                        if AIMove is None:
                            AIMove = randomMoveAI(validMoves)
                            print(f"{playerName} made a random move")
                        if AIMove.isPawnPromotion:
                            possiblePromotions = calculatePossiblePromotions(gameStates, i)
                            possibleRequiredPromotions = [bbOfSquares[key[1]][key[0]] for key, value in possiblePromotions.items() if value[1] == AIMove.promotedTo]
                            promotion = possibleRequiredPromotions[randint(0, len(possibleRequiredPromotions) - 1)]
                            AIMove = Move(AIMove.startSquare, AIMove.endSquare, gameStates[i], movedPiece=AIMove.movedPiece, promotedTo=AIMove.promotedTo, promotedPiecePosition=promotion)
                        gameStates[i].makeMove(AIMove, gameStates[1 - i])
                        for j in range(2):
                            validMoves[j] = gameStates[j].getValidMoves()
                            gameStates[j].updatePawnPromotionMoves(validMoves[j], gameStates[1 - j])
                        if not gameOver:
                            gameOver = gameOverCheck(gameStates, AIExists)
                        moveMade[i] = True
                        activeBoard = 1 - activeBoard
                        hourglass = Hourglass(getCurrentPlayer(gameStates, activeBoard), IMAGES["hourglass"], MARGIN, MARGIN_LEFT, SQ_SIZE, SCREEN_HEIGHT)
                        AIThinking = False
                        selectedSq[i] = ()
                        clicks[i] = []
            if moveMade[i]:
                drawGameState(screen, gameStates, validMoves, selectedSq, toMenu_btn, restart_btn, AIExists)
                if not soundPlayed and SETTINGS["sounds"]:
                    SOUNDS["move"].play()
                soundPlayed = False
                pg.display.flip()
                moveMade[i] = False
        pg.display.flip()


def drawEndGameText(screen: pg.Surface, gameStates: list, AIExists: bool):
    if (gameStates[0].checkmate and not gameStates[0].whiteTurn) or (gameStates[1].checkmate and gameStates[1].whiteTurn):
        drawTopText(screen, endGame["T1"])
    elif gameStates[0].stalemate and gameStates[1].stalemate:
        drawTopText(screen, endGame["D"])
    elif AIExists and (gameStates[0].stalemate or gameStates[1].stalemate):
        drawTopText(screen, endGame["D"])
    elif (gameStates[0].checkmate and gameStates[0].whiteTurn) or (gameStates[1].checkmate and not gameStates[1].whiteTurn):
        drawTopText(screen, endGame["T2"])


def gameOverCheck(gameStates: list, AIExists: bool):
    if (gameStates[0].checkmate and not gameStates[0].whiteTurn) or (gameStates[1].checkmate and gameStates[1].whiteTurn):
        return True
    elif gameStates[0].stalemate and gameStates[1].stalemate:
        return True
    elif AIExists and (gameStates[0].stalemate or gameStates[1].stalemate):
        return True
    elif (gameStates[0].checkmate and gameStates[0].whiteTurn) or (gameStates[1].checkmate and not gameStates[1].whiteTurn):
        return True
    # if len(gameStates[1].gameLog) == 30:
    #     return True
    # if len(gameStates[0].gameLog) == 1:
    #     return True
    return False


def getCurrentPlayer(gameStates: list, activeBoard: int):
    if activeBoard == 0 and gameStates[0].whiteTurn:
        return 0
    elif activeBoard == 0 and not gameStates[0].whiteTurn:
        return 1
    elif activeBoard == 1 and gameStates[1].whiteTurn:
        return 2
    else:
        return 3


def highlightSq(screen: pg.Surface, gameStates: list, validMoves: list, selectedSq: list):
    for i in range(2):
        if selectedSq[i] != ():
            color = "w" if selectedSq[i][1] == 8 else "b"
            isReserve = True if selectedSq[i][1] == -1 or selectedSq[i][1] == 8 else False
            square = bbOfSquares[selectedSq[i][1]][selectedSq[i][0]] if not isReserve else -abs(selectedSq[i][0])
            piece = gameStates[i].getPieceBySquare(square) if not isReserve else color + PIECES[selectedSq[i][0]]
            if piece is not None:
                s = pg.Surface((SQ_SIZE, SQ_SIZE))
                s.fill(pg.Color(110, 90, 0))
                if not isReserve:
                    if i == 0:
                        screen.blit(s, (selectedSq[i][0] * SQ_SIZE + MARGIN, selectedSq[i][1] * SQ_SIZE + MARGIN))
                    else:
                        screen.blit(s, ((DIMENSION - 1 - selectedSq[i][0]) * SQ_SIZE + MARGIN_LEFT,
                                        (DIMENSION - 1 - selectedSq[i][1]) * SQ_SIZE + MARGIN))
                else:
                    if i == 0:
                        screen.blit(s, ((selectedSq[i][0] - 1) * SQ_SIZE + MARGIN + RESERVE_MARGIN, selectedSq[i][1] * SQ_SIZE + MARGIN))
                    else:
                        screen.blit(s, ((selectedSq[i][0] - 1) * SQ_SIZE + MARGIN_LEFT + RESERVE_MARGIN,
                                        (DIMENSION - 1 - selectedSq[i][1]) * SQ_SIZE + MARGIN))
                s.set_alpha(100)
                s.fill(pg.Color("yellow"))
                if not isReserve or (isReserve and gameStates[i].reserve[color][piece[1]] > 0):
                    if piece[0] == ("w" if gameStates[i].whiteTurn else "b"):
                        endSquares = []
                        for part in validMoves[i]:
                            for move in part:
                                if move.startSquare == square and move.endSquare not in endSquares:
                                    endSquares.append(move.endSquare)
                                    if i == 0:
                                        screen.blit(s, (move.endLoc % 8 * SQ_SIZE + MARGIN, move.endLoc // 8 * SQ_SIZE + MARGIN))
                                    else:
                                        r = DIMENSION - 1 - move.endLoc // 8
                                        c = DIMENSION - 1 - move.endLoc % 8
                                        screen.blit(s, (c * SQ_SIZE + MARGIN_LEFT, r * SQ_SIZE + MARGIN))


def highlightLastMove(screen: pg.Surface, gameStates: list, selectedSq: list):
    for i in range(2):
        piece = None
        if selectedSq[i] != ():
            color = "w" if selectedSq[i][1] == 8 else "b"
            isReserve = True if selectedSq[i][1] == -1 or selectedSq[i][1] == 8 else False
            square = bbOfSquares[selectedSq[i][1]][selectedSq[i][0]] if not isReserve else -1
            piece = gameStates[i].getPieceBySquare(square) if not isReserve else color + PIECES[selectedSq[i][0]]
            if isReserve and (gameStates[i].reserve[color][PIECES[selectedSq[i][0]]] == 0 or color == ("b" if gameStates[i].whiteTurn else "w")):
                piece = None
        if piece is None or selectedSq[i] == ():
            if len(gameStates[i].gameLog) != 0:
                lastMove = gameStates[i].gameLog[-1]
                s = pg.Surface((SQ_SIZE, SQ_SIZE))
                s.set_alpha(100)
                s.fill(pg.Color(0, 0, 255))
                if not lastMove.isReserve:
                    if i == 0:
                        screen.blit(s, (lastMove.startLoc % 8 * SQ_SIZE + MARGIN, lastMove.startLoc // 8 * SQ_SIZE + MARGIN))
                        screen.blit(s, (lastMove.endLoc % 8 * SQ_SIZE + MARGIN, lastMove.endLoc // 8 * SQ_SIZE + MARGIN))
                    else:
                        screen.blit(s, ((DIMENSION - 1 - lastMove.startLoc % 8) * SQ_SIZE + MARGIN_LEFT,
                                        (DIMENSION - 1 - lastMove.startLoc // 8) * SQ_SIZE + MARGIN))
                        screen.blit(s, ((DIMENSION - 1 - lastMove.endLoc % 8) * SQ_SIZE + MARGIN_LEFT,
                                        (DIMENSION - 1 - lastMove.endLoc // 8) * SQ_SIZE + MARGIN))
                else:
                    if i == 0:
                        marginTop = MARGIN - SQ_SIZE if lastMove.startLoc < 0 else MARGIN + BOARD_SIZE
                        screen.blit(s, ((abs(lastMove.startLoc) - 1) * SQ_SIZE + MARGIN + RESERVE_MARGIN, marginTop))
                        screen.blit(s, (lastMove.endLoc % 8 * SQ_SIZE + MARGIN, lastMove.endLoc // 8 * SQ_SIZE + MARGIN))
                    else:
                        marginTop = MARGIN - SQ_SIZE if lastMove.startLoc > 0 else MARGIN + BOARD_SIZE
                        screen.blit(s, ((abs(lastMove.startLoc) - 1) * SQ_SIZE + MARGIN_LEFT + RESERVE_MARGIN, marginTop))
                        screen.blit(s, ((DIMENSION - 1 - lastMove.endLoc % 8) * SQ_SIZE + MARGIN_LEFT,
                                        (DIMENSION - 1 - lastMove.endLoc // 8) * SQ_SIZE + MARGIN))


def calculatePossiblePromotions(gameStates: list, promotion: int):
    possiblePromotions = {}
    if promotion == 0:
        color = "w" if gameStates[0].whiteTurn else "b"
        for piece in POSSIBLE_PIECES_TO_PROMOTE:
            splitPositions = numSplit(gameStates[1].bbOfPieces[color + piece])
            for position in splitPositions:
                if gameStates[1].canBeRemoved(position, "w" if gameStates[0].whiteTurn else "b"):
                    pos = getPower(position)
                    possiblePromotions[(pos % 8, pos // 8)] = color + piece
    elif promotion == 1:
        color = "w" if gameStates[1].whiteTurn else "b"
        for piece in POSSIBLE_PIECES_TO_PROMOTE:
            splitPositions = numSplit(gameStates[0].bbOfPieces[color + piece])
            for position in splitPositions:
                if gameStates[0].canBeRemoved(position, "w" if gameStates[1].whiteTurn else "b"):
                    pos = getPower(position)
                    possiblePromotions[(pos % 8, pos // 8)] = color + piece
    return possiblePromotions


def highlightPossiblePromotions(screen: pg.Surface, possiblePromotions: dict, promotion: int):
    if possiblePromotions != {}:
        if promotion == 0:
            for column, row in possiblePromotions.keys():
                screen.blit(IMAGES["frame"], pg.Rect((DIMENSION - 1 - column) * SQ_SIZE + MARGIN_LEFT, (DIMENSION - 1 - row) * SQ_SIZE + MARGIN, SQ_SIZE, SQ_SIZE))
        elif promotion == 1:
            for column, row in possiblePromotions.keys():
                screen.blit(IMAGES["frame"], pg.Rect(column * SQ_SIZE + MARGIN, row * SQ_SIZE + MARGIN, SQ_SIZE, SQ_SIZE))


def drawGameState(screen: pg.Surface, gameStates: list, validMoves: list, selectedSq: list, toMenu_btn: RadioButton, restart_btn: RadioButton, AIExists: bool, promotion=-1, possiblePromotions=None):
    # screen.fill(PALETTE["brown"])
    screen.blit(IMAGES["BG"], (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
    drawEndGameText(screen, gameStates, AIExists)
    drawPlayersNames(screen)
    drawBoard(screen)
    for btn in [toMenu_btn, restart_btn]:
        btn.update(screen)
    highlightPossiblePromotions(screen, possiblePromotions, promotion)
    if promotion == -1:
        highlightLastMove(screen, gameStates, selectedSq)
        highlightSq(screen, gameStates, validMoves, selectedSq)
    drawPieces(screen, gameStates)


def drawBoard(screen: pg.Surface):
    s2 = pg.Surface((BOARD_SIZE + 4, BOARD_SIZE + 4))
    s2.set_alpha(100)
    s2.fill(pg.Color("black"))
    screen.blit(s2, pg.Rect(MARGIN - 2, MARGIN - 2, BOARD_SIZE + 4, BOARD_SIZE + 4))
    screen.blit(IMAGES["board"], pg.Rect(MARGIN, MARGIN, BOARD_SIZE, BOARD_SIZE))
    screen.blit(s2, pg.Rect(MARGIN_LEFT - 2, MARGIN - 2, BOARD_SIZE + 4, BOARD_SIZE + 4))
    screen.blit(IMAGES["board"], pg.Rect(MARGIN_LEFT, MARGIN, BOARD_SIZE, BOARD_SIZE))


def drawPieces(screen: pg.Surface, gameStates: list):
    marginTop1 = MARGIN - SQ_SIZE
    marginTop2 = MARGIN + BOARD_SIZE
    font = pg.font.SysFont("Helvetica", FONT_SIZE, True, False)
    for i in range(2):
        k = {"w": 0, "b": 0}
        marginLeft = MARGIN if i == 0 else MARGIN_LEFT
        for piece in COLORED_PIECES:
            splitPositions = numSplit(gameStates[i].bbOfPieces[piece])
            for position in splitPositions:
                pos = getPower(position) if i == 0 else 63 - getPower(position)
                screen.blit(IMAGES[piece], pg.Rect(pos % 8 * SQ_SIZE + marginLeft, pos // 8 * SQ_SIZE + MARGIN, SQ_SIZE, SQ_SIZE))
            if piece != "wK" and piece != "bK":
                marginTop = marginTop1 if (piece[0] == "b" and i == 0) or (piece[0] == "w" and i == 1) else marginTop2
                marginTextTop = -5 if (piece[0] == "b" and i == 0) or (piece[0] == "w" and i == 1) else SQ_SIZE + 5
                marg = marginLeft + k[piece[0]] * SQ_SIZE + RESERVE_MARGIN
                if gameStates[i].reserve[piece[0]][piece[1]] > 0:
                    screen.blit(IMAGES[piece], pg.Rect(marg, marginTop, SQ_SIZE, SQ_SIZE))
                    tmp_lbl = Label(f"{gameStates[i].reserve[piece[0]][piece[1]]}", (marg + SQ_SIZE // 2 - 1, marginTop + marginTextTop), font, shift=1)
                    tmp_lbl.update(screen)
                elif gameStates[i].reserve[piece[0]][piece[1]] == 0:
                    screen.blit(IMAGES[f"e{piece[1]}"], pg.Rect(marg, marginTop, SQ_SIZE, SQ_SIZE))
                k[piece[0]] += 1


def getPlayerName(gameState: GameState, playerNames: list):
    if gameState.whiteTurn:
        return playerNames[0]
    else:
        return playerNames[1]


def getPromotion(screen: pg.Surface, gameStates: list, playerNames: list, boardNum: int, toMenu_btn: RadioButton, restart_btn: RadioButton, AIExists: bool):
    possiblePromotions = calculatePossiblePromotions(gameStates, boardNum)
    if possiblePromotions == {}:
        return 0, None
    drawGameState(screen, gameStates, [], [], toMenu_btn, restart_btn, AIExists, promotion=boardNum, possiblePromotions=possiblePromotions)
    playerName = getPlayerName(gameStates[boardNum], playerNames[boardNum * 2:(boardNum + 1) * 2])
    drawTopText(screen, f"{playerName} {promText}")
    pg.display.flip()
    working = True
    while working:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.event.post(pg.event.Event(pg.QUIT))
                return 0, None
            if e.type == pg.MOUSEBUTTONDOWN:
                if e.button == 1:
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
    font = pg.font.SysFont("Helvetica", FONT_SIZE * 2, True, False)
    topText_lbl = Label(text, (SCREEN_WIDTH // 2, SQ_SIZE), font)
    topText_lbl.update(screen)


def drawPlayersNames(screen: pg.Surface):
    font = pg.font.SysFont("Helvetica", FONT_SIZE * 7 // 4, True, False)
    xBoard1 = MARGIN + BOARD_SIZE // 2
    xBoard2 = MARGIN_LEFT + BOARD_SIZE // 2
    yTop = MARGIN // 2
    yBot = SCREEN_HEIGHT - MARGIN // 2
    player1_lbl = Label(names[0], (xBoard1, yBot), font, shift=2)
    player2_lbl = Label(names[1], (xBoard1, yTop), font, shift=2)
    player3_lbl = Label(names[2], (xBoard2, yTop), font, shift=2)
    player4_lbl = Label(names[3], (xBoard2, yBot), font, shift=2)
    for lbl in [player1_lbl, player2_lbl, player3_lbl, player4_lbl]:
        lbl.update(screen)


def drawMenu(screen: pg.Surface, menuName_lbl: Label):
    # screen.fill(PALETTE["brown"])
    screen.blit(IMAGES["BG"], (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(IMAGES["header"], (SCREEN_WIDTH // 8, 0, SCREEN_WIDTH // 4 * 3, SCREEN_HEIGHT // 5))
    menuName_lbl.update(screen)


def createMainMenu(screen: pg.Surface):
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
        for button in [newGame_btn, settings_btn, quit_btn]:
            button.changeColor(mousePos)
            button.update(screen)
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
        back_btn.changeColor(mousePos)
        for item in [lang_img, sound_img, back_btn, sound_btn, sound_lbl, lang_btn, lang_lbl]:
            item.update(screen)
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
    for i, ddm_lst in enumerate([newGameMenu["DDM1"], newGameMenu["DDM2"], newGameMenu["DDM3"], newGameMenu["DDM4"]]):
        ddm_lst[0] = ddm_lst[difficulties[i]]
        if difficulties[i] == 1:
            names[i] = constNames[i]
        elif difficulties[i] in [2, 3, 4]:
            names[i] = f"{constNames[i]} {AItxt} ({difficultiesNames[difficulties[i]]})"
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
        for item in [board1_img, board2_img, player1_ddm, player2_ddm, player3_ddm, player4_ddm]:
            item.update(screen)
        for btn in player1_ddm.buttons + player2_ddm.buttons + player3_ddm.buttons + player4_ddm.buttons:
            btn.changeColor(mousePos)
        for btn in [back_btn, play_btn]:
            btn.update(screen)
            btn.changeColor(mousePos)
        for e in pg.event.get():
            if e.type == pg.QUIT:
                working = False
            elif e.type == pg.MOUSEBUTTONDOWN:
                if e.button == 1:
                    if back_btn.checkForInput(mousePos):
                        working = False
                    if play_btn.checkForInput(mousePos):
                        main(screen)
                        working = False
                    for i, ddm in enumerate([player1_ddm, player2_ddm, player3_ddm, player4_ddm]):
                        if ddm.checkForInput(mousePos):
                            ddm.switch()
                        choice = ddm.checkForChoice(mousePos)
                        if choice == 1:
                            boardPlayers[i] = True
                            names[i] = constNames[i]
                        elif choice in [2, 3, 4]:
                            boardPlayers[i] = False
                            names[i] = f"{constNames[i]} {AItxt} ({difficultiesNames[choice]})"
                        if choice is not None:
                            difficulties[i] = choice
        pg.display.flip()


def createDialogWindow(screen: pg.Surface, text: str):
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
    mainScreen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pg.display.set_caption("SwiChess")
    pg.display.set_icon(IMAGES["icon"])
    createMainMenu(mainScreen)
    pg.quit()
