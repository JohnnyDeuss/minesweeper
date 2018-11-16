""" Play minesweeper using the QT interface. To play it in the commandline interface, pass 'cmd' as a commandline
    argument.
"""
from . import Minesweeper
from .gui import MinesweeperGUI
import sys


def enable_qt_exceptions():
    """ Qt doesn't do feedback from exceptions well, due to threads, so override the exception handling
        to print out the exceptions and then pass it through to the original hook.
    """
    def exception_hook(exctype, value, traceback):
        """ Print out any exception and pass it through to the original exception hook. """
        print(exctype, value, traceback)
        sys._excepthook(exctype, value, traceback)
        sys.exit(1)
    sys._excepthook = sys.excepthook    # Back up the original exception hook...
    sys.excepthook = exception_hook     # And replace it with one that will print out exceptions.


game = Minesweeper()
game.set_config('expert')
enable_qt_exceptions()
gui = MinesweeperGUI(game)
gui.exec()
