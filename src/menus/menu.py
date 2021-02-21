from tcod.console import Console
from typing import Iterable, Optional, Callable, List, Tuple, Optional, MutableSequence, Deque
from copy import deepcopy
from collections import deque

# Custom type for an RGB color tuple
RGB = Tuple[int, int, int]


# Custom types for a 2D list of tuples, each with a character and a color to be rendered.
RenderableItem = Tuple[str, Tuple[int, int, int]]
RenderableArray = MutableSequence[MutableSequence[Tuple[str, Tuple[int, int, int]]]]


class MenuOption:
    """Represents a single row in a menu. Is able to render itself as a list of strings."""
    @staticmethod
    def _text_dimensions(text: str) -> [int, int]:
        """Returns the minimum width and height to show a \n-delineated block of text without word wrapping."""
        lines: List[str] = text.split("\n")

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
                 color: RGB = (240, 240, 240)):
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
    def rows(self) -> RenderableArray:
        """Renders this menu option as a list of lists of (char, color_tuple), including margins/border/padding"""
        def char_to_tuple(char: str):
            return char, self._color

        def line_to_tuples(line: str):
            return [char_to_tuple(c) for c in line]

        def pad_string(line: str):
            """Center-align a specified string based on own width."""
            text_width = len(line)
            tgt_width = self._width
            new_line = deepcopy(line)

            # Pad it left or right based on evens/odds.
            # Stagger the count by 1 so the modulus trick doesn't throw a div-by-zero error
            for j in range(1, tgt_width - text_width + 2):
                if j % 2:
                    new_line = " " + new_line
                else:
                    new_line = new_line + " "

            return new_line

        # Get text, split it, and cast it to character lists. Also pad width.
        str_lines: List[str] = [pad_string(s) for s in self._text.split("\n")]
        lines: List[List[str]] = [[char for char in l] for l in str_lines]

        # Pad empty string rows to top and bottom to match height.
        # Iterator is offset by 1 to avoid div-by-0 error in the modulus
        height_diff = self._height - len(lines)
        for i in range(1, height_diff + 1):
            new_row: List[str] = [" " for j in range(0, len(lines[0]))]
            if i % 2:
                lines = lines + [new_row]
            else:
                lines = [new_row] + lines
        print([len(l) for l in lines])
        print(lines)

        # TODO: Rewrite this padding business more sensibly

        # Apply margins and border, if appropriate
        if self._pad_vertical:
            for i in range(0, self._pad_vertical + 1):
                # Pad top and bottom by one full row per pad_vertical
                blank_row: List[str] = [" " for i in range(0, self._width + 2*self._pad_horizontal)]
                lines.insert(0, blank_row)
                lines.append(blank_row)
        #
        # if self._pad_horizontal:
        #     for i in range(0, len(lines)):
        #         # Pad left and right once each per pad_horizontal
        #         lines[i]: str = " " + str(lines[i])
        #         lines[i]: str = lines[i] + " "

        print(len(lines))
        if self._has_border:
            # If this MenuOption has a border, construct and write that into the edge characters.
            # This should, as per value testing, only run if there's padding to safely write in.
            new_top = ["─" for i in lines[0]]
            new_top[0] = "┌"
            new_top[-1] = "┐"

            new_bottom = ["─" for i in lines[0]]
            new_bottom[0] = "└"
            new_bottom[-1] = "┘"

            # Append the top and bottom borders
            lines = new_top + lines[1:len(lines):1] + new_bottom

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

    @property
    def horizontal_padding(self) -> int:
        """Return the current padding applied to the left and right of the MenuOption."""
        return self._pad_horizontal

    @property
    def color(self) -> RGB:
        """Returns the color property of this MenuItem, to be used as the foreground color when it is rendered."""
        return self._color

    @color.setter
    def color(self, new_rgb: RGB) -> None:
        """Sets the color of this MenuItem, assuming it's a tuple of 3 integers in range 0-255."""
        r, g, b = new_rgb
        for c in (r, g, b):
            if not 0 <= c <= 255:
                raise ValueError("RGB values must be in range 0-255. Got {}".format(str(new_rgb)))
        self._color = new_rgb

    @property
    def subtext(self) -> str:
        return self._subtext

    @subtext.setter
    def subtext(self, st: str):
        self._subtext = st


class Menu:
    """Base class for a menu. Subclass to add specific functionality or context/console/game awareness."""

    @staticmethod
    def _intersperse_list(seq, value):
        """Intersperses elements of seq with value. Borrowed from Sven Marnach on StackOverflow.
        https://stackoverflow.com/questions/5655708/python-most-elegant-way-to-intersperse-a-list-with-an-element.

        Used in this module to insert rows of empty tiles as spacing between rendered menu items."""
        res = [value] * (2 * len(seq) - 1)
        res[::2] = seq
        return res

    @staticmethod
    def _imaginary_row(width: int,
                       color: RGB = (0, 0, 0)):
        return [(width, color)
                for i in range(0, width)]

    @property
    def padding(self) -> Tuple[int, int, int, int]:
        """Returns the current padding tuple, in tiles, as (top, right, bottom, left)."""
        return self._padding

    @padding.setter
    def padding(self, pad) -> None:
        """Sets new padding, in numbers of tiles (at least 0), in the format (top, right, bottom, left)."""
        if sum([p >= 0 for p in pad]) == 4:
            self._padding = pad
        else:
            raise ValueError("All padding values must be integers of no less than 0, given {}".format(str(pad)))

    @property
    def pad_top(self) -> int:
        """Returns the top padding, in tiles."""
        return self.padding[0]

    @pad_top.setter
    def pad_top(self, pad: int) -> None:
        raise ValueError("Single-value padding assignment not supported; assign a new tuple to .padding")

    @property
    def pad_right(self) -> int:
        """Returns the right side padding, in tiles."""
        return self.padding[1]

    @pad_right.setter
    def pad_right(self, pad: int) -> None:
        raise ValueError("Single-value padding assignment not supported; assign a new tuple to .padding")

    @property
    def pad_bottom(self):
        """Returns the bottom padding, in tiles."""
        return self.padding[2]

    @pad_bottom.setter
    def pad_bottom(self, pad: int):
        raise ValueError("Single-value padding assignment not supported; assign a new tuple to .padding")

    @property
    def pad_left(self):
        """Returns the left side padding, in tiles."""
        return self.padding[3]

    @pad_left.setter
    def pad_left(self, pad: int):
        raise ValueError("Single-value padding assignment not supported; assign a new tuple to .padding")

    @property
    def spacing(self) -> int:
        """Returns the number of tiles of spacing drawn between each of this menu's items."""
        return self._spacing

    @spacing.setter
    def spacing(self, spacing: int) -> None:
        """Sets the spacing between selections for this menu, if given an integer value of at least zero tiles."""
        if spacing >= 0:
            self._spacing = spacing
        else:
            raise ValueError(".spacing must be an integer of at least zero tiles--given {}".format(str(spacing)))

    @property
    def shape(self):
        """Returns this Menu's dimensions as (width, height)"""
        return self._width, self._height

    @shape.setter
    def shape(self, new_shape: Tuple[int, int]):
        """Sets a new width and height given a tuple of (w, h), both of which are integers greater than zero."""
        if sum([el > 0 for el in new_shape]) != 2:
            raise ValueError("Both width and height must be greater than zero--given (width: {}, height: {}"
                             .format(str(new_shape[0]),
                                     str(new_shape[1])))

        else:
            self._width, self._height = new_shape

    @property
    def color(self) -> RGB:
        """Returns the color property of this Menu, applied to its border.
        TODO: Make a menu header as well and apply it there too"""
        return self._color

    @color.setter
    def color(self, new_rgb: RGB) -> None:
        """Sets the color of this MenuItem, assuming it's a tuple of 3 integers in range 0-255."""
        for c in new_rgb:
            if not 0 <= c <= 255:
                raise ValueError("RGB values must be in range 0-255. Got {}".format(str(new_rgb)))
        self._color = new_rgb

    @property
    def contents(self) -> List[MenuOption]:
        """Return this menu's list of MenuOptions."""
        return self._contents

    def clear(self) -> None:
        """Removes all contents. Irreversible."""
        self._contents = []

    def add_option(self, opt: MenuOption):
        self._contents = [] + self._contents + [opt]

    def __init__(self,
                 width: int, height: int,
                 spacing: int = 2,
                 has_border: bool = False,
                 padding: Tuple[int, int, int, int] = (1, 1, 1, 1),
                 contents: Optional[Iterable[MenuOption]] = (),
                 color: RGB = (255, 255, 255)):
        """
        Generate a new menu with specified dimensions.
        :param width: Total width of the menu, in tiles
        :param height: Total height of the menu, in tiles
        :param spacing: How many empty rows to draw between each menu item
        :param padding: A tuple of (top, right, bottom, left), in tiles with which to pad the menu
        :param contents: An iterable of MenuOption instances, in order, to be added to this menu. Can be empty.
        """
        # Ensure width and height are both at least one tile
        if sum([dim > 0 for dim in (width, height)]) == 2:
            self._width, self._height = width, height
        else:
            raise ValueError("Width and height must both be greater than zero--given (width: {}, height: {})"
                             .format(str(width),
                                     str(height)))

        # Test if all padding values are no less than zero
        if sum([p >= 0 for p in padding]) == 4:
            self._padding = padding
        else:
            raise ValueError("All padding values must be integers of no less than 0, given {}".format(str(padding)))

        # Test that spacing is no less than zero
        if spacing >= 0:
            self._spacing = spacing
        else:
            raise ValueError("Param spacing must be an integer of at least zero tiles--given {}".format(str(spacing)))

        # Test that, if has_border is true, there's some padding on all sides to draw it in.
        if has_border and sum([p > 0 for p in self._padding]) < 4:
            raise ValueError("Menu cannot have a border if padding is not at least 1 tile in each direction, given {}"
                             .format(str(self._padding)))
        else:
            self._has_border = has_border

        # Coerce contents to a list and assign
        self._contents = [c for c in contents]

        if sum(0 <= c <= 255 for c in color) < 3:
            raise ValueError()
        else:
            self._color = color

    def renderable(self) -> RenderableArray:
        """Returns the entire menu as a 2D height-by-width RenderableArray."""
        # If we generated the options correctly, row_width will be the same for all rows returned.
        # Remain aware that opt_rows is a list of these lists, and we'll eventually flatten them.
        opt_rows: List[RenderableArray] = [c.rows for c in self._contents]
        row_width: int = len(opt_rows[0][0])
        print("opt_row lengths: {}".format(str([len(el) for el in opt_rows])))

        # Test that contents are of the correct width for this Menu
        left_pad = self._padding[3]
        right_pad = self._padding[1]
        if row_width != self._width - (left_pad + right_pad):
            raise ValueError("Row width must match menu width minus padding.\n" +
                             "width: {}, row_width: {}, padding: L-{} + R-{}"
                             .format(str(self._width),
                                     str(row_width),
                                     str(left_pad),
                                     str(right_pad)))

        # Test that all rows are of equal length to the first.
        for row in opt_rows:
            if len(row[0]) != row_width:
                raise ValueError("Rows must be of equal width. First row: {} tiles. This row: {} tiles."
                                 .format(str(row_width),
                                         str(len(row[0]))))

        # Intersperse the lists of menu item rows with lists of empty rows
        spaced_opt_rows = self._intersperse_list(seq=opt_rows,
                                                 value=self._imaginary_row(width=self._spacing))

        # At last, flatten the whole kebab to combine the lists of rows into a single RenderableArray.
        # We're doing a fair bit of left-pushing, so we'll use double-ended queues
        rows: Deque[Deque[RenderableItem]] = deque(sum(spaced_opt_rows, []))

        # TODO: Condense this blursed mess into local functions
        # Append left padding
        if self.pad_left != 0:
            for i in range(0, len(rows)):
                new_tile: RenderableItem = (" ", self._color)
                row: Deque[RenderableItem] = deque(rows[i])

                for j in range(0, self.pad_left + 1):
                    row.appendleft(new_tile)

        # Append right padding
        if self.pad_right != 0:
            for i in range(0, len(rows)):
                new_tile: RenderableItem = (" ", self._color)
                row: Deque[RenderableItem] = deque(rows[i])

                for j in range(0, self.pad_right + 1):
                    row.append(new_tile)

        # Append top and bottom padding
        if self.pad_top != 0:
            # Copy a new blank tile into a list as wide as the rest of the rows
            new_tile: RenderableItem = (" ", self._color)
            new_row: Deque[RenderableItem] = deque([new_tile for t in range(0, len(rows[0]))])
            rows.appendleft(new_row)

        if self.pad_bottom != 0:
            new_tile: RenderableItem = (" ", self._color)
            new_row: Deque[RenderableItem] = deque([new_tile for t in range(0, len(rows[0]))])
            rows.append(new_row)

        # Write border, if desired
        if self._has_border:
            # Reference vars for special characters from the tileset
            flat, vertical, top_left, top_right, bottom_left, bottom_right = ("═", "║", "╔", "╗", "╚", "╝")

            # Top border and corners
            rows[0] = deque([(flat, self._color) for item in rows[0]])
            rows[0][0] = (top_left, self._color)
            rows[0][-1] = (top_right, self._color)

            # Bottom border and corners
            rows[-1] = deque([(flat, self._color) for item in rows[-1]])
            rows[-1][0] = (bottom_left, self._color)
            rows[-1][-1] = (bottom_right, self._color)

            # Apply side bits
            for i in range(1, len(rows)-1):
                rows[i][0] = (vertical, self._color)
                rows[i][-1] = (vertical, self._color)

        return [list(row) for row in rows]

    def open_menu(self, x: int, y: int, console: Console) -> None:
        is_open = True

        print("menu opened! :)")
        while is_open:
            # Run a movement handler here
            is_open = False
