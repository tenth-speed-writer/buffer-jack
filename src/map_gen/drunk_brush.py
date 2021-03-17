from src.map_gen.map_generator import MapGenerator
from copy import deepcopy
from typing import Tuple, List
import numpy as np
from math import floor, sqrt
from random import random, sample, randint, choices
from time import time_ns

# In the words of Jaq: "oh boy here we go."
import multiprocessing as mp

# Includes x,y as well as 1 orthogonal step in each direction
brush_plus = ((-1, 0),
              (1, 0),
              (0, -1),
              (0, 1),
              (0, 0))

# Top-left corner at x, y
brush_2x2 = ((0, 0),
             (0, 1),
             (1, 0),
             (1, 1))
brush_3x3 = ((0, 0), (0, 1), (0, 2),
             (1, 0), (1, 1), (1, 2),
             (2, 0), (2, 1), (2, 2))


def decide_fate(x: int, y: int,
                width: int, height: int,
                field: np.ndarray,
                survive_range: Tuple,
                born_range: Tuple) -> Tuple[int, int, bool]:
    # Determine what's adjacent to this specific cell
    adjacents_positions = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            # Don't test this exact cell
            if not (dx == 0 and dy == 0):
                x_is_valid = 0 <= x + dx < width
                y_is_valid = 0 <= y + dy < height

                if x_is_valid and y_is_valid:
                    adjacents_positions.append((x + dx,
                                                y + dy))
    adjacents = [field[y, x] for x, y in adjacents_positions]
    num_living_neighbors = sum(adjacents)
    is_alive = field[y, x]

    if len(adjacents) < 8:
        # If it's a map edge cell, just mark it True
        return x, y, True

    else:
        if is_alive and num_living_neighbors not in survive_range:
            # If it's alive and not enough neighbors, kill it
            return x, y, False

        elif num_living_neighbors in born_range:
            # If it's not alive and has enough neighbors, birth it
            return x, y, True

        else:
            # Otherwise, leave it as it was
            return x, y, is_alive


class DrunkArtist:
    """Represents a wandering paint brush."""

    def __init__(self, x0, y0,
                 field: np.ndarray,
                 brush: Tuple[Tuple[int, int]] = ((0, 0),),
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
        """Marks every valid tile under this Drunkard's brush as False, essentially carving out the map."""
        for x, y in self.valid_brushables:
            self.field[y, x] = False

    def tick(self):
        want_to_stick_with_path = random() <= self.same_path_prob
        has_moved_at_least_once = self.last_move is not None
        last_path_still_valid = self.last_move in self.move_options

        if want_to_stick_with_path and has_moved_at_least_once and last_path_still_valid:
            direction = self.last_move
        else:
            direction = sample(self.move_options, 1)[0]

        dx, dy = direction
        self.x += dx
        self.y += dy

        self.apply_brush()


class CenterMindedArtist(DrunkArtist):
    def __init__(self, x0: int, y0: int,
                 field: np.ndarray,
                 brush=(0, 0),
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
        want_to_stick_with_path = random() <= self.same_path_prob
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

            direction = choices(population=directions,
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
                 brush=((0, 0),),
                 center_weight=.85):
        super().__init__(x0, y0, field, brush, same_path_prob, center_weight)


class SlightlyCenterMindedArtist(CenterMindedArtist):
    def __init__(self, x0: int, y0: int,
                 field,
                 same_path_prob: float,
                 brush=((0, 0),),
                 center_weight=.35):
        super().__init__(x0, y0, field, brush, same_path_prob, center_weight)


class DrunkBrush(MapGenerator):
    """Generates a map by running one or more (spawned) drunk walkers through a full field,
    clearing tiles as they go until the map has reached a certain percentage of openness."""

    def __init__(self, width: int, height: int,
                 brush: Tuple[Tuple[int, int]] = ((0, 0),),
                 target_fullness: float = 0.5,
                 drunk_add_prob: float = 0,  # Chance to spawn another drunk from a living one at each tick
                 drunk_die_prob: float = 0,  # Chance for a drunk to die each tick if it's not the last one alive
                 drunk_same_path_prob: float = 0,  # Chance for a drunk to use its last direction instead of rolling
                 artist_class=DrunkArtist):  # The class from which to spawn this class's artist or artists

        # The initial state for a drunken walk should be a fully True field
        initial = np.full(shape=(height, width),
                          fill_value=True,
                          dtype=bool)

        super().__init__(map_width=width,
                         map_height=height,
                         initial=initial)

        self.initial = initial
        self.field = deepcopy(self.initial)  # A deep copy of the initial field. The starting point of our generation.

        # Design parameters and brush choice
        self.brush = brush
        self._target_fullness = target_fullness
        self._add_prob = drunk_add_prob
        self._die_prob = drunk_die_prob
        self._same_path_prob = drunk_same_path_prob

        self.artist_class = artist_class

    @property
    def field_full_proportion(self) -> float:
        """Returns a float between 0 and 1 representing what proportion of the field is still True."""
        trues = np.sum(self.field)
        total = self.field.size
        return trues / total

    def apply_automata_smoothing(self,
                                 survive_range: Tuple = (4, 5, 6, 7, 8),
                                 born_range: Tuple = (5, 6, 7, 8)):
        next_field = deepcopy(self.field)

        cells_to_decide_fate = []
        for y_ in range(0, self.height):
            for x_ in range(0, self.width):
                cells_to_decide_fate.append((x_, y_))

        fate_arguments = [(x, y, self.width, self.height, self.field, survive_range, born_range)
                          for x, y in cells_to_decide_fate]

        # HNNNNNNNNNNNG here we go
        # Create a pool with 1 process per available CPU
        fate_decision_pool = mp.Pool(processes=mp.cpu_count())

        # Delegate out decide_fate calls to each x, y in cells_to_decide_fate
        decisions = fate_decision_pool.starmap(decide_fate, fate_arguments)
        fate_decision_pool.close()

        for x, y, truth in decisions:
            next_field[y, x] = truth

        self.field = next_field

        # If the boolean map already exists, update it. Don't, if it hasn't been.
        if self.bool_map is not None:
            self.bool_map = next_field

    def generate(self) -> np.ndarray:
        if self.bool_map is not None:
            return self.bool_map

        else:
            # Initialize our list of drunk artists with one situated at a random place on the map.
            artists = [self.artist_class(x0=randint(floor(.45 * self.width),
                                                    floor(.55 * self.width)),
                                         y0=randint(floor(.45 * self.height),
                                                    floor(.55 * self.height)),
                                         field=self.field,
                                         same_path_prob=self._same_path_prob,
                                         brush=self.brush)]

            # Define a limit on how many ticks we'll run the drunks run
            tick_no = 0
            max_ticks = 10000

            # Tick the artists until our finish condition is met or we hit the tick limit
            while self.field_full_proportion > self._target_fullness and tick_no <= max_ticks:
                # Decide whether to kill an existing artist, if there's more than one.
                if len(artists) > 1:
                    # Make a random roll against the artist death probability
                    should_kill_artist = random() <= self._die_prob

                    # If we roll True, pick one at random and kill it
                    if should_kill_artist:
                        artists.remove(sample(artists, 1)[0])

                # Decide whether to spawn a new artist
                should_spawn_artist = random() <= self._add_prob
                if should_spawn_artist:
                    # If so, select one existing artist and spawn a new one on the same tile.
                    parent = sample(artists, 1)[0]
                    artists.append(self.artist_class(x0=parent.x,
                                                     y0=parent.y,
                                                     field=self.field,
                                                     brush=self.brush,
                                                     same_path_prob=self._same_path_prob))
                # Tick artists
                [a.tick() for a in artists]

                # Increment tick counter to test against max_ticks
                tick_no += 1

            # Cache the generated map and return it
            self.bool_map = deepcopy(self.field)
            return self.bool_map


if __name__ == "__main__":
    mp.freeze_support()

    start_time = time_ns() / 1e6
    gen = DrunkBrush(width=30, height=30, target_fullness=0.65,
                     drunk_same_path_prob=.25,
                     drunk_add_prob=.45,
                     drunk_die_prob=.10,
                     artist_class=CenterMindedArtist,
                     brush=brush_plus)

    for row in gen.as_string_rows():
        print(row)
    print("\n")

    gen.apply_automata_smoothing(survive_range=(3, 4, 5, 6, 7, 8),
                                 born_range=(4, 5, 6, 7, 8))

    for row in gen.as_string_rows():
        print(row)
    print("\n")

    # gen.apply_automata_smoothing(survive_range=(4, 5, 6, 7, 8),
    #                              born_range=(5, 6, 7, 8))
    #
    # for row in gen.as_string_rows():
    #     print(row)
    # print("\n")

    end_time = time_ns() / 1e6

    print("Process took {} milliseconds.".format(str(end_time - start_time).split(".")[0]))
