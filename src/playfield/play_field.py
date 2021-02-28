from typing import Optional, Iterable, Tuple, List, Dict
from src.entity import Entity
from src.entity.entities import Static, Mobile
from src.inputs import GameplayHandler
from tcod.event import EventDispatch
from math import floor
from .cell import Cell


class PlayField:
    """Contains an easily-accessed two-dimensional array of Cell objects.
    Stored in [y][x] order of ordinal position."""

    def __init__(self, width: int, height: int,
                 interface,
                 # Should only be special in that we pause sim when the PC's cooldown==0
                 player_character: Optional[Mobile] = None,
                 pc_spawn_point: Optional[Tuple[int, int]] = None,  # Where to drop the player character
                 window_height: int = 0, window_width: int = 0,
                 window_x0: int = 0, window_y0: int = 0,
                 dispatch: Optional[EventDispatch] = None,
                 contents: Optional[Iterable[Tuple[int, int, Entity]]] = ()):
        """
        Initialize a new PlayField of given dimensions, optionally with an iterable of initial entities.

        :param width: Width of the PlayField, in tiles
        :param height: Height of the PlayField, in tiles
        :param contents: A list of (x, y, entity) tuples containing entities and where to spawn them.
        """
        if width < 2 or height < 2:
            raise ValueError("Width and height must be at least 2 each!")
        self._width = width
        self._height = height

        # Iteratively initiate the PlayField with empty Cells,
        # populating the _field variable by the row.
        self._field: List[List[Cell]] = []

        self._window_height = window_height
        self._window_width = window_width
        self._window_x0 = window_x0
        self._window_y0 = window_y0

        self._animations: List = []

        if dispatch:
            self._dispatch = dispatch
        else:
            self._dispatch = GameplayHandler(interface=self.interface)

        for y in range(0, self._height):
            # Create a row which includes one cell, in order,
            # for every tile between 0 and the opposite map edge.
            row = [Cell(x=x,
                        y=y,
                        parent=self)
                   for x in range(0, self._width)]

            # Then append it to the field.
            self._field += [row]

        for x, y, e in contents:
            # Add each provided entity (e) into its specified location
            e.introduce_at(x, y, self)

        self._player_character = player_character
        if (player_character and not pc_spawn_point) or (pc_spawn_point and not player_character):
            raise ValueError("If either player_character or pc_spawn_point is given, then both must be provided.")
        elif player_character:
            self.player_character.introduce_at(x=pc_spawn_point[0],
                                               y=pc_spawn_point[1],
                                               playfield=self)

        # Establish parent/child relationship with the assigned Interface
        self.interface = interface
        interface.playfield = self

    @property
    def shape(self) -> Tuple[int, int]:
        """Returns the shape of this playfield in terms of (width, height)"""
        return self._width, self._height

    def __str__(self) -> str:
        """When printed as a string, the playfield will <> itself and state its shape."""
        return "<PlayField - Shape: {}, {}>".format(str(self._width),
                                                    str(self._height))

    def get_cell(self, x: int, y: int) -> Cell:
        """Returns the specified Cell, so long x and y are within bounds."""
        x_lim = self.width - 1
        y_lim = self.height - 1
        if 0 <= x <= x_lim and 0 <= y <= y_lim:
            return self._field[y][x]
        else:
            raise ValueError("Location (x:{}, y:{}) is out of bounds!"
                             .format(str(x), str(y)))

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    def get_cells(self,
                  cells: Optional[Iterable[Tuple[int, int]]] = None) -> List[Cell]:
        """Gets a list of all cells in a list of (x, y) tuples if given, or all cells otherwise."""
        # print(cells)
        if cells:
            # If specified, return the cells corresponding to the given (x, y) tuples
            c = [self.get_cell(x, y) for x, y in cells if x and y]
            return c
        else:
            # Return all cells in this PlayField
            c = []
            for row in self._field:
                for value in row:
                    c += [value]
            return c

    def has_cell(self, cell: Cell) -> bool:
        """Skims the _field arrays for any instance of the specified Cell.
        :param cell An instance of playfield.Cell"""

        def row_has_cell(r) -> bool:
            return cell in r

        return True in [row_has_cell(row) for row in self._field]

    def drawables(self, center_on: Tuple[int, int]) -> List[Dict]:
        """Render own cells into an iterable which can be printed to a console line by line."""

        # TODO: Implement animations here as an alternative to just showing the first top sigil
        console_x0, console_y0 = self.origin  # The top-left console tile in which the window is drawn
        console_x_max, console_y_max = self.window  # The maximum height and width we can render at once

        # We'll start drawing at x0, y0, so the maximums are relative to those tiles.
        console_x_max += console_x0
        console_y_max += console_y0

        center_x, center_y = center_on

        # Where--in regards to the playfield--to sample the drawables.
        # Greater of zero or half a screen to the left
        window_x0 = max(floor(center_x - 0.5 * self.window[0]), 0)
        window_y0 = max(floor(center_y - 0.5 * self.window[1]), 0)

        # Filter positions based on whether a corresponding list index would actually exist.
        # If the player is standing at the bottom right extreme of a big map, we just print 1/4th of a screen.
        window_positions = [[(x, y)
                             for x in range(window_x0,
                                            window_x0 + self.window[0])
                             if x < self.width]
                            for y in range(window_y0,
                                           window_y0 + self.window[1])
                            if y < self.height]

        # Flatten the array of positions and request corresponding Cell instances
        flat_window_positions = sum(window_positions, [])
        cells: List[Cell] = self.get_cells(cells=flat_window_positions)
        # a = min([c.position[0] for c in cells])
        # b = max([c.position[0] for c in cells])
        # c = min([c.position[1] for c in cells])
        # d = max([c.position[1] for c in cells])
        # print ("x:{} - {},   y:{} - {}".format(str(a), str(b), str(c), str(d)))

        drawables = [{"x": c.position[0] - window_x0,
                      "y": c.position[1] - window_y0,
                      "character": c.sigils[0].character,
                      "priority": c.sigils[0].priority,
                      "rgb": c.sigils[0].color}
                     for c in cells
                     if c.contents and len(c.contents) != 0]

        return drawables

    @property
    def entities(self) -> List[Entity]:
        cells = self.get_cells()

        # Extract contents from each non-empty cell and flatten them into one list
        ent_lists = [c.contents for c in cells if c.contents]
        flat_ents = sum(ent_lists, [])

        return flat_ents

    @property
    def mobiles(self) -> List[Mobile]:
        """Returns a list of Mobile entities in this playfield."""

        # Only return those entities which are instances of Mobile or its subclasses
        ents = self.entities
        return [ent for ent in ents
                if isinstance(ent, Mobile) or issubclass(ent.__class__, Mobile)]

    @property
    def statics(self) -> List[Static]:
        """Returns a list of Static entities in this playfield."""

        # As per .mobiles, only return those which are instances of Static or its subclasses
        ents = self.entities
        return [ent for ent in ents
                if isinstance(ent, Static) or issubclass(ent.__class__, Static)]

    @property
    def dispatch(self) -> EventDispatch:
        return self._dispatch

    @dispatch.setter
    def dispatch(self, d: EventDispatch) -> None:
        if issubclass(d.__class__, EventDispatch):
            self._dispatch = d
        else:
            raise ValueError("d must be a subclass of tcod.event.EventDispatch, got {}"
                             .format(str(d)))

    @property
    def window(self):
        return self._window_width, self._window_height

    @window.setter
    def window(self, dims: Tuple[int, int]):
        """Assigns a new visible window for the playfield, given a tuple of (width, height)"""
        w, h = dims
        if w >= 0 and h >= 0:
            self._window_width = w
            self._window_height = h
        else:
            raise ValueError("Both width and height must be greater than zero. Got ({}, {})"
                             .format(str(w), str(h)))

    @property
    def origin(self):
        """Returns the top left cell (x0, y0) from which to draw this playfield."""
        return self._window_x0, self._window_y0

    @origin.setter
    def origin(self, new_origin: Tuple[int, int]):
        """Assigns a new tuple(x, y) as the topleft console cell from which to render this playfield."""
        x0, y0 = new_origin
        if x0 >= 0 and y0 >= 0:
            self._window_x0 = x0
            self._window_y0 = y0
        else:
            raise ValueError("Both x0 and y0 must be >= 0. Given ({}, {})"
                             .format(str(x0), str(y0)))

    def tick(self) -> None:
        """Calls .tick on all child cells' entities, then updates own animations/delays/etc"""
        mobs = self.mobiles
        for m in mobs:
            m.tick()

    @property
    def player_character(self) -> Mobile:
        return self._player_character

    @player_character.setter
    def player_character(self, pc: Mobile) -> None:
        if pc not in self.mobiles:
            raise ValueError("pc must be a Mobile and already have been introduced to the playfield.")
        else:
            self._player_character = pc
