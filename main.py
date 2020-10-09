import sys

from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic  # Импортируем uic
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import QTimer
from random import randint
from constants import *
from classes import *


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        uic.loadUi('ui.ui', self)

        #  время, через которое обновляется экран, мс
        self.update_time = 200

        # привязываем кнопочки
        self.start_or_stop_button.clicked.connect(self.change_start_or_stop)
        self.started = False

        self.simulation_speed_box.valueChanged.connect(self.change_update_time)

        #  таймер необходим для того, чтобы правильно обновлять поле битвы. напрямую влияет на скорость симуляции.
        self.timer = QTimer()
        self.timer.timeout.connect(self.repaint)
        self.timer.start(self.update_time)

        # карта со всеми объектами типо бактрий или минералов. Пока заполняем пустыми клетками
        # сразу присвиваем клеткам x и y, отрисовывать потом будем именно по ним.
        # 2D массив только для того, чтобы правильно задать координаты. Обращаться с ним неудобно, поэтому сразу
        # же преобразуем в 1D
        self.map = [[BaseCell(i, j, (255, 255, 255)) for j in range(0, WINDOW_HEIGHT, CELL_SIZE)]
                    for i in range(300, WINDOW_WIDTH, CELL_SIZE)]
        self.map = [item for sublist in self.map for item in sublist]

    def change_start_or_stop(self):
        if not self.started:
            self.start_or_stop_button.setText('Стоп')
            self.started = True
        else:
            self.start_or_stop_button.setText('Старт симуляции')
            self.started = False

    def change_update_time(self):
        self.update_time = self.simulation_speed_box.value()
        self.timer.start(self.update_time)

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
        # разделена линией) - 600 на 600. Получается, что размер поля 59 на 59 (один выходит за границы).
        for cell in self.map:
            # обновляем клетки только если не на паузе
            if self.started:
                cell.update()
            qp.setBrush(QColor(*cell.get_color()))
            #  qpainter по умлочанию рисует границу квадрата, если нужно чтобы появилась "сетка",
            #  закомментировать следующую строку
            qp.setPen(QPen(QColor(*cell.get_color())))

            qp.drawRect(cell.get_x(), cell.get_y(), CELL_SIZE, CELL_SIZE)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Window()
    ex.show()
    sys.exit(app.exec())
