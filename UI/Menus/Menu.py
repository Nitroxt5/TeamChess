from TeamChess.UI.WindowSizeConsts import SCREEN_HEIGHT, SCREEN_WIDTH


class Menu:
    def __init__(self, screen, resourceLoader, menuName_lbl):
        self._screen = screen
        self._RL = resourceLoader
        self._menuName_lbl = menuName_lbl

    def _drawMenu(self):
        """Draws background and a header for menus"""
        self._screen.blit(self._RL.IMAGES["BG"], (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        self._screen.blit(self._RL.IMAGES["header"], (SCREEN_WIDTH // 8, 0, SCREEN_WIDTH // 4 * 3, SCREEN_HEIGHT // 5))
        self._updateUIObjects([self._menuName_lbl])

    def _updateUIObjects(self, UIObjects: list):
        """Calls update method for every object in UIObjects"""
        for obj in UIObjects:
            obj.update(self._screen)

    @staticmethod
    def _changeColorOfUIObjects(mousePos: tuple, UIObjects: list):
        """Calls changeColor method for every object in UIObjects"""
        for obj in UIObjects:
            obj.changeColor(mousePos)

    def create(self, *args):
        pass
