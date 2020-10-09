import sys

from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import QTimer
from random import randint
from constants import *


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setWindowTitle('ALife')

        #  таймер необходим для того, чтобы правильно обновлять поле битвы. напрямую влияет на скорость симуляции.
        self.timer = QTimer()
        self.timer.timeout.connect(self.repaint)
        self.timer.start(UPDATE_TIME)

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.update_field(qp)
        qp.end()

    def update_field(self, qp):
        for i in range(0, WINDOW_WIDTH, CELL_SIZE):
            for j in range(0, WINDOW_HEIGHT, CELL_SIZE):
                qp.setBrush(QColor(randint(0, 255), randint(0, 255), randint(0, 255), ))
                qp.drawRect(i, j, CELL_SIZE, CELL_SIZE)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Window()
    ex.show()
    sys.exit(app.exec())