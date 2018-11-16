""" The top bar component, with the reset bar timer and mine counter for the minesweeper GUI. """
from PyQt5.QtWidgets import QWidget, QHBoxLayout
from PyQt5.QtCore import Qt

from .seven_segment_display import SevenSegmentDisplay
from .reset_button import ResetButton


class ResetBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        # The mine counter.
        mine_counter = SevenSegmentDisplay(self)
        mine_counter.setObjectName('mine_counter')
        layout.addWidget(mine_counter, 0, Qt.AlignLeft)
        # The reset button.
        layout.addWidget(ResetButton(self), 0, Qt.AlignCenter)
        # The timer.
        timer = SevenSegmentDisplay(self)
        timer.setObjectName('timer')
        layout.addWidget(timer, 0, Qt.AlignRight)
        self.setLayout(layout)
        # Styling.
        layout.setSpacing(0)
        self.setAttribute(Qt.WA_StyledBackground, True)
