import numpy as np
import random as rand
import multiprocessing as mp

from typing import List, Tuple
from math import sqrt, floor
from numpy.linalg import norm

BRUSH_2x2 = ((0, 0), (0, 1), (1, 0), (1, 1))
BRUSH_4x4 = [position for position, value in np.ndenumerate(np.full(shape=(4, 4), fill_value=False))]
BRUSH_ROUNDED_4x4 = [pos for pos in BRUSH_4x4
                     if pos not in [(0, 0), (0, 3), (3, 0), (3, 3)]]

BRUSH_5x5 = [position for position, val in
             np.ndenumerate(np.full(shape=(5, 5), fill_value=False))]  # Hacky as frick tho, lmao
BRUSH_ROUNDED_5x5 = [pos for pos in BRUSH_5x5
                     if pos not in [(0, 0), (0, 1), (1, 0),
                                    (4, 0), (3, 0), (4, 1),
                                    (4, 4), (4, 3), (3, 4),
                                    (0, 4), (0, 3), (1, 4)]]
BRUSH_PLUS = [(0, 0,), (-1, 0), (0, -1), (1, 0), (0, 1)]


def _cellular_automata_smoothing(x, y, field,
                                 born=(5, 6, 7, 8),
                                 survive=(4, 5, 6, 7, 8)):
    # We're smoothing the room edges, not the passable tiles, so flip the logic values of input and output.
    cell_alive = not field[y, x]
    h, w = field.shape
    neighbors = [field[y + dy, x + dx]
                 for dx, dy in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
                 if 0 <= x + dx < w and 0 <= y + dy < h]

    # If this is an edge cell, just pad it and we'll trim the excess later.
    if len(neighbors) < 8:
        return x, y, False
    else:
        # Else if it's a live cell in the survive range, it's alive.
        if cell_alive:
            if sum([not n for n in neighbors]) in survive:
                return x, y, False

            # Otherwise it dies.
            else:
                return x, y, True

        # And if it's a dead cell in the born range, it's alive.
        else:
            if sum([not n for n in neighbors]) in born:
                return x, y, False
            # Otherwise it stays dead.
            else:
                return x, y, True


def _passability_field_to_walls(x, y, field):
    # We want to return True if a cell is False in Field and does not have 8 False neighbors
    cell_passable = field[y, x]

    if cell_passable:
        return x, y, False

    else:
        h, w = field.shape
        neighbors = [field[y + dy, x + dx]
                     for dx, dy in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
                     if 0 <= x + dx < w and 0 <= y + dy < h]

        if True in neighbors:
            return x, y, True

        else:
            return x, y, False



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


class VerySlightlyCenterMindedArtist(CenterMindedArtist):
    def __init__(self, x0, y0, field, brush):
        super().__init__(x0, y0, field, brush,
                         same_path_prob=.25,
                         center_weight=.75,
                         not_center_weight=.60)


class SlightlyCenterMindedArtist(CenterMindedArtist):
    def __init__(self, x0, y0, field, brush):
        super().__init__(x0, y0, field, brush,
                         same_path_prob=.25,
                         center_weight=.85,
                         not_center_weight=.40)


class CentroidMindedArtist(DrunkArtist):
    def __init__(self, x0: int, y0: int,
                 cx: int, cy: int,
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
        self.centroid = (cx, cy)

    def tick(self):
        want_to_stick_with_path = rand.random() <= self.same_path_prob
        has_moved_at_least_once = self.last_move is not None
        last_path_still_valid = self.last_move in self.move_options

        if want_to_stick_with_path and has_moved_at_least_once and last_path_still_valid:
            direction = self.last_move
        else:
            # Move in a direction randomly chosen with preferential weight given to moving toward the center
            center_x, center_y = self.centroid

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


def _roll_centroid(width, height):
    x_max, y_max = width - 1, height - 1
    return (rand.randint(0, x_max),
            rand.randint(0, y_max))


def _centroid_avg_dist(x, y, centroids):
    distances = [norm(np.array((xi, yi)) - np.array((x, y)))
                 for xi, yi in centroids
                 if xi != x and yi != y]
    return np.average(distances)


class WholeDrunkMapGen:
    def __init__(self,
                 width: int,
                 height: int,
                 num_centers: int,
                 passability_tgt: float,
                 wanderer_born_prob: float,
                 wanderer_die_prob: float,
                 centroidal_born_prob: float,
                 centroidal_die_prob: float):
        # Roll five times as many candidate centroids as we'll actually need
        center_candidates = [_roll_centroid(width, height) for i in range(0, 5 * num_centers)]

        pool = mp.Pool(mp.cpu_count())
        avg_dists = pool.starmap(func=_centroid_avg_dist,
                                 iterable=[(x, y, center_candidates)
                                           for x, y in center_candidates])
        pool.close()

        candidates_and_avg_dists = [(center_candidates[i], dist)
                                    for i, dist in enumerate(avg_dists)]

        # Since these are centers, let's filter for those
        min_x, max_x = floor(.10 * width), floor(.90 * width)
        min_y, max_y = floor(.10 * height), floor(.90 * height)

        # Sort the list descending by average distance to other centroids
        candidates_and_avg_dists.sort(key=lambda row: row[1],
                                      reverse=True)

        # Select the first num_centers points from the sorted list,
        # filtering by being within the inner 80% of the map on either axis.
        # We'll occasionally spawn artists who want to go toward and work around those points.
        centroids = [candidate
                     for candidate, dist
                     in candidates_and_avg_dists
                     if min_x <= candidate[0] <= max_x
                     and min_y <= candidate[1] <= max_y][0:num_centers]

        # Field of passability
        field = np.full(shape=(height, width),
                        fill_value=False)

        # Pick a centroid to spawn one wanderer and also a centroidal for the same point

        # _x0, _y0 = rand.choice(centroids)
        _x0, _y0 = round(field.shape[1] / 2), round(field.shape[0] / 2)
        wanderer = CenterMindedArtist(x0=_x0, y0=_y0,
                                      brush=BRUSH_ROUNDED_5x5,
                                      field=field,
                                      same_path_prob=.25,
                                      center_weight=.65,
                                      not_center_weight=.25)
        centroidal = CentroidMindedArtist(x0=_x0, y0=_y0,
                                          cx=_x0, cy=_y0,
                                          brush=BRUSH_ROUNDED_4x4,
                                          field=field)
        wanderers = [wanderer]
        centroidals = [centroidal]

        # Tick the artists until we hit the tick limit or meet our passability target
        tick_no = 0
        max_ticks = 2500
        while tick_no < max_ticks and np.count_nonzero(field) / field.size < passability_tgt:
            for w in wanderers:
                w.tick()

                # Maybe birth a new wanderer
                if rand.random() <= wanderer_born_prob:
                    wanderers.append(DrunkArtist(x0=w.x, y0=w.y,
                                                 brush=BRUSH_ROUNDED_5x5,
                                                 field=field))

                # Maybe birth a new centroidal
                if rand.random() <= centroidal_born_prob:
                    c = rand.choice(centroids)
                    centroidals.append(CentroidMindedArtist(x0=w.x, y0=w.y,
                                                            cx=c[0], cy=c[1],
                                                            brush=BRUSH_ROUNDED_4x4,
                                                            field=field))

                # Maybe die, if there's more than one wanderer around.
                if len(wanderers) > 1 and rand.random() <= wanderer_die_prob:
                    wanderers.remove(w)

            for c in centroidals:
                c.tick()

                # Maybe die, if there's more than one centroidal around.
                if len(centroidals) > 1 and rand.random() <= centroidal_die_prob:
                    centroidals.remove(c)

            tick_no += 1

        # Apply cellular-automatic smoothing
        pool = mp.Pool(mp.cpu_count())
        smoothed_cells = pool.starmap(func=_cellular_automata_smoothing,
                                      iterable=[(pos[1], pos[0], field)
                                                for pos, value in np.ndenumerate(field)
                                                if 1 <= pos[0] < field.shape[1] - 1
                                                and 1 <= pos[1] < field.shape[0] - 1])
        pool.close()

        for x, y, truth in smoothed_cells:
            field[y, x] = truth

        # Another round, if we please
        pool = mp.Pool(mp.cpu_count())
        smoothed_cells = pool.starmap(func=_cellular_automata_smoothing,
                                      iterable=[(pos[1], pos[0], field)
                                                for pos, value in np.ndenumerate(field)
                                                if 1 <= pos[0] < field.shape[1] - 1
                                                and 1 <= pos[1] < field.shape[0] - 1])

        pool.close()

        for x, y, truth in smoothed_cells:
            field[y, x] = truth

        walls = np.full(shape=field.shape,
                        fill_value=False)
        pool = mp.Pool(mp.cpu_count())
        wall_cells = pool.starmap(func=_passability_field_to_walls,
                                  iterable=[(pos[1], pos[0], field)
                                            for pos, val in np.ndenumerate(field)])
        pool.close()

        for x, y, truth in wall_cells:
            walls[y,x] = truth

        self.walls = walls
        self.field = field

        for row in walls:
            char_row = ["#" if truth else " "
                        for truth in row]
            print("".join(char_row))
# if __name__ == "__main__":
#     mp.freeze_support()
#     mapgen = WholeDrunkMapGen(width=80, height=60,
#                               num_centers=12,
#                               passability_tgt=0.25,
#                               wanderer_born_prob=0,
#                               wanderer_die_prob=0,
#                               centroidal_born_prob=0.10,
#                               centroidal_die_prob=0.0125)
