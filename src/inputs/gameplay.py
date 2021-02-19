import tcod
from src.playfield import PlayField, Cell
from src.entity import entities, Entity


class GameplayHandler(tcod.event.EventDispatch[None]):
    """Handles all non-menu, non-specialty gameplay key commands.

    Be sure to create a new instance when moving to a new PlayField."""

    def __init__(self,
                 playfield: PlayField,
                 player_entity: entities.Mobile):
        """Initializes with references to the active playfield and player entity.
        Thus, be sure to create a new GameplayHandler when moving to a new PlayField,
        and to do so after the player's entity has been introduced to it.."""
        if player_entity.playfield != playfield:
            raise ValueError("Given a player entity who isn't assigned the given playfield!")

        super().__init__()

        self._playfield = playfield
        self._player_entity = player_entity


    def cmd_quit(self) -> None:
        raise SystemExit


    def cmd_move_pc(self, event: tcod.event.Event):
        """Run on a movement command."""
        pass

    def cmd_wait(self, ticks=10):

    def ev_quit(self, event: tcod.event.Quit) -> None:
        self.cmd_quit()
