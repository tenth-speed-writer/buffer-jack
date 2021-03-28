from src.map_generation.cellulose import Cellulose
from typing import List, Tuple, Dict
from math import floor, sqrt
from random import choice
import numpy as np
import multiprocessing as mp


def _euclidean_dist_from_origin(origin: Tuple[int, int],
                                dest: Tuple[int, int]) -> Tuple[Tuple[int, int], float]:
    x0, y0 = origin
    x1, y1 = dest

    dx = x1 - x0
    dy = y1 - y0

    return origin, sqrt(dx ** 2 + dy ** 2)


def _manhattan_dist_from_origin(origin: Tuple[int, int],
                                dest: Tuple[int, int]) -> Tuple[Tuple[int, int], int]:
    return origin, abs(dest[0] - origin[0]) + abs(dest[1] - origin[1])


def _closest_point_to(x_pt: int, y_pt: int, field: np.ndarray) -> Tuple[int, int]:
    field_height, field_width = field.shape
    pts = []

    # Pts is an argument list for parallelized operation _euclidean_dist_from_origin,
    # which includes pt as the origin and all x, y combos in the same block which
    # aren't outside the range of the map.
    for x in [x for x in range(x_pt - 3, x_pt + 4)
              if 0 <= x <= field_width]:
        for y in [y for y in range(y_pt - 3, y_pt + 4)
                  if 0 <= y <= field_width]:
            pts.append(((x_pt, y_pt),
                        (x, y)))

    # Spin up a pool and calculate the euclidean distance from
    # each point in the cell to the specified edge point.
    pool = mp.Pool(mp.cpu_count())
    points_and_dists = pool.starmap(func=_manhattan_dist_from_origin,
                                    iterable=pts)
    pool.close()

    # Calculate the distances and return the corresponding point.
    # If two points tie, the nature of sequence.index means that
    # it'll be left/top biased since it pulls the first match.
    distances = [dist for point, dist in points_and_dists]
    shortest_distance = min(distances)
    closest_index = distances.index(shortest_distance)
    closest_point = [point for point, dist in points_and_dists][closest_index]

    return closest_point


def find_door_pt(field: np.ndarray,
                 mid_pt: int,
                 side: str) -> Tuple[int, int]:
    """
    Determines based on a bool passability matrix and a specified side where to assign a door_point.

    :param field: A boolean passability matrix representing a RoomCellophane's .field
    :param mid_pt: Where, on the relevant axis, to treat as the center for purposes of deciding where to draw the door.
    :param side: One of: 'top', 'middle', 'left', 'bottom'.

    :return: An (x, y) tuple; a tile on this room's cellophane to declare as a door point for the specified side.
    """
    assert (side in ('top', 'left', 'bottom', 'right'))
    field_height, field_width = field.shape

    if side == 'top':
        # Pick a column, and scan down from y=0 until we find a cell just before a passable one.
        col_range = [val for val in range(-2, 3)
                     if 0 <= val + mid_pt < field_width]
        door_x = mid_pt + choice(col_range)

        # Get the first index from the top in which this column is true
        first_empty_y = np.where(field[:, door_x] is True)[0]

        # The y for the door will be 1 tile before that.
        door_y = first_empty_y - 1 if 0 < first_empty_y else 0
        return door_x, door_y

    elif side == 'left':
        # Pick a row, and scan right from x=0 until we find a cell just before a passable one.
        row_range = [val for val in range(-2, 3)
                     if 0 <= val + mid_pt <= field_height]
        door_y = mid_pt + choice(row_range)

        # Get the first index from the left in which this row is true
        first_empty_x = np.where(field[door_y, :] is True)[0]

        # The x for the door will be 1 tile before that.
        door_x = first_empty_x - 1 if 0 < first_empty_x else 0
        return door_x, door_y

    elif side == 'right':
        # Pick a row, and scan left from -1 until we find a passable cell.
        row_range = [val for val in range(-2, 3)
                     if val + mid_pt < field_height]
        door_y = mid_pt + choice(row_range)

        last_empty_x = np.where(field[door_y, :] is True)[-1]

        door_x = last_empty_x + 1 if last_empty_x < field_width - 1 else field_width - 1
        return door_x, door_y

    elif side == 'bottom':
        # Pick a column, and scan up from -1 until we find a passable cell.
        col_range = [val for val in range(-2, 3)
                     if val + mid_pt < field_width]
        door_x = mid_pt + choice(col_range)

        last_empty_y = np.where(field[:, door_x] is True)[-1]

        door_y = last_empty_y + 1 if last_empty_y < field_height - 1 else field_height - 1
        return door_x, door_y

    else:
        raise ValueError("No side specified.")


class RoomCellulose(Cellulose):
    def __init__(self,
                 grid_x0: int,
                 grid_y0: int,
                 grid_width: int,
                 grid_height: int,
                 generator):
        """

        :param grid_width: Room arrangement grid width
        :param grid_height: Room arrangement grid height
        :param generator: The MapGenerator or subclass which intends to use this cello. Must have a .grid.
        """
        super().__init__(width=15 * grid_width,
                         height=15 * grid_height)

        self.grid_position = (grid_x0,
                              grid_y0)
        self.grid_shape = (grid_width,
                           grid_height)

        self.generator = generator
        self.grid: np.ndarray = generator.grid

        # Append this RoomCellulose's UUID to all grid cells it occupies
        self.grid[grid_y0:grid_y0 + grid_height,
        grid_x0:grid_x0 + grid_width] = self.uuid
        # Append this RoomCellulose itself to the generator's list of rooms
        self.generator.rooms.append(self)

    @property
    def door_points(self) -> List[Dict]:
        def neighbors_of(position):
            x_, y_ = position
            return [
                (x_-1, y_-1),
                (x_, y_-1),
                (x_+1, y_-1),
                (x_-1, y_),
                (x_+1, y_),
                (x_-1, y_+1),
                (x_, y_+1),
                (x_+1, y_+1)
            ]

        # Specify all points which are 1 orthogonal step away from grid cells
        # covered by this room and which aren't also part of this room or outside
        # the range of indices of the map generation grid
        x0, y0 = self.grid_position                        # Where this room's top left square sits on the grid
        grid_width, grid_height = self.grid_shape          # The shape of the space this room takes up on the grid
        map_grid_height, map_grid_width = self.grid.shape  # The shape of the entire map grid

        # Identify which cells already belong to this room
        own_cells = []
        for y in range(y0, y0 + grid_height):
            for x in range(x0, x0 + grid_width):
                own_cells.append((x, y))

        doors: List[Dict] = []
        for c in own_cells:
            neighbors = [n for n in neighbors_of(c)
                         if n not in own_cells                   # If it's not one of this room's cells
                         and (0 <= n[0] < map_grid_width         # And if it's in range on the map generator's grid
                              and 0 <= n[1] < map_grid_height)]

            for n in neighbors:
                cell_x, cell_y = c
                neighbor_x, neighbor_y = n

                # If it's a top-side neighbor
                if neighbor_y < cell_y:
                    grid_diff = cell_x - x0
                    mid_pt = 7 + (15 * grid_diff)
                    doors.append({
                        "origin": c,
                        "destination": n,
                        "door_pt": find_door_pt(self.field,
                                                mid_pt=mid_pt,
                                                side="top")
                    })

                # If it's a bottom-side neighbor
                elif neighbor_y > cell_y:
                    grid_diff = cell_x - x0
                    mid_pt = 7 + (15 * grid_diff)
                    doors.append({
                        "origin": c,
                        "destination": n,
                        "door_pt": find_door_pt(self.field,
                                                mid_pt=mid_pt,
                                                side="bottom")
                    })

                # If it's a left-side neighbor
                elif neighbor_x < cell_x:
                    grid_diff = cell_y - y0
                    mid_pt = 7 + (15 * grid_diff)
                    doors.append({
                        "origin": c,
                        "destination": n,
                        "door_pt": find_door_pt(self.field,
                                                mid_pt=mid_pt,
                                                side="left")
                    })

                # If it's a right-side cell
                elif neighbor_x > cell_x:
                    grid_diff = cell_y - y0
                    mid_pt = 7 + (15 * grid_diff)
                    doors.append({
                        "origin": c,
                        "destination": n,
                        "door_pt": find_door_pt(self.field,
                                                mid_pt=mid_pt,
                                                side="right")
                    })

                # If the logic above somehow doesn't catch it
                else:
                    raise ValueError("Couldn't match a side to neighbors {} and {}"
                                     .format(str(c), str(n)))

        return doors

    # @property
    # def door_points(self) -> List[Tuple[Tuple[int, int],
    #                                     Tuple[int, int],
    #                                     Tuple[int, int]]]:
    #     """
    #     Returns a list of paired grid and tile positions which describe the door positions open to adjacent grid cells.
    #     The order of tuples returned is the grid position of the cell with the door, the grid position of the cell
    #     to which that door connects, and the field position of the door_pt relative to this cellulose.
    #     :return: A list of thruples in the format [(grid_dx, grid_dy),
    #                                                (grid_dx_joined, grid_dy_joined),
    #                                                (cellophane_dx, cellophane_dy)]
    #     """
    #     grid_width, grid_height = (floor(self.width / 15),
    #                                floor(self.height / 15))
    #     grid_x_indices = range(0, grid_width)
    #     grid_y_indices = range(0, grid_height)
    #
    #     # Own grid position, neighbor grid position, door point position on the cellulose.
    #     doors: List[Tuple[Tuple[int, int],
    #                       Tuple[int, int],
    #                       Tuple[int, int]]] = []
    #
    #     for grid_y in grid_x_indices:
    #         for grid_x in grid_y_indices:
    #             own_grid_pos = (grid_x, grid_y)
    #             cell_has_left_neighbor = grid_x > 0
    #             cell_has_right_neighbor = grid_x < grid_x_indices[-1]
    #             cell_has_top_neighbor = grid_y > 0
    #             cell_has_bottom_neighbor = grid_y < grid_y_indices[-1]
    #
    #             print("Checking for neighbors")
    #
    #             # In all cases, the center of the dimension which isn't at the edge
    #             # is located at 7 + 15 * grid_y tiles along the corresponding axis.
    #             if cell_has_top_neighbor:
    #                 print("Has top neighbor")
    #                 g_x, g_y = grid_x, grid_y - 1
    #                 neighbor_pos = (g_x, g_y)
    #                 if not self.grid[g_y, g_x] == self:
    #                     # Calculate midpoint and append position, neighbor position, and door_pt to doors
    #                     c_x, c_y = 7 + 15 * grid_x, 0
    #                     doors.append((own_grid_pos,
    #                                   neighbor_pos,
    #                                   find_door_pt(field=self.field,
    #                                                mid_pt=c_x,
    #                                                side="top")))
    #
    #             if cell_has_bottom_neighbor:
    #                 print("Has bottom neighbor")
    #                 g_x, g_y = grid_x, grid_y + 1
    #                 neighbor_pos = (g_x, g_y)
    #                 if not self.grid[g_y, g_x] == self:
    #                     # Calculate midpoint and append position, neighbor position, and door_pt to doors
    #                     c_x, c_y = 7 + 15 * grid_x, self.height - 1
    #                     doors.append((own_grid_pos,
    #                                   neighbor_pos,
    #                                   find_door_pt(field=self.field,
    #                                                mid_pt=c_x,
    #                                                side="bottom")))
    #
    #             if cell_has_left_neighbor:
    #                 print("Has left neighbor")
    #                 g_x, g_y = grid_x - 1, grid_y
    #                 neighbor_pos = (g_x, g_y)
    #                 if not self.grid[g_y, g_x] == self:
    #                     c_x, c_y = 0, 7 + 15 * grid_y
    #                     doors.append((own_grid_pos,
    #                                   neighbor_pos,
    #                                   find_door_pt(field=self.field,
    #                                                mid_pt=c_y,
    #                                                side="left")))
    #
    #             if cell_has_right_neighbor:
    #                 print("Has right neighbor")
    #                 g_x, g_y = grid_x + 1, grid_y
    #                 neighbor_pos = (g_x, g_y)
    #                 if not self.grid[g_y, g_x] == self:
    #                     c_x, c_y = self.width - 1, 7 + 15 * grid_y
    #                     doors.append((own_grid_pos,
    #                                   neighbor_pos,
    #                                   find_door_pt(field=self.field,
    #                                                mid_pt=c_y,
    #                                                side="right")))
    #
    #     return doors

# if __name__ == '__main__':
#     mp.freeze_support()
#
#     foo = RoomCellulose(2, 2)
#     print(foo.door_points)
