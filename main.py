import sys

from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic  # Импортируем uic
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import QTimer
from random import randint
from constants import *


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        uic.loadUi('ui.ui', self)

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

        # рисуем линию - ограничитель
        qp.setBrush(QColor(0, 0, 0))
        qp.drawLine(300, 0, 300, 600)

        # размер одной клетки - 10 пикселей. Размер поля, на котором мы его будем рисовать (та часть, которая
        # разделена линией) - 600 на 600. Получается, что размер поля 59 на 59 (ин выходит за границы).
        for i in range(300, WINDOW_WIDTH, CELL_SIZE):
            for j in range(0, WINDOW_HEIGHT, CELL_SIZE):
                qp.setBrush(QColor(randint(0, 255), randint(0, 255), randint(0, 255), ))
                qp.drawRect(i, j, CELL_SIZE, CELL_SIZE)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Window()
    ex.show()
    sys.exit(app.exec())