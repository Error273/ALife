from constants import *
from random import randint, uniform
import numpy as np


class NeuralNetwork:
    def __init__(self, inputnodes, hiddennodes1, hiddennodes2, outputnodes):
        # всего использую 4 слоя. 1 вход, 2 скрытых, 1 выход.
        # кол-во входных нейронов
        self.inodes = inputnodes
        # первый скрытый слой
        self.hnodes1 = hiddennodes1
        # второй скрытый слой
        self.hnodes2 = hiddennodes2
        # выходной
        self.onodes = outputnodes
        # веса вход - первый скрытый слой + веса для нейрона смещения
        # добавляем веса нейрона смещения только на одном слое, так как нейроны смещения соседних слоев не соединяются
        self.wih1 = np.random.rand(self.hnodes1, self.inodes + 1)
        # веса первый скрытый - второй скрытый + веса для нейрона смещения
        self.wh1h2 = np.random.rand(self.hnodes2, self.hnodes1 + 1)
        # веса второй скрытый - выход + веса для нейрона смещения
        self.wh2o = np.random.rand(self.onodes, self.hnodes2 + 1)

    def activate(self, inputs_list):
        # преобразуем вход в правильный вид
        inputs = np.array(inputs_list, ndmin=2).T
        # по сути, все, что мы делаем дальше это перемножаем матрицы весов и результата, полученного на прошлом слое.
        # так, мы умножаем матрицу весов и входные данные, подвергаем функции активации, получаем новые данные,
        # повторяем.
        # функция активации - relu, выражается как np.maximum(0, layer). relu для примера, ее можно легко изменить
        # на любую другую.
        # P.S я понимаю, что relu ни на что не влияет, так как у меня нет отрицательных весов. сделал я так для того,
        # чтобы ее при необходимости можно было
        # легко заменить на любую другую. Да и тем более, мне понравилось как бактерии ведут себя при relu =)
        # и еще, тут нельзя использовать функции, которые создаются в других функциях из-за pickle. Если нужно сделать
        # функцию активации, то только глобальную

        # перед тем, как перемножить, мы добавляем к входному слою 1 - нейрон смещения.
        hidden_inputs1 = np.dot(self.wih1, np.append(inputs, 1))
        hidden_outputs1 = np.maximum(0, hidden_inputs1)
        hidden_inputs2 = np.dot(self.wh1h2, np.append(hidden_outputs1, 1))
        hidden_outputs2 = np.maximum(0, hidden_inputs2)
        final_inputs = np.dot(self.wh2o, np.append(hidden_outputs2, 1))
        final_outputs = np.maximum(0, final_inputs)
        return final_outputs

    def get_weights(self):
        return self.wih1, self.wh1h2, self.wh2o

    def set_weights(self, wih1, wh1h2, wh2o):
        self.wih1 = wih1
        self.wh1h2 = wh1h2
        self.wh2o = wh2o

    def get_nodes(self):
        return self.inodes, self.hnodes1, self.hnodes2, self.onodes


class BaseCell:
    """Базовый класс клетки."""

    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        # цвет, который задается при создании и не может измениться. определяет, какому роду принадлежит клетка.
        self.team_color = color
        # цвет, который определяется тем, что клетка ест.
        self.eating_color = [255, 255, 255]
        self.current_color_mode = 0  # 0 - команды, 1 - предпочтительность
        self.name = 'BaseCell'  # "имя" класса. удобно, когда нужно узнать, кто находится на какой-то клетке
        self.updated = False
        self.energy = 1

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_color(self):
        if self.current_color_mode:
            return self.eating_color
        return self.team_color

    def set_x(self, x):
        self.x = x

    def set_y(self, y):
        self.y = y

    def update(self, newmap, i, j, sun_map):
        return i, j, False

    def set_updated(self, flag: bool):
        self.updated = flag

    def get_updated(self):
        return self.updated

    def get_energy(self):
        return self.energy

    def set_energy(self, energy):
        self.energy = energy

    def switch_color(self):
        self.current_color_mode = not self.current_color_mode

    def get_team_color(self):
        return self.team_color

    def get_eating_color(self):
        return self.eating_color

    def get_current_color_mode(self):
        return self.current_color_mode

    def set_current_color_mode(self, mode):
        self.current_color_mode = mode


class Bacteria(BaseCell):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)

        self.name = 'Bacteria'
        #  важный параметр. при рождении бактерия появляется с 100 энергии, а их предок теряет эти 100 энергии.
        self.energy = 100
        #  ну тут понятно.
        self.net = NeuralNetwork(21, 19, 19, 7)

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
            if i - 1 < 0:  # если сверху край
                whats_around[0][1] = 1
            else:
                up = map1[i - 1][j]
                if up.name == 'BaseCell':
                    whats_around[0][0] = 1
                elif up.name == 'Mineral':
                    whats_around[0][3] = 1
                elif up.name == 'Bacteria':
                    # проверяем, клетка своего ли рода
                    # случайные входные данные для теста
                    test_data = [uniform(0, 1) for _ in range(21)]
                    # получаем результаты от двух нейронок. если они одинаковые, то и клетки к одному роду принадлежат
                    res1 = self.net.activate(test_data)
                    res2 = up.net.activate(test_data)
                    # сравнение numpy массивов сравнивает каждый элемент на одинаковых позициях, поэтому возвращает еще
                    # один массив, где элементы либо True, либо False
                    # если ответы совпали, то клетка своя.
                    if all(res1 == res2):
                        whats_around[0][3] = 1
                    else:
                        whats_around[0][2] = 1

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
                    # сравнение numpy массивов сравнивает каждый элемент на одинаковых позициях, поэтому возвращает еще
                    # один массив, где элементы либо True, либо False
                    # если ответы совпали, то клетка своя.
                    if all(res1 == res2):
                        whats_around[1][3] = 1
                    else:
                        whats_around[1][2] = 1

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
                    # сравнение numpy массивов сравнивает каждый элемент на одинаковых позициях, поэтому возвращает еще
                    # один массив, где элементы либо True, либо False
                    # если ответы совпали, то клетка своя.
                    if all(res1 == res2):
                        whats_around[2][3] = 1
                    else:
                        whats_around[2][2] = 1

            if j - 1 < 0:
                whats_around[3][1] = 1
            else:
                left = map1[i][j - 1]
                if left.name == 'BaseCell':
                    whats_around[3][0] = 1
                elif left.name == 'Mineral':
                    whats_around[3][3] = 1
                elif left.name == 'Bacteria':
                    test_data = [uniform(0, 1) for _ in range(21)]
                    res1 = self.net.activate(test_data)
                    res2 = left.net.activate(test_data)
                    # сравнение numpy массивов сравнивает каждый элемент на одинаковых позициях, поэтому возвращает еще
                    # один массив, где элементы либо True, либо False
                    # если ответы совпали, то клетка своя.
                    if all(res1 == res2):
                        whats_around[3][3] = 1
                    else:
                        whats_around[3][2] = 1

            # --- НЕЙРОНКА
            output = list(self.net.activate([j for sub in whats_around for j in sub] + [sun, energy, temp_i,
                                                                                        temp_j, orientation]))
            # получаем индекс самого большого значения выходного слоя. он и будет решать, что делать клетке.
            res = output.index(max(output))
            self.energy -= 1

            # если команда на фотосинтез
            if res == 4:
                # "зеленеем"
                if self.eating_color[0] - 10 > 0 and self.eating_color[2] - 10 > 0:
                    self.eating_color[0] -= 10
                    self.eating_color[2] -= 10
                self.energy += sun
                if self.energy > MAX_ENERGY:  # ограничиваем максимальную энергию
                    self.energy = MAX_ENERGY


            elif res == 5:  # если команда на съедение
                new_i, new_j = self.get_i_j_by_orientation(map1, i, j)
                if map1[new_i][new_j].name == 'Bacteria':
                    # "краснеем"
                    if self.eating_color[1] - 20 > 0 and self.eating_color[2] - 20 > 0:
                        self.eating_color[1] -= 20
                        self.eating_color[2] -= 20
                    # получаем энергию съеденной клетки.
                    self.energy += map1[new_i][new_j].get_energy()
                elif map1[new_i][new_j].name == 'Mineral':
                    # "синеем"
                    if self.eating_color[0] - 50 > 0 and self.eating_color[1] - 50 > 0:
                        self.eating_color[0] -= 50
                        self.eating_color[1] -= 50
                    # получаем энергию минералов.
                    self.energy += MINERAL_ENERGY
                if self.energy > MAX_ENERGY:
                    self.energy = MAX_ENERGY
                return (new_i, new_j, True)

            elif res == 6:  # если команда на передвижение
                new_i, new_j = self.get_i_j_by_orientation(map1, i, j)
                #  если в предполагаемой координате никого нет, то можем двигаться
                if map1[new_i][new_j].name == 'BaseCell':
                    self.x = 300 + new_j * CELL_SIZE
                    self.y = new_i * CELL_SIZE  # координата рассчитывается на основе преполагаемого индекса
                    return (new_i, new_j, False)

            else:  # если вращаемся
                self.orientation = res
        self.updated = True
        return (i, j, False)

    def get_genome(self):
        return self.net.get_weights()

    def set_genome(self, wih1, wh1h2, wh2o):
        self.net.set_weights(wih1, wh1h2, wh2o)

    def mutate(self, mutate_chance):
        # получаем веса
        new_wih1, new_wh1h2, new_wh2o = self.net.get_weights()
        new_wih1, new_wh1h2, new_wh2o = new_wih1.flatten(), new_wh1h2.flatten(), new_wh2o.flatten()
        # получем количество нейронов
        inodes, hnodes1, hnodes2, onodes = self.net.get_nodes()
        # проходимся по каждому весу и изменяем его на случайное число, если мутируем.
        for i in range(len(new_wih1)):
            if randint(0, 100) < mutate_chance:
                new_wih1[i] = uniform(0, 1)
        for i in range(len(new_wh1h2)):
            if randint(0, 100) < mutate_chance:
                new_wh1h2[i] = uniform(0, 1)
        for i in range(len(new_wh2o)):
            if randint(0, 100) < mutate_chance:
                new_wh2o[i] = uniform(0, 1)
        # возвращаем веса в нормальный вид и устанавливаем нейронке.
        self.net.set_weights(np.reshape(new_wih1, (hnodes1, inodes + 1)), np.reshape(new_wh1h2, (hnodes2, hnodes1 + 1)),
                             np.reshape(new_wh2o, (onodes, hnodes2 + 1)))

    def get_i_j_by_orientation(self, map1, i, j):
        # функция для того, чтобы получить координаты того, что находится перед собой.
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
                self.x = 300 + new_j * CELL_SIZE  # 300 прибавляем для того, чтобы сделать отступ от левой части экрана
                self.y = new_i * CELL_SIZE  # и клетки отрисовывались за чертой
                return new_i, new_j, False
        return i, j, False


class Map:
    def __init__(self):
        # создаем пустое поле с обычными фоновыми клетками
        self.map_main = [[BaseCell(i, j, WHITE) for j in range(0, WINDOW_HEIGHT, CELL_SIZE)]
                         for i in range(300, WINDOW_WIDTH, CELL_SIZE)]
        self.age = 0

        """список с данными для статистики.
        0) общее количество бактерий -
        1) общее количество минералов -
        2) Количество рожденных за ход -
        3) Количество умерших за ход -
        4) Количество солнцеедов
        5) Количество мясоедов
        6) Количество минералоедов
        7) Количество съеденных"""
        self.statistics = [0, 0, 0, 0, 0, 0, 0, 0]
        # настройки симуляции. количество минералов, солнечной энергии, шанс мутации.
        self.settings = [0, 0, 0]

    def update(self, sun_map):
        """Для того, чтобы бактерии двигались более плавно, необходимо было ввести им параметр updated.
        Без него получается так,что бактерии обновляются по несколько раз.
        Потом, после того, как мы обновили все клетки, нужно им заного дать возможность обновиться."""
        self.age += 1
        # сбрасываем статистику
        self.statistics = [0, 0, 0, 0, 0, 0, 0, 0]
        # обновляем карту
        #
        new_map = self.map_main[:]
        for i in range(len(self.map_main)):
            for j in range(len(self.map_main[0])):
                cell = self.map_main[i][j]
                new_i, new_j, kill = cell.update(self.map_main[:], i, j, sun_map)
                if not kill:
                    new_map[i][j] = BaseCell(cell.x, cell.y, WHITE)
                    new_map[new_i][new_j] = cell
                else:
                    if new_map[new_i][new_j].name == 'Bacteria':  # если бактерию съели, добавляем к статистике
                        self.statistics[7] += 1
                    new_map[new_i][new_j] = BaseCell(cell.x, cell.y, WHITE)

        self.map_main = new_map

        # генерируем минерал
        self.generate_mineral(self.settings[0])

        # убиваем тех, у кого 0 энергии
        for i in range(len(self.map_main)):
            for j in range(len(self.map_main[0])):
                cell = self.map_main[i][j]
                if cell.get_energy() <= 0:
                    self.set_cell(i, j, Mineral(cell.x, cell.y, GREY))
                    # подсчитываем умерших
                    self.statistics[3] += 1

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
                    new_cell.mutate(self.settings[2])
                    cell.set_energy(cell.get_energy() - 100)
                    self.statistics[2] += 1  # добавляем новорожденного в статистику
        # заного даем всем обновиться и подсчитываем клетки
        for line in self.map_main:
            for cell in line:
                cell.set_updated(False)
                if cell.name == 'Bacteria':  # общее кол-во бактерия
                    self.statistics[0] += 1
                    color = cell.get_eating_color()  # получаем цвет клетки
                    if color != [255, 255, 255]:
                        color = color.index(max(color))  # смотрим, какой из цветов преобладает
                        if color == 0:  # если клетка красная, то она мясоед
                            self.statistics[5] += 1
                        elif color == 1:  # если клетка зеленая, то она солцеед
                            self.statistics[4] += 1
                        elif color == 2:  # если клетка синяя, то она минералоед
                            self.statistics[6] += 1
                elif cell.name == 'Mineral':  # общее кол-во минералов
                    self.statistics[1] += 1

    def generate_mineral(self, frequency):
        """Генерируем минерал"""
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
        # меняем у всех клеткок цвет, если изменен вид показа.
        for line in self.map_main:
            for cell in line:
                cell.switch_color()

    def set_cell(self, i, j, cell):
        #  установить на какую-то позицию на карте клетку
        self.map_main[i][j] = cell

    def get_cell(self, i, j):
        return self.map_main[i][j]

    def get_map(self):
        return self.map_main[:]

    def set_map(self, newmap):
        self.map_main = newmap

    def get_age(self):
        return self.age

    def set_age(self, age):
        self.age = age

    def get_statistics(self):
        return self.statistics

    def set_statistics(self, statistics):
        self.statistics = statistics

    def get_settings(self):
        return self.settings

    def set_settings(self, settings):
        self.settings = settings

    def clone(self):
        res_map = []
        for i in self.map_main:
            line = []
            for j in i:
                line.append(j)
            res_map.append(line)
        res = Map()
        res.set_map(res_map)
        res.set_age(self.age)
        res.set_statistics(self.statistics)
        res.set_settings(self.settings)
        return res
