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

        #  устанавливаем фиксированный размер окна.
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)

        #  время, через которое обновляется экран, мс
        self.update_time = 200

        # привязываем кнопочки
        self.start_or_stop_button.clicked.connect(self.change_start_or_stop)
        self.started = False

        self.simulation_speed_box.valueChanged.connect(self.change_update_time)

        #  таймер необходим для того, чтобы правильно обновлять поле битвы. напрямую влияет на скорость симуляции.
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(self.update_time)

        # карта со всеми объектами типо бактрий или минералов. Пока заполняем пустыми клетками
        # сразу присвиваем клеткам x и y, отрисовывать потом будем именно по ним.
        self.map = Map()

        self.map.set_cell(10, 5, Bacteria(350, 100, (255, 255, 0)))
        self.map.map_main[10][5].move = 'right'

        self.map.set_cell(30, 5, Bacteria(350, 300, (0, 255, 255)))
        self.map.map_main[30][5].move = 'left'

        self.map.set_cell(20, 10, Bacteria(350, 400, (0, 255, 0)))
        self.map.map_main[20][10].move = 'up'
        self.map.set_cell(20, 20, Bacteria(350, 500, (0, 0, 255)))
        self.map.map_main[20][20].move = 'down'




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
        if self.started:
            self.map.update()
        # отрисовываем карту
        map = self.map.get_map()
        for i in map:
            for cell in i:
                if cell.__class__.__name__ != 'BaseCell':
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
