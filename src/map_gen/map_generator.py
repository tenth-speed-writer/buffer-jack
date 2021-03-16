from typing import Optional, Tuple
import numpy as np


class MapGenerator:
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

        if initial:
            # If an initial array is provided, assert its shape and use that.
            if initial.shape == self._shape:
                self._initial = initial
            else:
                err_msg = "If an initial map is provided, it must be an ndarray of the specified width and height."
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

