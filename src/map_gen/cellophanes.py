import numpy as np
from typing import Callable
from src.map_gen.drunk_brush import DrunkBrush, SlightlyCenterMindedArtist, CenterMindedArtist, \
    VerySlightlyCenterMindedArtist, brush_plus, brush_2x2, DrunkArtist
from copy import deepcopy
from random import random


def _trim(x: int, y: int,
          field: np.ndarray):
    """
    :param field: The boolean map of wall tiles
    """
    height, width = field.shape
    this_cell = bool(field[y, x])

    if this_cell is True:
        # If this cell is a wall (True), check if it's fully surrounded.

        # Define a map of position deltas to the 8 surrounding tiles
        deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

        # Gather the truth values of those cells
        neighbors = [(x+dx, y+dy)
                     for dx, dy in deltas
                     if 0 <= y + dy < height and 0 <= x + dx < width]

        neighbor_is_room = False in [bool(field[y, x]) for x, y in neighbors]

        if neighbor_is_room:
            return x, y, True
        else:
            return x, y, False

        # neighbor_truths = [field[y_, x_]
        #                    for x_, y_ in neighbors]
        #
        # if sum(neighbor_truths) == 8:
        #     # If it's completely surrounded, return that we should falsify it.
        #     return x, y, False
        #
        # else:
        #     # If it's not completely surrounded but doesn't border a room, trim that too.
        #     if True in neighbor_is_room:
        #         return x, y, True
        #     else:
        #         return x, y, False

    else:
        # If this cell wasn't a wall to begin with, just return its position and False.
        return x, y, False


class Cellophane:
    grid_shape = [0, 0]
    _room_map = None

    def __init__(self, width: int, height: int, room_generator: Callable):
        self.room_gen = room_generator(width, height)

    def generate(self):
        self.room_gen.generate()

        # The room map will be True for every False in the freshly-generated bool_map.
        self._room_map = np.logical_not(self.room_gen.bool_map)

    def render_on(self, x0: int, y0: int, field: np.ndarray):
        x_i, y_i = [dim - 1 for dim in self.room_gen.shape]
        field[range(y0, y_i), range(x0, x_i)] = self.bool_map

    @property
    def bool_map(self):
        if self.room_gen.bool_map is not None:
            return self.room_gen.bool_map
        else:
            raise Exception("Requested .bool_map of a cellophane whose generator has not yet been run.")

    @property
    def room_map(self):
        """Returns a boolean array of the tiles originally marked as False, to be referenced after trimming things."""
        if self._room_map is None:
            raise Exception("Called the .room_map of a cellophane whose generator has not yet been run!")
        else:
            return self._room_map

    def trim(self):
        # Establish dimensions
        height, width = self.bool_map.shape

        # Create a working copy of the boolean map
        trimmable = deepcopy(self.bool_map)

        # Establish points to be checked, which should be all but the edge cells.
        # May this be the most Pythonic thing I write, ever.
        points_to_check = []
        for y in range(0, height):
            for x in range(0, width):
                points_to_check.append((x, y, trimmable))

        # Spin up a pool with 1 process per available CPU
        pool = mp.Pool(mp.cpu_count())

        # Delegate out the point-check logic
        # print(points_to_check)
        trimmed = pool.starmap(func=_trim, iterable=points_to_check)

        pool.close()

        # Recombine the deltas into the working copy of the map, then return it.
        for x, y, truth in trimmed:
            trimmable[y, x] = truth

        # Update the bool_map, which will now be distinct from the inverse of the room map.
        self.room_gen.bool_map = trimmable

        # Return it
        return trimmable


class SmallDrunkArtistCellophane(Cellophane):
    grid_shape = (1, 1)
    @staticmethod
    def __room_generator(width, height):
        return DrunkBrush(width=width,
                          height=height,
                          target_fullness=.5 + .25*random(),
                          drunk_add_prob=.25 + .2*random(),
                          drunk_die_prob=.025 + .075*random(),
                          drunk_same_path_prob=.015 + .03*random(),
                          artist_class=CenterMindedArtist)

    def __init__(self):
        super().__init__(width=15, height=15,
                         room_generator=self.__room_generator)

        self.generate()
        self.room_gen.apply_automata_smoothing(survive_range=(4, 5, 6, 7, 8),
                                               born_range=(5, 6, 7, 8))

        self.field = deepcopy(self.bool_map)


class MediumDrunkArtistCellophane(Cellophane):
    grid_shape = (2, 2)

    @staticmethod
    def __room_generator(width, height):
        return DrunkBrush(width=width,
                          height=height,
                          target_fullness=.35 + .10*random(),
                          drunk_add_prob=.35 + .2*random(),
                          drunk_die_prob=.05 + .075*random(),
                          drunk_same_path_prob=.55,
                          artist_class=SlightlyCenterMindedArtist)

    def __init__(self):
        super().__init__(width=30, height=30,
                         room_generator=self.__room_generator)

        self.generate()
        self.room_gen.apply_automata_smoothing(survive_range=(4, 5, 6, 7, 8),
                                               born_range=(5, 6, 7, 8))

        self.field = deepcopy(self.bool_map)


class LargeDrunkArtistCellophane(Cellophane):
    grid_shape = (3, 3)

    @staticmethod
    def __room_generator(width, height):
        return DrunkBrush(width=width,
                          height=height,
                          target_fullness=.35 + .10*random(),
                          drunk_add_prob=.15 + .05*random(),
                          drunk_die_prob=.05 + .075*random(),
                          drunk_same_path_prob=.35,
                          artist_class=VerySlightlyCenterMindedArtist,
                          brush=brush_plus)

    def __init__(self):
        super().__init__(width=45, height=45,
                         room_generator=self.__room_generator)

        self.generate()
        self.room_gen.apply_automata_smoothing(survive_range=(4, 5, 6, 7, 8),
                                               born_range=(5, 6, 7, 8))

        self.field = deepcopy(self.bool_map)


if __name__ == "__main__":
    import multiprocessing as mp

    mp.freeze_support()

    foo = LargeDrunkArtistCellophane()
    foo.room_gen.generate()
    foo.room_gen.apply_automata_smoothing(survive_range=(4, 5, 6, 7, 8),
                                          born_range=(5, 6, 7, 8))

    foo.trim()
    for row in foo.room_gen.as_string_rows():
        print(row)
    print("\n")