import Engine
import pygame as pg
# import pygame_menu as pgm
import AI
from math import ceil, floor
from multiprocessing import Process, Queue

pg.init()
# SCREEN_WIDTH, SCREEN_HEIGHT = pg.display.Info().current_w, pg.display.Info().current_h
SCREEN_WIDTH, SCREEN_HEIGHT = 960, 540
BOARD_HEIGHT = 600 * SCREEN_HEIGHT // 1080
MARGIN = (SCREEN_HEIGHT - BOARD_HEIGHT) // 2
SQ_SIZE = BOARD_HEIGHT // Engine.DIMENSION
BOARD_WIDTH = BOARD_HEIGHT = SQ_SIZE * Engine.DIMENSION
FPS = 30
IMAGES = {}
BOARD_COLORS = (pg.Color((240, 217, 181)), pg.Color((181, 136, 99)), pg.Color("black"))


def loadImages():
    for piece in Engine.COLORED_PIECES:
        IMAGES[piece] = pg.transform.scale(pg.image.load(f"images/2/{piece}.png"), (SQ_SIZE, SQ_SIZE))
        # IMAGES[piece] = pg.image.load(f"images/{piece}.png")
    IMAGES["icon"] = pg.image.load("images/icon.png")
    IMAGES["BG"] = pg.transform.scale(pg.image.load("images/BG.png"), (SCREEN_WIDTH, SCREEN_HEIGHT))
    # IMAGES["BG"] = pg.image.load("images/BG.png")


def main():
    loadImages()
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    # screen = pg.display.set_mode((BOARD_HEIGHT, BOARD_HEIGHT))
    boardPlayers = [(True, True), (True, True)]
    gameStates = [Engine.GameState(), Engine.GameState()]
    pg.display.set_caption("SwiChess")
    pg.display.set_icon(IMAGES["icon"])
    working = True
    validMoves = [gameStates[0].getValidMoves(), gameStates[1].getValidMoves()]
    print(validMoves)
    moveMade = [False, False]
    gameOver = False
    AIThinking = [False, False]
    AIThinkingTime = [0, 0]
    AIPositionCounter = [0, 0]
    AIProcess = [Process(), Process()]
    returnQ = [Queue(), Queue()]
    selectedSq = [(), ()]
    clicks = [[], []]
    while working:
        pg.clock.tick(FPS)
        playerTurn = [(gameStates[0].whiteTurn and boardPlayers[0][0]) or (not gameStates[0].whiteTurn and boardPlayers[0][1]),
                      (gameStates[1].whiteTurn and boardPlayers[1][0]) or (not gameStates[1].whiteTurn and boardPlayers[1][1])]
        for e in pg.event.get():
            if e.type == pg.QUIT:
                for i in range(2):
                    if AIThinking[i]:
                        AIProcess[i].terminate()
                        AIProcess[i].close()
                        AIThinking[i] = False
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
                if not gameOver:
                    location = pg.mouse.get_pos()
                    if MARGIN < location[0] < MARGIN + BOARD_WIDTH and MARGIN < location[1] < MARGIN + BOARD_HEIGHT:
                        column = (location[0] - MARGIN) // SQ_SIZE
                        row = (location[1] - MARGIN) // SQ_SIZE
                        if selectedSq[0] == (column, row):
                            selectedSq[0] = ()
                            clicks[0] = []
                        else:
                            selectedSq[0] = (column, row)
                            clicks[0].append(selectedSq[0])
                        if len(clicks[0]) == 2 and playerTurn[0]:
                            startSq = Engine.ONE >> (8 * clicks[0][0][1] + clicks[0][0][0])
                            endSq = Engine.ONE >> (8 * clicks[0][1][1] + clicks[0][1][0])
                            move = Engine.Move(startSq, endSq, gameStates[0])
                            for validMove in validMoves[0]:
                                if move == validMove:
                                    gameStates[0].makeMove(validMove, gameStates[1])
                                    moveMade[0] = True
                                    selectedSq[0] = ()
                                    clicks[0] = []
                                    break
                            if not moveMade[0]:
                                clicks[0] = [selectedSq[0]]
                    elif SCREEN_WIDTH - MARGIN - BOARD_WIDTH < location[0] < SCREEN_WIDTH - MARGIN and MARGIN < location[1] < MARGIN + BOARD_HEIGHT:
                        column = (location[0] - (SCREEN_WIDTH - MARGIN - BOARD_WIDTH)) // SQ_SIZE
                        row = (location[1] - MARGIN) // SQ_SIZE
                        column = Engine.DIMENSION - column - 1
                        row = Engine.DIMENSION - row - 1
                        if selectedSq[1] == (column, row):
                            selectedSq[1] = ()
                            clicks[1] = []
                        else:
                            selectedSq[1] = (column, row)
                            clicks[1].append(selectedSq[1])
                        if len(clicks[1]) == 2 and playerTurn[1]:
                            startSq = Engine.ONE >> (8 * clicks[1][0][1] + clicks[1][0][0])
                            endSq = Engine.ONE >> (8 * clicks[1][1][1] + clicks[1][1][0])
                            move = Engine.Move(startSq, endSq, gameStates[1])
                            for validMove in validMoves[1]:
                                if move == validMove:
                                    gameStates[1].makeMove(validMove, gameStates[0])
                                    moveMade[1] = True
                                    selectedSq[1] = ()
                                    clicks[1] = []
                                    break
                            if not moveMade[1]:
                                clicks[1] = [selectedSq[1]]
                    else:
                        selectedSq = [(), ()]
                        clicks = [[], []]
            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_r:
                    for i in range(2):
                        if AIThinking[i]:
                            AIThinking[i] = False
                            AIProcess[i].terminate()
                            AIProcess[i].close()
                            playerTurn[i] = (gameStates[i].whiteTurn and boardPlayers[i][0]) or (not gameStates[i].whiteTurn and boardPlayers[i][1])
                    gameStates = [Engine.GameState(), Engine.GameState()]
                    validMoves = [gameStates[0].getValidMoves(), gameStates[1].getValidMoves()]
                    AIThinkingTime = [0, 0]
                    AIPositionCounter = [0, 0]
                    if gameOver:
                        gameOver = False
                        playerTurn = [(gameStates[0].whiteTurn and boardPlayers[0][0]) or (not gameStates[0].whiteTurn and boardPlayers[0][1]),
                                      (gameStates[1].whiteTurn and boardPlayers[1][0]) or (not gameStates[1].whiteTurn and boardPlayers[1][1])]
                    selectedSq = [(), ()]
                    clicks = [[], []]
                    moveMade = [False, False]
        for i in range(2):
            if not gameOver and not playerTurn[i]:
                if not AIThinking[i]:
                    print(f"Board {i + 1} AI is thinking...")
                    print(validMoves[i])
                    AIThinking[i] = True
                    AIProcess[i] = Process(target=AI.negaScoutMoveAI, args=(gameStates[i], validMoves[i], returnQ[i]))
                    AIProcess[i].start()
                if not AIProcess[i].is_alive():
                    AIMove, thinkingTime, positionCounter = returnQ[i].get()
                    AIThinkingTime[i] += thinkingTime
                    AIPositionCounter[i] += positionCounter
                    print(f"Board {i + 1} AI came up with a move")
                    print(f"Board {i + 1} AI thinking time: {thinkingTime} s")
                    print(f"Board {i + 1} AI positions calculated: {positionCounter}")
                    if AIMove is None:
                        AIMove = AI.randomMoveAI(validMoves)
                        print(f"Board {i + 1} AI made a random move")
                    gameStates[i].makeMove(AIMove, gameStates[1 - i])
                    moveMade[i] = True
                    AIThinking[i] = False
                    selectedSq[i] = ()
                    clicks[i] = []
            if moveMade[i]:
                validMoves[i] = gameStates[i].getValidMoves()
                moveMade[i] = False
        drawGameState(screen, gameStates, validMoves, selectedSq)
        if (gameStates[0].checkmate and not gameStates[0].whiteTurn) or (gameStates[1].checkmate and gameStates[1].whiteTurn):
            gameOver = True
            drawText(screen, "Team 1 wins")
        elif gameStates[0].stalemate or gameStates[1].stalemate:
            gameOver = True
            drawText(screen, "Draw")
        elif (gameStates[0].checkmate and gameStates[0].whiteTurn) or (gameStates[1].checkmate and not gameStates[1].whiteTurn):
            gameOver = True
            drawText(screen, "Team 2 wins")
        # if len(gameState.gameLog) == 40:
        #     gameOver = True
        pg.display.flip()


def highlightSq(screen: pg.Surface, gameStates: list, validMoves: list, selectedSq: list):
    marginLeft = SCREEN_WIDTH - BOARD_WIDTH - MARGIN
    for i in range(2):
        if selectedSq[i] != ():
            square = Engine.ONE >> (8 * selectedSq[i][1] + selectedSq[i][0])
            piece = gameStates[i].getPieceBySquare(square)
            if piece is not None:
                s = pg.Surface((SQ_SIZE, SQ_SIZE))
                s.fill(pg.Color(110, 90, 0))
                if i == 0:
                    screen.blit(s, (selectedSq[i][0] * SQ_SIZE + MARGIN, selectedSq[i][1] * SQ_SIZE + MARGIN))
                else:
                    screen.blit(s, ((Engine.DIMENSION - 1 - selectedSq[i][0]) * SQ_SIZE + marginLeft,
                                    (Engine.DIMENSION - 1 - selectedSq[i][1]) * SQ_SIZE + MARGIN))
                s.set_alpha(100)
                s.fill(pg.Color("yellow"))
                if piece[0] == ("w" if gameStates[i].whiteTurn else "b"):
                    for move in validMoves[i]:
                        if move.startSquare == square:
                            if i == 0:
                                screen.blit(s, (move.endLoc % 8 * SQ_SIZE + MARGIN, move.endLoc // 8 * SQ_SIZE + MARGIN))
                            else:
                                r = Engine.DIMENSION - 1 - move.endLoc // 8
                                c = Engine.DIMENSION - 1 - move.endLoc % 8
                                screen.blit(s, (c * SQ_SIZE + marginLeft, r * SQ_SIZE + MARGIN))


def highlightLastMove(screen: pg.Surface, gameStates: list):
    marginLeft = SCREEN_WIDTH - BOARD_WIDTH - MARGIN
    for i in range(2):
        if len(gameStates[i].gameLog) != 0:
            lastMove = gameStates[i].gameLog[-1]
            s = pg.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(pg.Color(0, 0, 255))
            if i == 0:
                screen.blit(s, (lastMove.startLoc % 8 * SQ_SIZE + MARGIN, lastMove.startLoc // 8 * SQ_SIZE + MARGIN))
                screen.blit(s, (lastMove.endLoc % 8 * SQ_SIZE + MARGIN, lastMove.endLoc // 8 * SQ_SIZE + MARGIN))
            else:
                screen.blit(s, ((Engine.DIMENSION - 1 - lastMove.startLoc % 8) * SQ_SIZE + marginLeft,
                                (Engine.DIMENSION - 1 - lastMove.startLoc // 8) * SQ_SIZE + MARGIN))
                screen.blit(s, ((Engine.DIMENSION - 1 - lastMove.endLoc % 8) * SQ_SIZE + marginLeft,
                                (Engine.DIMENSION - 1 - lastMove.endLoc // 8) * SQ_SIZE + MARGIN))


def drawGameState(screen: pg.Surface, gameStates: list, validMoves: list, selectedSq: list):
    screen.fill((237, 235, 233))
    drawBoard(screen)
    highlightLastMove(screen, gameStates)
    highlightSq(screen, gameStates, validMoves, selectedSq)
    drawPieces(screen, gameStates)


def drawBoard(screen: pg.Surface):
    marginLeft = SCREEN_WIDTH - BOARD_WIDTH - MARGIN
    pg.draw.rect(screen, BOARD_COLORS[2], pg.Rect(MARGIN - 1, MARGIN - 1, BOARD_WIDTH + 2, BOARD_HEIGHT + 2))
    pg.draw.rect(screen, BOARD_COLORS[2], pg.Rect(marginLeft - 1, MARGIN - 1, BOARD_WIDTH + 2, BOARD_HEIGHT + 2))
    for column in range(Engine.DIMENSION):
        for row in range(Engine.DIMENSION):
            color = BOARD_COLORS[(row + column) % 2]
            pg.draw.rect(screen, color, pg.Rect(column * SQ_SIZE + MARGIN, row * SQ_SIZE + MARGIN, SQ_SIZE, SQ_SIZE))
            pg.draw.rect(screen, color, pg.Rect(column * SQ_SIZE + marginLeft, row * SQ_SIZE + MARGIN, SQ_SIZE, SQ_SIZE))


def drawPieces(screen: pg.Surface, gameStates: list):
    for i in range(2):
        marginLeft = MARGIN if i == 0 else SCREEN_WIDTH - BOARD_WIDTH - MARGIN
        for piece in Engine.COLORED_PIECES:
            splitPositions = Engine.numSplit(gameStates[i].bbOfPieces[piece])
            for position in splitPositions:
                pos = Engine.getPower(position) if i == 0 else 63 - Engine.getPower(position)
                screen.blit(IMAGES[piece], pg.Rect(pos % 8 * SQ_SIZE + marginLeft, pos // 8 * SQ_SIZE + MARGIN, SQ_SIZE, SQ_SIZE))


def drawText(screen: pg.Surface, text: str):
    font = pg.font.SysFont("Helvetica", 32, True, False)
    textObj = font.render(text, False, pg.Color("gray"))
    textLocation = pg.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT).move(SCREEN_WIDTH / 2 - textObj.get_width() / 2,
                                                                   SCREEN_HEIGHT / 2 - textObj.get_height() / 2)
    screen.blit(textObj, textLocation)
    textObj = font.render(text, False, pg.Color("black"))
    screen.blit(textObj, textLocation.move(2, 2))


if __name__ == "__main__":
    main()
    pg.quit()
