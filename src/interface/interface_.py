import tcod
from typing import List, Optional
from src.playfield import PlayField
from src.menus import Menu


class Interface:
    def open_menu(self, menu: Menu):
        """Menus can have their own on_open and on_close callbacks,
        so generally only override for purposes of interface screw."""
        self._menus.append(menu)

    def close_menu(self, menu: Menu):
        """Menus can have their own on_open and on_close callbacks,
        so generally only override for purposes of interface screw."""
        self._menus.remove(menu)

    @property
    def context(self):
        return self._context

    @property
    def playfield(self):
        return self._pf

    def new_console(self,
                    min_width: int = 96,
                    min_height: int = 64) -> tcod.console.Console:
        """Returns a new console from self._context based on a specified minimum width and height."""
        return self._context.new_console(min_columns=min_height,
                                         min_rows=min_width,
                                         order="F")  # Specifies that the console is in x-major order (x, y)

    @property
    def console(self):
        return self._console

    @console.setter
    def console(self, c: tcod.console.Console):
        self._console = c

    def tick(self) -> None:
        """Fetches a fresh console and ticks the playfield.
        Override to apply on-tick interface screw."""
        self.playfield.tick()

        # Refresh console and draw contents
        self.console = self.new_console()


    def __init__(self,
                 context: tcod.context.Context,
                 playfield: PlayField):
        self._context = context
        self._pf = playfield
        self._menus: List[Menu] = []
        self._console: Optional[tcod.console.Console] = self.new_console()