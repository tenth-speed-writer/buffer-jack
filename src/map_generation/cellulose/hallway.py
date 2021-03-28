import numpy as np
import random as rand

from math import sin, cos
from typing import Tuple
from src.map_generation.cellulose import Cellulose


class HallwayCellulose(Cellulose):
    def _generate(self):
        def paint(x, y):
            x_range = [x_ for x_ in range(x, x + self.brush_size)
                       if 0 <= x + self.brush_size < self.width - self.brush_size]
            y_range = [y_ for y_ in range(y, y + self.brush_size)
                       if 0 <= y + self.brush_size < self.height - self.brush_size]
            for x_ in x_range:
                for y_ in y_range:
                    self.field[y_, x_] = True

        cursor = [param for param in self.origin]
        while cursor != self.destination:
            paint(cursor[0], cursor[1])

            dx, dy = self.destination[0] - cursor[0], self.destination[1] - cursor[1]

            can_go_sideways = False if dx == 0 else True
            go_sideways = rand.random() < 0.5 if can_go_sideways else False

            if go_sideways:
                delta = 1 if dx > 0 else -1
                cursor = (cursor[0] + delta,
                          cursor[1])
            else:
                delta = 1 if dy > 0 else -1
                cursor = (cursor[0],
                          cursor[1] + delta)



    def __init__(self,
                 origin: Tuple[int, int],
                 destination: Tuple[int, int],
                 brush_size: int = 2):
        min_x, max_x = min([origin[0], destination[0]]), max([origin[0], destination[0]])
        min_y, max_y = min([origin[1], destination[1]]), max([origin[1], destination[1]])

        width, height = max_x - min_x, max_y - min_y
        super().__init__(width=width,
                         height=height)

        self.origin = origin
        self.destination = destination
        self.brush_size = brush_size