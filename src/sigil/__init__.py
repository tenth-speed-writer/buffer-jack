from typing import Tuple
from copy import deepcopy

# Corresponds to CP437. Update if necessary.
# If that happens more than once, make a class for the tilesets w/ permitted characters as a property.
#
# Future dev: I compiled this by hand, copy-paste.
#             If you decide to do something less insane,
#             leave it commented as a testament to my hubris.
characters_cp437 = ["\x00", "", "☺", "☻", "♥", "♦", "♣", "♠",
                    "•", "◘", "○", "◙", "♂", "♀", "♪", "♫", "☼",
                    "►", "◄", "↕", "‼", "¶", "§", "▬", "↨", "↑",
                    "↓", "→", "←", "∟", "↔", "▲", "▼", " ", "!",
                    "\"", "#", "$", "%", "&", "'", "(", ")", "*",
                    "+", ",", "-", ".", "/", "0", "1", "2", "3",
                    "4", "5", "6", "7", "8", "9", ":", ";", "<",
                    "=", ">", "?", "@", "A", "B", "C", "D", "E",
                    "F", "G", "H", "I", "J", "K", "L", "M", "N",
                    "O", "P", "Q", "R", "S", "T", "U", "V", "W",
                    "X", "Y", "Z", "[", "\\", "]", "^", "_", "`",
                    "a", "b", "c", "d", "e", "f", "g", "h", "i",
                    "j", "k", "l", "m", "n", "o", "p", "q", "r",
                    "s", "t", "u", "v", "w", "x", "y", "z", "{",
                    "|", "}", "~", "\x7f", "Ç", "ü", "é", "â",
                    "ä", "à", "å", "ç", "ê", "ë", "è", "ï", "î",
                    "ì", "Ä", "Å", "æ", "Æ", "ô", "ö", "ò", "û",
                    "ù", "ÿ", "Ö", "Ü", "¢", "£", "¥", "₧", "ƒ",
                    "á", "í", "ó", "ú", "ñ", "Ñ", "ª", "º", "¿",
                    "⌐", "¬", "½", "¼", "¡", "«", "»", "░", "▒",
                    "▓", "│", "┤", "╡", "╢", "╖", "╕", "╣", "║",
                    "╗", "╝", "╜", "╛", "┐", "└", "┴", "┬", "├",
                    "─", "┼", "╞", "╟", "╚", "╔", "╩", "╦", "╠",
                    "═", "╬", "╧", "╨", "╤", "╥", "╙", "╘", "╒",
                    "╓", "╫", "╪", "┘", "┌", "█", "▄", "▌", "▐",
                    "▀", "α", "ß", "Γ", "π", "Σ", "σ", "µ", "τ",
                    "Φ", "Θ", "Ω", "δ", "∞", "φ", "ε", "∩", "≡",
                    "±", "≥", "≤", "⌠", "⌡", "÷", "≈", "°", "∙",
                    "·", "√", "ⁿ", "²", "■", "\xa0"]


class Sigil:
    def __init__(self,
                 character: str,
                 priority: int = 3,
                 color: Tuple[int, int, int] = (255, 255, 255)):
        if len(character) > 1:
            raise ValueError("Sigils may only be a single character; given \"{}\""
                             .format(character))
        if character not in characters_cp437:
            raise ValueError("Cannot create sigil; {} is not a valid CP437 character."
                             .format(character))
        self.character = character
        self._priority = priority

        # Cast color to a list, as it should be a mutable attribute,
        # but also keep the original color in case we want to clear it.
        self._color = [c for c in color]
        self._base_color = deepcopy(self.color)

    @property
    def r(self) -> int:
        """Returns the red (first) component (RGB: 0-255) of the sigil's color."""
        return self._color[0]

    @r.setter
    def r(self, red: int):
        """Assigns a new red color value, assuming the one provided is a valid integer in [0-255]."""
        if not 0 <= red <= 255:
            raise ValueError("Red RGB value must be 0 <= red <= 255")
        self._color[0] = red

    @property
    def g(self) -> int:
        """Returns the green (middle) component (RGB: 0-255) of the sigil's color."""
        return self._color[1]

    @g.setter
    def g(self, green: int):
        """Assigns a new green color value, assuming the one provided is a valid integer in [0-255]."""
        if not 0 <= green <= 255:
            raise ValueError("Green RGB value must be 0 <= green <= 255")
        self._color[1] = green

    @property
    def b(self) -> int:
        """Returns the blue (third) component (RGB: 0-255) of the sigil's color."""
        return self._color[2]

    @b.setter
    def b(self, blue: int):
        """Assigns a new blue color value, assuming the one provided is a valid integer in [0-255]."""
        if not 0 <= blue <= 255:
            raise ValueError("Blue RGB value must be 0 <= blue <= 255")
        self._color[2] = blue

    @property
    def color(self) -> Tuple[int, int, int]:
        """Returns the Red, Green, and Blue RGB values for this sigil's color as an (R, G, B) tuple."""
        return self.r, self.g, self.b

    @color.setter
    def color(self, rgb: Tuple[int, int, int]):
        """Assigns a new red, blue, and green value from a tuple--assuming they're valid integers in [0-255]."""
        self.r, self.g, self.b = rgb

    def as_tuple(self) -> Tuple[str, Tuple[int, int, int]]:
        """Returns a tuple with the sigil's character and its color tuple."""
        return self.character, (self.r, self.g, self.b)

    @property
    def priority(self) -> int:
        """Returns the priority of this sigil, between 1 and 5.
        Highest priority/priorities in a cell will be rendered on the map."""
        return self._priority

    @priority.setter
    def priority(self, p: int) -> None:
        """Checks if a new specified sigil priority is valid before assigning it."""
        p_out_of_range = not 1 <= p <= 5
        if p_out_of_range:
            raise ValueError("Sigil priority must be in range [1-5]. Given {}"
                             .format(str(p)))

        self._priority = p

    def __str__(self):
        """Casting the sigil to a string should probably just return its character."""
        return self.character

# Testing statements! :)
#
# foo = Sigil("ó")
# # bar = Sigil("く")
# print(foo.color)
# foo.g = 42
# print(foo.color)
# foo.color = (195, 214, 129)
# print(foo.color)
