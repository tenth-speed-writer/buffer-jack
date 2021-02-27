import tcod
from typing import List, Optional, Tuple
from src.playfield import PlayField
from src.menus import Menu
from math import floor


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

    def _print_playfield(self, center_on: Tuple[int, int]):
        window_width, window_height = self.playfield.window
        # TODO: Replace this with a mutable camera_center attribute in order to make this player-character-independent
        # Set the camera center equal to the greater of the player's position or half-a-window from the PlayField edge.
        center_x = max(floor(window_width / 2),
                       self.playfield.player_character.position[0])
        center_y = max(floor(self.playfield.window[1] / 2),
                       self.playfield.player_character.position[1])

        drawables = self.playfield.drawables(center_on=(center_x,
                                                        center_y))
        for d in drawables:
            self.console.print(x=d["x"],
                               y=d["y"],
                               string=d["character"],
                               fg=d["rgb"])

    def print_self(self):
        # TODO: Render other interface elements like stats and UI console
        self.console.draw_frame(x=0, y=0,
                                width=self.console.width,
                                height=self.console.height,
                                title="BUFFER.JACK()")
        self.playfield.origin = 1, 1
        self.playfield.window = (self.console.width - 24 - 1,
                                 self.console.height - 12 - 1)
        if self._menus:
            for m in self._menus:
                drawables = m.render_menu(x0=10, y0=10)
                for d in drawables:
                    x, y, sigil = d
                    self.console.print(x=x,
                                       y=y,
                                       string=sigil.character,
                                       fg=sigil.color)

        self.context.present(self.console,
                             keep_aspect=True,
                             integer_scaling=True)

    def tick(self) -> None:
        """Fetches a fresh console and ticks the playfield.
        Override to apply on-tick interface screw."""

        # Simulate only if the player isn't in a menu and it's not their turn to act
        pc = self.playfield.player_character
        if pc.cooldown != 0 or self._menus:
            self.playfield.tick()

        # Refresh console and draw contents
        self.console = self.new_console()
        self.print_self()

        # Determine whether to use a menu dispatcher or the playfield dispatcher
        if self._menus:
            dispatcher = self._menus[-1].dispatch  # From the top-most menu
        else:
            dispatcher = self.playfield.dispatch

        # And hand off events! :)
        for event in tcod.event.get():
            dispatcher.dispatch(event)

    def __init__(self,
                 context: tcod.context.Context,
                 playfield: PlayField):
        self._context = context
        self._pf = playfield
        self._menus: List[Menu] = []
        self._console: Optional[tcod.console.Console] = self.new_console()
