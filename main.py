import pickle
import sys

from PyQt5 import uic  # Импортируем uic
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QFileDialog, QWidget
from PyQt5 import QtCore, QtWidgets
import sqlite3

from windows import *
from classes import *


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        uic.loadUi('main_ui.ui', self)

        #  устанавливаем фиксированный размер окна.
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)

        # создаем подсказки
        self.speed_label.setToolTip('Через какое время в милисекундах будет обновляться симуляция')
        self.simulation_speed_box.setToolTip('Через какое время в милисекундах будет обновляться симуляция')

        self.minerals_label.setToolTip('Какая вероятность создания минерала каждое обновление экрана')
        self.minerals_amount_box.setToolTip('Какая вероятность создания минерала каждое обновление экрана')

        self.speed_label.setToolTip('Через какое время в милисекундах будет обновляться симуляция')
        self.simulation_speed_box.setToolTip('Через какое время в милисекундах будет обновляться симуляция')

        self.sun_label.setToolTip('Чем больше этот показатель - тем сильнее солнце светит и ниже проходит')
        self.sun_amount_box.setToolTip('Чем больше этот показатель - тем сильнее солнце светит и ниже проходит')

        self.mutation_label.setToolTip('С какой вероятнстью изменится вес нейросети при рождении')
        self.mutation_chance_box.setToolTip('С какой вероятнстью изменится вес нейросети при рождении')

        self.show_label.setToolTip('''Команды - какому роду принадлежит каждая бактерия. Предпочтительность - 
        солнцееды зеленеют, мясоеды краснеют, а минералоеды синеют''')
        self.view_mode_box.setToolTip('''Команды - какому роду принадлежит каждая бактерия. Предпочтительность - 
        солнцееды зеленеют, мясоеды краснеют, а минералоеды синеют''')

        #  время, через которое обновляется экран, мс
        self.simulation_speed_box.valueChanged.connect(self.change_update_time)
        self.update_time = 200

        # привязываем кнопочки
        self.start_or_stop_button.clicked.connect(self.change_start_or_stop)
        self.started = False

        self.minerals_amount_box.valueChanged.connect(self.change_mineral_frequency)
        self.minerals_frequency = 10

        self.sun_amount_box.valueChanged.connect(self.change_sun_amount)
        self.sun_amount = 40

        self.mutation_chance_box.valueChanged.connect(self.change_mutate_chance)
        self.mutation_chance = 5

        self.view_mode_box.addItem('Команды')
        self.view_mode_box.addItem('Предпочтительность')
        self.view_mode_box.currentTextChanged.connect(self.switch_view_mode)

        self.save_sim_btn.clicked.connect(self.save_sim)
        self.load_sim_btn.clicked.connect(self.load_sim)

        self.start_simulation_btn.clicked.connect(self.start_simulation)

        self.save_statistics_btn.clicked.connect(self.save_stats)
        #  таймер необходим для того, чтобы правильно обновлять поле битвы. напрямую влияет на скорость симуляции.
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.repaint)

        self.start_simulation()

        self.timer.start(self.update_time)

    def start_simulation(self):
        # карта со всеми объектами типо бактрий или минералов.
        # сразу присвиваем клеткам x и y, отрисовывать потом будем именно по ним.
        self.map = Map()
        self.update_map_settings()
        for i in range(START_GENERATION):
            i, j = randint(0, 59), randint(0, 59)
            while self.map.get_cell(i, j).name != 'BaseCell':
                i, j = randint(0, 59), randint(0, 59)
            self.map.set_cell(i, j, Bacteria(300 + j * CELL_SIZE, i * 10,
                                             (randint(0, 255), randint(0, 255), randint(0, 255))))
        self.history = [self.map.clone()]

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
        self.update_map_settings()

    def change_sun_amount(self):
        self.sun_amount = self.sun_amount_box.value()
        self.update_map_settings()

    def change_mutate_chance(self):
        self.mutation_chance = self.mutation_chance_box.value()
        self.update_map_settings()

    def switch_view_mode(self):
        self.map.switch_cells_color()

    def update_map_settings(self):
        self.map.set_settings([self.minerals_frequency, self.sun_amount, self.mutation_chance])

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.update_field(qp, self.sender())
        qp.end()

    def update_field(self, qp, sender):
        """sender принимаем для того, чтобы смотреть,от кого отправлен сигнал.
        paintEvent почему то вызывается сам по себе и обновляет карту, а мне нужно чтобы
         карта обновлялась только по таймеру.
        """
        # рисуем линию - ограничитель
        qp.setBrush(QColor(0, 0, 0))
        qp.drawLine(300, 0, 300, 600)
        if self.started and sender.__class__.__name__ == 'QTimer':
            """sun_map это одномерный массив с размером 60 элементов.
            Каждый элемент обозначает кол-во энергии, которое можно получить за фотосинтез на уровне i, где i - это
            номер элемента в списке sun_map. Это очень удобно тем, что можно задавать свои формулы распространения света.
            Я использовал геометрическую прогрессию, где 0 < q < 1 """
            sun_map = []
            last_n = self.sun_amount
            for i in range(60):
                sun_map.append(last_n)
                last_n = int(last_n * 0.9)
            self.map.update(sun_map)
            self.history.append(self.map.clone())
            self.age_label.setText(f'Прошло ходов: {self.map.get_age()}')
        # отрисовываем карту
        map = self.map.get_map()
        for i in map:
            for cell in i:
                # пустые клетки не отрисовываем
                if cell.name != 'BaseCell':
                    qp.setBrush(QColor(*cell.get_color()))
                    qp.setPen(QPen(QColor(*cell.get_color())))

                    qp.drawRect(cell.get_x(), cell.get_y(), CELL_SIZE, CELL_SIZE)

    def save_sim(self):
        path = QFileDialog.getSaveFileName(self, 'Сохранить симуляцию', '', 'Симуляция (*.sim)')[0]
        if path:
            with open(path, 'wb') as f:
                pickle.dump(self.history, f)

    def load_sim(self):
        path = QFileDialog.getOpenFileName(self, 'Открыть симуляцию', '', 'Симуляция (*.sim)')[0]
        if path:
            OpenSimulationDialog(path, self)

    def load_last_step(self, path):
        with open(path, 'rb') as f:
            self.history = pickle.load(f)
            self.map = self.history[-1]

    def load_history(self, path):
        with open(path, 'rb') as f:
            SimulationHistoryWindow(pickle.load(f), self)

    def save_stats(self):
        path = QFileDialog.getSaveFileName(self, 'Сохранить статистику', '', 'База данных sqlite (*.sqlite3)')[0]
        if path:
            db = sqlite3.connect(path)
            cur = db.cursor()
            cur.execute("""CREATE TABLE statistics (
            id INTEGER NOT NULL UNIQUE PRIMARY KEY AUTOINCREMENT,
            age INTEGER NOT NULL UNIQUE,
            minerals_setting INTEGER,
            sun_setting INTEGER,
            mutation_rate INTEGER,
            bacteria_number INTEGER,
            minerals_amount INTEGER,
            born_amount INTEGER,
            died_amount INTEGER,
            sun_eaters_amount INTEGER,
            flesh_eaters_amount INTEGER,
            minerals_eaters_amount INTEGER);""")
            for frame in self.history:
                settings = frame.get_settings()
                statistics = frame.get_statistics()
                cur.execute(f"""INSERT INTO statistics(age,
                                                      minerals_setting,
                                                      sun_setting,
                                                      mutation_rate,
                                                      bacteria_number,
                                                      minerals_amount,
                                                      born_amount,
                                                      died_amount,
                                                      sun_eaters_amount,
                                                      flesh_eaters_amount,
                                                      minerals_eaters_amount)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", [frame.get_age()] + settings + statistics)
            db.commit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Window()
    ex.show()
    sys.exit(app.exec())
