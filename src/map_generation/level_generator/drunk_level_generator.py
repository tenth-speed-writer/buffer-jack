import numpy as np
import random as rand

from typing import List, Tuple
from src.map_generation.level_generator.level_generator_ import LevelGenerator
from src.map_generation.map_generator import WholeDrunkMapGen
from src.entity import Entity, Mobile
from src.sigil import Sigil


class DrunkLevelGenerator(LevelGenerator):
    def __init__(self):
        map_gen = WholeDrunkMapGen(width=80, height=60,
                                   num_centers=12,
                                   passability_tgt=0.25,
                                   wanderer_born_prob=0,
                                   wanderer_die_prob=0,
                                   centroidal_born_prob=0.10,
                                   centroidal_die_prob=0.0125)

        def generate_content(walls: np.ndarray, field: np.ndarray) -> List[Tuple[int, int, Entity]]:
            ents = [Mobile(size=4,
                           sigil=Sigil("m", color=(190, 190, 240)),
                           name="Memeish boi"),
                    Mobile(size=4,
                           sigil=Sigil("m", color=(220, 200, 255)),
                           name="Memey McMemeFace")]
            positions = [(pos[1], pos[0]) for pos, truth in np.ndenumerate(field) if truth]

            ents_and_positions = [(ent, rand.choice(positions)) for ent in ents]
            return [(pos[0], pos[1], ent) for ent, pos in ents_and_positions]

        super().__init__(width=60, height=40,
                         map_generator=map_gen,
                         content_generator=generate_content)

