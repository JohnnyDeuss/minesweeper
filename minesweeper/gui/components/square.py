""" A graphics item for a single square on the minefield for the minesweeper GUI. """
from PyQt5.QtGui import QPixmapCache, QTransform
from PyQt5.QtWidgets import QGraphicsObject
from PyQt5.QtCore import pyqtSignal, Qt, QRectF


class Square(QGraphicsObject):
    mouse_down = pyqtSignal()
    mouse_release = pyqtSignal()
    left_clicked = pyqtSignal()
    right_clicked = pyqtSignal()

    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.set_state(None)

    def set_state(self, state):
        """ Set the state of the square. Values must correspond to a value from `Minesweeper.state` """
        if state is None:
            self._pixmap = QPixmapCache.find_or_get(':closed.png')
        elif state == '?':
            self._pixmap = QPixmapCache.find_or_get(':question_mark.png')
        else:
            self._pixmap = QPixmapCache.find_or_get(':{}.png'.format(state))
        if self._pixmap.isNull():
            raise ValueError('The given state does not exist.')

    def paint(self, painter, option, widget=None):
        if self._pixmap is not None:
            painter.drawPixmap(self.x*16, self.y*16, self._pixmap)

    def mousePressEvent(self, event):
        self.pressed_buttons = event.buttons()
        self.mouse_down.emit()

    def mouseReleaseEvent(self, event):
        # Only trigger if the mouse is released over the same square.
        self.mouse_release.emit()
        target = self.scene().itemAt(event.scenePos(), QTransform())
        if isinstance(target, Square):
            if self.pressed_buttons == Qt.LeftButton:
                target.left_clicked.emit()
            elif self.pressed_buttons == Qt.RightButton:
                target.right_clicked.emit()

    def boundingRect(self):
        return QRectF(self.x*16, self.y*16, 16, 16)