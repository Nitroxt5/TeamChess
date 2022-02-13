import pygame as pg


class Button:
    def __init__(self, image: pg.image, pos: tuple, text_input: str, font: [pg.font.SysFont, None], base_color: [tuple, str, pg.Color, None], hovering_color: [tuple, str, pg.Color, None]):
        self.image = image
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.font = font
        self.base_color, self.hovering_color = base_color, hovering_color
        self.text_input = text_input
        if self.font is not None:
            self.text1 = self.font.render(self.text_input, True, self.base_color)
            self.text2 = self.font.render(self.text_input, True, self.hovering_color)
        if self.image is None:
            self.image = self.text1
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        if self.font is not None:
            self.text_rect1 = self.text1.get_rect(center=(self.x_pos, self.y_pos))
            self.text_rect2 = self.text2.get_rect(center=(self.x_pos + 2, self.y_pos + 2))

    def update(self, screen: pg.Surface):
        if self.image is not None:
            screen.blit(self.image, self.rect)
        if self.font is not None:
            screen.blit(self.text1, self.text_rect1)
            screen.blit(self.text2, self.text_rect2)

    def checkForInput(self, position: tuple):
        if self.rect.left < position[0] < self.rect.right and self.rect.top < position[1] < self.rect.bottom:
            return True
        return False

    def changeColor(self, position: tuple):
        if self.font is not None:
            if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
                self.text1 = self.font.render(self.text_input, True, self.hovering_color)
                self.text2 = self.font.render(self.text_input, True, self.base_color)
            else:
                self.text1 = self.font.render(self.text_input, True, self.base_color)
                self.text2 = self.font.render(self.text_input, True, self.hovering_color)


class Hourglass:
    def __init__(self, currentPlayer: int, image: pg.Surface, MARGIN: int, MARGIN_LEFT: int, SQ_SIZE: int, SCREEN_HEIGHT: int):
        self.image = image
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
