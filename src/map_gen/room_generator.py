from typing import Optional, Tuple, List, Callable
from src.entity.entity_ import Entity
from src.entity.entities import Static
from src.sigil import Sigil
import numpy as np

# An entity (such as a wall), and an x and y position to render it, in the format (x, y, ent)
RenderableEntity = Tuple[int, int, Entity]


def make_wall():
    return Static(size=9,
                  sigil=Sigil("#",
                              priority=3,
                              color=(220, 220, 255)),
                  name="Boundary",
                  passable=False)


class RoomGenerator:
    def initial_map(self) -> np.ndarray:
        """By default, initialize with a solid block of Trues.
        Override to add different default initial seeds."""
        shape = (self._height, self._width)
        return np.full(shape,
                       fill_value=True)

    def __init__(self,
                 map_width: int,
                 map_height: int,
                 initial: Optional[np.ndarray] = None):
        """
        Initializer for a base MapGenerator class.

        The goal of a class like this is, when its generate() method is called,
        to render a boolean array with True representing a wall in the environment.
        :param map_width: Integer, in tiles.
        :param map_height: Integer, in tiles.
        :param initial: An optional map_height x map_width numpy array with initial values for generation
        """
        self._width = map_width
        self._height = map_height

        self.bool_map: Optional[np.ndarray] = None

        if initial is not None:
            # If an initial array is provided, assert its shape and use that.
            if initial.shape == self.shape:
                self._initial = initial

            else:
                # Throw a ValueError if the dimensions don't match.
                err_msg = "If an initial map is provided, it must be a 2D array of the specified width and height."
                raise ValueError(err_msg)

        else:
            # Otherwise, create one from overridable method self.initial_map()
            self._initial = self.initial_map()

    # Dimensions are gettable but should be immutable after instantiation.
    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def shape(self) -> Tuple[int, int]:
        return self._height, self._width

    @staticmethod
    def _bool_array_to_ents(arr: np.ndarray,
                            x0: int = 0,
                            y0: int = 0,
                            wall_func: Callable = make_wall) -> List[RenderableEntity]:
        """
        Converts a 2D numpy array of boolean values to a list of entities generated
        by wall_func, each paired with its x and y positions from the input array.

        Optionally offsets the entities' positions by a specified x0 and y0.

        :param arr: A numpy array of 2 dimensions, containing boolean values. Trues will be made into walls.
        :param x0: An optional offset x, in tiles. (x0, y0) together are the top-left corner of the offset space.
        :param y0: An optional offset y, in tiles. (x0, y0) together are the top-left corner of the offset space.
        :param wall_func: A function which returns a wall or other barrier-forming entity.
        :return: A list of tuples, each in the format (x, y, entity)
        """
        if len(arr.shape) != 2:
            raise ValueError("The boolean array to convert must have exactly two dimensions, got {}"
                             .format(str(arr.shape)))
        height, width = arr.shape

        ents: List[Tuple[int, int, Entity]] = []

        # Iterate through y, x combinations
        for y in range(0, height):
            for x in range(0, width):
                # For every cell that's True, add a new wall for that position using the provided function.
                if arr[y, x]:
                    ent = wall_func()
                    ent_x = x + x0
                    ent_y = y + y0
                    ents.append((ent_x, ent_y, ent))

        return ents

    def generate(self) -> np.ndarray:
        """Run this MapGenerator's actual map generation logic. Highly overridable,
        since this base method just renders and returns the map's initial state.

        :return: An ndarray of bools indicating where to draw walls.
        """
        return self._initial

    def _generate_if_necessary(self):
        """A utility method called when something needs to access this generator's map but it hasn't been generated."""
        if self.bool_map is None:
            self.bool_map = self.generate()

    def as_string_rows(self,
                       wall_char: str = "#",
                       floor_char: str = " ") -> List[str]:
        """Runs this MapGenerator's .generate() if it hasn't been run yet, then prints it as wall chars or spaces.

        Used mostly for debugging, parameter tweaking, and other developer nonsense."""
        # Just in case we didn't .generate() this map already.
        self._generate_if_necessary()

        # Define a return variable before iteration
        row_strings: List[str] = []

        # Iterate over the bool_map's rows, converting them to strings.
        for row in self.bool_map:
            def pick_character(val: bool):
                """It's a wall if it's true, otherwise it's a floor."""
                if val:
                    return wall_char
                else:
                    return floor_char

            # Cast the row to a list of characters
            char_list = [pick_character(val) for val in row]

            # Join the characters into a single string
            row_string = "".join(char_list)

            # Append it to the return variable
            row_strings.append(row_string)

        return row_strings

    def as_entities(self) -> List[RenderableEntity]:
        """Runs this MapGenerator's .generate() if it hasn't been run yet, then returns it as a list of (x, y, ent)."""
        # Just in case we didn't .generate() this map already.
        self._generate_if_necessary()
        return self._bool_array_to_ents(arr=self.bool_map)
