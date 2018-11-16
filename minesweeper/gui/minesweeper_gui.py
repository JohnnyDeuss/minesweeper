""" The QT application that acts as the controller for `Minesweepermain_window`."""
from PyQt5.QtWidgets import QApplication, QAction, QActionGroup
from PyQt5.QtGui import QPixmap, QPixmapCache

from .components import MainWindow, ResetButton, Minefield, SevenSegmentDisplay
from . import resources


class MinesweeperGUI(QApplication):

    def __init__(self, game):
        super().__init__([])
        self.game = game
        self.game.add_listener(self.update_timer)
        self.setup_cache()
        self.main_window = MainWindow()
        # Set up the reset button to actually reset the game.
        self.main_window.findChild(ResetButton).clicked.connect(self.reset)
        # Set up the quit menu item to actually quit the application.
        self.main_window.findChild(QAction, 'new_menu_item').triggered.connect(self.reset)
        self.main_window.findChild(QAction, 'quit_menu_item').triggered.connect(self.quit)
        # Set up the difficulty menu items.
        self.main_window.findChild(QActionGroup).triggered.connect(self.difficulty_selected)
        self.set_config('expert')
        self.main_window.show()

    def setup_cache(self):
        """ Add a better lookup method to the QPixmapCache, that retrieves items from the cache, but on failure
            retrieves it from the resources and caches it.
        """
        def find_or_get(path):
            pixmap = QPixmapCache.find(path)
            if pixmap is None:
                return QPixmap(path)
            return pixmap
        QPixmapCache.find_or_get = find_or_get

    def set_config(self, difficulty, **kwargs):
        """ Set the config. The kwargs are used to define width and height for 'custom' difficulty. """
        self.game.set_config(difficulty, **kwargs)
        self.main_window.findChild(SevenSegmentDisplay, 'mine_counter').set_value(self.game.num_mines)
        self.main_window.findChild(SevenSegmentDisplay, 'timer').set_value(0)
        minefield = self.main_window.findChild(Minefield)
        minefield.set_shape(self.game.width, self.game.height)
        for square in minefield.scene().items():
            square.left_clicked.connect(self.left_click_action)
            square.right_clicked.connect(self.right_click_action)
            square.mouse_down.connect(self.minefield_mouse_down)
            square.mouse_release.connect(self.minefield_mouse_release)
        self.main_window.setFixedSize(0, 0)
        self.main_window.centralWidget().adjustSize()

    def reset(self):
        """ Reset the game and the minefield. """
        self.game.reset()
        self.main_window.findChild(SevenSegmentDisplay, 'mine_counter').set_value(self.game.mines_left)
        self.main_window.findChild(SevenSegmentDisplay, 'timer').set_value(0)
        # Reset the squares.
        self.main_window.findChild(Minefield).reset()
        # Set the reset image to the normal reset one.
        self.main_window.findChild(ResetButton).set_state(None)
        self.main_window.findChild(Minefield).repaint()

    def minefield_mouse_down(self):
        """ Change the reset button to a guy with an open mouth when holding down the mouse. """
        if not self.game.done:
            self.main_window.findChild(ResetButton).set_state('clicking')

    def minefield_mouse_release(self):
        """ Change the reset button back to the normal icon. """
        if not self.game.done:
            self.main_window.findChild(ResetButton).set_state(None)

    def left_click_action(self):
        """ Attempt to dig at the given location. """
        x, y = self.sender().x, self.sender().y
        done, opened = self.game.select(x, y)
        minefield = self.main_window.findChild(Minefield)
        for square in opened:
            minefield.square_at(square.x, square.y).set_state(square.value)
        minefield.repaint()
        if done:
            self.main_window.findChild(SevenSegmentDisplay, 'mine_counter').set_value(0)
            self.main_window.findChild(ResetButton).set_state('won' if self.game.is_won() else 'lost')
        self.processEvents()

    def right_click_action(self):
        """ Attempt to place a flag or question mark at the given location. """
        x, y = self.sender().x, self.sender().y
        if self.game.state[y][x] is None:
            if self.game.flag(x, y):
                self.sender().set_state('flag')
                self.main_window.findChild(SevenSegmentDisplay, 'mine_counter').set_value(self.game.mines_left)
        else:
            if self.game.question(x, y):
                self.sender().set_state('flag')
                self.sender().set_state(self.game.state[y][x])
                self.main_window.findChild(SevenSegmentDisplay, 'mine_counter').set_value(self.game.mines_left)
        self.main_window.findChild(Minefield).repaint()

    def difficulty_selected(self, action):
        if action.objectName() == 'custom':
            pass
        elif action.objectName() != self.game.difficulty:
            self.set_config(action.objectName())

    def update_timer(self):
        """ Caller by the minesweeper game whenever the timer changes. Updates the displayed time. """
        self.main_window.findChild(SevenSegmentDisplay, 'timer').set_value(self.game.time())
