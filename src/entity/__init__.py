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

    @playfield.setter
    def playfield(self, pf):
        """Sets the object's new playfield, assuming it passes some ducktype testing."""

        # Simple test since we're limited by a circular import reference and can't use true type hinting. :(
        assert hasattr(pf, "_field")
        self._parent_playfield = pf

    def _change_cell(self, c) -> None:
        # TODO: Consider cells having a "can_accept" @property that we check here
        self._parent_cell = c

    @cell.setter
    def cell(self, new_cell) -> None:
        """Change this entity's cell, including changing its playfield if necessary.
        This generally corresponds to the entity being moved or placed."""

        self.playfield = new_cell.playfield
        self._change_cell(new_cell)

    def move_to(self, x, y):
        """Get Cell x, y from the entity's playfield, then attempt to move the entity there."""

        # Find the cell in question and reassign it, firing the
        # above-written setter to handle both pf and cell changes
        new_cell = self.playfield.get_cell(x, y)
        self.cell = new_cell

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


class ToyBoi(Entity):
    def __init__(self):
        name = "Toy Boi the delightful!"
        super().__init__(size=3,
                         sigil="@",
                         name=name,)