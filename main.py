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

        self.minerals_amount_box.valueChanged.connect(self.change_mineral_frequency)
        self.minerals_frequency = 10

        self.sun_amount_box.valueChanged.connect(self.change_sun_amount)
        self.sun_amount = 40

        self.mutation_chance_box.valueChanged.connect(self.change_mutate_chance)
        self.mutation_chance = 5
        #  таймер необходим для того, чтобы правильно обновлять поле битвы. напрямую влияет на скорость симуляции.
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(self.update_time)

        # карта со всеми объектами типо бактрий или минералов. Пока заполняем пустыми клетками
        # сразу присвиваем клеткам x и y, отрисовывать потом будем именно по ним.
        self.map = Map()
        for i in range(10):
            i, j = randint(0, 59), randint(0, 59)
            while self.map.get_cell(i, j).name != 'BaseCell':
                i, j = randint(0, 59), randint(0, 59)
            self.map.set_cell(i, j, Bacteria(300 + j * CELL_SIZE, i * 10, (randint(0, 255), randint(0, 255), randint(0, 255))))


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

    def change_mineral_frequency(self):
        self.minerals_frequency = self.minerals_amount_box.value()

    def change_sun_amount(self):
        self.sun_amount = self.sun_amount_box.value()

    def change_mutate_chance(self):
        self.mutation_chance = self.mutation_chance_box.value()


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
            """sun_map это одномерный массив с размером 60 элементов.
            Каждый элемент обозначает кол-во энергии, которое можно получить за фотосинтез на уровне i, где i - это
            номер элемента в списке sun_map. Это очень удобно тем, что можно задавать свои формулы распространения света.
            Я использовал геометрическую прогрессию, где 0 < q < 1 """
            sun_map = []
            last_n = self.sun_amount
            for i in range(60):
                sun_map.append(last_n)
                last_n = int(last_n * 0.9)
            self.map.update(self.minerals_frequency, sun_map, self.mutation_chance)
        # отрисовываем карту
        map = self.map.get_map()
        for i in map:
            for cell in i:
                if cell.name != 'BaseCell':
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
