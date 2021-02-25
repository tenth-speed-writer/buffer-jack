import tcod
from typing import Iterable, Callable, List, Tuple, Optional, MutableSequence, Type
from copy import deepcopy
from math import floor
from src.inputs import PositionDelta
from src.sigil import Sigil

# Custom type for an RGB color tuple
RGB = Tuple[int, int, int]

# Custom types for a 2D list of tuples, each with a character and a color to be rendered.
RenderableItem = Tuple[str, Tuple[int, int, int]]
RenderableArray = MutableSequence[MutableSequence[RenderableItem]]


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
                 color: RGB = (240, 240, 240),
                 on_highlight_icon: str = "°"):
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
        self.on_select = on_select
        self._pad_horizontal = pad_horizontal
        self._pad_vertical = pad_vertical
        self._has_border = has_border

        self._color = color

        self._highlight_icon = on_highlight_icon

    @property
    def text(self):
        """Returns the primary text for this menu option."""
        return self._text

    @property
    def rows(self) -> RenderableArray:
        """Renders this menu option as a list of lists of (char, color_tuple), including margins/border/padding"""

        def char_to_tuple(char: str):
            return char, self.color

        def lines_to_tuples(lines_: List[List[str]]):
            return [[char_to_tuple(char)
                     for char in row]
                    for row in lines_]

        def pad_string(line: str):
            """Center-align a specified string based on own width."""
            text_width = len(line)
            tgt_width = self._width
            new_line = deepcopy(line)

            # Pad it left or right based on evens/odds.
            # Stagger the count by 1 so the modulus trick doesn't throw a div-by-zero error
            # Developer confession: I don't know why "+3" fixes this.
            for j in range(1, tgt_width - text_width + 3):
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

        # TODO: Rewrite this padding business more sensibly

        # Apply margins and border, if appropriate
        # if self._pad_vertical:
        #     for i in range(0, self._pad_vertical + 1):
        #         # Pad top and bottom by one full row per pad_vertical
        #         blank_row: List[str] = [" " for i in range(0, self._width + 2*self._pad_horizontal)]
        #         lines.insert(0, blank_row)
        #         lines.append(blank_row)
        #
        # if self._pad_horizontal:
        #     for i in range(0, len(lines)):
        #         # Pad left and right once each per pad_horizontal
        #         lines[i]: str = " " + str(lines[i])
        #         lines[i]: str = lines[i] + " "

        if self._has_border:
            # If this MenuOption has a border, construct and write that into the edge characters.
            # This should, as per value testing, only run if there's padding to safely write in.

            # Insert side borders
            for i in range(0, len(lines)):
                lines[i][0] = "│"
                lines[i][-1] = "│"

            # Generate and append top and bottom borders
            new_top = ["─" for i in lines[0]]
            new_top[0] = "┌"
            new_top[-1] = "┐"

            new_bottom = ["─" for i in lines[0]]
            new_bottom[0] = "└"
            new_bottom[-1] = "┘"

            lines[0] = new_top
            lines[-1] = new_bottom
            # print(lines)
            # Convert characters to (char, (r, g, b)) format
            return lines_to_tuples(lines)

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


class MenuInputHandler(tcod.event.EventDispatch):
    def __init__(self, menu):
        self._menu = menu
        super().__init__()

    def cmd_close_menu(self):
        """Set its .is_open to False, breaking the menu loop."""
        self._menu.close()

    def ev_keydown(self, event: tcod.event.KeyDown):
        up_keys = [tcod.event.K_UP, tcod.event.K_KP_8, tcod.event.K_KP_PLUS]
        down_keys = [tcod.event.K_DOWN, tcod.event.K_KP_2, tcod.event.K_KP_MINUS]
        select_keys = [tcod.event.K_SPACE,
                       tcod.event.K_RETURN,
                       tcod.event.K_RETURN2,
                       tcod.event.K_KP_ENTER]
        exit_keys = [tcod.event.K_ESCAPE]

        # TODO: Add page up/page down for multi-entity skips
        if event.sym in up_keys:
            self._menu.change_selection(PositionDelta(dx=0, dy=-1))
        elif event.sym in down_keys:
            self._menu.change_selection(PositionDelta(dx=0, dy=1))
        elif event.sym in select_keys:
            opt: MenuOption = self._menu.contents[self._menu.selected]
            opt.on_select(None)
        elif event.sym in exit_keys:
            # TODO: Tell the menu to close
            self.cmd_close_menu()

    def ev_quit(self, event: tcod.event.Quit):
        SystemExit()


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
        if not len(new_rgb) == 3:
            raise ValueError("new_rgb must be a sequence of length 3 (given {})".format(str(new_rgb)))
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
        """Add a menu option to the end of this menu's list of contents."""
        self._contents = [] + self._contents + [opt]

    def remove_option(self, opt: MenuOption):
        if opt in self._contents:
            self._contents.remove(opt)

    def open_menu(self) -> None:
        """Set this menu as the last element of the interface menus list"""
        self._menus.append(self)

    def close_menu(self) -> None:
        self._menus.remove(self)
        del self

    def __init__(self,
                 width: int, height: int,
                 menus: List,
                 spacing: int = 2,
                 has_border: bool = False,
                 padding: Tuple[int, int, int, int] = (1, 1, 1, 1),
                 contents: Optional[Iterable[MenuOption]] = (),
                 color: RGB = (255, 255, 255),
                 dispatch: tcod.event.EventDispatch = MenuInputHandler):
        """
        Generate a new menu with specified dimensions.
        :param width: Total width of the menu, in tiles
        :param height: Total height of the menu, in tiles
        :param menus: The ordered list of active menus from/to which to add/remove this menu
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

            # Assign color, if it's valid
            if sum(0 <= c <= 255 for c in color) < 3:
                raise ValueError()
            else:
                self._color = color

        # Coerce contents to a list and assign
        self._contents = [c for c in contents]

        # The index of the currently selected menu_option.
        self._selected: int = 0

        # Assigns a flag to be used by the open_menu logic to eventually break the menu loop
        self._is_open = False

        self._dispatch: tcod.event.EventDispatch = MenuInputHandler(self)

        self._menus = menus

    @property
    def selected(self):
        """Returns the index of the currently selected menu option."""
        return self._selected

    def change_selection(self, delta: PositionDelta):
        """Changes the selection based on the dy of a PositionDelta.
        Also implements looping behavior."""
        num_options = len(self._contents)
        y_max = num_options - 1  # Minus 1, because it's an index.
        dy = deepcopy(delta.dy)
        y0 = self.selected
        y1 = y0+dy

        # If y1 is past the end of the list indices, loop back.
        while y1 > y_max:
            y1 -= num_options

        self._selected = y1

    @property
    def dispatch(self) -> tcod.event.EventDispatch:
        return self._dispatch

    @dispatch.setter
    def dispatch(self, d: Type[tcod.event.EventDispatch]) -> None:
        if issubclass(d.__class__, tcod.event.EventDispatch):
            self._dispatch = d()
        else:
            raise ValueError("d must be a subclass of tcod.event.EventDispatch, got {}"
                             .format(str(d)))

    def render_menu(self, x0: int, y0: int) -> List[Tuple[int, int, Sigil]]:
        """

        :param x0 - The x component of the top-left corner of this menu
        :param y0 - The y component of the top-left corner of this menu
        """
        def rows_to_drawables(x_0: int, y_0: int, opt_rows: RenderableArray) -> List[Tuple[int, int, Sigil]]:
            """

            :param x_0: The x component of the top-left corner of this set of things to be drawn
            :param y_0: The y component of the top-left corner of this set of things to be drawn
            :param opt_rows: A batch of rows (usually given by a MenuObject) to be drawn
            :return: A list of (x, y, Sigil) tuples, where x and y are true console positions.
            """
            drawables_ = []
            for dy in range(0, len(opt_rows)):  # dy is both change from y0 and our row iterator
                for dx in range(0, len(opt_rows[dy])):  # same for dx, x0, and our our column iterator
                    char = opt_rows[dy][dx][0]
                    color = opt_rows[dy][dx][1]
                    drawables_.append((x_0 + dx,
                                      y_0 + dy,
                                      Sigil(char,
                                            color=color)))
            return drawables_

        # Disregard drawing menu borders here.
        # If we want one, we can make the console draw it elsewhere.
        #
        # if self._has_border:
        #     console.draw_frame(x0, y0, self._width, self._height)
        #     h = self._height - 2  # Effective width and height after drawing the border
        #     w = self._width - 2
        # else:
        h = self._height
        w = self._width

        # Print menu contents
        # TODO: Replace this with robust handling for opening empty menus
        if not self.contents:
            raise Exception("Tried to open an empty menu.")

        # Left offset should be left pad, plus 1/2 rounded down of half of the diff
        # between working width and option width. -1 'cause we want corresponding index.
        # TODO: Make .width/.height getters or find a more graceful way of doing this.

        # Determine the x position of the menu options and the first y position
        opt_x0 = self.pad_left + floor(0.5 * (w - self.contents[0]._width)) - 1
        opt_y0 = self.pad_top
        locations = [(opt_x0, opt_y0)]  # Valid top left corner tiles for drawing MenuItems

        dy = self.spacing + self.contents[0]._height  # Determine how many y steps are between each top left
        yi = opt_y0 + dy  # The first new step will be dy steps down
        while (yi + dy) < h:
            locations.append((x0, yi))  # As will each additional one.
            yi += dy

        num_opts = len(locations)
        if num_opts >= len(self.contents):                   # If no more contents than places to put them
            opts = self.contents                             # Just render them all
        else:                                                # Otherwise
            opts = self.contents[self._selected + num_opts]  # Render as many as we can

        drawables: List[Tuple[int, int, Sigil]] = []
        for i in range(0, len(opts)):
            rows = opts[i].rows
            pos = locations[i]
            drawables += rows_to_drawables(x_0=x0 + pos[0], y_0=y0 + pos[1], opt_rows=rows)

        return drawables
