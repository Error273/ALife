from constants import *
from random import randint


def pretty_print(map):
    for i in map:
        for j in i:
            if j.__class__.__name__ == 'BaseCell':
                print('-', end='')
            else:
                print('B', end='')
        print()


class BaseCell:
    """Базовый класс клетки."""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.name = 'BaseCell'  # "имя" класса. удобно, когда нужно узнать, кто находится на какой-то клетке
        self.updated = False

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_color(self):
        return self.color

    def set_x(self, x):
        self.x = x

    def set_y(self, y):
        self.y = y

    def set_color(self, color):
        self.color = color

    def update(self, map, i, j):
        return i, j

    def set_updated(self, flag: bool):
        self.updated = flag

    def get_updated(self):
        return self.updated


class Bacteria(BaseCell):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)

        self.name = 'Bacteria'

        self.energy = 50
        #  куда сейчас смотрит клетка. 0 - вверх, 1 - вправо, 2 - вниз, 3 - влево
        self.orientation = 0

        self.move = 'up'


    def update(self, map1, i, j):
        """Карта нужна для того, чтобы дать клеткам возможность смотреть вокруг.
        i и j это координаты себя на этой самой карте. Вместо того, искать себя на этой карте двумя циклами,
        мы один раз идем циклом в методе update у самой карты и выдаем всем клеткам их позиции.
        Если клетка решила подвинуться, то двигаем ее в том же методе update у карты
        Решение может быть немного сложное, но ничего лучшего я не придумал."""

        # --- НЕЙРОНКА
        move = self.move
        # --- НЕЙРОНКА

        if not self.updated:
            self.updated = True
            new_i, new_j = i, j

            if move == 'right':
                if j < len(map1[0]) - 1:
                    new_j += 1
                else:
                    new_j = 0

            elif move == 'left':
                if j > 0:
                    new_j -= 1
                else:
                    new_j = 59

            elif move == 'down':
                if i < 59:
                    new_i += 1

            elif move == 'up':
                if i > 0:
                    new_i -= 1

            #  если в предполагаемой координате никого нет, то можем двигаться
            if map1[new_i][new_j].name == 'BaseCell':
                self.x = 300 + new_j * CELL_SIZE
                self.y = new_i * CELL_SIZE # координата рассчитывается на основе преполагаемого индекса
                return new_i, new_j
        return i, j


class Mineral(BaseCell):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)

        self.name = 'Mineral'

    def update(self, map1, i, j):
        """Движение минерала заключается в том, что он всегда оседает на пол"""
        if not self.updated:
            self.updated = True
            new_i, new_j = i, j
            if i < 59:
                new_i += 1
            #  если в предполагаемой координате никого нет, то можем двигаться
            if map1[new_i][new_j].name == 'BaseCell':

                self.x = 300 + new_j * CELL_SIZE
                self.y = new_i * CELL_SIZE
                return new_i, new_j
        return i, j


class Map:
    def __init__(self):
        # создаем пустое поле с обычными фоновыми клетками
        self.map_main = [[BaseCell(i, j, WHITE) for j in range(0, WINDOW_HEIGHT, CELL_SIZE)]
                    for i in range(300, WINDOW_WIDTH, CELL_SIZE)]

    def update(self, mineral_frequency):
        """Для того, чтобы бактерии двигались более плавно, необходимо было ввести им параметр updated.
        Без него получается так,что бактерии обновляются по несколько раз.
        Потом, после того, как мы обновили все клетки, нужно им заного дать возможность обновиться."""
        new_map = self.map_main[:]
        for i in range(len(self.map_main)):
            for j in range(len(self.map_main[0])):
                cell = self.map_main[i][j]
                new_i, new_j = cell.update(self.map_main[:], i, j)
                # new_map[i].insert(new_j, new_map[i].pop(j))
                new_map[i][j] = BaseCell(cell.x, cell.y, WHITE)
                new_map[new_i][new_j] = cell
        self.map_main = new_map

        self.generate_mineral(mineral_frequency)

        for line in self.map_main:
            for cell in line:
                cell.set_updated(False)

    def generate_mineral(self, frequency):
        """Гинерируем минерал"""
        if randint(0, 100) < frequency:
            i, j = randint(30, 59), randint(0, 59)  # случайная позиция на карте
            while self.map_main[i][j].name != 'BaseCell':
                """ генерируем, пока не можем быть уверены, что
                 на этой клетке никого нет"""
                i, j = randint(30, 59), randint(0, 59)
            x, y = 300 + j * CELL_SIZE, i * CELL_SIZE  # рассчитываем координаты
            self.set_cell(i, j, Mineral(x, y, GREY))



    def set_cell(self, i, j, cell):
        #  установить на какую-то позицию на карте клетку
        self.map_main[i][j] = cell

    def get_cell(self, i, j):
        return self.map_main[i][j]

    def get_map(self):
        return self.map_main

    def set_map(self, map):
        self.map_main = map