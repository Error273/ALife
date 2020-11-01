from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget
from PyQt5 import QtCore
from PyQt5.QtGui import QPainter, QColor, QPen
from constants import *


class OpenSimulationDialog(QWidget):
    def __init__(self, path, parent=None):
        super().__init__(parent, QtCore.Qt.Window)
        self.setGeometry(300, 300, 320, 240)
        self.path = path
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


class SimulationHistoryWindow(QWidget):
    def __init__(self, history, parent=None):
        super().__init__(parent, QtCore.Qt.Window)
        self.setGeometry(300, 300, 750, 650)
        self.setWindowTitle('История симуляции')
        self.setFixedSize(750, 650)
        self.history = history
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(5, 5, 100, 100)
        self.label.setText('Показ')
        self.comboBox = QtWidgets.QComboBox(self)
        self.comboBox.setGeometry(40, 40, 100, 30)
        self.comboBox.addItem('Команды')
        self.comboBox.addItem('Предпочтительность')
        self.slider = QtWidgets.QSlider(self)
        self.slider.setOrientation(1)
        self.slider.setGeometry(155, 610, 585, 40)
        self.slider.setMinimum(0)
        self.slider.setMaximum(len(self.history) - 1)
        self.slider.setValue(0)
        self.slider.valueChanged.connect(self.repaint)
        self.show()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        qp.setBrush(QColor(0, 0, 0))
        qp.drawLine(150, 0, 150, 750)
        self.frame = self.history[self.slider.value()].get_map()
        for i in self.frame:
            for cell in i:
                if cell.name != 'BaseCell':
                    qp.setBrush(QColor(*cell.get_color()))
                    qp.setPen(QPen(QColor(*cell.get_color())))
                    qp.drawRect(cell.get_x() - 150, cell.get_y(), CELL_SIZE, CELL_SIZE)
        qp.end()