import pygame as pg

BACK_COLOR = "gray"
# TOP_COLOR = "black"
# BACK_COLOR = (201, 112, 68)
TOP_COLOR = (33, 11, 0)


class Button:
    def __init__(self, image: pg.image, pos: tuple, text: str, font: [pg.font.SysFont, None], shift=3, topleft=False):
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
                self.textRect2 = self.text2.get_rect(topleft=(self.xPos + shift, self.yPos + shift))
            else:
                self.textRect1 = self.text1.get_rect(center=pos)
                self.textRect2 = self.text2.get_rect(center=(self.xPos + shift, self.yPos + shift))

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
    def __init__(self, text: str, pos: tuple, font: pg.font.SysFont, shift=3, topleft=False):
        self.textInput = text
        self.xPos = pos[0]
        self.yPos = pos[1]
        self.font = font
        self.text1 = self.font.render(self.textInput, True, BACK_COLOR)
        self.text2 = self.font.render(self.textInput, True, TOP_COLOR)
        if topleft:
            self.textRect1 = self.text1.get_rect(topleft=pos)
            self.textRect2 = self.text2.get_rect(topleft=(self.xPos + shift, self.yPos + shift))
        else:
            self.textRect1 = self.text1.get_rect(center=pos)
            self.textRect2 = self.text2.get_rect(center=(self.xPos + shift, self.yPos + shift))

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
    def __init__(self, center: tuple, text: list, font: [pg.font.SysFont, None], head: pg.Surface, body: pg.Surface):
        self.xPos = center[0]
        self.yPos = center[1]
        self.headText = text[0]
        self.bodyText = text[1:]
        self.font = font
        self.state = False
        self.head = head
        self.body = body
        self.buttons = [Button(self.head, center, self.headText, font, shift=2)]
        for i in range(1, len(text)):
            self.buttons.append(Button(self.body, (self.xPos, self.yPos + i * self.body.get_height()), self.bodyText[i - 1], font, shift=2))

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
        return None

    def update(self, screen: pg.Surface):
        self.buttons[0].update(screen)
        if self.state:
            for i in range(1, len(self.buttons)):
                self.buttons[i].update(screen)

    def changeHead(self, index: int):
        if index != 0:
            self.headText = self.bodyText[index - 1]
            self.buttons[0] = Button(self.head, (self.xPos, self.yPos), self.headText, self.font, shift=2)


class ImgDropDownMenu:
    def __init__(self, pos: tuple, images: list, headImages: list, up=False, topLeft=False):
        self.xPos = pos[0]
        self.yPos = pos[1]
        self.state = False
        self.images = images
        self.headImages = headImages
        self.topLeft = topLeft
        self.buttons = [Button(self.headImages[0], pos, "", None, topleft=self.topLeft)]
        mul = -1 if up else 1
        for i in range(len(images)):
            self.buttons.append(Button(self.images[i], (self.xPos, self.yPos + mul * (i + 1) * self.images[i].get_height()), "", None, topleft=self.topLeft))

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
        return None

    def update(self, screen: pg.Surface):
        self.buttons[0].update(screen)
        if self.state:
            for i in range(1, len(self.buttons)):
                self.buttons[i].update(screen)

    def changeHead(self, index: int):
        if index != 0:
            self.buttons[0] = Button(self.headImages[index - 1], (self.xPos, self.yPos), "", None, topleft=self.topLeft)


class DialogWindow:
    def __init__(self, text: str, SCREEN_HEIGHT: int, SCREEN_WIDTH: int, FONT_SIZE: int, bg: pg.Surface, lang: bool):
        self.textInput = text
        self.window = bg
        self.windowRect = self.window.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.font = pg.font.SysFont("Helvetica", FONT_SIZE * 2, True, False)
        self.firstLine, self.secondLine = self.textAdaptation(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.line1_lbl = Label(self.firstLine, (SCREEN_WIDTH // 2, (SCREEN_HEIGHT - self.windowRect.height // 2) // 2), self.font, shift=2)
        if self.secondLine is not None:
            self.line2_lbl = Label(self.secondLine, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), self.font, shift=2)
        else:
            self.line2_lbl = None
        self.yes_btn = Button(None, ((SCREEN_WIDTH - self.windowRect.width // 2) // 2, (SCREEN_HEIGHT + self.windowRect.height // 2) // 2), "Yes" if lang else "Да", self.font)
        self.no_btn = Button(None, ((SCREEN_WIDTH + self.windowRect.width // 2) // 2, (SCREEN_HEIGHT + self.windowRect.height // 2) // 2), "No" if lang else "Нет", self.font)

    def textAdaptation(self, SCREEN_WIDTH: int, SCREEN_HEIGHT: int):
        text = self.font.render(self.textInput, True, BACK_COLOR)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, (SCREEN_HEIGHT - self.windowRect.height // 2) // 2))
        if rect.width + 30 < self.windowRect.width:
            return self.textInput, None
        else:
            words = self.textInput.split(" ")
            firstLine = ""
            line = words[0]
            index = 0
            for word in words[1:]:
                index += 1
                firstLine = line
                line += f" {word}"
                text = self.font.render(line, True, BACK_COLOR)
                rect = text.get_rect(center=(SCREEN_WIDTH // 2, (SCREEN_HEIGHT - self.windowRect.height // 2) // 2))
                if rect.width + 30 >= self.windowRect.width:
                    break
            return firstLine, " ".join(words[index:])

    def update(self, screen: pg.Surface, position: tuple):
        screen.blit(self.window, self.windowRect)
        self.line1_lbl.update(screen)
        if self.line2_lbl is not None:
            self.line2_lbl.update(screen)
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
        else:
            self.image = image
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
        self.angle += 4
        if self.angle == 360:
            self.angle = 0
        self.rotate()
        screen.blit(self.image, self.rect)

    def rotate(self):
        self.image = pg.transform.rotate(self.orig_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
