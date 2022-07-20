import pygame as pg
from Utils.MagicConsts import DIM

pg.init()
SCREEN_WIDTH, SCREEN_HEIGHT = pg.display.Info().current_w, pg.display.Info().current_h
# SCREEN_WIDTH, SCREEN_HEIGHT = 960, 540
BOARD_SIZE = 600 * SCREEN_HEIGHT // 1080
SQ_SIZE = BOARD_SIZE // DIM
BOARD_SIZE = SQ_SIZE * DIM
# top and left margin for the left board in pixels
MARGIN = (SCREEN_HEIGHT - BOARD_SIZE) // 2
# left margin for the right board in pixels, top margin is the same as for the left board
MARGIN_LEFT = SCREEN_WIDTH - BOARD_SIZE - MARGIN
# distance between the left edge of the board and the left edge of reserve pieces in pixels
RESERVE_MARGIN = (BOARD_SIZE - 5 * SQ_SIZE) // 2
# standard font size; every label size in the game is a scale of this constant
FONT_SIZE = 25 * SCREEN_HEIGHT // 1080
FPS = 30
pg.quit()
