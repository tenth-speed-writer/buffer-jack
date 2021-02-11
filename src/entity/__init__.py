__all__ = ["Entity"]

from typing import Optional, Tuple


class CannotMoveException(Exception):
    """Raised when an entity wants to move to a tile but can't.
    Things should generally not try to move where they can't to begin with,
    so when this appears in the log it probably indicates AI logic failure."""
    pass


class NotOnPlayFieldException(Exception):
    """Raised when something tries to do something with an entity's position,
    but the entity does not currently have one (i.e. it isn't on the playfield.)"""
    pass


class Entity:
    """Anything which can be rendered in a PlayField, be it terrain or actor."""
    def __init__(self,
                 size: int,
                 sigil: str,
                 name: Optional[str],
                 parent_cell: Optional[object],
                 parent_playfield: Optional[object],
                 position: Optional[Tuple[int, int]] = None,
                 sigil_priority: int = 3):
        self._sigil = sigil
        self._sigil_priority = sigil_priority
        self._size = size
        self._position = position
        self._name = name

        self._parent_cell = parent_cell
        self._parent_playfield = parent_playfield

    @property
    def cell(self):
        """Returns the cell in which the entity exists.
        Raises a NotOnPlayFieldException if parent playfield and cell aren't both defined."""
        if self._parent_cell and not self._parent_playfield:
            raise NotOnPlayFieldException("Entity {} has a parent Cell, but not a parent PlayField.".format(str(self._name)))
        elif self._parent_cell:
            return self._parent_cell
        else:
            raise NotOnPlayFieldException("Entity {} does not have a parent Cell.".format(str(self._name)))

    @property
    def playfield(self):
        """Returns the PlayField in which the entity exists.
        Raises a NotOnPlayFieldException if parent playfield and cell aren't both defined."""
        if self._parent_playfield and not self._parent_cell:
            raise NotOnPlayFieldException("Entity {} has a parent PlayField, but not a parent Cell.".format(str(self._name)))
        elif self._parent_playfield:
            return self._parent_playfield
        else:
            raise NotOnPlayFieldException("Entity {} does not have a parent PlayField.".format(str(self._name)))

    def move_to(self, x, y):
        """Moves the entity to a specified location on the playfield."""
        #TODO: Test if it -actually can- move where it wants to go, and if not, raise a CannotMoveException
        old_cell = self.cell
        new_cell = self.playfield.get_cell(x, y)

        new_cell.add_entity(self)
        old_cell.remove_entity(self)

    @property
    def position(self):
        if not self._parent_playfield:
            raise NotOnPlayFieldException("Entity {} does not have a parent PlayField.".format(str(self._name)))
        elif not self._parent_cell:
            raise NotOnPlayFieldException("Entity {} does not have a parent Cell.".format(str(self._name)))
        else:
            return self._parent_cell.position()

    @property
    def sigil(self):
        """Returns the class's sigil and that sigil's priority.
        A higher priority means this sigil will be rendered over the others.
        Level 3 is mobs and terrain, level 2 is stuff on the floor, level 4 is obscuring stuff like smoke."""
        return self._sigil, self._sigil_priority

    @property
    def size(self) -> int:
        return self._size

    @property
    def name(self) -> str:
        return str(self._name)