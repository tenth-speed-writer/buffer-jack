from math import floor, sqrt
from typing import List, Tuple, Type, Sequence
from src.map_generation.cellulose import RoomCellulose

import random as rand
import numpy as np
import multiprocessing as mp


BRUSH_2x2 = ((0, 0), (0, 1), (1, 0), (1, 1))


def _cellular_automata(x, y, field,
                       born: Tuple[int],
                       survive: Tuple[int]):
    # Keep in mind that a false cell is alive in this context
    cell_is_alive = not(field[y, x])
    neighbors = _neighbors_of(x, y, field)
    neighbors_alive = sum([not(n) for n in neighbors])

    if cell_is_alive and neighbors_alive in survive:
        return x, y, False
    elif not cell_is_alive and neighbors_alive in born:
        return x, y, False
    elif cell_is_alive and neighbors_alive not in survive:
        return x, y, True
    elif not cell_is_alive and neighbors_alive not in born:
        return x, y, True


def _neighbors_of(x: int, y: int, field: np.ndarray):
    return (field[y-1, x-1], field[y, x-1], field[x+1, x-1],
            field[y-1, x], field[x+1, x],
            field[y+1, x-1], field[y+1, x], field[y+1, x+1])


class DrunkArtist:
    """Represents a wandering paint brush."""

    def __init__(self, x0, y0,
                 field: np.ndarray,
                 brush: Tuple[int, int],
                 same_path_prob: float = 0):
        # The field and this drunk's initial position on it.
        self.x = x0
        self.y = y0
        self.field = field

        # A tuple of dx, dy directions from x, y to paint when called upon.
        self.brush = brush

        # Last move and probability to prefer it to the exclusion of rolling
        self.same_path_prob = same_path_prob
        self.last_move = None

        # Dimensions
        self.height, self.width = field.shape

    @property
    def move_options(self):
        opts = []
        x_max, y_max = self.width - 1, self.height - 1

        at_top_edge = self.y == 0
        at_bottom_edge = self.y == y_max
        at_left_edge = self.x == 0
        at_right_edge = self.x == x_max

        # Up move
        if at_top_edge == 0:
            opts.append((0, -1))

        # Up right move
        if not (at_top_edge or at_right_edge):
            opts.append((1, -1))

        # Right move
        if not at_right_edge:
            opts.append((1, 0))

        # Down right move
        if not (at_right_edge or at_bottom_edge):
            opts.append((1, 1))

        # Down move
        if not at_bottom_edge:
            opts.append((0, 1))

        # Down left move
        if not (at_left_edge or at_bottom_edge):
            opts.append((-1, 1))

        # Left move
        if not at_left_edge:
            opts.append((-1, 0))

        # Up left move
        if not (at_left_edge or at_top_edge):
            opts.append((-1, -1))

        return opts

    @property
    def valid_brushables(self):
        """Returns a list of cells under this Drunkard's brush which are within the bounds of the field."""
        x_max, y_max = self.width - 1, self.height - 1  # The index limits of the field
        to_brush: List[Tuple[int, int]] = []  # A return value aggregator

        # Iterate over each dx, dy combo in this Drunkard's brush
        for dx, dy in self.brush:
            # Determine if it's on a valid pair of indices
            x_in_range = 0 <= self.x + dx <= x_max
            y_in_range = 0 <= self.y + dy <= y_max

            # If so, append it to the aggregator. Otherwise, fail silently.
            if x_in_range and y_in_range:
                to_brush.append((self.x + dx,
                                 self.y + dy))

        return to_brush

    def apply_brush(self):
        """Marks every valid tile under this Drunkard's brush as True, essentially carving out the map."""
        for x, y in self.valid_brushables:
            self.field[y, x] = True

    def tick(self):
        want_to_stick_with_path = rand.random() <= self.same_path_prob
        has_moved_at_least_once = self.last_move is not None
        last_path_still_valid = self.last_move in self.move_options

        if want_to_stick_with_path and has_moved_at_least_once and last_path_still_valid:
            direction = self.last_move
        else:
            direction = rand.sample(self.move_options, 1)[0]

        dx, dy = direction
        self.x += dx
        self.y += dy

        self.apply_brush()


class CenterMindedArtist(DrunkArtist):
    def __init__(self, x0: int, y0: int,
                 field: np.ndarray,
                 brush=BRUSH_2x2,
                 same_path_prob=0,
                 center_weight=0.55,
                 not_center_weight=0.2):
        super().__init__(x0=x0, y0=y0,
                         field=field,
                         brush=brush,
                         same_path_prob=same_path_prob)

        self.center_weight = center_weight
        self.not_center_weight = not_center_weight

    def tick(self):
        want_to_stick_with_path = rand.random() <= self.same_path_prob
        has_moved_at_least_once = self.last_move is not None
        last_path_still_valid = self.last_move in self.move_options

        if want_to_stick_with_path and has_moved_at_least_once and last_path_still_valid:
            direction = self.last_move
        else:
            # Move in a direction randomly chosen with preferential weight given to moving toward the center
            center_x, center_y = self.width / 2 - 1, self.height / 2 - 1

            def dist_to_center(x_, y_):
                return sqrt((center_x - x_) ** 2 + (center_y - y_) ** 2)

            # Calculate own distance to the center
            own_dist_to_center = dist_to_center(self.x, self.y)
            directions = self.move_options
            destinations = [(self.x + dx,
                             self.y + dy)
                            for dx, dy in directions]

            # Get which destinations are closer to the center, then use that to determine the weights
            dest_closer_to_center = [dist_to_center(x_, y_) < own_dist_to_center
                                     for x_, y_ in destinations]
            weights = [self.center_weight if is_closer else self.not_center_weight
                       for is_closer in dest_closer_to_center]

            direction = rand.choices(population=directions,
                                     weights=weights,
                                     k=1)[0]

        dx, dy = direction
        self.x += dx
        self.y += dy

        self.apply_brush()


class VeryCenterMindedArtist(CenterMindedArtist):
    def __init__(self, x0: int, y0: int,
                 field,
                 same_path_prob: float,
                 brush=BRUSH_2x2,
                 center_weight=.85):
        super().__init__(x0, y0, field, brush, same_path_prob, center_weight)


class SlightlyCenterMindedArtist(CenterMindedArtist):
    def __init__(self, x0: int, y0: int,
                 field,
                 same_path_prob: float,
                 brush=BRUSH_2x2,
                 center_weight=.35):
        super().__init__(x0, y0, field, brush, same_path_prob, center_weight)


class VerySlightlyCenterMindedArtist(CenterMindedArtist):
    def __init__(self, x0: int, y0: int,
                 field,
                 same_path_prob: float,
                 brush=BRUSH_2x2,
                 center_weight=.3):
        super().__init__(x0, y0, field, brush, same_path_prob, center_weight)


class DrunkRoomCel(RoomCellulose):
    def __init__(self, grid_x0: int, grid_y0: int,
                 grid_width: int, grid_height: int,
                 artist: Type[DrunkArtist],
                 generator,
                 tgt_fullness: float,
                 new_artist_prob: float = 0,
                 kill_artist_prob: float = 0,
                 same_path_prob: float = 0):
        super().__init__(grid_x0=grid_x0,
                         grid_y0=grid_y0,
                         grid_width=grid_width,
                         grid_height=grid_height,
                         generator=generator)
        self._artist = artist
        self._tgt_fullness = tgt_fullness
        self._new_artist_prob = new_artist_prob
        self._kill_artist_prob = kill_artist_prob
        self._same_path_prob = same_path_prob

        self._generate()
        self.apply_automata_smoothing()

    def apply_automata_smoothing(self,
                                 born=(5, 6, 7, 8),
                                 survive=(4, 5, 6, 7, 8)):
        """Executes the _cellular_automata function in parallel using specified born and survive thresholds."""
        inputs = [(pos[1], pos[0], self.field, born, survive)
                  for pos, truth in np.ndenumerate(self.field)
                  if 0 < pos[1] < self.field.shape[1] - 1
                  and 0 < pos[0] < self.field.shape[0] - 1]

        pool = mp.Pool(mp.cpu_count())
        deltas = pool.starmap(_cellular_automata, inputs)
        pool.close()
        for d in deltas:
            x, y, truth = d
            self.field[y, x] = truth
        field_height, field_width = self.field.shape

        # Set borders impassable
        self.field[0, :] = False
        self.field[field_height - 1, :] = False
        self.field[:, 0] = False
        self.field[:, field_width - 1] = False

    @property
    def _room_fullness_ratio(self):
        """Returns the ratio of cells filled in as passable (True) to total field size."""
        return sum(self.field.flatten()) / self.field.size

    def _new_artist(self, x, y):
        return self._artist(x, y,
                            field=self.field,
                            same_path_prob=self._same_path_prob)

    def _generate(self):
        mid_x, mid_y = floor(self.grid_shape[0] * 15 / 2), \
                       floor(self.grid_shape[1] * 15 / 2)

        artists: List[DrunkArtist] = [self._new_artist(x=mid_x,
                                                       y=mid_y)]

        tick_counter = 0
        tick_limit = 1000
        while self._room_fullness_ratio < self._tgt_fullness and tick_counter < tick_limit:
            # Tick all the artists, moving them and making them paint
            for a in artists:
                a.tick()

            # Maybe spawn artists
            if rand.random() <= self._new_artist_prob:
                parent = rand.choice(artists)
                artists.append(self._new_artist(parent.x, parent.y))

            # Maybe kill an artist
            if len(artists) > 1 and rand.random() <= self._kill_artist_prob:
                artists.remove(rand.choice(artists))

            tick_counter += 1


class SmallDrunkRoom(DrunkRoomCel):
    grid_shape = (1, 1)

    def __init__(self, grid_x, grid_y, generator):
        super().__init__(grid_x, grid_y,
                         grid_width=1,
                         grid_height=1,
                         artist=VeryCenterMindedArtist,
                         tgt_fullness=.65,
                         new_artist_prob=0.15,
                         kill_artist_prob=0.025,
                         same_path_prob=0,
                         generator=generator)


class MediumDrunkRoom(DrunkRoomCel):
    grid_shape = (2, 2)

    def __init__(self, grid_x, grid_y, generator):
        super().__init__(grid_x, grid_y,
                         grid_width=2,
                         grid_height=2,
                         artist=CenterMindedArtist,
                         tgt_fullness=.55,
                         new_artist_prob=0.15,
                         kill_artist_prob=0.025,
                         same_path_prob=0.15,
                         generator=generator)


class LargeDrunkRoom(DrunkRoomCel):
    grid_shape = (3, 3)

    def __init__(self, grid_x, grid_y, generator):
        super().__init__(grid_x, grid_y,
                         grid_width=3,
                         grid_height=3,
                         artist=SlightlyCenterMindedArtist,
                         tgt_fullness=.475,
                         new_artist_prob=0.25,
                         kill_artist_prob=0.03,
                         same_path_prob=0.20,
                         generator=generator)


if __name__ == "__main__":
    import multiprocessing as mp

    mp.freeze_support()


    def row_as_string(row: Sequence):
        result = ""
        for passability in row:
            result += " " if passability else "#"
        return result


    from src.map_generation.map_generator.map_generator_ import MapGenerator

    mapgen = MapGenerator(5, 4,
                          candidates=[SmallDrunkRoom,],
                          candidate_weights=[1.0])
    mapgen.generate_room(0, 0)
    # for row in mapgen.rooms[0].field:
    #     print(row_as_string(row))
    #
    # print("\n")

    mapgen.generate_room(1, 0)
    # for row in mapgen.rooms[1].field:
    #     print(row_as_string(row))
    #
    # print("\n")

    mapgen.link_door_pts((0, 0), (1, 0))
    #print(mapgen.rooms)


    from src.map_generation.cellulose.hallway import HallwayCellulose
