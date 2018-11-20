""" Play minesweeper using the QT interface. To play it in the commandline interface, pass 'cmd' as a commandline
    argument.
"""
from .gui import MinesweeperGUI
from .parser import parse_args


args = parse_args()
gui = MinesweeperGUI(**vars(args))
gui.exec()
