__all__ = ["Cell", "PlayField"]

# Bless type hinting.
from collections.abc import Iterable
from src.entity import Entity
from src.entity.entities import Mobile, Static
from typing import Optional, List, Tuple, Dict
from src.sigil import Sigil

class Cell:
    """A collection of entities that exist in the same place on the PlayField."""
    def __init__(self, parent, x: int, y: int,
                 contents: Optional[Iterable[Entity]] = tuple()):
        self._parent = parent
        self._x = x
        self._y = y

        # Cast contents to a list regardless of their type
        self._contents = [c for c in contents]

    @property
    def sigils(self) -> List[Sigil]:
        """Returns an iterable of the highest-priority sigil or sigils in this cell."""

        # DEVNOTE: The idea is to cycle through top sigils for a given rendered tile on the map
        if len(self.contents) > 0:
            # Get the highest sigil priority from all (sigil, priority)
            # tuples, then return a list of sigils with that priority.
            sigils = [(entity.sigil, entity.sigil.priority) for entity in self.contents]
            max_value = max([s[1] for s in sigils])

            top_sigils = [s[0]
                          for s in sigils
                          if s[1] == max_value]

            return top_sigils

        else:
            # If there's nothing here, return an iterable with an empty string."
            return []

    @property
    def contents(self) -> List[Entity]:
        return self._contents

    @property
    def position(self) -> Tuple[int, int]:
        """Returns own position as (x, y)."""
        return self._x, self._y

    def add_entity(self, entity: Entity) -> None:
        """Appends a new entity to this cell's contents, assuming it's not
        already there, and pairs that entity with this cell."""

        if not entity in self.contents:
            self._contents = [] + self._contents + [entity]
        else:
            print("Warning: tried to move Entity {} into a cell that it's already in."
                  .format(entity.name))

    def remove_entity(self, entity: Entity) -> None:
        """Removes an entity from .contents if it exists, or prints a warning if not."""
        if entity in self.contents:
            self._contents = self._contents.remove(entity)
        else:
            print("Can't remove entity {} from cell x:{}, y:{} as it isn't there!"
                  .format(entity.name,
                          str(self._x),
                          str(self._y)))

    @property
    def playfield(self):
        return self._parent

    @property
    def passable(self) -> bool:
        """If this cell is empty, or it's not empty but none of its contents are impassable, then it's passable."""
        #print([c for c in self.contents])
        if not self.contents:
            return True
        elif sum([c.passable for c in self.contents]) != len(self.contents):
            return False
        else:
            return True


class PlayField:
    """Contains an easily-accessed two-dimensional array of Cell objects.
    Stored in [y][x] order of ordinal position."""
    def __init__(self, width: int, height: int,
                 contents: Optional[Iterable[Tuple[int, int, Entity]]] = ()):
        """
        Initialize a new PlayField of given dimensions, optionally with an iterable of initial entities.

        :param width: Width of the PlayField, in tiles
        :param height: Height of the PlayField, in tiles
        :param contents: A list of (x, y, entity) tuples containing entities and where to spawn them.
        """
        self._width = width
        self._height = height

        # Iteratively initiate the PlayField with empty Cells,
        # populating the _field variable by the row.
        self._field: List[List[Cell]] = []

        self._animations: List = []

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

    def tick(self) -> None:
        """Calls .tick on all child cells' entities, then updates own animations/delays/etc"""
        mobs = self.mobiles
        for m in mobs:
            m.tick()


############
# Import for testing:
# from src.entity import entities
#
#
# class ToyBoi(Entity):
#     def __init__(self, name: str = "Toy Boi the delightful!"):
#         super().__init__(size=3,
#                          sigil=Sigil("@"),
#                          name=name)
#
# boi = ToyBoi()
# foo = PlayField(40, 30, contents=((2, 3, boi),))
# print(len(foo._field))
# print(foo._field[0][0].__dir__())
# print(foo._field[5][8].position)
# print(foo._field[5][0].sigils)
# print(foo.has_cell(foo._field[4][2]))
# print(foo.has_cell(Cell(PlayField(5,5), 2, 3)))
# print(str(boi.position))
# foo.get_cell(2, 3).contents[0].move_to(4, 6)
# print(boi.position)
#
#
# bar = PlayField(30, 20, contents=((0, 0, entities.Barricade()),
#                                   (0, 1, entities.Barricade()),
#                                   (0, 2, entities.Barricade()),
#                                   (1, 0, entities.Barricade()),
#                                   (1, 2, entities.Barricade()),
#                                   (2, 0, entities.Barricade()),
#                                   (2, 2, entities.Barricade()),
#                                   (3, 0, entities.Barricade()),
#                                   (3, 2, entities.Barricade()),
#                                   (3, 1, entities.Barricade()),
#                                   (4, 0, entities.Barricade()),
#                                   (4, 1, entities.Barricade()),
#                                   (4, 1, entities.Barricade()),
#                                   (4, 2, entities.Barricade())
#                                   ))
#
#
# print(bar.get_cell(x=4, y=1).sigils)
#
# print(bar.drawables())
