import json
from src.sigil import Sigil
from src.entity.entities import Static, Entity
from src.entity.landscape import WalkableTerrain, Wall, Door
from src.playfield import PlayField
from typing import List, Optional, Callable, Tuple
from random import randint

EntityArray = List[List[Optional[List[Entity]]]]


def make_wall() -> Static:
    return Wall()


def make_floor() -> Static:
    if randint(0, 3) >= 1:
        char = "."
    else:
        char = ","

    return WalkableTerrain(character=char)


class Room:
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

    def __init__(self, width: int, height: int,
                 wall_func: Callable = make_wall,
                 floor_func: Callable = make_floor):
        self._contents: EntityArray = [[[] for x in range(0, width)]
                                       for y in range(0, height)]

        self._wall_func = wall_func
        self._floor_func = floor_func

        self._width = width
        self._height = height

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height


class RectangularRoom(Room):
    """The bog standard room generator. Creates a 1-tile wall from a specifiable
    function wall_func, then fills the whole shebang with floors from a likewise
    specifiable floor_func."""
    def draw_rect_room(self):
        """Draws a rectangular room"""
        # Top and bottom walls
        self._contents[0] = [[self._wall_func()] for x in range(0, self._width)]
        self._contents[-1] = [[self._wall_func()] for x in range(0, self._width)]

        # Left and right walls
        x_limits = (0, self._width - 1)
        for y in range(1, self._height - 1):
            for x in range(0, self._width):
                if x in x_limits:
                    self._contents[y][x].append(self._wall_func())

        # Floors, including under walls
        for y in range(0, self._height):
            for x in range(0, self._width):
                self._contents[y][x].append(self._floor_func())

    def __init__(self, width: int, height: int,
                 wall_func: Callable = make_wall,
                 floor_func: Callable = make_floor):
        super().__init__(width, height, wall_func, floor_func)
        self.draw_rect_room()

    def add_door(self, x, y):
        is_in_range = x <= self.width or y <= self.height
        is_on_edge = (x == 0) or (y == 0) or (x == self.width - 1) or (y == self.height - 1)

        if not (is_in_range and is_on_edge):
            raise ValueError("Can only add a door on a room edge; got {}, {}"
                             .format(str(x), str(y)))

        else:
            # Remove any walls from that point and add a door
            for ent in self._contents[y][x]:
                if issubclass(ent.__class__, Wall):
                    print("Removed {}".format(str(ent)))
                    self._contents[y][x].remove(ent)
            print(self._contents[y][x])
            self._contents[y][x] = [] + self._contents[y][x] + [Door()]