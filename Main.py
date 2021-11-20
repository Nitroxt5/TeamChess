import Engine
import pygame as pg

BOARD_WIDTH = BOARD_HEIGHT = 512
DIMENSION = 8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
IMAGES = {}
BOARD_COLORS = (pg.Color("white"), pg.Color("dark gray"))


def loadImages():
    print(Engine.COLORED_PIECES)
    for piece in Engine.COLORED_PIECES:
        IMAGES[piece] = pg.transform.scale(pg.image.load(f"images/{piece}.png"), (SQ_SIZE, SQ_SIZE))
    IMAGES["icon"] = pg.transform.scale(pg.image.load(f"images/icon.png"), (SQ_SIZE, SQ_SIZE))


def main():
    pg.init()
    # screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
    screen = pg.display.set_mode((1500, 750))
    screen.fill(pg.Color("white"))
    gameState = Engine.GameState(True)
    gameOver = False
    moveMade = False

    loadImages()
    pg.display.set_caption("SwiChess")
    pg.display.set_icon(IMAGES["icon"])
    selectedSq = ()
    clicks = []

    while True:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                quit()
            elif e.type == pg.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = pg.mouse.get_pos()
                    column = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if selectedSq == (column, row) or column > 7 or column < 0 or row > 7 or row < 0:
                        selectedSq = ()
                        clicks = []
                    else:
                        selectedSq = (column, row)
                        clicks.append(selectedSq)
                    if len(clicks) == 2:
                        move = Engine.Move(clicks[0], clicks[1], gameState)
                        gameState.makeMove(move)
                        moveMade = True
                        selectedSq = ()
                        clicks = []
                        if not moveMade:
                            clicks = [selectedSq]
            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_ESCAPE:
                    quit()
                if e.key == pg.K_u:
                    gameState.undoMove()
                    moveMade = True
                    if gameOver:
                        gameOver = False
        drawGameState(screen, gameState)
        pg.display.update()


# def highlightSq(screen, gameState, validMoves, selectedSq):
#     if selectedSq != ():
#         column, row = selectedSq
#         if gameState.board[row][column][0] == ("w" if gameState.whiteTurn else "b"):
#             s = pg.Surface((SQ_SIZE, SQ_SIZE))
#             s.fill(pg.Color(110, 90, 0))
#             screen.blit(s, (column * SQ_SIZE, row * SQ_SIZE))
#             s.set_alpha(100)
#             s.fill(pg.Color("yellow"))
#             for move in validMoves:
#                 if move.startColumn == column and move.startRow == row:
#                     screen.blit(s, (move.endColumn * SQ_SIZE, move.endRow * SQ_SIZE))
#
#
# def highlightLastMove(screen, gameState):
#     if len(gameState.gameLog) != 0:
#         lastMove = gameState.gameLog[-1]
#         s = pg.Surface((SQ_SIZE, SQ_SIZE))
#         s.set_alpha(100)
#         s.fill(pg.Color(182, 255, 0))
#         screen.blit(s, (lastMove.startColumn * SQ_SIZE, lastMove.startRow * SQ_SIZE))
#         screen.blit(s, (lastMove.endColumn * SQ_SIZE, lastMove.endRow * SQ_SIZE))


# def drawGameState(screen, gameState, validMoves, selectedSq):
#     drawBoard(screen)
#     highlightLastMove(screen, gameState)
#     highlightSq(screen, gameState, validMoves, selectedSq)
#     drawPieces(screen, gameState.board)


def drawGameState(screen, gameState):
    drawBoard(screen)
    # highlightLastMove(screen, gameState)
    # highlightSq(screen, gameState, validMoves, selectedSq)
    drawPieces(screen, gameState)


def drawBoard(screen):
    for column in range(DIMENSION):
        for row in range(DIMENSION):
            color = BOARD_COLORS[(row + column) % 2]
            pg.draw.rect(screen, color, pg.Rect(column * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPieces(screen, gameState):
    for column in range(DIMENSION):
        for row in range(DIMENSION):
            for piece in Engine.COLORED_PIECES:
                if gameState.getSqState(piece, column, row):
                    screen.blit(IMAGES[piece], pg.Rect(column * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawText(screen, text):
    font = pg.font.SysFont("Helvetica", 32, True, False)
    textObj = font.render(text, False, pg.Color("gray"))
    textLocation = pg.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - textObj.get_width() / 2,
                                                                 BOARD_HEIGHT / 2 - textObj.get_height() / 2)
    screen.blit(textObj, textLocation)
    textObj = font.render(text, False, pg.Color("black"))
    screen.blit(textObj, textLocation.move(2, 2))


if __name__ == "__main__":
    main()
