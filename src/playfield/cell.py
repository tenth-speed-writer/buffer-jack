from typing import Optional, Iterable, List, Tuple
from src.sigil import Sigil
from src.entity import Entity


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
        return self._contents if self._contents else []

    @property
    def position(self) -> Tuple[int, int]:
        """Returns own position as (x, y)."""
        return self._x, self._y

    def add_entity(self, entity: Entity) -> None:
        """Appends a new entity to this cell's contents, assuming it's not
        already there, and pairs that entity with this cell."""

        if not self.contents:
            self._contents = [entity]
        elif entity not in self.contents:
            self._contents.append(entity)
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
        if not self.contents:
            return True
        elif sum([c.passable for c in self.contents]) != len(self.contents):
            return False
        else:
            return True
