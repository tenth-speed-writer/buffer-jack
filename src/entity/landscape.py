from typing import Tuple, Optional
from .entities import Static
from src.sigil import Sigil
from tcod.event import Event


class WalkableTerrain(Static):
    def __init__(self,
                 character: str = "#",
                 name: str = "",
                 color=(100, 100, 100)):
        """By default, instantiates as a passable, bland-gray, priority 2, size 1 hash mark."""
        super().__init__(size=1,
                         sigil=Sigil(character,
                                     priority=2,
                                     color=color),
                         name=name,
                         passable=True)

    def on_move_to(self, *args, **kwargs):
        """In a stunning twist of fate, this is just a dummy function
           for you to override when creating logic that fires when an
           entity steps into the same tile as this entity. :)"""
        pass


class Wall(Static):
    def __init__(self,
                 char: str = "█",
                 name: str = "",
                 color = (200, 200, 200)):
        super().__init__(size=9,
                         sigil=Sigil(char, priority=4),
                         name=name,
                         passable=False)


class Door(Wall):
    def __init__(self,
                 open_char: str = "",
                 closed_char: str = "",
                 color: Tuple[int, int, int] = (240, 240, 240),
                 start_open: bool = False):
        self._open_sigil = Sigil(open_char, 2, color)
        self._closed_sigil = Sigil(closed_char, 2, color)
        self._is_open = False

        # Call the super's constructor
        super().__init__(name="Door", color=color)

        # Replace the default sigil with the appropriate sigil for this door's initial state
        self._sigil = self._open_sigil if start_open else self._closed_sigil

    @property
    def is_open(self):
        """Getter for ._is_open. No matching setter, as that should happen through .open_door() and .close_door()!"""
        return self._is_open

    def _on_open(self):
        """Override to add logic that fires when the door is opened."""
        pass

    def _on_close(self):
        """Override to add logic that fires when the door is closed."""
        pass

    def _open_door(self):
        """When the door is opened, fire its _on_open method and change _is_open to true.
        Override if you need to change the signature of _on_open."""
        if not self.is_open:
            self._on_open()
            self._is_open = True

    def _close_door(self):
        """When the door is closed, fire its _on_close method and change _is_open to false.
        Override if you need to change the signature of _on_closed."""
        if self.is_open:
            self._on_close()
            self._is_open = False

    def on_use(self, event: Optional[Event] = None):
        """Opens it if it's closed, closes it if it's open.

        Override if you want to change the signature of _open_door() or _close_door(),
        or just to add shenanigans that fire any time the door is interacted with."""
        if self.is_open:
            self._close_door()
        else:
            self._open_door()

    @property
    def sigil(self) -> Sigil:
        """Return the appropriate sigil, based on whether the door is open or closed."""
        if self.is_open:
            return self._open_sigil
        else:
            return self._closed_sigil