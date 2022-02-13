from TestDLL import getPower, numSplit
from Engine import DIMENSION, GameState, Move, PIECES, bbOfSquares, COLORED_PIECES, POSSIBLE_PIECES_TO_PROMOTE
import pygame as pg
from AI import randomMoveAI, negaScoutMoveAI
from math import ceil, floor
from multiprocessing import Process, Queue
from copy import deepcopy
from random import randint
from UI import Button, Hourglass

pg.init()
# SCREEN_WIDTH, SCREEN_HEIGHT = pg.display.Info().current_w, pg.display.Info().current_h
SCREEN_WIDTH, SCREEN_HEIGHT = 960, 540
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
IMAGES = {}
SOUNDS = {}


def loadResources():
    for piece in COLORED_PIECES:
        IMAGES[piece] = pg.transform.scale(pg.image.load(f"images/{SKIN_PACK}/{piece}.png"), (SQ_SIZE, SQ_SIZE))
    for piece in EMPTY_PIECES:
        IMAGES[piece] = pg.transform.scale(pg.image.load(f"images/{SKIN_PACK}/{piece}.png"), (SQ_SIZE, SQ_SIZE))
    IMAGES["icon"] = pg.image.load("images/icon.png")
    IMAGES["board"] = pg.transform.scale(pg.image.load("images/board.png"), (BOARD_SIZE, BOARD_SIZE))
    IMAGES["frame"] = pg.transform.scale(pg.image.load("images/frame.png"), (SQ_SIZE, SQ_SIZE))
    IMAGES["frame"].set_alpha(200)
    IMAGES["hourglass"] = pg.transform.scale(pg.image.load("images/hourglass.png"), (SQ_SIZE, SQ_SIZE))
    IMAGES["menu_button"] = pg.transform.scale(pg.image.load("images/menu_button.png"), (SQ_SIZE, SQ_SIZE))
    SOUNDS["move"] = pg.mixer.Sound("sounds/move.wav")
    # IMAGES["BG"] = pg.transform.scale(pg.image.load("images/BG.png"), (SCREEN_WIDTH, SCREEN_HEIGHT))


def main(screen: pg.Surface):
    clock = pg.time.Clock()
    # boardPlayers = [(True, True), (True, True)]
    boardPlayers = [(False, False), (False, False)]
    playerNames = ["Player 1", "Player 2", "Player 3", "Player 4"]
    for i in range(4):
        if not boardPlayers[i * (i - 1) * (-2 * i + 7) // 6][i * (i - 2) * (2 * i - 5) // 3]:
            playerNames[i] += " (AI)"
    AIExists = not (boardPlayers[0][0] and boardPlayers[0][1] and boardPlayers[1][0] and boardPlayers[1][1])
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
    AIProcess = Process()
    returnQ = Queue()
    selectedSq = [(), ()]
    clicks = [[], []]
    hourglass = Hourglass(0, IMAGES["hourglass"], MARGIN, MARGIN_LEFT, SQ_SIZE, SCREEN_HEIGHT)
    noAIActivePlayer = [0, 2]
    hourglasses = [Hourglass(noAIActivePlayer[0], IMAGES["hourglass"], MARGIN, MARGIN_LEFT, SQ_SIZE, SCREEN_HEIGHT),
                   Hourglass(noAIActivePlayer[1], IMAGES["hourglass"], MARGIN, MARGIN_LEFT, SQ_SIZE, SCREEN_HEIGHT)]
    toMenu_btn = Button(IMAGES["menu_button"], (SCREEN_WIDTH - SQ_SIZE, SQ_SIZE), "", None, None, None)
    while working:
        clock.tick(FPS)
        playerTurn = [(gameStates[0].whiteTurn and boardPlayers[0][0]) or (not gameStates[0].whiteTurn and boardPlayers[0][1]),
                      (gameStates[1].whiteTurn and boardPlayers[1][0]) or (not gameStates[1].whiteTurn and boardPlayers[1][1])]
        drawGameState(screen, gameStates, validMoves, playerNames, selectedSq, toMenu_btn)
        if not gameOver and AIExists:
            hourglass.update(screen)
        elif not gameOver and not AIExists:
            hourglasses[0].update(screen)
            hourglasses[1].update(screen)
        for e in pg.event.get():
            if e.type == pg.QUIT:
                gameOver = True
                if AIThinking:
                    AIProcess.terminate()
                    AIProcess.join()
                    AIProcess.close()
                    AIThinking = False
                for i in range(2):
                    print(f"Board {i + 1}:")
                    print(gameStates[i].gameLog)
                    if not boardPlayers[i][0] and not boardPlayers[i][1]:
                        moveCount = len(gameStates[i].gameLog)
                    else:
                        moveCountCeil = ceil(len(gameStates[i].gameLog) / 2)
                        moveCountFloor = floor(len(gameStates[i].gameLog) / 2)
                        moveCount = moveCountCeil if not boardPlayers[i][0] else moveCountFloor
                    print(f"Moves: {moveCount}")
                    print(f"Overall thinking time: {AIThinkingTime[i]}")
                    print(f"Overall positions calculated: {AIPositionCounter[i]}")
                    if moveCount != 0 and AIPositionCounter[i] != 0:
                        print(f"Average time per move: {AIThinkingTime[i] / moveCount}")
                        print(f"Average calculated positions per move: {AIPositionCounter[i] / moveCount}")
                        print(f"Average time per position: {AIThinkingTime[i] / AIPositionCounter[i]}")
                working = False
                pg.event.post(pg.event.Event(pg.QUIT))
            elif e.type == pg.MOUSEBUTTONDOWN:
                if e.button == 1:
                    if not gameOver:
                        location = pg.mouse.get_pos()
                        boardNum = -1
                        reserveBoardNum = -1
                        toMenu = False
                        if MARGIN < location[0] < MARGIN + BOARD_SIZE and MARGIN < location[1] < MARGIN + BOARD_SIZE:
                            boardNum = 0
                        elif MARGIN_LEFT < location[0] < SCREEN_WIDTH - MARGIN and MARGIN < location[1] < MARGIN + BOARD_SIZE:
                            boardNum = 1
                        elif MARGIN + RESERVE_MARGIN < location[0] < MARGIN + BOARD_SIZE - RESERVE_MARGIN and (MARGIN - SQ_SIZE < location[1] < MARGIN or MARGIN + BOARD_SIZE < location[1] < MARGIN + BOARD_SIZE + SQ_SIZE):
                            reserveBoardNum = 0
                        elif MARGIN_LEFT + RESERVE_MARGIN < location[0] < MARGIN_LEFT + BOARD_SIZE - RESERVE_MARGIN and (MARGIN - SQ_SIZE < location[1] < MARGIN or MARGIN + BOARD_SIZE < location[1] < MARGIN + BOARD_SIZE + SQ_SIZE):
                            reserveBoardNum = 1
                        elif toMenu_btn.checkForInput(location):
                            toMenu = True
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
                                                    pos, piece = getPromotion(screen, gameStates, playerNames, boardNum, toMenu_btn)
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
                                                    if not soundPlayed:
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
                        elif toMenu:
                            gameOver = True
                            if AIThinking:
                                AIProcess.terminate()
                                AIProcess.join()
                                AIProcess.close()
                                AIThinking = False
                            for i in range(2):
                                print(f"Board {i + 1}:")
                                print(gameStates[i].gameLog)
                                if not boardPlayers[i][0] and not boardPlayers[i][1]:
                                    moveCount = len(gameStates[i].gameLog)
                                else:
                                    moveCountCeil = ceil(len(gameStates[i].gameLog) / 2)
                                    moveCountFloor = floor(len(gameStates[i].gameLog) / 2)
                                    moveCount = moveCountCeil if not boardPlayers[i][0] else moveCountFloor
                                print(f"Moves: {moveCount}")
                                print(f"Overall thinking time: {AIThinkingTime[i]}")
                                print(f"Overall positions calculated: {AIPositionCounter[i]}")
                                if moveCount != 0 and AIPositionCounter[i] != 0:
                                    print(f"Average time per move: {AIThinkingTime[i] / moveCount}")
                                    print(f"Average calculated positions per move: {AIPositionCounter[i] / moveCount}")
                                    print(f"Average time per position: {AIThinkingTime[i] / AIPositionCounter[i]}")
                            working = False
                        else:
                            selectedSq = [(), ()]
                            clicks = [[], []]
                        drawGameState(screen, gameStates, validMoves, playerNames, selectedSq, toMenu_btn)
                        pg.display.flip()
            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_r:
                    if AIThinking:
                        AIProcess.terminate()
                        AIProcess.join()
                        AIProcess.close()
                        AIThinking = False
                    gameStates = [GameState(), GameState()]
                    validMoves = [gameStates[0].getValidMoves(), gameStates[1].getValidMoves()]
                    AIThinkingTime = [0, 0]
                    AIPositionCounter = [0, 0]
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
                    playerTurn = [(gameStates[0].whiteTurn and boardPlayers[0][0]) or (not gameStates[0].whiteTurn and boardPlayers[0][1]),
                                  (gameStates[1].whiteTurn and boardPlayers[1][0]) or (not gameStates[1].whiteTurn and boardPlayers[1][1])]
                    drawGameState(screen, gameStates, validMoves, playerNames, selectedSq, toMenu_btn)
                    pg.display.flip()
        if not gameOver:
            gameOver = gameOverCheck(gameStates, AIExists)
        for i in range(2):
            if not gameOver and not playerTurn[i]:
                if AIExists and activeBoard == i:
                    playerName = getPlayerName(gameStates[i], playerNames[i * 2:(i + 1) * 2])
                    if not AIThinking:
                        print(f"{playerName} is thinking...")
                        AIThinking = True
                        AIProcess = Process(target=negaScoutMoveAI, args=(gameStates[i], gameStates[1 - i], validMoves[i], returnQ))
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
                drawGameState(screen, gameStates, validMoves, playerNames, selectedSq, toMenu_btn)
                if not soundPlayed:
                    SOUNDS["move"].play()
                soundPlayed = False
                pg.display.flip()
                moveMade[i] = False
        if (gameStates[0].checkmate and not gameStates[0].whiteTurn) or (gameStates[1].checkmate and gameStates[1].whiteTurn):
            drawTopText(screen, "Team 1 wins")
        elif gameStates[0].stalemate and gameStates[1].stalemate:
            drawTopText(screen, "Draw")
        elif AIExists and (gameStates[0].stalemate or gameStates[1].stalemate):
            drawTopText(screen, "Draw")
        elif (gameStates[0].checkmate and gameStates[0].whiteTurn) or (gameStates[1].checkmate and not gameStates[1].whiteTurn):
            drawTopText(screen, "Team 2 wins")
        pg.display.flip()


def gameOverCheck(gameStates: list, AIExists: bool):
    if (gameStates[0].checkmate and not gameStates[0].whiteTurn) or (gameStates[1].checkmate and gameStates[1].whiteTurn):
        return True
    elif gameStates[0].stalemate and gameStates[1].stalemate:
        return True
    elif AIExists and (gameStates[0].stalemate or gameStates[1].stalemate):
        return True
    elif (gameStates[0].checkmate and gameStates[0].whiteTurn) or (gameStates[1].checkmate and not gameStates[1].whiteTurn):
        return True
    # if len(gameStates[1].gameLog) == 20:
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


def drawGameState(screen: pg.Surface, gameStates: list, validMoves: list, playerNames: list, selectedSq: list, toMenu_btn: Button, promotion=-1, possiblePromotions=None):
    screen.fill((181, 136, 99))
    # screen.blit(IMAGES["BG"], (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
    drawPlayersNames(screen, playerNames)
    drawBoard(screen)
    toMenu_btn.update(screen)
    highlightPossiblePromotions(screen, possiblePromotions, promotion)
    if promotion == -1:
        highlightLastMove(screen, gameStates, selectedSq)
        highlightSq(screen, gameStates, validMoves, selectedSq)
    drawPieces(screen, gameStates)


def drawBoard(screen: pg.Surface):
    s2 = pg.Surface((BOARD_SIZE, BOARD_SIZE))
    s2.set_alpha(80)
    s2.fill(pg.Color("black"))
    screen.blit(s2, pg.Rect(MARGIN + 3, MARGIN + 3, BOARD_SIZE, BOARD_SIZE))
    screen.blit(IMAGES["board"], pg.Rect(MARGIN, MARGIN, BOARD_SIZE, BOARD_SIZE))
    screen.blit(s2, pg.Rect(MARGIN_LEFT + 3, MARGIN + 3, BOARD_SIZE, BOARD_SIZE))
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
                    textObj = font.render(f"{gameStates[i].reserve[piece[0]][piece[1]]}", False, pg.Color("black"))
                    text_rect = textObj.get_rect(center=(marg + SQ_SIZE // 2, marginTop + marginTextTop))
                    screen.blit(textObj, text_rect)
                elif gameStates[i].reserve[piece[0]][piece[1]] == 0:
                    screen.blit(IMAGES[f"e{piece[1]}"], pg.Rect(marg, marginTop, SQ_SIZE, SQ_SIZE))
                k[piece[0]] += 1


def getPlayerName(gameState: GameState, playerNames: list):
    if gameState.whiteTurn:
        return playerNames[0]
    else:
        return playerNames[1]


def getPromotion(screen: pg.Surface, gameStates: list, playerNames: list, boardNum: int, toMenu_btn: Button):
    possiblePromotions = calculatePossiblePromotions(gameStates, boardNum)
    if possiblePromotions == {}:
        return 0, None
    drawGameState(screen, gameStates, [], playerNames, [], toMenu_btn, promotion=boardNum, possiblePromotions=possiblePromotions)
    playerName = getPlayerName(gameStates[boardNum], playerNames[boardNum * 2:(boardNum + 1) * 2])
    drawTopText(screen, f"{playerName} chooses a piece to promote")
    pg.display.flip()
    working = True
    while working:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.event.post(pg.event.Event(256))
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
    textObj = font.render(text, False, pg.Color("gray"))
    textLocation = pg.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT).move(SCREEN_WIDTH // 2 - textObj.get_width() // 2,
                                                                   textObj.get_height() // 2)
    screen.blit(textObj, textLocation)
    textObj = font.render(text, False, pg.Color("black"))
    screen.blit(textObj, textLocation.move(2, 2))


def drawPlayersNames(screen: pg.Surface, names: list):
    font = pg.font.SysFont("Helvetica", int(FONT_SIZE * 1.5), True, False)
    textObj = font.render(names[0], False, pg.Color("gray"))

    textLocation = pg.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT).move(MARGIN + (BOARD_SIZE - textObj.get_width()) // 2,
                                                                   SCREEN_HEIGHT - (MARGIN + textObj.get_height()) // 2)
    screen.blit(textObj, textLocation)
    textObj = font.render(names[0], False, pg.Color("black"))
    screen.blit(textObj, textLocation.move(2, 2))

    textObj = font.render(names[1], False, pg.Color("gray"))
    textLocation = pg.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT).move(MARGIN + (BOARD_SIZE - textObj.get_width()) // 2,
                                                                   (MARGIN - textObj.get_height()) // 2)
    screen.blit(textObj, textLocation)
    textObj = font.render(names[1], False, pg.Color("black"))
    screen.blit(textObj, textLocation.move(2, 2))

    textObj = font.render(names[2], False, pg.Color("gray"))
    textLocation = pg.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT).move(MARGIN_LEFT + (BOARD_SIZE - textObj.get_width()) // 2,
                                                                   (MARGIN - textObj.get_height()) // 2)
    screen.blit(textObj, textLocation)
    textObj = font.render(names[2], False, pg.Color("black"))
    screen.blit(textObj, textLocation.move(2, 2))

    textObj = font.render(names[3], False, pg.Color("gray"))
    textLocation = pg.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT).move(MARGIN_LEFT + (BOARD_SIZE - textObj.get_width()) // 2,
                                                                   SCREEN_HEIGHT - (MARGIN + textObj.get_height()) // 2)
    screen.blit(textObj, textLocation)
    textObj = font.render(names[3], False, pg.Color("black"))
    screen.blit(textObj, textLocation.move(2, 2))


def drawMenu(screen: pg.Surface, name: str):
    screen.fill((181, 136, 99))
    drawMenuName(screen, name)


def drawMenuName(screen: pg.Surface, name: str):
    font = pg.font.SysFont("Helvetica", FONT_SIZE * 5, True, False)
    textObj = font.render(name, False, pg.Color("gray"))
    pg.draw.polygon(screen, (127, 97, 70), ((0, 0), (SCREEN_WIDTH, 0), (SCREEN_WIDTH, textObj.get_height() // 2),
                                            (textObj.get_width() + textObj.get_height() // 2 + 2, textObj.get_height() // 2),
                                            (textObj.get_width() + 2, textObj.get_height() + 2), (0, textObj.get_height() + 2)))
    textLocation = pg.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT).move(2, 2)
    screen.blit(textObj, textLocation)
    textObj = font.render(name, False, pg.Color("black"))
    screen.blit(textObj, textLocation.move(2, 2))


def createMainMenu(screen: pg.Surface):
    working = True
    clock = pg.time.Clock()
    font = pg.font.SysFont("Helvetica", FONT_SIZE * 3, True, False)
    createGame_btn = Button(None, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - FONT_SIZE * 5), "Create a game", font, "gray", "black")
    settings_btn = Button(None, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), "Settings", font, "gray", "black")
    quit_btn = Button(None, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + FONT_SIZE * 5), "Quit", font, "gray", "black")
    while working:
        mousePos = pg.mouse.get_pos()
        clock.tick(FPS)
        drawMenu(screen, "SwiChess")
        for button in [createGame_btn, settings_btn, quit_btn]:
            button.changeColor(mousePos)
            button.update(screen)
        for e in pg.event.get():
            if e.type == pg.QUIT:
                working = False
            elif e.type == pg.MOUSEBUTTONDOWN:
                if e.button == 1:
                    if createGame_btn.checkForInput(mousePos):
                        main(screen)
                    if settings_btn.checkForInput(mousePos):
                        pass
                    if quit_btn.checkForInput(mousePos):
                        working = False
        pg.display.flip()


if __name__ == "__main__":
    mainScreen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    loadResources()
    pg.display.set_caption("SwiChess")
    pg.display.set_icon(IMAGES["icon"])
    createMainMenu(mainScreen)
    # main(mainScreen)
    pg.quit()
