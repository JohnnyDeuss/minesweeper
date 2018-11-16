""" The square minefield grid component for the Minesweeper GUI. """
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTransform

from .square import Square


class Minefield(QGraphicsView):

    def __init__(self, parent):
        super().__init__(parent)
        scene = QGraphicsScene(self)
        self.setScene(scene)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def reset(self):
        """ Reset the minefield, closing up all squares. """
        for square in self.scene().items():
            square.set_state(None)

    def set_shape(self, width, height):
        """ Set the shape of the minefield to fit exactly the squares. """
        self.width = width
        self.height = height

        scene = self.scene()
        for square in scene.items():
            square.disconnect()
        scene.clear()
        for x in range(width):
            for y in range(height):
                scene.addItem(Square(x, y))
        self.setFixedSize(width*16+4, height*16+4)  # +4 for borders, apparently.

    def square_at(self, x, y):
        return self.scene().itemAt(x*16, y*16, QTransform())
