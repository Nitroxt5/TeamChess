import Engine
import pygame as pg
# import pygame_menu as pgm
import AI
from math import ceil, floor
from multiprocessing import Process, Queue
from copy import deepcopy
from random import randint

pg.init()
SCREEN_WIDTH, SCREEN_HEIGHT = pg.display.Info().current_w, pg.display.Info().current_h
# SCREEN_WIDTH, SCREEN_HEIGHT = 960, 540
BOARD_SIZE = 600 * SCREEN_HEIGHT // 1080
MARGIN = (SCREEN_HEIGHT - BOARD_SIZE) // 2
SQ_SIZE = BOARD_SIZE // Engine.DIMENSION
BOARD_SIZE = SQ_SIZE * Engine.DIMENSION
MARGIN_LEFT = SCREEN_WIDTH - BOARD_SIZE - MARGIN
RESERVE_MARGIN = (BOARD_SIZE - 5 * SQ_SIZE) // 2
FONT_SIZE = 25 * SCREEN_HEIGHT // 1080
EMPTY_PIECES = ["e" + piece for piece in Engine.PIECES if piece != "K"]
SKIN_PACK = 2
FPS = 60
IMAGES = {}


def loadImages():
    for piece in Engine.COLORED_PIECES:
        IMAGES[piece] = pg.transform.scale(pg.image.load(f"images/{SKIN_PACK}/{piece}.png"), (SQ_SIZE, SQ_SIZE))
        # IMAGES[piece] = pg.image.load(f"images/{piece}.png")
    for piece in EMPTY_PIECES:
        IMAGES[piece] = pg.transform.scale(pg.image.load(f"images/{SKIN_PACK}/{piece}.png"), (SQ_SIZE, SQ_SIZE))
    IMAGES["icon"] = pg.image.load("images/icon.png")
    IMAGES["board"] = pg.transform.scale(pg.image.load("images/board.png"), (BOARD_SIZE, BOARD_SIZE))
    IMAGES["frame"] = pg.transform.scale(pg.image.load("images/frame.png"), (SQ_SIZE, SQ_SIZE))
    IMAGES["frame"].set_alpha(200)
    IMAGES["hourglass"] = pg.transform.scale(pg.image.load("images/hourglass.png"), (SQ_SIZE, SQ_SIZE))
    # IMAGES["BG"] = pg.transform.scale(pg.image.load("images/BG.png"), (SCREEN_WIDTH, SCREEN_HEIGHT))


def main():
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    loadImages()
    clock = pg.time.Clock()
    # boardPlayers = [(True, True), (True, True)]
    boardPlayers = [(False, False), (False, False)]
    playerNames = ["Player 1", "Player 2", "Player 3", "Player 4"]
    AIExists = not (boardPlayers[0][0] and boardPlayers[0][1] and boardPlayers[1][0] and boardPlayers[1][1])
    activeBoard = 0
    gameStates = [Engine.GameState(), Engine.GameState()]
    pg.display.set_caption("SwiChess")
    pg.display.set_icon(IMAGES["icon"])
    working = True
    validMoves = [gameStates[0].getValidMoves(), gameStates[1].getValidMoves()]
    moveMade = [False, False]
    gameOver = False
    AIThinking = False
    AIThinkingTime = [0, 0]
    AIPositionCounter = [0, 0]
    AIProcess = Process()
    returnQ = Queue()
    selectedSq = [(), ()]
    clicks = [[], []]
    hourglass = Hourglass(0)
    while working:
        clock.tick(FPS)
        playerTurn = [(gameStates[0].whiteTurn and boardPlayers[0][0]) or (not gameStates[0].whiteTurn and boardPlayers[0][1]),
                      (gameStates[1].whiteTurn and boardPlayers[1][0]) or (not gameStates[1].whiteTurn and boardPlayers[1][1])]
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
            elif e.type == pg.MOUSEBUTTONDOWN:
                if e.button == 1:
                    if not gameOver:
                        location = pg.mouse.get_pos()
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
                                    column = Engine.DIMENSION - column - 1
                                    row = Engine.DIMENSION - row - 1
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
                                        movedPiece = color + Engine.PIECES[clicks[boardNum][0][0]]
                                    else:
                                        startSq = Engine.ONE >> (8 * clicks[boardNum][0][1] + clicks[boardNum][0][0])
                                    if 0 <= clicks[boardNum][1][1] <= 7:
                                        endSq = Engine.ONE >> (8 * clicks[boardNum][1][1] + clicks[boardNum][1][0])
                                    elif clicks[boardNum][1][1] == -1 or clicks[boardNum][1][1] == 8:
                                        endSq = -1
                                    else:
                                        endSq = 0
                                    move = Engine.Move(startSq, endSq, gameStates[boardNum], movedPiece=movedPiece, isReserve=isReserve)
                                    for part in validMoves[boardNum]:
                                        for validMove in part:
                                            if move == validMove or (move.moveID == validMove.moveID and move.isPawnPromotion and len(validMoves[boardNum][2]) > 0):
                                                if move.isPawnPromotion:
                                                    pos, piece = getPromotion(screen, gameStates, playerNames, boardNum)
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
                                                    hourglass = Hourglass(getCurrentPlayer(gameStates, activeBoard))
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
                                    row = Engine.DIMENSION - row - 1
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
            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_r:
                    if AIThinking:
                        AIProcess.terminate()
                        AIProcess.join()
                        AIProcess.close()
                        AIThinking = False
                    gameStates = [Engine.GameState(), Engine.GameState()]
                    validMoves = [gameStates[0].getValidMoves(), gameStates[1].getValidMoves()]
                    AIThinkingTime = [0, 0]
                    AIPositionCounter = [0, 0]
                    activeBoard = 0
                    gameOver = False
                    selectedSq = [(), ()]
                    clicks = [[], []]
                    moveMade = [False, False]
                    playerTurn = [(gameStates[0].whiteTurn and boardPlayers[0][0]) or (not gameStates[0].whiteTurn and boardPlayers[0][1]),
                                  (gameStates[1].whiteTurn and boardPlayers[1][0]) or (not gameStates[1].whiteTurn and boardPlayers[1][1])]
        if not gameOver:
            gameOver = gameOverCheck(gameStates, AIExists)
        for i in range(2):
            if not gameOver and not playerTurn[i]:
                if AIExists and activeBoard == i:
                    playerName = getPlayerName(gameStates[i], playerNames[i * 2:(i + 1) * 2])
                    if not AIThinking:
                        print(f"{playerName} AI is thinking...")
                        AIThinking = True
                        AIProcess = Process(target=AI.negaScoutMoveAI, args=(gameStates[i], gameStates[1 - i], validMoves[i], returnQ))
                        AIProcess.start()
                    if not AIProcess.is_alive():
                        AIMove, thinkingTime, positionCounter = returnQ.get()
                        AIThinkingTime[i] += thinkingTime
                        AIPositionCounter[i] += positionCounter
                        print(f"{playerName} AI came up with a move")
                        print(f"{playerName} AI thinking time: {thinkingTime} s")
                        print(f"{playerName} AI positions calculated: {positionCounter}")
                        if AIMove is None:
                            AIMove = AI.randomMoveAI(validMoves)
                            print(f"{playerName} AI made a random move")
                        if AIMove.isPawnPromotion:
                            possiblePromotions = calculatePossiblePromotions(gameStates, i)
                            possibleRequiredPromotions = [Engine.ONE >> (8 * key[1] + key[0]) for key, value in possiblePromotions.items() if value[1] == AIMove.promotedTo]
                            promotion = possibleRequiredPromotions[randint(0, len(possibleRequiredPromotions) - 1)]
                            AIMove = Engine.Move(AIMove.startSquare, AIMove.endSquare, gameStates[i], movedPiece=AIMove.movedPiece, promotedTo=AIMove.promotedTo, promotedPiecePosition=promotion)
                        gameStates[i].makeMove(AIMove, gameStates[1 - i])
                        for j in range(2):
                            validMoves[j] = gameStates[j].getValidMoves()
                            gameStates[j].updatePawnPromotionMoves(validMoves[j], gameStates[1 - j])
                        if not gameOver:
                            gameOver = gameOverCheck(gameStates, AIExists)
                        moveMade[i] = True
                        activeBoard = 1 - activeBoard
                        hourglass = Hourglass(getCurrentPlayer(gameStates, activeBoard))
                        AIThinking = False
                        selectedSq[i] = ()
                        clicks[i] = []
            if moveMade[i]:
                moveMade[i] = False
        drawGameState(screen, gameStates, validMoves, playerNames, selectedSq)
        hourglass.update(screen)
        if (gameStates[0].checkmate and not gameStates[0].whiteTurn) or (gameStates[1].checkmate and gameStates[1].whiteTurn):
            drawTopText(screen, "Team 1 wins")
        elif gameStates[0].stalemate and gameStates[1].stalemate:
            drawTopText(screen, "Draw")
        elif AIExists and (gameStates[0].stalemate or gameStates[1].stalemate):
            drawTopText(screen, "Draw")
        elif (gameStates[0].checkmate and gameStates[0].whiteTurn) or (gameStates[1].checkmate and not gameStates[1].whiteTurn):
            drawTopText(screen, "Team 2 wins")
        # if len(gameState.gameLog) == 40:
        #     gameOver = True
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
            square = Engine.ONE >> (8 * selectedSq[i][1] + selectedSq[i][0]) if not isReserve else -1
            piece = gameStates[i].getPieceBySquare(square) if not isReserve else color + Engine.PIECES[selectedSq[i][0]]
            if piece is not None:
                s = pg.Surface((SQ_SIZE, SQ_SIZE))
                s.fill(pg.Color(110, 90, 0))
                if not isReserve:
                    if i == 0:
                        screen.blit(s, (selectedSq[i][0] * SQ_SIZE + MARGIN, selectedSq[i][1] * SQ_SIZE + MARGIN))
                    else:
                        screen.blit(s, ((Engine.DIMENSION - 1 - selectedSq[i][0]) * SQ_SIZE + MARGIN_LEFT,
                                        (Engine.DIMENSION - 1 - selectedSq[i][1]) * SQ_SIZE + MARGIN))
                else:
                    if i == 0:
                        screen.blit(s, ((selectedSq[i][0] - 1) * SQ_SIZE + MARGIN + RESERVE_MARGIN, selectedSq[i][1] * SQ_SIZE + MARGIN))
                    else:
                        screen.blit(s, ((selectedSq[i][0] - 1) * SQ_SIZE + MARGIN_LEFT + RESERVE_MARGIN,
                                        (Engine.DIMENSION - 1 - selectedSq[i][1]) * SQ_SIZE + MARGIN))
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
                                        r = Engine.DIMENSION - 1 - move.endLoc // 8
                                        c = Engine.DIMENSION - 1 - move.endLoc % 8
                                        screen.blit(s, (c * SQ_SIZE + MARGIN_LEFT, r * SQ_SIZE + MARGIN))


def highlightLastMove(screen: pg.Surface, gameStates: list, selectedSq: list):
    for i in range(2):
        piece = None
        if selectedSq[i] != ():
            color = "w" if selectedSq[i][1] == 8 else "b"
            isReserve = True if selectedSq[i][1] == -1 or selectedSq[i][1] == 8 else False
            square = Engine.ONE >> (8 * selectedSq[i][1] + selectedSq[i][0]) if not isReserve else -1
            piece = gameStates[i].getPieceBySquare(square) if not isReserve else color + Engine.PIECES[selectedSq[i][0]]
            if isReserve and (gameStates[i].reserve[color][Engine.PIECES[selectedSq[i][0]]] == 0 or color == ("b" if gameStates[i].whiteTurn else "w")):
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
                        screen.blit(s, ((Engine.DIMENSION - 1 - lastMove.startLoc % 8) * SQ_SIZE + MARGIN_LEFT,
                                        (Engine.DIMENSION - 1 - lastMove.startLoc // 8) * SQ_SIZE + MARGIN))
                        screen.blit(s, ((Engine.DIMENSION - 1 - lastMove.endLoc % 8) * SQ_SIZE + MARGIN_LEFT,
                                        (Engine.DIMENSION - 1 - lastMove.endLoc // 8) * SQ_SIZE + MARGIN))
                else:
                    if i == 0:
                        marginTop = MARGIN - SQ_SIZE if lastMove.startLoc < 0 else MARGIN + BOARD_SIZE
                        screen.blit(s, ((abs(lastMove.startLoc) - 1) * SQ_SIZE + MARGIN + RESERVE_MARGIN, marginTop))
                        screen.blit(s, (lastMove.endLoc % 8 * SQ_SIZE + MARGIN, lastMove.endLoc // 8 * SQ_SIZE + MARGIN))
                    else:
                        marginTop = MARGIN - SQ_SIZE if lastMove.startLoc > 0 else MARGIN + BOARD_SIZE
                        screen.blit(s, ((abs(lastMove.startLoc) - 1) * SQ_SIZE + MARGIN_LEFT + RESERVE_MARGIN, marginTop))
                        screen.blit(s, ((Engine.DIMENSION - 1 - lastMove.endLoc % 8) * SQ_SIZE + MARGIN_LEFT,
                                        (Engine.DIMENSION - 1 - lastMove.endLoc // 8) * SQ_SIZE + MARGIN))


def calculatePossiblePromotions(gameStates: list, promotion: int):
    possiblePromotions = {}
    if promotion == 0:
        color = "w" if gameStates[0].whiteTurn else "b"
        for piece in Engine.POSSIBLE_PIECES_TO_PROMOTE:
            splitPositions = Engine.numSplit(gameStates[1].bbOfPieces[color + piece])
            for position in splitPositions:
                if gameStates[1].canBeRemoved(position, "w" if gameStates[0].whiteTurn else "b"):
                    pos = Engine.getPower(position)
                    possiblePromotions[(pos % 8, pos // 8)] = color + piece
    elif promotion == 1:
        color = "w" if gameStates[1].whiteTurn else "b"
        for piece in Engine.POSSIBLE_PIECES_TO_PROMOTE:
            splitPositions = Engine.numSplit(gameStates[0].bbOfPieces[color + piece])
            for position in splitPositions:
                if gameStates[0].canBeRemoved(position, "w" if gameStates[1].whiteTurn else "b"):
                    pos = Engine.getPower(position)
                    possiblePromotions[(pos % 8, pos // 8)] = color + piece
    return possiblePromotions


def highlightPossiblePromotions(screen: pg.Surface, possiblePromotions: dict, promotion: int):
    if possiblePromotions != {}:
        if promotion == 0:
            for column, row in possiblePromotions.keys():
                screen.blit(IMAGES["frame"], pg.Rect((Engine.DIMENSION - 1 - column) * SQ_SIZE + MARGIN_LEFT, (Engine.DIMENSION - 1 - row) * SQ_SIZE + MARGIN, SQ_SIZE, SQ_SIZE))
        elif promotion == 1:
            for column, row in possiblePromotions.keys():
                screen.blit(IMAGES["frame"], pg.Rect(column * SQ_SIZE + MARGIN, row * SQ_SIZE + MARGIN, SQ_SIZE, SQ_SIZE))


def drawGameState(screen: pg.Surface, gameStates: list, validMoves: list, playerNames: list, selectedSq: list, promotion=-1, possiblePromotions=None):
    screen.fill((181, 136, 99))
    # screen.blit(IMAGES["BG"], (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
    drawPlayersNames(screen, playerNames)
    drawBoard(screen)
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
        for piece in Engine.COLORED_PIECES:
            splitPositions = Engine.numSplit(gameStates[i].bbOfPieces[piece])
            for position in splitPositions:
                pos = Engine.getPower(position) if i == 0 else 63 - Engine.getPower(position)
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


def getPlayerName(gameState: Engine.GameState, playerNames: list):
    if gameState.whiteTurn:
        return playerNames[0]
    else:
        return playerNames[1]


def getPromotion(screen: pg.Surface, gameStates: list, playerNames: list, boardNum: int):
    possiblePromotions = calculatePossiblePromotions(gameStates, boardNum)
    if possiblePromotions == {}:
        return 0, None
    drawGameState(screen, gameStates, [], playerNames, [], promotion=boardNum, possiblePromotions=possiblePromotions)
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
                                return Engine.ONE >> (8 * row + column), possiblePromotions[(column, row)]
                    if boardNum == 0:
                        if MARGIN_LEFT < location[0] < MARGIN_LEFT + BOARD_SIZE and MARGIN < location[1] < MARGIN + BOARD_SIZE:
                            column = (location[0] - MARGIN_LEFT) // SQ_SIZE
                            row = (location[1] - MARGIN) // SQ_SIZE
                            column = Engine.DIMENSION - column - 1
                            row = Engine.DIMENSION - row - 1
                            if (column, row) in possiblePromotions:
                                return Engine.ONE >> (8 * row + column), possiblePromotions[(column, row)]


def drawTopText(screen: pg.Surface, text: str):
    font = pg.font.SysFont("Helvetica", FONT_SIZE * 2, True, False)
    textObj = font.render(text, False, pg.Color("gray"))
    textLocation = pg.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT).move(SCREEN_WIDTH // 2 - textObj.get_width() // 2,
                                                                   textObj.get_height() // 2)
    screen.blit(textObj, textLocation)
    textObj = font.render(text, False, pg.Color("black"))
    screen.blit(textObj, textLocation.move(2, 2))


class Hourglass:
    def __init__(self, currentPlayer: int):
        self.image = IMAGES["hourglass"]
        self.orig_image = self.image
        if currentPlayer == 0:
            self.rect = pg.Rect(MARGIN, SCREEN_HEIGHT - MARGIN + 5, SQ_SIZE, SQ_SIZE)
        elif currentPlayer == 1:
            self.rect = pg.Rect(MARGIN, MARGIN - SQ_SIZE - 5, SQ_SIZE, SQ_SIZE)
        elif currentPlayer == 2:
            self.rect = pg.Rect(MARGIN_LEFT, MARGIN - SQ_SIZE - 5, SQ_SIZE, SQ_SIZE)
        else:
            self.rect = pg.Rect(MARGIN_LEFT, SCREEN_HEIGHT - MARGIN + 5, SQ_SIZE, SQ_SIZE)
        self.angle = 0

    def update(self, screen: pg.Surface):
        self.angle += 2
        if self.angle == 360:
            self.angle = 0
        self.rotate()
        screen.blit(self.image, self.rect)

    def rotate(self):
        self.image = pg.transform.rotate(self.orig_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)


def drawPlayersNames(screen: pg.Surface, names: list):
    font = pg.font.SysFont("Helvetica", int(FONT_SIZE * 1.5), True, False)
    textObj = font.render(names[0], False, pg.Color("gray"))

    # if currentPlayer == 0:
    #     rect = pg.Rect(MARGIN + (BOARD_SIZE - textObj.get_width()) // 2, SCREEN_HEIGHT - (MARGIN + textObj.get_height()) // 2, textObj.get_width() + 2, textObj.get_height() + 2)
    # elif currentPlayer == 1:
    #     rect = pg.Rect(MARGIN + (BOARD_SIZE - textObj.get_width()) // 2, (MARGIN - textObj.get_height()) // 2, textObj.get_width() + 2, textObj.get_height() + 2)
    # elif currentPlayer == 2:
    #     rect = pg.Rect(MARGIN_LEFT + (BOARD_SIZE - textObj.get_width()) // 2, (MARGIN - textObj.get_height()) // 2, textObj.get_width() + 2, textObj.get_height() + 2)
    # else:
    #     rect = pg.Rect(MARGIN_LEFT + (BOARD_SIZE - textObj.get_width()) // 2, SCREEN_HEIGHT - (MARGIN + textObj.get_height()) // 2, textObj.get_width() + 2, textObj.get_height() + 2)
    # pg.draw.rect(screen, pg.Color("red"), rect)

    # if currentPlayer == 0:
    #     rect = pg.Rect(MARGIN + (BOARD_SIZE - textObj.get_width()) // 2 - SQ_SIZE, SCREEN_HEIGHT - (MARGIN + SQ_SIZE) // 2, SQ_SIZE, SQ_SIZE)
    # elif currentPlayer == 1:
    #     rect = pg.Rect(MARGIN + (BOARD_SIZE - textObj.get_width()) // 2 - SQ_SIZE, (MARGIN - SQ_SIZE) // 2, SQ_SIZE, SQ_SIZE)
    # elif currentPlayer == 2:
    #     rect = pg.Rect(MARGIN_LEFT + (BOARD_SIZE - textObj.get_width()) // 2 - SQ_SIZE, (MARGIN - SQ_SIZE) // 2, SQ_SIZE, SQ_SIZE)
    # else:
    #     rect = pg.Rect(MARGIN_LEFT + (BOARD_SIZE - textObj.get_width()) // 2 - SQ_SIZE, SCREEN_HEIGHT - (MARGIN + SQ_SIZE) // 2, SQ_SIZE, SQ_SIZE)
    # screen.blit(IMAGES["hourglass"], rect)

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


if __name__ == "__main__":
    main()
    pg.quit()
