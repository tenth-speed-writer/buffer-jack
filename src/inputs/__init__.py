__all__ = ["is_movement_key", "get_position_delta"]

import tcod
from .position_delta import PositionDelta


def is_movement_key(event: tcod.event.Event) -> bool:
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


def is_wait_action(event: tcod.event.Event) -> bool:
    """Returns true if the event is a keydown"""
    wait_symbols = [tcod.event.K_KP_5, tcod.event.K_PERIOD]
    return event.type == "KEYDOWN" and event.sym in wait_symbols


def get_position_delta(event: tcod.event.Event) -> PositionDelta:
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