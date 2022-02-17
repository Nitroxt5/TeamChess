import pygame as pg

BACK_COLOR = "gray"
TOP_COLOR = "black"


class Button:
    def __init__(self, image: pg.image, pos: tuple, text: str, font: [pg.font.SysFont, None], topleft=False):
        self.image = image
        self.xPos = pos[0]
        self.yPos = pos[1]
        self.font = font
        self.textInput = text
        if self.font is not None:
            self.text1 = self.font.render(self.textInput, True, BACK_COLOR)
            self.text2 = self.font.render(self.textInput, True, TOP_COLOR)
        if self.image is None:
            self.image = self.text1
        if topleft:
            self.rect = self.image.get_rect(topleft=(self.xPos, self.yPos))
        else:
            self.rect = self.image.get_rect(center=(self.xPos, self.yPos))
        if self.font is not None:
            if topleft:
                self.textRect1 = self.text1.get_rect(topleft=pos)
                self.textRect2 = self.text2.get_rect(topleft=(self.xPos + 2, self.yPos + 2))
            else:
                self.textRect1 = self.text1.get_rect(center=pos)
                self.textRect2 = self.text2.get_rect(center=(self.xPos + 2, self.yPos + 2))

    def update(self, screen: pg.Surface):
        if self.image is not None:
            screen.blit(self.image, self.rect)
        if self.font is not None:
            screen.blit(self.text1, self.textRect1)
            screen.blit(self.text2, self.textRect2)

    def checkForInput(self, position: tuple):
        if self.rect.left < position[0] < self.rect.right and self.rect.top < position[1] < self.rect.bottom:
            return True
        return False

    def changeColor(self, position: tuple):
        if self.font is not None:
            if self.checkForInput(position):
                self.text1 = self.font.render(self.textInput, True, TOP_COLOR)
                self.text2 = self.font.render(self.textInput, True, BACK_COLOR)
            else:
                self.text1 = self.font.render(self.textInput, True, BACK_COLOR)
                self.text2 = self.font.render(self.textInput, True, TOP_COLOR)


class RadioButton:
    def __init__(self, center: tuple, state: bool, onImage: pg.Surface, offImage: pg.Surface):
        self.onImage = onImage
        self.offImage = offImage
        self.state = state
        if self.state:
            self.activeImage = self.onImage
        else:
            self.activeImage = self.offImage
        self.xPos = center[0]
        self.yPos = center[1]
        self.rect = self.activeImage.get_rect(center=center)

    def switch(self):
        self.state = not self.state
        if self.state:
            self.activeImage = self.onImage
        else:
            self.activeImage = self.offImage

    def update(self, screen: pg.Surface):
        screen.blit(self.activeImage, self.rect)

    def checkForInput(self, position: tuple):
        if self.rect.left < position[0] < self.rect.right and self.rect.top < position[1] < self.rect.bottom:
            return True
        return False

    def changeColor(self, position: tuple):
        if self.checkForInput(position):
            self.activeImage = self.onImage
        else:
            self.activeImage = self.offImage


class Label:
    def __init__(self, text: str, pos: tuple, font: pg.font.SysFont, topleft=False):
        self.textInput = text
        self.xPos = pos[0]
        self.yPos = pos[1]
        self.font = font
        self.text1 = self.font.render(self.textInput, True, BACK_COLOR)
        self.text2 = self.font.render(self.textInput, True, TOP_COLOR)
        if topleft:
            self.textRect1 = self.text1.get_rect(topleft=pos)
            self.textRect2 = self.text2.get_rect(topleft=(self.xPos + 2, self.yPos + 2))
        else:
            self.textRect1 = self.text1.get_rect(center=pos)
            self.textRect2 = self.text2.get_rect(center=(self.xPos + 2, self.yPos + 2))

    def update(self, screen: pg.Surface):
        screen.blit(self.text1, self.textRect1)
        screen.blit(self.text2, self.textRect2)


class RadioLabel:
    def __init__(self, text1: str, text2: str, state: bool, topleft: tuple, font: pg.font.SysFont):
        self.textInput1 = text1
        self.textInput2 = text2
        self.state = state
        self.xPos = topleft[0]
        self.yPos = topleft[1]
        self.font = font
        self.text1 = (self.font.render(self.textInput1, True, BACK_COLOR), self.font.render(self.textInput1, True, TOP_COLOR))
        self.text2 = (self.font.render(self.textInput2, True, BACK_COLOR), self.font.render(self.textInput2, True, TOP_COLOR))
        self.textRect1 = (self.text1[0].get_rect(topleft=topleft), self.text1[1].get_rect(topleft=(self.xPos + 2, self.yPos + 2)))
        self.textRect2 = (self.text2[0].get_rect(topleft=topleft), self.text2[1].get_rect(topleft=(self.xPos + 2, self.yPos + 2)))

    def switch(self):
        self.state = not self.state

    def update(self, screen: pg.Surface):
        if self.state:
            screen.blit(self.text1[0], self.textRect1[0])
            screen.blit(self.text1[1], self.textRect1[1])
        else:
            screen.blit(self.text2[0], self.textRect2[0])
            screen.blit(self.text2[1], self.textRect2[1])


class DropDownMenu:
    def __init__(self, center: tuple, text: list, font: pg.font.SysFont, BOARD_SIZE: int, SQ_SIZE: int):
        self.xPos = center[0]
        self.yPos = center[1]
        self.headText = text[0]
        self.bodyText = text[1:]
        self.font = font
        self.state = False
        self.head = pg.Surface((BOARD_SIZE // 4, SQ_SIZE // 2))
        self.head.fill((127, 97, 70))
        self.body = pg.Surface((BOARD_SIZE // 4, SQ_SIZE // 2))
        self.body.fill((153, 117, 85))
        self.rects = [self.head.get_rect(center=center)]
        self.buttons = [Button(None, center, self.headText, font)]
        for i in range(1, len(text)):
            self.rects.append(self.body.get_rect(center=(self.xPos, self.yPos + i * SQ_SIZE // 2)))
            self.buttons.append(Button(None, (self.xPos, self.yPos + i * SQ_SIZE // 2), self.bodyText[i - 1], font))

    def switch(self):
        self.state = not self.state

    def checkForInput(self, position: tuple):
        return self.buttons[0].checkForInput(position)

    def checkForChoice(self, position: tuple):
        if self.state:
            for i in range(1, len(self.buttons)):
                if self.buttons[i].checkForInput(position):
                    self.changeHead(i)
                    self.switch()
                    return i
        return 0

    def update(self, screen: pg.Surface):
        screen.blit(self.head, self.rects[0])
        self.buttons[0].update(screen)
        if self.state:
            for i in range(1, len(self.rects)):
                screen.blit(self.body, self.rects[i])
                self.buttons[i].update(screen)

    def changeHead(self, index: int):
        if index != 0:
            self.headText = self.bodyText[index - 1]
            self.buttons[0] = Button(None, (self.xPos, self.yPos), self.headText, self.font)


class DialogWindow:
    def __init__(self, text: str, SCREEN_HEIGHT: int, SCREEN_WIDTH: int, FONT_SIZE: int):
        self.textInput = text
        self.window = pg.Surface((SCREEN_WIDTH // 3, SCREEN_HEIGHT // 4))
        self.window.fill((127, 97, 70))
        self.windowRect = self.window.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.font = pg.font.SysFont("Helvetica", FONT_SIZE * 2, True, False)
        self.question = Label(text, (SCREEN_WIDTH // 2, (SCREEN_HEIGHT - self.windowRect.height // 2) // 2), self.font)
        self.yes_btn = Button(None, ((SCREEN_WIDTH - self.windowRect.width // 2) // 2, (SCREEN_HEIGHT + self.windowRect.height // 2) // 2), "Yes", self.font)
        self.no_btn = Button(None, ((SCREEN_WIDTH + self.windowRect.width // 2) // 2, (SCREEN_HEIGHT + self.windowRect.height // 2) // 2), "No", self.font)

    def update(self, screen: pg.Surface, position: tuple):
        screen.blit(self.window, self.windowRect)
        self.question.update(screen)
        for btn in [self.yes_btn, self.no_btn]:
            btn.update(screen)
            btn.changeColor(position)


class Image:
    def __init__(self, image: pg.Surface, center: tuple, imageSize: [tuple, None]):
        self.xPos = center[0]
        self.yPos = center[1]
        if imageSize is not None:
            self.width = imageSize[0]
            self.height = imageSize[1]
            self.image = pg.transform.scale(image, (self.width, self.height))
        self.rect = self.image.get_rect(center=(self.xPos, self.yPos))

    def update(self, screen: pg.Surface):
        screen.blit(self.image, self.rect)

    def move(self, newPos: tuple):
        self.xPos = newPos[0]
        self.yPos = newPos[1]
        self.rect = self.image.get_rect(center=(self.xPos, self.yPos))


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
