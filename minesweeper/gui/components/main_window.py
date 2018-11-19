""" The minesweeper GUI. """
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from .menu_bar import MenuBar
from .reset_bar import ResetBar
from .minefield import Minefield


class MainWindow(QMainWindow):
    def __init__(self, debug_mode=False):
        """ :param debug_mode: Whether to create the debug menu, allowing exporting of the state and ground truth of the
                          game.
        """
        super().__init__()
        self.setWindowTitle('Minesweeper')
        self.setMenuBar(MenuBar(self, debug_mode))
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)
        self.centralWidget().setLayout(layout)
        layout.addWidget(ResetBar(self))
        layout.addWidget(Minefield(self))
        # Styling.
        layout.setSizeConstraint(layout.SetFixedSize)
        layout.setSpacing(0)
        self.setWindowIcon(QIcon(':logo.ico'))
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet('''
            * {
                spacing: 0;
                margin: 0;
                padding: 0;
            }
            QMenuBar {
                background-color: #BEBEBE;
            }
            QMenuBar::item {
                background-color: none;
                border: none;
                padding: 3px 5px 3px 5px;
                color: #000;
            }
            QMenuBar::item:selected {
                color: #0000DF;
            }
            QMenu::item:selected {
                color: #0000DF;
            }
            /*QMenu::indicator:checked {
                image: url(:check_mark.png);
            }*/
            QMenu {
                background-color: #BEBEBE;
                border: 4px double #7F7F7F;
            }
            .MainWindow > .QWidget {
                background-color: #BEBEBE;
                padding: 6px;
                border: 2px solid #FFF;
                border-bottom: 2px solid #7A7A7A;
                border-right: 2px solid #7A7A7A;
            }
            .SevenSegmentDisplay {
                background-color: red;
                border: 1px solid #7A7A7A;
                border-bottom: 1px solid #FFF;
                border-right: 1px solid #FFF;
            }
            .ResetBar {
                background-color: #BEBEBE;
                border: 2px solid #7A7A7A;
                border-bottom: 2px solid #FFF;
                border-right: 2px solid #FFF;
                margin-bottom: 6px;
            }
            .Minefield {
                background-color: #BEBEBE;
                border: 2px solid #7A7A7A;
                border-bottom: 2px solid #FFF;
                border-right: 2px solid #FFF;
            }
            .ResetButton {
                height: 26px;
                width: 26px;
            }
            .Square {
                background-color: blue;
            }
        ''')
