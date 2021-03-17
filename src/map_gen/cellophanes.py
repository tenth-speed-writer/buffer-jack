import numpy as np
from typing import Callable
from src.map_gen.drunk_brush import DrunkBrush, SlightlyCenterMindedArtist, CenterMindedArtist, \
    VeryCenterMindedArtist, brush_plus, brush_2x2
from copy import deepcopy


def _trim(x: int, y: int,
          field: np.ndarray,
          room_cells: np.ndarray):
    """
    :param field: The boolean map of wall tiles
    :param room_cells: Which of the cells in `field` are also room cells
    """
    width, height = field.shape
    this_cell = field[y, x]

    if this_cell:
        # If this cell is a wall (True), check if it's fully surrounded.

        # Define a map of position deltas to the 8 surrounding tiles
        deltas = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1), (0, 1),
                  (1, -1), (1, 0), (1, 1)]

        # Gather the truth values of those cells
        neighbors = [field[y + dy,
                           x + dx]
                     for dx, dy in deltas
                     if 0 <= y + dy < height and 0 <= x + dx < width]

        if sum(neighbors) == 8:
            # If it's completely surrounded, return that we should falsify it.
            return x, y, False
        else:
            borders_a_room = False
            for x_, y_ in neighbors:
                if room_cells[y_, x_] is True:
                    borders_a_room
            return x, y, True

    else:
        # If this cell wasn't a wall to begin with, just return its position and False.
        return x, y, False


class Cellophane:
    _room_map = None

    def __init__(self, width: int, height: int, room_generator: Callable):
        self.room_gen = room_generator(width, height)

    def generate(self):
        self.room_gen.generate()
        self._room_map = deepcopy(self.room_gen.bool_map)

    def render_on(self, dx: int, dy: int, field: np.ndarray):
        pass

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
            raise Exception("Called the room_bool_map of a cellophane whose generator has not yet run!")
        else:
            return self._room_map

    def trim(self):
        # Establish dimensions
        height, width = self.bool_map.shape

        # Create a working copy of the boolean map
        trimmable = deepcopy(self.bool_map)

        # Establish points to be checked, which should be all but the edge cells.
        # May this be the most Pythonic thing I write, ever.
        points_to_check = sum([[(x, y, trimmable)
                                for x in range(1, width - 1)]
                               for y in range(1, height - 1)],
                              [])

        # Spin up a pool with 1 process per available CPU
        pool = mp.Pool(mp.cpu_count())

        # Delegate out the point-check logic
        trimmed = pool.starmap(_trim, points_to_check)
        pool.close()

        # Recombine the deltas into the working copy of the map, then return it.
        for x, y, truth in trimmed:
            trimmable[y, x] = truth

        return trimmable


class SmallDrunkArtistCellophane(Cellophane):
    @staticmethod
    def __room_generator(width, height):
        return DrunkBrush(width=width,
                          height=height,
                          target_fullness=.55,
                          drunk_add_prob=.25,
                          drunk_die_prob=.05,
                          drunk_same_path_prob=0.45,
                          artist_class=CenterMindedArtist)

    def __init__(self):
        super().__init__(width=15, height=15,
                         room_generator=self.__room_generator)

        self.room_gen.generate()
        self.room_gen.apply_automata_smoothing(survive_range=(4, 5, 6, 7, 8),
                                               born_range=(5, 6, 7, 8))

        self.field = deepcopy(self.bool_map)


if __name__ == "__main__":
    import multiprocessing as mp

    mp.freeze_support()

    foo = SmallDrunkArtistCellophane()
    foo.room_gen.generate()
    foo.room_gen.apply_automata_smoothing(survive_range=(4, 5, 6, 7, 8),
                                          born_range=(5, 6, 7, 8))

    for row in foo.room_gen.as_string_rows():
        print(row)

    foo.room_gen.bool_map = foo.trim()
    print("\n")

    for row in foo.room_gen.as_string_rows():
        print(row)
