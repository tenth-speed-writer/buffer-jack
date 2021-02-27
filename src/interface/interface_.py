import tcod
from typing import List, Optional, Tuple
from src.playfield import PlayField
from src.menus import Menu
from src.entity import Entity
from src.entity.entities import Mobile
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

    def new_playfield(self, width: int, height: int,
                      contents: Optional[List[Tuple[int, int, Entity]]] = [],
                      player_character: Optional[Entity] = None,
                      player_spawn: Optional[Tuple[int, int]] = None):
        """Replace the current playfield in this interface with a new one using specified parameters."""
        pf = PlayField(width=width,
                       height=height,
                       contents=[ent for ent in contents],
                       player_character=player_character,
                       pc_spawn_point=player_spawn)
        self._pf_width = pf.width
        self._pf_height = pf.height
        self._pf = pf

    def new_console(self,
                    min_width: int = 48,
                    min_height: int = 36) -> tcod.console.Console:
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

    def _print_playfield(self, center_on: Optional[Tuple[int, int]] = None):
        window_width, window_height = self.playfield.window
        # TODO: Replace this with a mutable camera_center attribute in order to make this player-character-independent
        # Set the camera center equal to the greater of the player's position or half-a-window from the PlayField edge.
        center_x = max(floor(window_width / 2),
                       self.playfield.player_character.position[0]) if not center_on else center_on[0]
        center_y = max(floor(self.playfield.window[1] / 2),
                       self.playfield.player_character.position[1]) if not center_on else center_on[1]

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

        # Determine where to center the camera
        player_x, player_y = self.playfield.player_character.position
        win_w, win_h = self.playfield.window

        # The larger of half the window's size or the player's position, for both dimensions
        view_center = (max(floor(win_w/2), player_x),
                       max(floor(win_h/2), player_y))
        self._print_playfield(center_on=view_center)

        if self._menus:
            for m in self._menus:
                m_width, m_height = m.shape
                drawables = m.render_menu(x0=floor(self.console.width/2 - m_width/2),
                                          y0=floor(self.console.height/2 - m_height/2))
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
        if self._menus:
            pass
        elif pc and pc.cooldown != 0:
            self.playfield.tick()
        else:
            pass

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

        # If pf_width and pf_height are not explicitly stated, assume based on the console.
        # Raise a ValueError if they and an initial playfield are given but do not agree.

        # if pf_width:
        #     if playfield and not pf_width == playfield.width:
        #         raise ValueError("pf_width does not correspond to the width of the provided playfield.")
        #     else:
        #         self._pf_width = pf_width
        # else:
        #     self._pf_width = self.console.width
        #
        # if pf_height:
        #     if playfield and not pf_height == playfield.height:
        #         raise ValueError("pf_height does not correspond to the height of the provided playfield.")
        #     else:
        #         self._pf_height = pf_height
        # else:
        #     self._pf_height = self.console.height