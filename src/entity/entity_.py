from typing import Optional, Tuple
from src.sigil import Sigil


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
                 sigil: Sigil,
                 name: Optional[str] = None,
                 parent_cell: Optional[object] = None,
                 parent_playfield: Optional[object] = None,
                 position: Optional[Tuple[int, int]] = None,
                 passable: bool = True):

        if not 0 <= size <= 10:
            raise ValueError("Size must be 0 <= size <= 10. Given {}".format(str(size)))

        self._sigil = sigil
        self._size = size
        self._position = position
        self._name = name

        self._parent_cell = parent_cell
        self._parent_playfield = parent_playfield
        self._passable = passable

    @property
    def cell(self):
        """Returns the cell in which the entity exists.
        Raises a NotOnPlayFieldException if parent playfield and cell aren't both defined."""
        if self._parent_cell and not self._parent_playfield:
            raise NotOnPlayFieldException("Entity {} has a parent Cell, but not a parent PlayField."
                                          .format(str(self._name)))
        elif self._parent_cell:
            return self._parent_cell
        else:
            raise NotOnPlayFieldException("Entity {} does not have a parent Cell.".format(str(self._name)))

    @property
    def playfield(self):
        """Returns the PlayField in which the entity exists.
        Raises a NotOnPlayFieldException if parent playfield and cell aren't both defined."""
        if self._parent_playfield and not self._parent_cell:
            raise NotOnPlayFieldException("Entity {} has a parent PlayField, but not a parent Cell."
                                          .format(str(self._name)))
        elif self._parent_playfield:
            return self._parent_playfield
        else:
            raise NotOnPlayFieldException("Entity {} does not have a parent PlayField.".format(str(self._name)))

    @playfield.setter
    def playfield(self, pf):
        """Sets the object's new playfield, assuming it passes some ducktype testing."""

        # Simple tests since we're limited by a circular import reference and can't use true type hinting. :(
        assert hasattr(pf, "_field")
        self._parent_playfield = pf

    def _change_cell(self, c) -> None:
        # TODO: Consider cells having a "can_accept" @property that we check here
        self._parent_cell = c

    @cell.setter
    def cell(self, new_cell) -> None:
        """Change this entity's cell, including changing its playfield if necessary.
        This generally corresponds to the entity being moved on the map.
        Can maybe override to add on-move logic, but move_to is a better place to do so."""

        self.playfield = new_cell.playfield
        self._change_cell(new_cell)

    @property
    def position(self):
        """Return the position of this object by asking its parent cell.
        You could override this, but probably shouldn't. Probably."""
        if not self._parent_playfield:
            raise NotOnPlayFieldException("Entity {} does not have a parent PlayField.".format(str(self._name)))
        elif not self._parent_cell:
            raise NotOnPlayFieldException("Entity {} does not have a parent Cell.".format(str(self._name)))
        else:
            return self._parent_cell.position

    @property
    def sigil(self) -> Sigil:
        """Returns the class's sigil and that sigil's priority.
        A higher priority means this sigil will be rendered over the others.
        Level 3 is mobs and terrain, level 2 is stuff on the floor, level 4 is obscuring stuff like smoke."""
        return self._sigil

    @sigil.setter
    def sigil(self, new_sigil: Sigil) -> None:
        self._sigil = new_sigil

    @property
    def size(self) -> int:
        """Returns the size of an entity.
        TODO: Make this have an impact somewhere in gameplay."""
        return self._size

    @size.setter
    def size(self, s: int) -> None:
        """Assigns a new size value, assuming it is an integer in range 0 <= s <= 10."""
        if 0 <= s <= 10:
            self._size = s
        else:
            raise ValueError("Size to be assigned must be in range 0 <= size <= 10, given {}".format(str(s)))

    @property
    def name(self) -> str:
        """Return the name of this entity. Override for contextual name generation."""
        return str(self._name)

    @name.setter
    def name(self, new_name: str) -> None:
        """Set the name of this Entity. Override to add on-change logic."""
        self._name = new_name

    def __on_destination_impassable(self):
        """What to do when this entity fails to move because its move_to target is impassable.
        In many cases a unit which fails to move this should do so quietly,
        but there's cases where we may want to override this as any movement failure
        would be indicative of, for instance, an AI failure."""
        pass

    def move_to(self, x, y) -> None:
        """Get Cell x, y from the entity's playfield, then attempt to move the entity there.
        The entity must already have a playfield in which it exists; otherwise, use introduce_at(x, y, playfield).

        Override to add on-move logic."""

        # Find the cell in question and reassign it, firing the112
        # above-written setter to handle both pf and cell changes

        # TODO: Destination passability logic
        if not (0 <= x <= self.playfield.width - 1) or not (0 <= y <= self.playfield.height - 1):
            raise ValueError("Move-to destination (x:{}, y:{}) for entity {} is out of bounds!"
                             .format(str(x), str(y), str(self.name)))

        new_cell = self.playfield.get_cell(x, y)

        if new_cell.passable:
            self.cell.remove_entity(self)
            new_cell.add_entity(self)
            self.cell = new_cell
        else:
            # Usually, fail quietly--but is overridable if we find reason.
            self.__on_destination_impassable()

    def introduce_at(self, x, y, playfield) -> None:
        """As per move_to, but assumes the Entity doesn't already have a playfield.
        Use when spawning an entity on the playfield for the first time.

        Override to add game logic when an entity spawns on the map."""
        self.playfield = playfield

        cell = playfield.get_cell(x=x, y=y)
        cell.add_entity(self)

        self.cell = cell

    @property
    def passable(self) -> bool:
        """Determines whether this tile is passable to other entities.
        Override to allow situational passability."""
        return self._passable

    @passable.setter
    def passable(self, can_pass: bool) -> None:
        """Set whether an entity is passable to other entities.
        Override to enact logic on variable change."""
        self._passable = can_pass

    def destroy(self):
        """Removes an entity from the playfield. Override to add on-destroyed logic."""
        if not self.cell:
            raise Exception("Tried to destroy entity {} which doesn't exist on the field."
                            .format(str(self)))
        self.cell.remove_entity(self)