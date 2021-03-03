import tcod
#from src.playfield import PlayField, Cell
from src.animation import OverlappingSigilAnimation
from .position_delta import PositionDelta
from math import floor

def _is_movement_key(event: tcod.event.Event) -> bool:
    """Returns true IIF event is a keydown event whose sym corresponds to a movement key."""

    # Up, down, left, right, and any numpad key except 5.
    # TODO: include the old vim style keys
    events = [tcod.event.K_KP_1,
              tcod.event.K_KP_2,
              tcod.event.K_KP_3,
              tcod.event.K_KP_4,
              tcod.event.K_KP_6,
              tcod.event.K_KP_7,
              tcod.event.K_KP_8,
              tcod.event.K_KP_9,
              tcod.event.K_UP,
              tcod.event.K_LEFT,
              tcod.event.K_RIGHT,
              tcod.event.K_DOWN]
    if event.type == "KEYDOWN" and event.sym in events:
        return True
    else:
        return False


def _is_wait_action(event: tcod.event.Event) -> bool:
    """Returns true if the event is a keydown and its sym corresponds to a short wait action.
    Currently this is period and numpad 5."""
    wait_symbols = [tcod.event.K_KP_5, tcod.event.K_PERIOD]
    return event.type == "KEYDOWN" and event.sym in wait_symbols


def _get_position_delta(event: tcod.event.Event) -> PositionDelta:
    """Returns a PositionDelta (a .dx and a .dy) if given a valid movement key event, else raises a ValueError."""

    # Numpad
    if event.sym == tcod.event.K_KP_1:
        return PositionDelta(dx=-1, dy=1)
    elif event.sym == tcod.event.K_KP_2:
        return PositionDelta(dx=0, dy=1)
    elif event.sym == tcod.event.K_KP_3:
        return PositionDelta(dx=1, dy=1)
    elif event.sym == tcod.event.K_KP_4:
        return PositionDelta(dx=-1, dy=0)
    elif event.sym == tcod.event.K_KP_6:
        return PositionDelta(dx=1, dy=0)
    elif event.sym == tcod.event.K_KP_7:
        return PositionDelta(dx=-1, dy=-1)
    elif event.sym == tcod.event.K_KP_8:
        return PositionDelta(dx=0, dy=-1)
    elif event.sym == tcod.event.K_KP_9:
        return PositionDelta(dx=1, dy=-1)

    # Arrow keys
    elif event.sym == tcod.event.K_UP:
        return PositionDelta(dx=0, dy=-1)
    elif event.sym == tcod.event.K_DOWN:
        return PositionDelta(dx=0, dy=--1)
    elif event.sym == tcod.event.K_LEFT:
        return PositionDelta(dx=-1, dy=0)
    elif event.sym == tcod.event.K_RIGHT:
        return PositionDelta(dx=1, dy=0)

    # Anything else that made it this far somehow
    else:
        raise ValueError("event.sym must be a valid directional movement key, its value is {}".format(event.sym))


class GameplayHandler(tcod.event.EventDispatch[None]):
    """Handles all non-menu, non-specialty gameplay key commands.

    Be sure to create a new instance when moving to a new PlayField."""
    def __init__(self, interface):
        """Initializes with references to the active playfield and player entity.
        Thus, be sure to create a new GameplayHandler when moving to a new PlayField,
        and to do so after the player's entity has been introduced to it.."""
        # if player_entity.playfield != playfield:
        #     raise ValueError("Given a player entity who isn't assigned the given playfield!")

        super().__init__()

        self._interface = interface

    @property
    def interface(self):
        return self._interface

    @property
    def player_character(self):
        return self._interface.playfield.player_character

    # Internal methods are prefixed cmd_.
    # The on-event methods we're overwriting are prefaced ev_.
    def cmd_quit(self) -> None:
        """When the player alt-F4s or X-es the window."""
        raise SystemExit

    def cmd_move_pc(self, event: tcod.event.Event) -> None:
        """Run on a movement command."""

        # Get the player, their position, and their delta
        pc = self.player_character
        x, y = pc.position
        delta = _get_position_delta(event)

        # Calculate new position and see if it's in range
        x_i, y_i = x + delta.dx, y + delta.dy
        x_in_range = 0 <= x_i < self.interface.playfield.width
        y_in_range = 0 <= y_i < self.interface.playfield.height

        if x_in_range and y_in_range:
            # Get the cell after testing for range, as it would bug out if the cell isn't there
            cell = self.interface.playfield.get_cell(x=x_i, y=y_i)
            if cell.passable:
                pc.move_to(x=x_i, y=y_i)

                # We can be sure that the window shifted if the new window position corresponds to the tipping point.
                win_moved_along_x = x_i >= floor(self.interface.playfield.window[0] / 2)
                win_moved_along_y = y_i >= floor(self.interface.playfield.window[1] / 2)
                if win_moved_along_x or win_moved_along_y:
                    # Clear OverlappingSigilAnimations whenever the window shifts so that they can be refreshed.
                    [self.interface.clear_animation(anim)
                     for x, y, anim in self.interface.animations
                     if isinstance(anim, OverlappingSigilAnimation)]

    def cmd_wait(self, ticks=10) -> None:
        """Called when a player briefly waits. Runs another 10 (default) ticks."""
        self.player_character.cooldown = ticks

    def ev_quit(self, event: tcod.event.Quit) -> None:
        """Fires on alt+F4 or window close request"""
        self.cmd_quit()

    def ev_keydown(self, event: tcod.event.KeyDown) -> None:
        """Fires when the player hits a keyboard key."""
        if _is_movement_key(event):
            self.cmd_move_pc(event)
        elif _is_wait_action(event):
            self.cmd_wait()
