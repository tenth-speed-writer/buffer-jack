import json
from src.sigil import Sigil
from src.entity.entities import Static, Entity
from src.playfield import PlayField
from typing import List, Optional, Callable, Tuple
from random import randint

EntityArray = List[List[Optional[List[Entity]]]]


def make_wall() -> Static:
    return Static(size=9,
                  sigil=Sigil("█", priority=3),
                  name="Wall",
                  passable=False)


def make_floor() -> Static:
    if randint(0, 3) >= 1:
        char = "."
    else:
        char = ","

    return Static(size=1,
                  sigil=Sigil(char,
                              priority=1,
                              color=(100, 100, 100)),
                  name="Floor",
                  passable=True)


class Room:
    def __init__(self, width: int, height: int,
                 wall_func: Callable = make_wall,
                 floor_func: Callable = make_floor):

        self._contents: EntityArray = [[[] for x in range(0, width)]
                                       for y in range(0, height)]

        # Top and bottom walls
        self._contents[0] = [[wall_func()] for x in range(0, width)]
        self._contents[-1] = [[wall_func()] for x in range(0, width)]

        # Left and right walls
        x_limits = (0, width - 1)
        for y in range(1, height-1):
            for x in range(0, width):
                if x in x_limits:
                    self._contents[y][x].append(wall_func())

        # Floors, including under walls
        for y in range(0, height):
            for x in range(0, width):
                self._contents[y][x].append(floor_func())

        self._width = width
        self._height = height

    def add_to_playfield(self, x0: int, y0: int,
                         pf: PlayField):
        """Given a playfield and an upper left corner, will attempt to draw itself on that playfield."""
        for y in range(0, self._height):
            for x in range(0, self._width):
                ents: List[Entity] = self._contents[y][x]
                for e in ents:
                    if x0+x < pf.width and y0+x < pf.height:
                        # If target cell is within playfield boundaries,
                        # introduce entities in this location at x, y plus offset
                        e.introduce_at(x0+x, y0+y, pf)
                    else:
                        print("Warning: Tried to draw entity outside PlayField bounds.")