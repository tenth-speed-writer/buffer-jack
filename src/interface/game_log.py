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


class GameLog:
    """Keeps a running log of text to be printed for the player during gameplay,
    as well as holds methods to render it into console-printable lines given a specified width."""
    def __init__(self, width: int, height: int,
                 initial_log: Optional[List[LogEntry]] = []):
        self._width = width
        self._height = height
        self._log = initial_log

    def add_entry(self, text: str,
                  color: RGBTuple = (255, 255, 255)) -> None:
        """Add a new LogEntry to this GameLog, given valid values of text and optionally color."""
        self._log.append(LogEntry(text=text,
                                  color=color))

    def remove_entry(self, entry: LogEntry):
        """Removes a specified entry from this log, if it exists in it. Fails quietly if it does not."""
        if entry in self._log:
            self._log.remove(entry)
        else:
            pass
