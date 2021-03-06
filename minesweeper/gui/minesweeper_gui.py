""" The QT application that acts as the controller for `gui.main_window`. """
import sys

from PyQt5.QtWidgets import QApplication, QAction, QActionGroup
from PyQt5.QtGui import QPixmap, QPixmapCache
from PyQt5.QtCore import pyqtSignal, pyqtSlot

from .components import MainWindow, ResetButton, Minefield, SevenSegmentDisplay
from . import resources     # Loads the resources, even though the module is not directly referenced.
from .. import Minesweeper


class MinesweeperGUI(QApplication):
    reset_value_changed = pyqtSignal(str)
    square_value_changed = pyqtSignal(int, int, str)
    shape_changed = pyqtSignal(int, int)
    game_reset = pyqtSignal()
    timer_changed = pyqtSignal(int)
    mine_counter_changed = pyqtSignal(int)
    move_ended = pyqtSignal()

    def __init__(self, debug_mode=False, difficulty='expert', **kwargs):
        super().__init__([])
        if debug_mode:
            self.enable_qt_exceptions()
        self.game = Minesweeper()
        self.setup_cache()
        self.main_window = MainWindow(debug_mode)
        self.connect_interface(debug_mode)
        self.set_config(difficulty, **kwargs)
        self.main_window.show()
        # Listen for timer updates.
        self.game.add_listener(self.update_timer)

    @staticmethod
    def enable_qt_exceptions():
        """ Qt doesn't do feedback from exceptions well due to threads, so override the exception handling
            to print out the exceptions and then pass it through to the original hook.
        """
        def exception_hook(exctype, value, traceback):
            """ Print out any exception and pass it through to the original exception hook. """
            print(exctype, value, traceback)
            sys._excepthook(exctype, value, traceback)
            sys.exit(1)

        sys._excepthook = sys.excepthook  # Back up the original exception hook...
        sys.excepthook = exception_hook   # And replace it with one that will print out exceptions.

    def connect_interface(self, debug_mode):
        """ Connect this controller with the different interface components.
            :param debug_mode: Whether we're in debug mode, meaning we have to connect some extras.
        """
        # Set up the reset button and the "New" menu item to reset the game.
        reset_button = self.main_window.findChild(ResetButton)
        reset_button.clicked.connect(self.reset)
        self.reset_value_changed.connect(reset_button.set_state)
        # Connect the SSD displays.
        self.timer_changed.connect(self.main_window.findChild(SevenSegmentDisplay, 'timer').set_value)
        self.mine_counter_changed.connect(self.main_window.findChild(SevenSegmentDisplay, 'mine_counter').set_value)
        # Connect the reset button.
        self.reset_value_changed.connect(reset_button.set_state)
        # Connect the minefield.
        minefield = self.main_window.findChild(Minefield)
        self.game_reset.connect(minefield.reset)
        self.shape_changed.connect(minefield.set_shape)
        self.move_ended.connect(minefield.refresh)
        # Menu items.
        self.main_window.findChild(QAction, 'new_menu_item').triggered.connect(self.reset)
        self.main_window.findChild(QAction, 'quit_menu_item').triggered.connect(self.main_window.close)
        self.main_window.findChild(QActionGroup).triggered.connect(self.difficulty_selected)
        # Debug mode extras.
        if debug_mode:
            self.main_window.findChild(QAction, 'log_state').triggered.connect(lambda: print(self.game.state))
            self.main_window.findChild(QAction, 'log_mines').triggered.connect(lambda: print(self.game._mines))

    @staticmethod
    def setup_cache():
        """ Add a better lookup method to the QPixmapCache; one that retrieves items from the cache, but on failure
            retrieves it from the resources and caches it.
        """
        def find_or_get(path):
            pixmap = QPixmapCache.find(path)
            if pixmap is None:
                pixmap = QPixmap(path)
                QPixmapCache.insert(path, pixmap)
                return pixmap
            return pixmap
        QPixmapCache.find_or_get = find_or_get

    def set_config(self, difficulty, **kwargs):
        """ Set the game's config. The kwargs are used to define width and height for 'custom' difficulty.
            After setting the config, it updates the interface to match the new state. Also does the connecting of
            slots and signals of the new minefield.
        """
        self.game.set_config(difficulty, **kwargs)
        # Make sure the Game menu's difficulty check mark reflects the difficulty change.
        self.main_window.findChild(QAction, difficulty).setChecked(True)
        # Reset the counters.
        self.mine_counter_changed.emit(self.game.num_mines)
        self.timer_changed.emit(0)
        # Reset the minefield.
        minefield = self.main_window.findChild(Minefield)
        self.shape_changed.emit(self.game.width, self.game.height)
        # Connect the squares to the different actions that can occur when clicking them.
        for square in minefield.scene().items():
            square.left_clicked.connect(self.left_click_action)
            square.right_clicked.connect(self.right_click_action)
            square.mouse_down.connect(self.minefield_mouse_down)
            square.mouse_release.connect(self.minefield_mouse_release)
            self.square_value_changed.connect(square.state_change)
        # Set the window to be the size of its contents.
        self.main_window.setFixedSize(0, 0)
        self.main_window.centralWidget().adjustSize()

    def reset(self):
        """ Reset the game and the minefield. """
        self.game.reset()
        self.mine_counter_changed.emit(self.game.mines_left)
        self.timer_changed.emit(0)
        # Reset the squares.
        self.game_reset.emit()
        # Set the reset image to the normal reset one.
        self.reset_value_changed.emit('None')

    def minefield_mouse_down(self):
        """ Change the reset button to a guy with an open mouth when holding down the mouse. """
        if not self.game.done:
            self.reset_value_changed.emit('clicking')

    def minefield_mouse_release(self):
        """ Change the reset button back to the normal icon. """
        if not self.game.done:
            self.reset_value_changed.emit('None')

    @pyqtSlot(int, int)
    def left_click_action(self, x, y):
        """ Attempt to dig at the given location. """
        done, opened = self.game.select(x, y)
        for square in opened:
            self.square_value_changed.emit(square.x, square.y, str(square.value))
        if done:
            self.mine_counter_changed.emit(0)
            self.reset_value_changed.emit('won' if self.game.is_won() else 'lost')
        self.move_ended.emit()
        self.processEvents()

    @pyqtSlot(int, int)
    def right_click_action(self, x, y):
        """ Attempt to place a flag or question mark at the given location. """
        if self.game.state[y][x] is None:
            if self.game.flag(x, y):
                self.square_value_changed.emit(x, y, 'flag')
                self.mine_counter_changed.emit(self.game.mines_left)
        else:
            if self.game.question(x, y):
                self.square_value_changed.emit(x, y, str(self.game.state[y][x]))
                self.mine_counter_changed.emit(self.game.mines_left)
        self.move_ended.emit()

    def difficulty_selected(self, action):
        if action.objectName() == 'custom':
            pass    # Maybe later.
        elif action.objectName() != self.game.difficulty:
            self.set_config(action.objectName())

    def update_timer(self):
        """ Called by the minesweeper game whenever the timer changes. Updates the displayed time. """
        self.timer_changed.emit(self.game.time())
