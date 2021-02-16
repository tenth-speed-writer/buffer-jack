from typing import Optional, Tuple
from src.entity import Entity
from src.sigil import Sigil

class Static(Entity):
    """Static vs Mobile determines whether an Entity has the logic to move under its own prerogative.
    A Static can still be moved, but will complain unless move_to is further overridden."""
    def move_to(self, x, y) -> None:
        print("Warning: using move_to on Static entity {} at (x:{}, y:{})")\
            .format(self.name, str(x), str(y))
        super().move_to(x, y)


class Mobile(Entity):
    """An entity which has both a base movement cost property and
    an @property move_cost which can be overridden for game logic."""
    def __init__(self,
                 size: int,
                 sigil: Sigil,
                 name: Optional[str] = None,
                 parent_cell: Optional[object] = None,
                 parent_playfield: Optional[object] = None,
                 position: Optional[Tuple[int, int]] = None,
                 base_move_cost: int = 100,
                 passable: bool = False) -> None:
        super().__init__(size=size, sigil=sigil, name=name,
                         parent_cell=parent_cell,
                         parent_playfield=parent_playfield,
                         position=position)
        self._base_move_cost = base_move_cost

        # DEVNOTE: When entities spawn, they'll be on their base cooldown.
        self._action_cooldown = base_move_cost

    @property
    def move_cost(self) -> int:
        """Returns number of ticks it costs move a tile on the map.
        Overwrite this method to apply stat logic and buffs/maluses."""
        return self._base_move_cost

    @property
    def cooldown(self):
        """Getter for own action cooldown remaining. Probably don't override... probably."""
        return self._action_cooldown

    def tick(self) -> None:
        """What happens to this entity every tick.
        Override as necessary, but be sure to decrement the action cooldown. :)"""
        if self._action_cooldown > 0:
            self._action_cooldown -= 1


# class ToyBoi(Mobile):
#     def __init__(self, name: str = "Toy Boi the delightful!"):
#         super().__init__(size=3,
#                          sigil="@",
#                          name=name)


class Barricade(Static):
    """A simple "█" impassible tile.
    TODO: Create a wall which picks a border tile based on its neighbors."""
    def __init__(self):
        super().__init__(name="Barricade",
                         size=5,
                         sigil=Sigil("█", color=(230, 230, 230)))

# foo = ToyBoi()
#
# while foo.cooldown > 0:
#     foo.tick()
#     print(foo.cooldown)