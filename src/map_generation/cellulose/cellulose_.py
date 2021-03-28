import numpy as np
from typing import List, Tuple
from math import floor
from uuid import uuid4


class Cellulose:
    def _generate(self):
        """Overridable to add specific room or path generation algorithms."""
        pass

    def __init__(self,
                 width: int,
                 height: int):
        if not (width % 15 == 0) and (height % 15 == 0):
            raise ValueError("Width and height must be multiples of 15 cells!")

        self.width = width
        self.height = height
        self.field = np.full(shape=(height, width),
                             fill_value=False)

        self.uuid = str(uuid4())

        self.grid_shape = (floor(self.width / 15),
                           floor(self.height / 15))

    def apply_to(self, x0: int, y0: int, tgt: np.ndarray) -> None:
        """Mutates tgt to True for every True in self.field, offsetting by x0, y0."""
        for position, truth in np.ndenumerate(self.field):
            if truth:
                dy, dx = position
                tgt[x0+dy, x0+dx] = truth
        # print([truth for position, truth in np.ndenumerate(self.field) if truth])
        # for y in range(0, self.height):
        #     for x in range(0, self.width):
        #         if self.field[y, x] is True:
        #             print("A cell was true and thus applied.")
        #             tgt[y + y0, x + x0] = True
