import Engine
import pygame as pg
import AI
from math import ceil, floor
from multiprocessing import Process, Queue

BOARD_WIDTH = BOARD_HEIGHT = 512
SQ_SIZE = BOARD_HEIGHT // Engine.DIMENSION
IMAGES = {}
BOARD_COLORS = (pg.Color("white"), pg.Color("dark gray"))


def isListNone(lst: list):
    for e in lst:
        if e is not None:
            return False
    return True


def areProcessesDead(processes: list):
    for proc in processes:
        if proc.is_alive():
            return False
    return True


def loadImages():
    for piece in Engine.COLORED_PIECES:
        IMAGES[piece] = pg.transform.scale(pg.image.load(f"images/{piece}.png"), (SQ_SIZE, SQ_SIZE))
    IMAGES["icon"] = pg.transform.scale(pg.image.load(f"images/icon.png"), (SQ_SIZE, SQ_SIZE))


def main():
    pg.init()
    screen = pg.display.set_mode((BOARD_WIDTH, BOARD_HEIGHT))
    screen.fill(pg.Color("white"))
    whitePlayer = False
    blackPlayer = False
    playerColor = False if blackPlayer and not whitePlayer else True
    gameState = Engine.GameState()
    validMoves = gameState.getValidMoves()
    moveMade = False
    gameOver = False
    AIThinking = False
    threadsAmount = 2
    AIProcess = [Process()] * threadsAmount
    returnQ = [Queue()] * threadsAmount

    loadImages()
    pg.display.set_caption("SwiChess")
    pg.display.set_icon(IMAGES["icon"])
    selectedSq = ()
    clicks = []
    AIThinkingTime = 0
    AIPositionCounter = 0

    while True:
        playerTurn = (gameState.whiteTurn and whitePlayer) or (not gameState.whiteTurn and blackPlayer)
        for e in pg.event.get():
            if e.type == pg.QUIT:
                if AIThinking:
                    for proc in AIProcess:
                        proc.terminate()
                    AIThinking = False
                print(gameState.gameLog)
                if not whitePlayer and not blackPlayer:
                    moveCountCeil = len(gameState.gameLog)
                    moveCountFloor = len(gameState.gameLog)
                else:
                    moveCountCeil = ceil(len(gameState.gameLog) / 2)
                    moveCountFloor = floor(len(gameState.gameLog) / 2)
                print(f"Moves: {moveCountCeil}")
                print(f"Overall thinking time: {AIThinkingTime}")
                print(f"Overall positions calculated: {AIPositionCounter}")
                if moveCountFloor != 0 and AIPositionCounter != 0:
                    print(f"Average time per move: {AIThinkingTime / moveCountFloor}")
                    print(f"Average calculated positions per move: {AIPositionCounter / moveCountFloor}")
                    print(f"Average time per position: {AIThinkingTime / AIPositionCounter}")
                quit()
            elif e.type == pg.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = pg.mouse.get_pos()
                    column = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if not playerColor:
                        column = Engine.DIMENSION - column - 1
                        row = Engine.DIMENSION - row - 1
                    if selectedSq == (column, row) or column > 7 or column < 0 or row > 7 or row < 0:
                        selectedSq = ()
                        clicks = []
                    else:
                        selectedSq = (column, row)
                        clicks.append(selectedSq)
                    if len(clicks) == 2 and playerTurn:
                        startSq = Engine.ONE >> (8 * clicks[0][1] + clicks[0][0])
                        endSq = Engine.ONE >> (8 * clicks[1][1] + clicks[1][0])
                        move = Engine.Move(startSq, endSq, gameState)
                        for validMove in validMoves:
                            if move == validMove:
                                gameState.makeMove(validMove)
                                moveMade = True
                                selectedSq = ()
                                clicks = []
                                break
                        if not moveMade:
                            clicks = [selectedSq]
            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_u:
                    gameState.undoMove()
                    moveMade = True
                    if gameOver:
                        gameOver = False
                        playerTurn = (gameState.whiteTurn and whitePlayer) or (not gameState.whiteTurn and blackPlayer)
                    if AIThinking:
                        for proc in AIProcess:
                            proc.terminate()
                        playerTurn = (gameState.whiteTurn and whitePlayer) or (not gameState.whiteTurn and blackPlayer)
                        AIThinking = False
                if e.key == pg.K_r:
                    gameState = Engine.GameState()
                    validMoves = gameState.getValidMoves()
                    selectedSq = ()
                    clicks = []
                    if gameOver:
                        gameOver = False
                        playerTurn = (gameState.whiteTurn and whitePlayer) or (not gameState.whiteTurn and blackPlayer)
                    moveMade = False
                    if AIThinking:
                        for proc in AIProcess:
                            proc.terminate()
                        playerTurn = (gameState.whiteTurn and whitePlayer) or (not gameState.whiteTurn and blackPlayer)
                        AIThinking = False
        if not gameOver and not playerTurn:
            if not AIThinking:
                print("thinking...")
                print(validMoves)
                AIThinking = True
                divider = ceil(len(validMoves) / threadsAmount)
                for i in range(threadsAmount):
                    part = validMoves[divider * i:divider * (i + 1)]
                    AIProcess[i] = Process(target=AI.negaScoutMoveAI, args=(gameState, part, returnQ[i]))
                    AIProcess[i].start()
            if areProcessesDead(AIProcess):
                AIMove = [Engine.Move()] * threadsAmount
                thinkingTime = [0] * threadsAmount
                positionCounter = [0] * threadsAmount
                for i in range(threadsAmount):
                    AIMove[i], thinkingTime[i], positionCounter[i] = returnQ[i].get()
                AIThinkingTime += max(thinkingTime)
                AIPositionCounter += sum(positionCounter)
                print("came up with a move")
                print(f"Thinking time: {max(thinkingTime)} s")
                print(f"Positions calculated: {sum(positionCounter)}")
                if not isListNone(AIMove):
                    bestScores = []
                    bestMoves = {}
                    for move in AIMove:
                        if move is not None:
                            bestScores.append(move.exactScore)
                            bestMoves[move.exactScore] = move
                    bestMove = bestMoves[max(bestScores)]
                    print(bestMoves)
                    print(bestMove)
                else:
                    bestMove = None
                if bestMove is None:
                    bestMove = AI.randomMoveAI(validMoves)
                    print("made a random move")
                gameState.makeMove(bestMove)
                moveMade = True
                AIThinking = False
                selectedSq = ()
                clicks = []
        if moveMade:
            validMoves = gameState.getValidMoves()
            moveMade = False
        drawGameState(screen, gameState, validMoves, selectedSq, playerColor)
        if gameState.checkmate:
            gameOver = True
            if gameState.whiteTurn:
                drawText(screen, "Black win by checkmate")
            else:
                drawText(screen, "White win by checkmate")
        elif gameState.stalemate:
            gameOver = True
            drawText(screen, "Stalemate")
        if len(gameState.gameLog) == 40:
            gameOver = True
        pg.display.flip()


def highlightSq(screen: pg.Surface, gameState: Engine.GameState, validMoves: list, selectedSq: tuple, playerColor: bool):
    if selectedSq != ():
        square = Engine.ONE >> (8 * selectedSq[1] + selectedSq[0])
        piece = gameState.getPieceBySquare(square)
        if piece is not None:
            s = pg.Surface((SQ_SIZE, SQ_SIZE))
            s.fill(pg.Color(110, 90, 0))
            if playerColor:
                screen.blit(s, (selectedSq[0] * SQ_SIZE, selectedSq[1] * SQ_SIZE))
            else:
                screen.blit(s, ((Engine.DIMENSION - 1 - selectedSq[0]) * SQ_SIZE,
                                (Engine.DIMENSION - 1 - selectedSq[1]) * SQ_SIZE))
            s.set_alpha(100)
            s.fill(pg.Color("yellow"))
            if piece[0] == ("w" if gameState.whiteTurn else "b"):
                for move in validMoves:
                    if move.startSquare == square:
                        if playerColor:
                            screen.blit(s, (move.endLoc % 8 * SQ_SIZE, move.endLoc // 8 * SQ_SIZE))
                        else:
                            r = Engine.DIMENSION - 1 - move.endLoc // 8
                            c = Engine.DIMENSION - 1 - move.endLoc % 8
                            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))


def highlightLastMove(screen: pg.Surface, gameState: Engine.GameState, playerColor: bool):
    if len(gameState.gameLog) != 0:
        lastMove = gameState.gameLog[-1]
        s = pg.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100)
        s.fill(pg.Color(0, 0, 255))
        if playerColor:
            screen.blit(s, (lastMove.startLoc % 8 * SQ_SIZE, lastMove.startLoc // 8 * SQ_SIZE))
            screen.blit(s, (lastMove.endLoc % 8 * SQ_SIZE, lastMove.endLoc // 8 * SQ_SIZE))
        else:
            screen.blit(s, ((Engine.DIMENSION - 1 - lastMove.startLoc % 8) * SQ_SIZE,
                            (Engine.DIMENSION - 1 - lastMove.startLoc // 8) * SQ_SIZE))
            screen.blit(s, ((Engine.DIMENSION - 1 - lastMove.endLoc % 8) * SQ_SIZE,
                            (Engine.DIMENSION - 1 - lastMove.endLoc // 8) * SQ_SIZE))


# def highlightThreatTable(screen: pg.Surface, gameState: Engine.GameState):
#     s = pg.Surface((SQ_SIZE, SQ_SIZE))
#     s.set_alpha(100)
#     s.fill(pg.Color(255, 0, 0))
#     splitTableWhite = Engine.numSplit(gameState.bbOfThreats["w"])
#     splitTableBlack = Engine.numSplit(gameState.bbOfThreats["b"])
#     for sq in splitTableWhite:
#         loc = Engine.getPower(sq)
#         screen.blit(s, (loc % 8 * SQ_SIZE, loc // 8 * SQ_SIZE))
#     s.fill(pg.Color(0, 0, 255))
#     for sq in splitTableBlack:
#         loc = Engine.getPower(sq)
#         screen.blit(s, (loc % 8 * SQ_SIZE, loc // 8 * SQ_SIZE))


def drawGameState(screen: pg.Surface, gameState: Engine.GameState, validMoves: list, selectedSq: tuple, playerColor: bool):
    drawBoard(screen)
    highlightLastMove(screen, gameState, playerColor)
    highlightSq(screen, gameState, validMoves, selectedSq, playerColor)
    # highlightThreatTable(screen, gameState)
    drawPieces(screen, gameState, playerColor)


def drawBoard(screen: pg.Surface):
    for column in range(Engine.DIMENSION):
        for row in range(Engine.DIMENSION):
            color = BOARD_COLORS[(row + column) % 2]
            pg.draw.rect(screen, color, pg.Rect(column * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPieces(screen: pg.Surface, gameState: Engine.GameState, playerColor: bool):
    if playerColor:
        for piece in Engine.COLORED_PIECES:
            splitPositions = Engine.numSplit(gameState.bbOfPieces[piece])
            for position in splitPositions:
                pos = Engine.getPower(position)
                screen.blit(IMAGES[piece], pg.Rect(pos % 8 * SQ_SIZE, pos // 8 * SQ_SIZE, SQ_SIZE, SQ_SIZE))
    else:
        for piece in Engine.COLORED_PIECES:
            splitPositions = Engine.numSplit(gameState.bbOfPieces[piece])
            for position in splitPositions:
                pos = 63 - Engine.getPower(position)
                screen.blit(IMAGES[piece], pg.Rect(pos % 8 * SQ_SIZE, pos // 8 * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawText(screen: pg.Surface, text: str):
    font = pg.font.SysFont("Helvetica", 32, True, False)
    textObj = font.render(text, False, pg.Color("gray"))
    textLocation = pg.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - textObj.get_width() / 2,
                                                                 BOARD_HEIGHT / 2 - textObj.get_height() / 2)
    screen.blit(textObj, textLocation)
    textObj = font.render(text, False, pg.Color("black"))
    screen.blit(textObj, textLocation.move(2, 2))


if __name__ == "__main__":
    main()
