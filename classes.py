from constants import *
from random import randint, uniform
import numpy
import time


class NeuralNetwork:
    def __init__(self, inputnodes, hiddennodes1, hiddennodes2, outputnodes):
        self.inodes = inputnodes
        self.hnodes1 = hiddennodes1
        self.hnodes2 = hiddennodes2
        self.onodes = outputnodes
        self.wih1 = numpy.random.rand(self.hnodes1, self.inodes)
        self.wh1h2 = numpy.random.rand(self.hnodes2, self.hnodes1)
        self.wh2o = numpy.random.rand(self.onodes, self.hnodes2)

    def activate(self, inputs_list):
        inputs = numpy.array(inputs_list, ndmin=2).T
        hidden_inputs1 = numpy.dot(self.wih1, inputs)
        hidden_outputs1 = numpy.maximum(0, hidden_inputs1)
        hidden_inputs2 = numpy.dot(self.wh1h2, hidden_outputs1)
        hidden_outputs2 = numpy.maximum(0, hidden_inputs2)
        final_inputs = numpy.dot(self.wh2o, hidden_outputs2)
        final_outputs = numpy.maximum(0, final_inputs)
        return final_outputs

    def get_weights(self):
        return self.wih1, self.wh1h2 , self.wh2o

    def set_weights(self, wih1, wh1h2, wh2o):
        self.wih1 = wih1
        self.wh1h2 = wh1h2
        self.wh2o = wh2o


class BaseCell:
    """Базовый класс клетки."""

    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.team_color = color
        self.eating_color = [255, 255, 255]
        self.current_color_mode = 0  # 0 - команды, 1 - предпочтительность
        self.name = 'BaseCell'  # "имя" класса. удобно, когда нужно узнать, кто находится на какой-то клетке
        self.updated = False
        self.energy = 1
        self.age = 0

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_color(self):
        if self.current_color_mode == 1:
            return self.eating_color
        else:
            return self.team_color

    def set_x(self, x):
        self.x = x

    def set_y(self, y):
        self.y = y

    def update(self, map, i, j, sun_map):
        return i, j, False

    def set_updated(self, flag: bool):
        self.updated = flag

    def get_updated(self):
        return self.updated

    def get_energy(self):
        return self.energy

    def set_energy(self, energy):
        self.energy = energy

    def get_age(self):
        return self.age

    def switch_color(self):
        if self.current_color_mode == 0:
            self.current_color_mode = 1
        else:
            self.current_color_mode = 0

    def get_team_color(self):
        return self.team_color

    def get_current_color_mode(self):
        return self.current_color_mode

    def set_current_color_mode(self, mode):
        self.current_color_mode = mode


class Bacteria(BaseCell):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)

        self.name = 'Bacteria'
        #  важный параметр. при рождении бактерия появляется с 50 энергии, а их предок теряет эти 50 энергии.
        self.energy = 100
        #  ну тут понятно.
        self.net = NeuralNetwork(21, 19, 19, 6)

        #  куда сейчас смотрит клетка. 0 - вверх, 1 - вправо, 2 - вниз, 3 - влево
        self.orientation = 1

    def update(self, map1, i, j, sun_map):
        """Карта нужна для того, чтобы дать клеткам возможность смотреть вокруг.
        i и j это координаты себя на этой самой карте. Вместо того, искать себя на этой карте двумя циклами,
        мы один раз идем циклом в методе update у самой карты и выдаем всем клеткам их позиции.
        Если клетка решила подвинуться, то двигаем ее в том же методе update у карты
        Решение может быть немного сложное, но ничего лучшего я не придумал.
        Возвращаем новую позицию на карте и bool - съедаем мы клетку на данной позиции.
        Если False, то мы передвигаемся на эту позицию. Если True - съедаем клетку на этой позиции."""

        if not self.updated:
            #self.age += 1
            # --- НЕЙРОНКА
            # подготавливаем данные, приводим к общему виду.
            sun = sun_map[i]
            energy = self.energy / 100
            temp_i, temp_j = i / 60, j / 60  # позиция на карте
            orientation = self.orientation / 3  # куда сейчас смотрим
            # что находится вокруг.
            whats_around = [[0, 0, 0, 0],  # вверх
                            [0, 0, 0, 0],  # низ
                            [0, 0, 0, 0],  # право
                            [0, 0, 0, 0]]  # лево
            # может быть ничего, край карты, союзная клетка, чужая клетка. минералы считаются чужими клетками.
            # ничего - 0, край - 1, союзник - 2, противник - 3
            # копипаст, но ниче другого не сделаешь.
            if i - 1 < 0:
                whats_around[0][1] = 1
            else:
                up = map1[i - 1][j]
                if up.name == 'BaseCell':
                    whats_around[0][0] = 1
                elif up.name == 'Mineral':
                    whats_around[0][3] = 1
                elif up.name == 'Bacteria':
                    test_data = [uniform(0, 1) for _ in range(21)]
                    res1 = self.net.activate(test_data)
                    res2 = up.net.activate(test_data)
                    if all(res1 == res2):
                        whats_around[0][3] = 1
                    else:
                        whats_around[0][2] = 1
            #
            if i + 1 > 59:
                whats_around[1][1] = 1
            else:
                down = map1[i + 1][j]
                if down.name == 'BaseCell':
                    whats_around[1][0] = 1
                elif down.name == 'Mineral':
                    whats_around[1][3] = 1
                elif down.name == 'Bacteria':
                    test_data = [uniform(0, 1) for _ in range(21)]
                    res1 = self.net.activate(test_data)
                    res2 = down.net.activate(test_data)
                    if all(res1 == res2):
                        whats_around[1][3] = 1
                    else:
                        whats_around[1][2] = 1
            #
            if j + 1 > 59:
                whats_around[2][1] = 1
            else:
                right = map1[i][j + 1]
                if right.name == 'BaseCell':
                    whats_around[2][0] = 1
                elif right.name == 'Mineral':
                    whats_around[2][3] = 1
                elif right.name == 'Bacteria':
                    test_data = [uniform(0, 1) for _ in range(21)]
                    res1 = self.net.activate(test_data)
                    res2 = right.net.activate(test_data)
                    if all(res1 == res2):
                        whats_around[2][3] = 1
                    else:
                        whats_around[2][2] = 1
            #
            if j - 1 < 0:
                whats_around[3][1] = 1
            else:
                left = map1[i][j - 1]
                if left.name == 'BaseCell':
                    whats_around[3][0] = 1
                elif left.name == 'Mineral':
                    whats_around[3][3] = 1
                elif left.name == 'Bacteria':
                    #  выясняем, союзная ли перед нами клетка.
                    test_data = [uniform(0, 1) for _ in range(21)]
                    res1 = self.net.activate(test_data)
                    res2 = left.net.activate(test_data)
                    if all(res1 == res2):
                        whats_around[3][3] = 1
                    else:
                        whats_around[3][2] = 1

            # --- НЕЙРОНКА
            output = list(self.net.activate([j for sub in whats_around for j in sub] + [sun, energy, temp_i,
                                                                                        temp_j, orientation]))
            res = output.index(max(output))
            self.energy -= 1
            #res = 5
            self.updated = True

            # если команда на фотосинтез
            if res == 4:
                if self.eating_color[0] - 10 > 0 and self.eating_color[2] - 10 > 0:
                    self.eating_color[0] -= 10
                    self.eating_color[2] -= 10
                self.energy += sun
                if self.energy > MAX_ENERGY:  # ограничиваем максимальную энергию
                    self.energy = MAX_ENERGY


            elif res == 5:  # если команда на съедение
                if self.eating_color[1] - 10 > 0 and self.eating_color[2] - 10 > 0:
                   self.eating_color[1] -= 10
                   self.eating_color[2] -= 10
                #self.eating_color = [255, 0, 0]
                new_i, new_j = self.get_i_j_by_orientation(map1, i, j)
                if map1[new_i][new_j].name == 'Bacteria':
                    self.energy += map1[new_i][new_j].get_energy()
                elif map1[new_i][new_j].name == 'Mineral':
                    self.energy += MINERAL_ENERGY
                if self.energy > MAX_ENERGY:
                    self.energy = MAX_ENERGY
                return (new_i, new_j, True)


            else:  # если передвинемся
                self.orientation = res
                new_i, new_j = self.get_i_j_by_orientation(map1, i, j)
                #  если в предполагаемой координате никого нет, то можем двигаться
                if map1[new_i][new_j].name == 'BaseCell':
                    self.x = 300 + new_j * CELL_SIZE
                    self.y = new_i * CELL_SIZE  # координата рассчитывается на основе преполагаемого индекса
                    return (new_i, new_j, False)
        return (i, j, False)

    def get_genome(self):
        return self.net.get_weights()

    def set_genome(self, wih1, wh1h2, wh2o):
        self.net.set_weights(wih1, wh1h2, wh2o)

    def mutate(self, mutate_chance):
        new_wih1, new_wh1h2, new_wh2o = self.net.get_weights()
        new_wih1, new_wh1h2, new_wh2o = new_wih1.flatten(), new_wh1h2.flatten(), new_wh2o.flatten()
        for i in range(len(new_wih1)):
            if randint(0, 100) < mutate_chance:
                new_wih1[i] = uniform(0, 1)
        for i in range(len(new_wh1h2)):
            if randint(0, 100) < mutate_chance:
                new_wh1h2[i] = uniform(0, 1)
        for i in range(len(new_wh2o)):
            if randint(0, 100) < mutate_chance:
                new_wh2o[i] = uniform(0, 1)
        self.net.set_weights(numpy.reshape(new_wih1, (19, 21)), numpy.reshape(new_wh1h2, (19, 19)),
                             numpy.reshape(new_wh2o, (6, 19)))

    def get_i_j_by_orientation(self, map1, i, j):
        eaten_i, eaten_j = i, j
        if self.orientation == 1:
            if j < len(map1[0]) - 1:
                eaten_j += 1
            else:
                eaten_j = 0

        elif self.orientation == 3:
            if j > 0:
                eaten_j -= 1
            else:
                eaten_j = 59

        elif self.orientation == 2:
            if i < 59:
                eaten_i += 1

        elif self.orientation == 0:
            if i > 0:
                eaten_i -= 1
        return eaten_i, eaten_j


class Mineral(BaseCell):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        self.eating_color = [*color]
        self.name = 'Mineral'

    def update(self, map1, i, j, sun_map):
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
                return new_i, new_j, False
        return i, j, False


class Map:
    def __init__(self):
        # создаем пустое поле с обычными фоновыми клетками
        self.map_main = [[BaseCell(i, j, WHITE) for j in range(0, WINDOW_HEIGHT, CELL_SIZE)]
                         for i in range(300, WINDOW_WIDTH, CELL_SIZE)]
        self.age = 0

    def update(self, mineral_frequency, sun_map, mutate_chance):
        """Для того, чтобы бактерии двигались более плавно, необходимо было ввести им параметр updated.
        Без него получается так,что бактерии обновляются по несколько раз.
        Потом, после того, как мы обновили все клетки, нужно им заного дать возможность обновиться."""
        self.age += 1
        # обновляем карту
        s = time.time()
        new_map = self.map_main[:]
        for i in range(len(self.map_main)):
            for j in range(len(self.map_main[0])):
                cell = self.map_main[i][j]
                new_i, new_j, kill = cell.update(self.map_main[:], i, j, sun_map)
                #print(i, j, new_i, new_j, kill)
                if not kill:
                    new_map[i][j] = BaseCell(cell.x, cell.y, WHITE)
                    new_map[new_i][new_j] = cell
                else:
                    new_map[new_i][new_j] = BaseCell(cell.x, cell.y, WHITE)

        self.map_main = new_map
        print(time.time() - s)

        # генерируем минерал
        self.generate_mineral(mineral_frequency)

        # убиваем тех, у кого 0 энергии
        for i in range(len(self.map_main)):
            for j in range(len(self.map_main[0])):
                cell = self.map_main[i][j]
                if cell.get_energy() <= 0 or cell.get_age() > CELL_AGE:
                    self.set_cell(i, j, Mineral(cell.x, cell.y, GREY))

        # отпочковываем клетки
        for i in range(len(self.map_main)):
            for j in range(len(self.map_main[0])):
                cell = self.map_main[i][j]
                #  если энергии достаточно, отпочковываемся.
                if cell.get_energy() > MAX_ENERGY - MAX_ENERGY / 4:
                    cell.set_energy(cell.get_energy() - 50)
                    if i != 0 and self.get_cell(i - 1, j).name == 'BaseCell':
                        new_i, new_j = i - 1, j
                    elif i != 59 and self.get_cell(i + 1, j).name == 'BaseCell':
                        new_i, new_j = i + 1, j
                    elif j != 0 and self.get_cell(i, j - 1).name == 'BaseCell':
                        new_i, new_j = i, j - 1
                    elif j != 59 and self.get_cell(i, j + 1).name == 'BaseCell':
                        new_i, new_j = i, j + 1
                    else:  # если места не нашлось, то просто пропускаем клетку
                        continue
                    self.set_cell(new_i, new_j, Bacteria(300 + new_j * CELL_SIZE, new_i * 10,
                                                         cell.get_team_color()))
                    new_cell = self.map_main[new_i][new_j]
                    new_cell.set_genome(*cell.get_genome())
                    new_cell.set_current_color_mode(cell.get_current_color_mode())
                    new_cell.mutate(mutate_chance)
        for line in self.map_main:
            for cell in line:
                cell.set_updated(False)

    def generate_mineral(self, frequency):
        """Гинерируем минерал"""
        attempts = 5  # количество попыток генерации минералов.
        # когда клеток становится слишком много и места просто нет, мы влетаем в вечный цикл.
        # мы просто ограничиваем количество попыток.
        if randint(0, 100) < frequency:
            i, j = randint(40, 59), randint(0, 59)  # случайная позиция на карте
            while self.map_main[i][j].name != 'BaseCell' and attempts > 0:
                """ генерируем, пока не можем быть уверены, что
                 на этой клетке никого нет"""
                i, j = randint(40, 59), randint(0, 59)
                attempts -= 1
            if attempts > 0:
                x, y = 300 + j * CELL_SIZE, i * CELL_SIZE  # рассчитываем координаты
                self.set_cell(i, j, Mineral(x, y, GREY))

    def switch_cells_color(self):
        for line in self.map_main:
            for cell in line:
                cell.switch_color()

    def set_cell(self, i, j, cell):
        #  установить на какую-то позицию на карте клетку
        self.map_main[i][j] = cell

    def get_cell(self, i, j):
        return self.map_main[i][j]

    def get_map(self):
        return self.map_main

    def set_map(self, map):
        self.map_main = map

    def get_age(self):
        return self.age
