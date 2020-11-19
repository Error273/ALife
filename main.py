import pickle
import sys

from PyQt5 import uic  # Импортируем uic
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QIcon
from datetime import datetime

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

        #  время, через которое обновляется экран, мс
        self.simulation_speed_box.valueChanged.connect(self.change_update_time)
        self.update_time = 200

        # привязываем кнопочки
        self.start_or_stop_button.clicked.connect(self.change_start_or_stop)
        self.start_or_stop_button.setIcon(QIcon('./icons/start_icon.png'))
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
        self.save_sim_btn.setIcon(QIcon('./icons/save_icon.png'))
        self.load_sim_btn.clicked.connect(self.load_sim)
        self.load_sim_btn.setIcon(QIcon('./icons/load_icon.png'))

        self.start_simulation_btn.clicked.connect(self.start_simulation)
        self.start_simulation_btn.setIcon(QIcon('./icons/restart_icon.png'))

        self.save_statistics_btn.clicked.connect(self.open_save_stats_dialogue)
        self.save_statistics_btn.setIcon(QIcon('./icons/save_stats_icon.jpg'))

        self.view_statistics_btn.clicked.connect(self.view_statistics)
        self.view_statistics_btn.setIcon(QIcon('./icons/view_db_icon.png'))

        self.save_history = True
        self.save_history_checkbox.stateChanged.connect(self.change_save_history)
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
            self.map.set_cell(i, j, Bacteria(300 + j * CELL_SIZE, i * CELL_SIZE,
                                             (randint(0, 255), randint(0, 255), randint(0, 255))))
        self.history = [self.map.clone()]
        self.age_label.setText(f'Прошло ходов: {self.map.get_age()}')

    def change_start_or_stop(self):
        if not self.started:
            self.start_or_stop_button.setToolTip('Стоп')
            self.start_or_stop_button.setIcon(QIcon('./icons/stop_icon.png'))
            self.started = True
        else:
            self.start_or_stop_button.setToolTip('Старт симуляции')
            self.start_or_stop_button.setIcon(QIcon('./icons/start_icon.png'))
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

    def change_save_history(self):
        self.save_history = not self.save_history
        if not self.save_history:
            self.save_sim_btn.setDisabled(True)
            self.save_statistics_btn.setDisabled(True)
        else:
            self.save_sim_btn.setDisabled(False)
            self.save_statistics_btn.setDisabled(False)

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
        qp.drawLine(299, 0, 300, 600)
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
            if self.save_history:
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
        if path.endswith('.sim'):  # защита но то, что пользователь не откроет что-нибудь другое
            OpenSimulationDialog(path, self)

    def load_last_step(self, path):
        with open(path, 'rb') as f:
            self.history = pickle.load(f)
            self.map = self.history[-1]
            self.minerals_frequency, self.sun_amount, self.mutation_chance = self.map.get_settings()
            self.minerals_amount_box.setValue(self.minerals_frequency)
            self.sun_amount_box.setValue(self.sun_amount)
            self.mutation_chance_box.setValue(self.mutation_chance)
            self.age_label.setText(f'Прошло ходов: {self.map.get_age()}')

    def load_history(self, path):
        with open(path, 'rb') as f:
            SimulationHistoryWindow(pickle.load(f), self)

    def open_save_stats_dialogue(self):
        """ когда мы нажимаем кнопку сохранения, Открывается диалог с выбором названия.
            после этого мы вызываем метод save_stats и передаем название сохранения
        """
        ChooseSimulationName(self)

    def save_stats(self, name):
        """ для сохранений статистики имеем бд statistics.db. в ней 2 таблицы.
            saves это список с описаниеми всех сохранений, такие как имя, дата, время и номер симуляции - случайное
             число data_id. вторая - это записи всех сохраненных симуляций. по data_id можно найти нужную симуляцию
        """
        db = sqlite3.connect('statistics.db')
        cur = db.cursor()
        data_id = randint(0, 99999)
        # отрезаем от datetime 19 символов, так это миллисекунды
        cur.execute("INSERT INTO saves(name, datetime, data_id) VALUES (?, ?, ?)", [name,
                                                                                    datetime.isoformat(datetime.now(),
                                                                                                       sep=' ')[0:19],
                                                                                    data_id])
        for frame in self.history:
            settings = frame.get_settings()
            statistics = frame.get_statistics()
            cur.execute(f"""INSERT INTO data(     data_id,
                                                  age,
                                                  minerals_setting,
                                                  sun_setting,
                                                  mutation_rate,
                                                  bacteria_number,
                                                  minerals_amount,
                                                  born_amount,
                                                  died_amount,
                                                  sun_eaters_amount,
                                                  flesh_eaters_amount,
                                                  minerals_eaters_amount,
                                                  eaten_amount)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        [data_id, frame.get_age()] + settings + statistics)
        db.commit()

    def view_statistics(self):
        StatiscticsViewWindow(self)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Window()
    ex.show()
    sys.exit(app.exec())
