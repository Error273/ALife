from random import randint


class BaseCell:
    """Базовый класс клетки."""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color

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

    def update(self):
        self.color = (randint(0, 255), randint(0, 255), randint(0, 255))

