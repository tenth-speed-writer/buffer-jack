__all__ = ["Cell", "PlayField"]

# Bless type hinting.
from collections import Iterable
from src.entity import Entity
from typing import Optional, List, Tuple


class Cell:
    """A collection of entities that exist in the same place on the PlayField."""
    def __init__(self, parent, x: int, y: int,
                 contents: Optional[Iterable[Entity]] = ()):
        self._parent = parent
        self._x = x
        self._y = y

        self.contents = [c for c in contents]

    @property
    def sigils(self):
        """Returns an iterable of the highest-priority sigil or sigils in this cell."""

        if len(self.contents) > 0:
            # Get the highest sigil priority from all (sigil, priority)
            # tuples, then return a list of sigils with that priority.
            sigils = [entity.sigil() for entity in self.contents]
            max_value = max([s[1] for s in sigils])
            top_sigils = [s[0] for s in sigils]
        else:
            # If there's nothing here, return an empty string."
            return tuple("")

    def add_entity(self, entity: Entity) -> None:
        """Appends a new entity to this cell's contents, assuming it's not already there."""
        if not entity in self.contents:
            self.contents = self.contents + entity
        else:
            print("Warning: tried to move Entity {} into a cell that it's already in.".format(entity.name))

    def remove_entity(self, entity: Entity) -> None:
        """Removes an entity from .contents if it exists, or prints a warning if not."""
        if entity in self.contents:
            self.contents = self.contents.remove(entity)
        else:
            print("Can't remove entity {} from cell x:{}, y:{} as it isn't there!".format(entity.name,
                                                                                          str(self._x),
                                                                                          str(self._y)))

    @property
    def position(self) -> Tuple[int, int]:
        """Returns own position as (x, y)."""
        return self._x, self._y

class PlayField:
    """Contains an easily-accessed two-dimensional array of Cell objects.
    Stored in [y][x] order of ordinal position."""
    def __init__(self, width: int, height: int,
                 contents: Optional[Iterable[Tuple[int, int, Entity]]]):
        """
        Initialize a new PlayField of given dimensions, optionally with an iterable of initial entities.

        :param width: Width of the PlayField, in tiles
        :param height: Height of the PlayField, in tiles
        :param contents: A list of (x, y, entity) tuples containing entities and where to spawn them.
        """
        self.width = width
        self.height = height

        # Iteratively initiate the PlayField with empty Cells,
        # populating the _field variable by the row.
        self._field: List[List[Cell]] = []
        for y in range(0, self.height):
            self._field[y] = []
            for x in range(0, self.width):
                self._field[y][x] = Cell(self, x, y)

        # Create each entity in contents

    @property
    def shape(self) -> Tuple[int, int]:
        return self.width, self.height

    def __str__(self) -> str:
        return "<PlayField - Shape: {}, {}>".format(str(self.width),
                                                    str(self.height))

    def get_cell(self, x: int, y: int) -> Cell:
        """Returns the specified Cell, so long x and y are within bounds."""
        if 0 <= x < len(self._field[0]) and 0 <= y < len(self._field):
            return self._field[y][x]
        else:
            raise ValueError("Location (x:{}, y:{}) is out of bounds!".format(str(x), str(y)))

foo = PlayField(40, 30)
print(foo)