from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog
from PyQt5 import QtCore
from PyQt5.QtGui import QPainter, QColor, QPen
import sqlite3
from constants import *


class OpenSimulationDialog(QDialog):
    # окно выбора, которое появляется при открытии симуляции
    def __init__(self, path, parent=None):
        super().__init__(parent, QtCore.Qt.Window)
        self.setGeometry(600, 300, 320, 240)
        self.setModal(True) # делаем так, чтобы нельзя было трогать другие окна, пока не закроем это.
        self.setFixedSize(320, 240)
        self.path = path # путь до файла
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(10, 30, 301, 101))
        self.look_btn = QtWidgets.QPushButton(self)
        self.look_btn.setGeometry(QtCore.QRect(0, 200, 93, 28))
        self.continue_btn = QtWidgets.QPushButton(self)
        self.continue_btn.setGeometry(QtCore.QRect(230, 200, 93, 28))

        self.setWindowTitle("Открыть симуляцию")
        self.label.setText( "<html><head/><body><p><span style=\" font-size:10pt;\">Вы желаете просмотреть историю"
                            "</span></p><p><span style=\" font-size:10pt;\"> симуляции или продолжить</span></p><p>"
                            "<span style=\" font-size:10pt;\"> с последнего хода?</span></p></body></html>")
        # если нажата одна из кнопок, вызываем соответсвующий метод родителя(MainWindow). А как открывается и
        # отображается файл, решается уже там.
        self.look_btn.setText("Просмотреть")
        self.look_btn.clicked.connect(self.view_history)
        self.continue_btn.setText("Продолжить")
        self.continue_btn.clicked.connect(self.continue_sim)
        self.show()

    def continue_sim(self):
        self.parent().load_last_step(self.path)
        self.close()

    def view_history(self):
        self.parent().load_history(self.path)
        self.close()


class SimulationHistoryWindow(QDialog):
    # окно просмотра истории симуляции.
    def __init__(self, history, parent=None):
        super().__init__(parent, QtCore.Qt.Window)
        self.setGeometry(500, 220, 750, 650)
        self.setWindowTitle('История симуляции')
        self.setFixedSize(900, 650)
        self.setModal(True) # делаем так, чтобы нельзя было трогать другие окна, пока не закроем это.
        self.history = history
        # устанавливаем всем клеткам показ "Команды". Это нужно для того, чтобы когда в процессе симуляции показ изменялся,
        # он не влиял на историю
        for frame in self.history:
            for line in frame.get_map():
                for cell in line:
                    cell.set_current_color_mode(0)

        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(5, 5, 100, 100)
        self.label.setText('Показ')
        self.comboBox = QtWidgets.QComboBox(self)
        self.comboBox.setGeometry(50, 40, 200, 30)
        self.comboBox.addItem('Команды')
        self.comboBox.addItem('Предпочтительность')
        self.comboBox.currentTextChanged.connect(self.switch_color)
        self.show_mode = 0
        self.slider = QtWidgets.QSlider(self)
        self.slider.setOrientation(1) # горизонтальное отображение
        self.slider.setGeometry(305, 610, 585, 40)
        self.slider.setMinimum(0)
        self.slider.setMaximum(len(self.history) - 1)
        self.slider.setValue(0)
        self.slider.valueChanged.connect(self.repaint)
        self.age_label = QtWidgets.QLabel(self)
        self.age_label.setGeometry(10, 580, 150, 100)
        self.age_label.setText('Прошло ходов: 0')
        self.show()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        qp.setBrush(QColor(0, 0, 0))
        qp.drawLine(299, 0, 299, 750)
        frame = self.history[self.slider.value()]
        self.age_label.setText(f'Прошло ходов: {frame.get_age()}')
        for i in frame.get_map():
            for cell in i:
                if cell.name != 'BaseCell':
                    qp.setBrush(QColor(*cell.get_color()))
                    qp.setPen(QPen(QColor(*cell.get_color())))
                    qp.drawRect(cell.get_x(), cell.get_y(), CELL_SIZE, CELL_SIZE)
        qp.end()

    def switch_color(self):
        self.show_mode = not self.show_mode
        for frame in self.history:
            for i in frame.get_map():
                for cell in i:
                    cell.set_current_color_mode(self.show_mode)
        self.update()


class ChooseSimulationName(QDialog):
    def __init__(self, parent):
        super().__init__(parent, QtCore.Qt.Window)
        self.setGeometry(600, 300, 300, 100)
        self.setFixedSize(300, 100)
        self.setModal(True)
        self.setWindowTitle('Введите название')
        self.label = QtWidgets.QLabel(self)
        self.label.move(10, 20)
        self.label.setText('Введите название')
        self.name_edit = QtWidgets.QLineEdit(self)
        self.name_edit.move(140, 20)
        self.ok_btn = QtWidgets.QPushButton(self)
        self.ok_btn.setText('OK')
        self.ok_btn.move(140, 60)
        self.ok_btn.clicked.connect(self.change_name)
        self.name = ''
        self.out_label = QtWidgets.QLabel(self)
        self.out_label.setGeometry(10, 40, 120, 50)
        self.show()

    def change_name(self):
        self.out_label.setText('')
        self.name = self.name_edit.text().strip()
        if not self.name or len(self.name) > 100:
            self.out_label.setText('Некорректное имя')
        else:
            self.parent().save_stats(self.name)
            self.close()


class StatiscticsViewWindow(QDialog):
    # окно просмотра статистики с 2 таблицами
    def __init__(self, parent):
        super().__init__(parent, QtCore.Qt.Window)
        self.setWindowTitle('Просмотр статистики')
        self.setGeometry(600, 300, 850, 600)
        self.setFixedSize(800, 600)
        self.setModal(True)

        # таблица с названиями сохранений
        self.saves_table = QtWidgets.QTableWidget(self)
        self.saves_table.resize(250, 550)
        self.saves_table.move(20, 30)
        self.saves_table.cellClicked.connect(self.update_statistics_table)

        # Таблица с самими записями
        self.statistics_table = QtWidgets.QTableWidget(self)
        self.statistics_table.resize(510, 550)
        self.statistics_table.move(280, 30)

        self.db = sqlite3.connect('statistics.db')
        self.cur = self.db.cursor()

        self.update_saves_table()
        self.update_statistics_table()
        self.show()

    def update_saves_table(self):
        # получаем все сохранения
        saves = self.cur.execute('SELECT name, datetime FROM saves').fetchall()
        self.saves_table.setColumnCount(2)
        self.saves_table.setRowCount(len(saves))
        self.saves_table.setHorizontalHeaderLabels(['Название', 'Дата и время'])
        for i, elem in enumerate(saves):
            for j, val in enumerate(elem):
                self.saves_table.setItem(i, j, QtWidgets.QTableWidgetItem(str(val)))
                item = self.saves_table.item(i, j)
                # устанавливаем 2 флага - первый не дает редактировать клетку, второй дает ее выделять
                item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        self.saves_table.resizeColumnsToContents()

    def update_statistics_table(self):
        # получаем номера выделенных строк
        row = list(set([i.row() for i in self.saves_table.selectedItems()]))
        # при запуски окна выделенных клеток нет
        if row:
            date = self.saves_table.item(row[0], 1).text()
            # получаем дату и время сохранения и используем ее для поиска всех записей сохранения
            res = self.cur.execute("""SELECT * FROM data WHERE data_id IN (
            SELECT data_id FROM saves WHERE datetime = ?)""", [date]).fetchall()
            self.statistics_table.setColumnCount(len(res[0]))
            self.statistics_table.setRowCount(len(res))
            column_names = self.cur.execute("SELECT name FROM PRAGMA_TABLE_INFO('data')").fetchall()
            column_names = list(map(lambda x: x[0], column_names))
            self.statistics_table.setHorizontalHeaderLabels(column_names)
            for i, elem in enumerate(res):
                for j, val in enumerate(elem):
                    self.statistics_table.setItem(i, j, QtWidgets.QTableWidgetItem(str(val)))
                    item = self.statistics_table.item(i, j)
                    item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
            self.statistics_table.resizeColumnsToContents()
