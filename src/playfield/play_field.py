from typing import Optional, Iterable, Tuple, List, Dict
from src.entity import Entity
from src.entity.entities import Static, Mobile
from tcod.event import EventDispatch
from src.inputs import GameplayHandler
from .cell import Cell


class PlayField:
    """Contains an easily-accessed two-dimensional array of Cell objects.
    Stored in [y][x] order of ordinal position."""
    def __init__(self, width: int, height: int,
                 contents: Optional[Iterable[Tuple[int, int, Entity]]] = (),
                 dispatch: EventDispatch = GameplayHandler):
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

        self._animations: List = []

        self._dispatch = dispatch

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
            self.get_cell(x, y).add_entity(entity=e)

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
        if 0 <= x < len(self._field[0]) and 0 <= y < len(self._field):
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
        if cells:
            # If specified, return the cells corresponding to the given (x, y) tuples
            return [self.get_cell(x, y) for x, y in cells]
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

    def drawables(self) -> List[Dict]:
        """Render own cells into an iterable which can be printed to a console line by line."""
        cells: List[Cell] = self.get_cells()

        # TODO: Implement animations here as an alternative to just showing the first top sigil
        drawables = [{"x": c.position[0],
                      "y": c.position[1],
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

    def tick(self) -> None:
        """Calls .tick on all child cells' entities, then updates own animations/delays/etc"""
        mobs = self.mobiles
        for m in mobs:
            m.tick()