import numpy as np
import multiprocessing as mp

from copy import deepcopy
from random import choices, random
from typing import List, Optional, Type, Tuple
from src.map_generation.cellulose import RoomCellulose
from src.map_generation.cellulose.hallway import HallwayCellulose


def _determine_wall(x0, y0, field: np.ndarray) -> Tuple[int, int, bool]:
    """Parallelizable function to determine a wall array given a passable array.

    Returns (x0, y0, True) for impassable tiles which border passable tiles, and (x0, y0, False) otherwise."""
    own_passability = field[y0, x0]

    # If this tile is already passable, it definitely shouldn't be a wall.
    if own_passability:
        return x0, y0, False

    # If it's not, then it's only a wall if it touches a cell that IS passable.
    else:
        # Get truth values of adjacent cells
        height, width = field.shape

        # Trim our selection range to the boundaries of the field's indices
        neighbor_indices = [(x, y) for x, y in [(x0-1, y0-1), (x0-1, y0), (x0-1, y0+1),
                                                (x0, y0-1), (x0, y0+1),
                                                (x0+1, y0-1), (x0+1, y0), (x0+1, y0+1)]
                            if 0 <= x < width and 0 <= y < height]

        neighbor_truths = [field[y, x] for x, y in neighbor_indices]

        # If any of the neighbors are passable, and this cell isn't, then this cell is a Genuine Wall :)
        if sum(neighbor_truths) > 0:
            return x0, y0, True

        # If not, trim it so as not to waste memory on static entities that'll never be seen.
        else:
            return x0, y0, False


class MapGenerator:
    def __init__(self,
                 grid_width: int, grid_height: int,
                 candidates: List[Type[RoomCellulose]],
                 candidate_weights: List[float],
                 max_grid_openness: float):
        if not len(candidates) == len(candidate_weights):
            raise ValueError("Lengths of candidates and candidate_weights must match!")
        self.shape = (grid_width, grid_height)

        self.candidates = candidates
        self.candidate_weights = candidate_weights

        # A grid of the UUID strings of its subordinate RoomCellophanes
        self.grid = np.full(shape=(grid_height, grid_width),
                            fill_value="",
                            dtype=np.dtype('U36'))  # IIRC the standard for UUID4 is 32 hex digits and 4 dashes

        # The generator will run until at least a certain ratio of the grid is not empty.
        self.max_grid_openness = max_grid_openness

        self.rooms: List[RoomCellulose] = []
        self.halls: List[HallwayCellulose] = []
        self.linked_cells: List[Tuple[Tuple[int, int], Tuple[int, int]]] = []

    def _room_by_uuid_str(self, uuid: str) -> RoomCellulose:
        # A list that -should- only have one element.
        rooms = [r for r in self.rooms if r.uuid == uuid]

        if len(rooms) > 1:
            raise Exception("Tried to get room by uuid, but more than one was returned!")
        return rooms[0]

    def room_in_grid_cell(self, x: int, y: int) -> Optional[RoomCellulose]:
        """Returns which room a specified grid cell is part of, or None."""
        if not (0 <= x < self.shape[1]) and (0 <= y <= self.shape[0]):
            raise ValueError("x and y must constitute a valid grid location; got {}, {}"
                             .format(str(x), str(y)))
        content_id = self.grid[y, x]
        if content_id == "":
            return None
        else:
            return self._room_by_uuid_str(content_id)

    def generate_room(self, x0, y0):
        if not (0 <= x0 < self.shape[0]) and (0 <= y0 < self.shape[1]):
            raise ValueError("x0 and y0 must be valid grid cells. Got {}, {}"
                             .format(str(x0), str(y0)))

        if self.room_in_grid_cell(x0, y0):
            raise Exception("Cannot generate a room in cell {}, {} as another room is already there."
                            .format(str(x0), str(y0)))

        # Try a number of times to roll a room that fits this spot
        try_counter = 0
        try_limit = 10
        chosen_cello: Optional[Type[RoomCellulose]] = None
        grid_width, grid_height = self.shape
        while try_counter < try_limit and chosen_cello is None:
            room = choices(population=self.candidates,
                           weights=self.candidate_weights,
                           k=1)[0]
            cel_width, cel_height = room.grid_shape
            if x0 + cel_width < grid_width and y0 + cel_height < grid_height:
                chosen_cello = room

            try_counter += 1

        cel = chosen_cello(grid_x=x0,
                           grid_y=y0,
                           generator=self)

        return cel

    def link_door_pts(self, grid_origin, grid_destination):
        x_0, y_0 = grid_origin
        x_i, y_i = grid_destination
        if (x_i - x_0 not in (-1, 0, 1)) or (y_i - y_0 not in (-1, 0, 1)):
            raise ValueError("grid_origin and grid_destination must be neighbors. Got {} and {}."
                             .format(str(grid_origin), str(grid_destination)))

        # Calculate door points for both the origin and destination grid cells
        origin_doors = self.room_in_grid_cell(x_0, y_0).door_points
        dest_doors = self.room_in_grid_cell(x_i, y_i).door_points

        # Extract the specific door points which connect to one another here
        origin_door = [d for d in origin_doors if d["destination"] == (x_i, y_i)][0]
        dest_door = [d for d in dest_doors if d["destination"] == (x_0, y_0)][0]

        # Calculate the map-wide tile positions of the two door cells
        origin_room = self.room_in_grid_cell(origin_door["origin"][0],
                                             origin_door["origin"][1])
        origin_grid_x0, origin_grid_y0 = origin_room.grid_position
        origin_door_x0, origin_door_y0 = origin_door["door_pt"]

        # Tiles-per-grid-cell being 15
        origin_pt = (origin_door_x0 + 15*origin_grid_x0,
                     origin_door_y0 + 15*origin_grid_y0)

        dest_room = self.room_in_grid_cell(dest_door["origin"][0],
                                           dest_door["origin"][1])
        dest_grid_x0, dest_grid_y0 = dest_room.grid_position
        dest_door_x0, dest_door_y0 = dest_door["door_pt"]

        dest_pt = (dest_door_x0 + 15*dest_grid_x0,
                   dest_door_y0 + 15*dest_grid_y0)

        # Generate the hallway cellulose and append it to the class-level lists
        hall = HallwayCellulose(origin=origin_pt,
                                destination=dest_pt)
        self.halls.append(hall)
        self.linked_cells.append((grid_origin, grid_destination))
        self.linked_cells.append((grid_destination, grid_origin))

    def _grid_openness(self):
        """Returns the proportion [0, 1] of empty to total cells."""
        not_empty = [val for position, val in np.ndenumerate(self.grid) if val]
        return (self.grid.size - len(not_empty))/self.grid.size

    def _render(self) -> Tuple[np.ndarray, np.ndarray]:
        """Returns a tuple of two 2D numpy bool arrays (walls, passability).
        In the first, truth represents where to draw walls,
        and the second is a reference for valid thing spawn points."""
        grid_shape = self.grid.shape

        # 15 tiles per grid cell.
        field_shape = (15 * grid_shape[0],
                       15 * grid_shape[1])

        # Generate the map-wide, tile-scale passability array
        field = np.full(shape=field_shape,
                        fill_value=False)

        # Apply each room
        for r in self.rooms:
            # Calculate x0, y0 in tiles
            gx0, gy0 = r.grid_position
            field_x0, field_y0 = (15*gx0, 15*gy0)

            # Apply the room cel's contents to the field
            r.apply_to(field_x0, field_y0, tgt=field)

        # Apply each hallway
        for h in self.halls:
            # Hallways already consider their origins in terms of tiles.
            # They're essentially map-sized cels.
            h.apply_to(0, 0, field)

        # Create a walls array, separate from the passability array so that we have both and can trim this one.
        walls = deepcopy(field)
        for row in walls:
            char_row = ["#" if truth else " "
                        for truth in row]

        # In parallel, calculate which cells are entirely surrounded by impassable tiles and should NOT be walls.
        enumerated_cells = [(position[1], position[0], field) for position, truth in np.ndenumerate(field)]
        pool = mp.Pool(mp.cpu_count())
        wall_deltas = pool.starmap(func=_determine_wall,
                                   iterable=enumerated_cells)
        pool.close()

        # Apply the calculated values to create a boolean map of where to draw walls
        for x, y, truth in wall_deltas:
            walls[y, x] = truth

        # Return the boolean truth arrays of walls and passability
        return walls, field

    def _generate(self):
        linked_rooms = []

        # First room has an even chance each for an x and y offset of one.
        first_x0 = round(random())
        first_y0 = round(random())
        first_room = self.generate_room(first_x0, first_y0)

        max_add_failures = 10
        add_failures = 0
        while self._grid_openness() > self.max_grid_openness and add_failures < max_add_failures:
            # Select a room that has unoccupied neighbor cells.
            # We'll define this as any room which has a door point connecting to cell in a list of empty grid cells.
            empty_grid_cells = [(position[1], position[0]) for position, value
                                in np.ndenumerate(self.grid)
                                if not value]

            def free_door_pts(r: RoomCellulose):
                return [d for d in r.door_points
                        if d["destination"] in empty_grid_cells]

            # Compile and flatten a list of available door points for each room
            origin_doors = sum([free_door_pts(r) for r in self.rooms if len(free_door_pts(r)) != 0], [])

            # TODO: This approach is simple and tends to make major rooms branch right/down. Make it better?
            def max_size_for_room_from_door(d):
                x_origin, y_origin = d["origin"]
                x_corner, y_corner = d["destination"]

            doors_and_max_sizes = []

            # Try some number of times to roll a room that fits that space
                # If we fail, increment add_failures
