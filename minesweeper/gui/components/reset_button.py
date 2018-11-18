""" The reset button for the Minesweeper GUI. """
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, pyqtSlot


class ResetButton(QPushButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName('reset_button')
        self.setFixedSize(26, 26)
        self.setIconSize(QSize(26, 26))
        self.set_state('None')

    @pyqtSlot(str)
    def set_state(self, state):
        """ Set the state of the reset button, which is either "None", if the game is just going, "won", "lost" or
            "clicking". "clicking" happens when the minefield is being clicked.
        """
        if state == 'None':
            icon = QIcon(':reset.png'.format())
        else:
            icon = QIcon(':reset_{}.png'.format(state))
            if icon.isNull():
                raise ValueError('The given state ({}) does not exist.'.format(state))
        self.setIcon(icon)
