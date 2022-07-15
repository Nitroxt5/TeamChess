import pygame as pg
from time import perf_counter

BACK_COLOR = "gray"
# TOP_COLOR = "black"
# BACK_COLOR = (201, 112, 68)
TOP_COLOR = (33, 11, 0)


class UIObject:
    def __init__(self, pos: tuple):
        self._xPos = pos[0]
        self._yPos = pos[1]

    def update(self, screen: pg.Surface):
        pass


class Button(UIObject):
    def __init__(self, image: pg.image, pos: tuple, text: str, font: [pg.font.SysFont, None], shift=3, topleft=False):
        super().__init__(pos)
        self._image = image
        self._font = font
        self._textInput = text
        if self._font is not None:
            self._text1 = self._font.render(self._textInput, True, BACK_COLOR)
            self._text2 = self._font.render(self._textInput, True, TOP_COLOR)
        if self._image is None:
            self._image = self._text1
        if topleft:
            self._rect = self._image.get_rect(topleft=(self._xPos, self._yPos))
        else:
            self._rect = self._image.get_rect(center=(self._xPos, self._yPos))
        if self._font is not None:
            if topleft:
                self._textRect1 = self._text1.get_rect(topleft=pos)
                self._textRect2 = self._text2.get_rect(topleft=(self._xPos + shift, self._yPos + shift))
            else:
                self._textRect1 = self._text1.get_rect(center=pos)
                self._textRect2 = self._text2.get_rect(center=(self._xPos + shift, self._yPos + shift))

    def update(self, screen: pg.Surface):
        if self._image is not None:
            screen.blit(self._image, self._rect)
        if self._font is not None:
            screen.blit(self._text1, self._textRect1)
            screen.blit(self._text2, self._textRect2)

    def checkForInput(self, position: tuple):
        if self._rect.left < position[0] < self._rect.right and self._rect.top < position[1] < self._rect.bottom:
            return True
        return False

    def changeColor(self, position: tuple):
        if self._font is not None:
            if self.checkForInput(position):
                self._text1 = self._font.render(self._textInput, True, TOP_COLOR)
                self._text2 = self._font.render(self._textInput, True, BACK_COLOR)
            else:
                self._text1 = self._font.render(self._textInput, True, BACK_COLOR)
                self._text2 = self._font.render(self._textInput, True, TOP_COLOR)

    @property
    def height(self):
        return self._rect.height


class RadioButton(UIObject):
    def __init__(self, center: tuple, state: bool, onImage: pg.Surface, offImage: pg.Surface):
        super().__init__(center)
        self._onImage = onImage
        self._offImage = offImage
        self._state = state
        if self._state:
            self._activeImage = self._onImage
        else:
            self._activeImage = self._offImage
        self._rect = self._activeImage.get_rect(center=center)

    def switch(self):
        self._state = not self._state
        if self._state:
            self._activeImage = self._onImage
        else:
            self._activeImage = self._offImage

    def update(self, screen: pg.Surface):
        screen.blit(self._activeImage, self._rect)

    def checkForInput(self, position: tuple):
        if self._rect.left < position[0] < self._rect.right and self._rect.top < position[1] < self._rect.bottom:
            return True
        return False

    def changeColor(self, position: tuple):
        if self.checkForInput(position):
            self._activeImage = self._onImage
        else:
            self._activeImage = self._offImage

    @property
    def state(self):
        return self._state


class Label(UIObject):
    def __init__(self, text: str, pos: tuple, font: pg.font.SysFont, shift=3, topleft=False):
        super().__init__(pos)
        self._textInput = text
        self._font = font
        self._text1 = self._font.render(self._textInput, True, BACK_COLOR)
        self._text2 = self._font.render(self._textInput, True, TOP_COLOR)
        if topleft:
            self._textRect1 = self._text1.get_rect(topleft=pos)
            self._textRect2 = self._text2.get_rect(topleft=(self._xPos + shift, self._yPos + shift))
        else:
            self._textRect1 = self._text1.get_rect(center=pos)
            self._textRect2 = self._text2.get_rect(center=(self._xPos + shift, self._yPos + shift))

    def update(self, screen: pg.Surface):
        screen.blit(self._text1, self._textRect1)
        screen.blit(self._text2, self._textRect2)


class RadioLabel(UIObject):
    def __init__(self, text1: str, text2: str, state: bool, topleft: tuple, font: pg.font.SysFont):
        super().__init__(topleft)
        self._textInput1 = text1
        self._textInput2 = text2
        self._state = state
        self._font = font
        self._text1 = (self._font.render(self._textInput1, True, BACK_COLOR), self._font.render(self._textInput1, True, TOP_COLOR))
        self._text2 = (self._font.render(self._textInput2, True, BACK_COLOR), self._font.render(self._textInput2, True, TOP_COLOR))
        self._textRect1 = (self._text1[0].get_rect(topleft=topleft), self._text1[1].get_rect(topleft=(self._xPos + 2, self._yPos + 2)))
        self._textRect2 = (self._text2[0].get_rect(topleft=topleft), self._text2[1].get_rect(topleft=(self._xPos + 2, self._yPos + 2)))

    def switch(self):
        self._state = not self._state

    def update(self, screen: pg.Surface):
        if self._state:
            screen.blit(self._text1[0], self._textRect1[0])
            screen.blit(self._text1[1], self._textRect1[1])
        else:
            screen.blit(self._text2[0], self._textRect2[0])
            screen.blit(self._text2[1], self._textRect2[1])


class DropDownMenu(UIObject):
    def __init__(self, center: tuple, text: list, font: [pg.font.SysFont, None], head: pg.Surface, body: pg.Surface):
        super().__init__(center)
        self._headText = text[0]
        self._bodyText = text[1:]
        self._font = font
        self._state = False
        self._head = head
        self._body = body
        self._buttons = [Button(self._head, center, self._headText, font, shift=2)]
        for i in range(1, len(text)):
            self._buttons.append(Button(self._body, (self._xPos, self._yPos + i * self._body.get_height()), self._bodyText[i - 1], font, shift=2))

    def _changeHead(self, index: int):
        if index != 0:
            self._headText = self._bodyText[index - 1]
            self._buttons[0] = Button(self._head, (self._xPos, self._yPos), self._headText, self._font, shift=2)

    def switch(self):
        self._state = not self._state

    def checkForInput(self, position: tuple):
        return self._buttons[0].checkForInput(position)

    def checkForChoice(self, position: tuple):
        if self._state:
            for i in range(1, len(self._buttons)):
                if self._buttons[i].checkForInput(position):
                    self._changeHead(i)
                    self.switch()
                    return i
        return None

    def update(self, screen: pg.Surface):
        self._buttons[0].update(screen)
        if self._state:
            for i in range(1, len(self._buttons)):
                self._buttons[i].update(screen)

    def changeColor(self, position):
        for button in self._buttons:
            button.changeColor(position)

    @property
    def height(self):
        return self._buttons[0].height


class ImgDropDownMenu(UIObject):
    def __init__(self, pos: tuple, images: list, headImages: list, up=False, topLeft=False):
        super().__init__(pos)
        self._state = False
        self._images = images
        self._headImages = headImages
        self._topLeft = topLeft
        self._buttons = [Button(self._headImages[0], pos, "", None, topleft=self._topLeft)]
        mul = -1 if up else 1
        for i in range(len(images)):
            self._buttons.append(Button(self._images[i], (self._xPos, self._yPos + mul * (i + 1) * self._images[i].get_height()), "", None, topleft=self._topLeft))

    def _changeHead(self, index: int):
        if index != 0:
            self._buttons[0] = Button(self._headImages[index - 1], (self._xPos, self._yPos), "", None, topleft=self._topLeft)

    def switch(self):
        self._state = not self._state

    def checkForInput(self, position: tuple):
        return self._buttons[0].checkForInput(position)

    def checkForChoice(self, position: tuple):
        if self._state:
            for i in range(1, len(self._buttons)):
                if self._buttons[i].checkForInput(position):
                    self._changeHead(i)
                    self.switch()
                    return i
        return None

    def update(self, screen: pg.Surface):
        self._buttons[0].update(screen)
        if self._state:
            for i in range(1, len(self._buttons)):
                self._buttons[i].update(screen)


class DialogWindow(UIObject):
    def __init__(self, text: str, SCREEN_HEIGHT: int, SCREEN_WIDTH: int, FONT_SIZE: int, bg: pg.Surface, lang: bool):
        super().__init__((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self._textInput = text
        self._window = bg
        self._windowRect = self._window.get_rect(center=(self._xPos, self._yPos))
        self._font = pg.font.SysFont("Helvetica", FONT_SIZE * 2, True, False)
        self._firstLine, self._secondLine = self._textAdaptation(SCREEN_WIDTH, SCREEN_HEIGHT)
        self._line1_lbl = Label(self._firstLine, (SCREEN_WIDTH // 2, (SCREEN_HEIGHT - self._windowRect.height // 2) // 2), self._font, shift=2)
        if self._secondLine is not None:
            self._line2_lbl = Label(self._secondLine, (self._xPos, self._yPos), self._font, shift=2)
        else:
            self._line2_lbl = None
        self._yes_btn = Button(None, ((SCREEN_WIDTH - self._windowRect.width // 2) // 2, (SCREEN_HEIGHT + self._windowRect.height // 2) // 2), "Yes" if lang else "Да", self._font)
        self._no_btn = Button(None, ((SCREEN_WIDTH + self._windowRect.width // 2) // 2, (SCREEN_HEIGHT + self._windowRect.height // 2) // 2), "No" if lang else "Нет", self._font)

    def _textAdaptation(self, SCREEN_WIDTH: int, SCREEN_HEIGHT: int):
        text = self._font.render(self._textInput, True, BACK_COLOR)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, (SCREEN_HEIGHT - self._windowRect.height // 2) // 2))
        if rect.width + 30 < self._windowRect.width:
            return self._textInput, None
        else:
            words = self._textInput.split(" ")
            firstLine = ""
            line = words[0]
            index = 0
            for word in words[1:]:
                index += 1
                firstLine = line
                line += f" {word}"
                text = self._font.render(line, True, BACK_COLOR)
                rect = text.get_rect(center=(SCREEN_WIDTH // 2, (SCREEN_HEIGHT - self._windowRect.height // 2) // 2))
                if rect.width + 30 >= self._windowRect.width:
                    break
            return firstLine, " ".join(words[index:])

    def update(self, screen: pg.Surface):
        screen.blit(self._window, self._windowRect)
        self._line1_lbl.update(screen)
        if self._line2_lbl is not None:
            self._line2_lbl.update(screen)
        for btn in [self._yes_btn, self._no_btn]:
            btn.update(screen)

    def changeColor(self, position: tuple):
        for btn in [self._yes_btn, self._no_btn]:
            btn.changeColor(position)

    def checkYesForInput(self, position: tuple):
        return self._yes_btn.checkForInput(position)

    def checkNoForInput(self, position: tuple):
        return self._no_btn.checkForInput(position)


class Image(UIObject):
    def __init__(self, image: pg.Surface, center: tuple, imageSize: [tuple, None]):
        super().__init__(center)
        if imageSize is not None:
            self._width = imageSize[0]
            self._height = imageSize[1]
            self._image = pg.transform.scale(image, (self._width, self._height))
        else:
            self._image = image
        self._rect = self._image.get_rect(center=(self._xPos, self._yPos))

    def update(self, screen: pg.Surface):
        screen.blit(self._image, self._rect)

    def move(self, newPos: tuple):
        self._xPos = newPos[0]
        self._yPos = newPos[1]
        self._rect = self._image.get_rect(center=(self._xPos, self._yPos))


class Hourglass:
    def __init__(self, currentPlayer: int, image: pg.Surface, MARGIN: int, MARGIN_LEFT: int, SQ_SIZE: int, SCREEN_HEIGHT: int):
        self._image = image
        self._orig_image = self._image
        if currentPlayer == 0:
            self._rect = pg.Rect(MARGIN, SCREEN_HEIGHT - MARGIN + 5, SQ_SIZE, SQ_SIZE)
        elif currentPlayer == 1:
            self._rect = pg.Rect(MARGIN, MARGIN - SQ_SIZE - 5, SQ_SIZE, SQ_SIZE)
        elif currentPlayer == 2:
            self._rect = pg.Rect(MARGIN_LEFT, MARGIN - SQ_SIZE - 5, SQ_SIZE, SQ_SIZE)
        else:
            self._rect = pg.Rect(MARGIN_LEFT, SCREEN_HEIGHT - MARGIN + 5, SQ_SIZE, SQ_SIZE)
        self._angle = 0

    def _rotate(self):
        self._image = pg.transform.rotate(self._orig_image, self._angle)
        self._rect = self._image.get_rect(center=self._rect.center)

    def update(self, screen: pg.Surface):
        self._angle += 4
        if self._angle == 360:
            self._angle = 0
        self._rotate()
        screen.blit(self._image, self._rect)


class Timer(UIObject):
    def __init__(self, center: tuple, value: [float, None], image: pg.Surface, font: pg.font.SysFont):
        super().__init__(center)
        self._value = value
        self._image = image
        self._rect = self._image.get_rect(center=(self._xPos, self._yPos))
        self._font = font
        self._state = False
        self._currentTime = None
        self._text1 = self._font.render(self._getMinSec(), True, BACK_COLOR)
        self._text2 = self._font.render(self._getMinSec(), True, TOP_COLOR)
        self._textRect1 = self._text1.get_rect(center=center)
        self._textRect2 = self._text2.get_rect(center=(self._xPos + 2, self._yPos + 2))

    def _getMinSec(self):
        return f"{(round(self._value) // 60):02}:{(round(self._value) % 60):02}"

    def _count(self):
        if self._state and self._currentTime is not None:
            self._value -= perf_counter() - self._currentTime
            self._currentTime = perf_counter()

    def switch(self):
        self._state = not self._state
        self._currentTime = perf_counter()

    def countdownEnd(self):
        if self._value < 0.5:
            self._state = False
            return True
        return False

    def update(self, screen: pg.Surface):
        self._count()
        self._text1 = self._font.render(self._getMinSec(), True, BACK_COLOR)
        self._text2 = self._font.render(self._getMinSec(), True, TOP_COLOR)
        screen.blit(self._image, self._rect)
        screen.blit(self._text1, self._textRect1)
        screen.blit(self._text2, self._textRect2)

    @property
    def value(self):
        return self._value

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value: bool):
        self._state = value
