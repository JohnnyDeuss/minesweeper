""" A seven segment display component for displaying numbers the minesweeper GUI.
    Displays any positive values up to 999.
"""
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QWidget
from PyQt5.QtGui import QPixmapCache
from PyQt5.QtCore import Qt, QCoreApplication


class SevenSegmentDisplay(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.setContentsMargins(1, 1, 0, 0)
        self.setLayout(layout)
        layout.setSpacing(0)
        self.labels = [QLabel() for i in range(3)]
        for i, label in enumerate(self.labels):
            label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            label.setFixedSize(13, 23)
            layout.addWidget(label)
        self.setFixedSize(41, 25)
        # Styling.
        self.setAttribute(Qt.WA_StyledBackground)

    def set_value(self, value):
        """ Set the value of the display. The display can show any positive value up to 999. Does not work with negative
            values.
        """
        value = int(max(min(value, 999), 0))
        digits = [value//100, (value % 100)//10, value % 10]
        for digit, label in zip(digits, self.labels):
            label.setPixmap(QPixmapCache.find_or_get(':ssd{}.png'.format(digit)))
            label.update()
        self.update()   # A lot of updates and more so Qt updates the damn Pixmap.
        QCoreApplication.processEvents()
