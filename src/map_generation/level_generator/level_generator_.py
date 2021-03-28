import random as rand
import numpy as np
import multiprocessing as mp

from typing import Callable, List, Tuple

from src.playfield import PlayField
from src.entity import Entity, Static, Mobile
from src.sigil import Sigil


class LevelGenerator:
    def __init__(self, width: int, height: int,
                 map_generator,
                 content_generator,
                 player_spawn_generator=None,
                 wall_generator=None):
        # After instantiation, should have attributes .walls and .fields, described below
        self._generator: Callable = map_generator

        # Should spawn a bunch of mobiles and map features and other good stuff based on the map generator.
        self._content_generator: Callable = content_generator

        # Should be a function which returns a new static entity representing a wall
        self._wall_generator: Callable = wall_generator if wall_generator else self._default_wall_generator

        # Walls is a 2d boolean numpy array of cells upon which to draw walls or other boundaries
        self.walls: np.ndarray = map_generator.walls

        # Field is a boolean numpy array of cells in which it is valid to spawn entities--the inside of the playfield.
        self.field: np.ndarray = map_generator.field

        # A running list of entities with which to generate the playfield, in the format [(x, y, entity),]
        self.entities: List[Tuple[int, int, Entity]] = []

        # Start generating entities by laying out the walls surrounding the playable space.
        self.entities += self._walls_as_entities()

        # Spin up the content for this map based on the provided content_generator function
        content: List[Entity] = content_generator(self.walls, self.field)
        self.entities += content

        # While we're at it, figure out where to spawn the player
        self._player_spawn: Tuple[int, int] = player_spawn_generator()\
            if player_spawn_generator\
            else self.place_player_spawn()

    @staticmethod
    def _default_wall_generator():
        """A stand-in for something specifiable at instantiation. Returns a bland little wall."""
        return lambda: Static(size=9,
                              sigil=Sigil("#",
                                          priority=3),
                              name="Wall",
                              passable=False)

    def _walls_as_entities(self) -> List[Tuple[int, int, Entity]]:
        """Returns this LevelGenerator's .walls as a list of (x, y, entity)"""
        #([x for x in np.ndenumerate(self.walls)])
        return [(pos[1], pos[0], self._wall_generator()) for pos, truth in np.ndenumerate(self.walls) if truth]

    def get_playfield(self, interface, player_character: Mobile):
        """Instantiates a new Playfield using the topography and entities generated by this class."""
        height, width = self.walls.shape
        return PlayField(width=width, height=height,
                         interface=interface,
                         player_character=player_character,
                         pc_spawn_point=self._player_spawn)

    def place_player_spawn(self):
        """If no more specific method is given, pick a random place in the field with no particular weight."""
        return rand.choice([(pos[1], pos[0]) for pos, truth in np.ndenumerate(self.field) if truth])