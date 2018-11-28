""" Play minesweeper using the QT interface. """
from .gui import MinesweeperGUI
from .parser import parse_args


args = parse_args()
gui = MinesweeperGUI(**vars(args))
gui.exec()
