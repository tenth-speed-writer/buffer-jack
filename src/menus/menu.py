from tcod.console import Console
from typing import Iterable, Optional, Callable, List, Tuple
from copy import deepcopy


class MenuOption:
    """Represents a single row in a menu. Is able to render itself as a list of strings."""
    @staticmethod
    def _text_dimensions(text: str) -> [int, int]:
        """Returns the minimum width and height to show a \n-delineated block of text without word wrapping."""
        lines: List[str] = str.split("\n")

        height = len(lines)
        width = max([len(l) for l in lines])

        return width, height

    @classmethod
    def _does_text_fit(cls, text: str, width: int, height: int,
                       pad_horizontal: Optional[int] = 1,
                       pad_vertical: Optional[int] = 1) -> bool:
        """Checks whether text fits into a specified block of width by height."""
        min_h, min_w = cls._text_dimensions(text)

        # Padding is applied to both sides equally
        fits_height = width >= min_h + 2 * pad_horizontal
        fits_width = height >= min_w + 2 * pad_vertical

        return fits_height and fits_width

    def __init__(self, text: str,
                 width: int, height: int,
                 on_select: Callable,
                 subtext: Optional[str] = None,
                 pad_horizontal: int = 1,
                 pad_vertical: int = 1,
                 has_border: bool = True,
                 color: Tuple[int, int, int] = (240, 240, 240)):
        """
        Initializes a menu_option with specified parameters. Override and call
        via super().__init__() to make default values for custom subclasses.

        :param text The primary text to display in this menu item--can contain newline chars, so long as it fits.
        :param width Width of the menu row, in tiles.
        :param height Height of the menu row, in tiles.
        :param on_select A function to call when this menu option is selected.
        :param subtext A string describing this menu option. Explains to the player what this menu option does."""

        # Assert requirements for the class parameters
        if pad_vertical < 0 or pad_horizontal < 0:
            raise ValueError("Padding values must be >= 0")

        if has_border and not (pad_vertical and pad_horizontal):
            raise ValueError("has_border must be False if either _pad value is 0")

        if not self._does_text_fit(text=text,
                                   width=width,
                                   height=height,
                                   pad_horizontal=pad_horizontal,
                                   pad_vertical=pad_vertical):
            raise ValueError("Provided text does not fit in the available area!")

        self._text = text
        self._width = width
        self._height = height
        self._subtext = subtext
        self._on_select = on_select
        self._pad_horizontal = pad_horizontal
        self._pad_vertical = pad_vertical
        self._has_border = has_border

        self._color = color

    @property
    def text(self):
        """Returns the primary text for this menu option."""
        return self._text

    @property
    def rows(self) -> List[List[Tuple[str, Tuple[int, int, int]]]]:
        """Renders this menu option as a list of lists of (char, color_tuple), including margins/border/padding"""
        def char_to_tuple(char: str):
            return char, self._color

        def line_to_tuples(line: str):
            return [char_to_tuple(c) for c in line]

        def pad_string(line: str):
            """Center-align a specified string based on own non-padded width."""
            text_width = self._width - 2*self._pad_horizontal
            new_line = deepcopy(line)

            # Pad it left or right based on evens/odds.
            # Stagger the count by 1 so the modulus trick doesn't throw a div-by-zero error
            for j in range(1, text_width + 1):
                if j % 2:
                    new_line = " " + new_line
                else:
                    new_line = new_line + " "

            return new_line

        # Get text, split it, and cast it to character lists. Also pad width.
        str_lines = [pad_string(s) for s in self._text.split("\n")]
        lines = [list(l) for l in str_lines]

        # Pad empty string rows to top and bottom to match height.
        # Iterator is offset by 1 to avoid div-by-0 error in the modulus
        height_diff = self._height - len(lines)
        for i in range(1, height_diff + 1):
            new_row = [" " for char in lines[0]]
            if i % 2:
                lines = lines + new_row
            else:
                lines = new_row + lines

        # Apply margins and border, if appropriate
        if self._pad_vertical:
            for i in range(0, self._pad_vertical + 1):
                # Pad top and bottom by one full row per pad_vertical
                blank_row = [" " for i in range(0, self._width + 2*self._pad_horizontal)]
                lines = blank_row + lines + blank_row

        if self._pad_horizontal:
            for i in range(0, len(lines)):
                # Pad left and right once each per pad_horizontal
                lines[i] = " " + lines[i] + " "

        if self._has_border:
            # If this MenuOption has a border, construct and write that into the edge characters.
            # This should, as per value testing, only run if there's padding to safely write in.
            new_top = ["─" for i in lines[0]]
            new_top[0] = "┌"
            new_top[-1] = "┐"

            new_bottom = ["─" for i in lines[0]]
            new_bottom[0] = "└"
            new_bottom[-1] = "┘"

            # First, apply horizontal borders to each line
            for i in range(0, len(lines)):
                lines[i][0] = "│"
                lines[i][-1] = "│"

            # Then append the top and bottom borders
            lines = new_top + lines + new_bottom
        return [line_to_tuples(l) for l in lines]

    @property
    def size(self) -> Tuple[int, int]:
        """Returns the dimensions of the MenuOption as (width, height)"""
        return self._width, self._height

    @text.setter
    def text(self, text: str) -> None:
        """Set the primary text of this menu option."""
        fits: bool = self._does_text_fit(text,
                                         width=self._width,
                                         height=self._height,
                                         pad_horizontal=self._pad_horizontal,
                                         pad_vertical=self._pad_vertical)
        if fits:
            self._text = text
        else:
            raise ValueError("Assigned text does not fit in the dimensions of this MenuOption")

    @property
    def vertical_padding(self) -> int:
        """Return the current padding applied to the top and bottom of the MenuOption."""
        return self._pad_vertical

    @vertical_padding.setter
    def vertical_padding(self, new_value: int) -> None:
        """Assigns a new _pad_vertical value, if it's a valid vertical padding amount."""
        if new_value < 0:
            raise ValueError("New vertical padding size must be no less than zero, given {}".format(str(new_value)))
        elif new_value == 0 and self._has_border:
            raise ValueError("Cannot set vertical padding to 0 when .has_border = True!")
        else:
            self._pad_vertical = new_value

    @property
    def horizontal_padding(self) -> int:
        """Return the current padding applied to the left and right of the MenuOption."""
        return self._pad_horizontal

    @horizontal_padding.setter
    def horizontal_padding(self, new_value: int) -> None:
        """Assigns a new _pad_horizontal value, if it's a valid horizontal padding amount."""
        if new_value < 0:
            raise ValueError("New horizontal padding size must be no less than zero, given {}".format(str(new_value)))
        elif new_value == 0 and self._has_border:
            raise ValueError("Cannot set horizontal padding to 0 when .has_border = True!")
        else:
            self._pad_horizontal = new_value

    @property
    def color(self):
        return self._color


class Menu:
    def __init__(self,
                 max_width: int, max_height: int,
                 pad_top: int = 2, pad_right: int = 2,
                 pad_bottom: int = 2, pad_left: int = 2,
                 options: Optional[Iterable[MenuOption]] = None):
        pass

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, opts: Iterable[MenuOption]):
        self._options = [o for o in opts]

    def open_menu(self, x: int, y: int, console: Console):
        is_open = True
        while is_open:
            # Run a movement handler here
            pass