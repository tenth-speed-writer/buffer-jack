from copy import deepcopy
from typing import List, Tuple, Optional

RGBTuple = Tuple[int, int, int]


class LogEntry:
    """A class representing a single chunk of text to be printed to the in-game console, as well as its color."""
    def __init__(self,
                 text: str,
                 color: RGBTuple = (255, 255, 255)):
        if len(text) == 0:
            raise ValueError("Cannot create a log entry with empty text!")

        self._text = text
        self._color = color

    @property
    def text(self) -> str:
        """Returns the text of this LogEntry as a single string."""
        return self._text

    @text.setter
    def text(self, t: str) -> None:
        """Assigns a new value of .text, assuming it's a string of length > 0."""
        if isinstance(t, str) and len(t) > 0:
            self._text = t
        else:
            raise ValueError(".text attribute of {} must be a string of length at least 0, got: {}"
                             .format(str(self),
                                     str(t)))

    @property
    def color(self) -> RGBTuple:
        """The color in which this LogEntry should be printed."""
        return self._color

    @color.setter
    def color(self, c: Tuple[int, int, int]) -> None:
        """Reassigns this entry's color if given a valid tuple of 3 integers in range 0-255, inclusive."""
        def __is_valid_color(val: int) -> bool:
            return isinstance(val, int) and 0 <= val <= 255

        if sum([__is_valid_color(el) for el in c]) == 3:
            self._color = c
        else:
            raise ValueError("New color 'c' must be a tuple of 3 integers in range 0-255. Got {}"
                             .format(str(c)))

    def as_rows(self, width) -> List[str]:
        """Returns a list of strings representing this LogEntry's .text, split into lengths of 'width'."""
        def row_gen():
            i = 0
            di = width

            while i < len(self.text):
                if i + di < len(self.text):
                    t = self.text[i:i+di]
                else:
                    t = self.text[i:]
                i += di
                yield(t)

        return [r for r in row_gen()]

    def as_drawables(self, x0: int, y0: int, width: int) -> List[Tuple[int, int, str, Tuple[int, int, int]]]:
        """Given a top-left corner (x0, y0), return a list of [(x, y, character, (r, g, b))]"""
        rows = self.as_rows(width)
        drawables: List[Tuple[int, int, str, Tuple[int, int, int]]] = []
        for y in range(0, len(rows)):
            row = rows[y]
            for x in range(0, len(row)):
                char = row[x]
                drawables.append((x + x0,
                                  y + y0,
                                  char,
                                  self.color))
        return drawables


class GameLog:
    """Keeps a running log of text to be printed for the player during gameplay,
    as well as holds methods to render it into console-printable lines given a specified width."""
    def __init__(self, width: int, height: int,
                 initial_log: Optional[List[LogEntry]] = []):
        self._width = width
        self._height = height
        self._log = initial_log

    @property
    def log(self):
        return self._log

    def add_entry(self, text: str,
                  color: RGBTuple = (255, 255, 255)) -> None:
        """Add a new LogEntry to this GameLog, given valid values of text and optionally color."""
        self._log.append(LogEntry(text=text,
                                  color=color))

    def remove_entry(self, entry: LogEntry):
        """Removes a specified entry from this log, if it exists in it. Fails quietly if it does not."""
        if entry in self._log:
            self._log.remove(entry)

    def as_drawables(self, x0: int, y0: int) -> List[Tuple[int, int, str, Tuple[int, int, int]]]:
        """Returns a list of tuples containing [x, y, character, (r, g, b)] from which to draw the
        contents of this interface element. Assumes that the range ends at x0+width, y0+height.

        :param x0 The x value of the top-left most point from which to render the menu.
        :param y0 The y value of the top-left most point from which to render the menu."""

        # Iterate through our available height in increments of each shown entry's height plus one margin row.
        yi = deepcopy(y0)  # The y offset
        i = -1             # The index--relative to the end of ._log-- that we wish to reference next.
        drawables = []     # A list to hold the drawable tuples we wish to return

        # While yi is between our origin point and origin + height,
        # and while we ALSO have more LogEntries left to render...
        while yi <= y0 + self._height and -i < len(self._log):
            # Render it on column dx and row yi, then append it to drawables.
            entry = self._log[i]
            drawables += entry.as_drawables(x0=x0,
                                            y0=yi,
                                            width=self._width)

            # Set the next top-left corner, adding an extra row between statements as a margin.
            yi += len(entry.as_rows(self._width)) + 1

            # Set the index back by one more element from the last
            i -= 1

        return drawables

