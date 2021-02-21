import unittest
from src.menus import Menu, MenuOption


class TestMenusOption(unittest.TestCase):
    def test_text(self):
        """Checks that .text has a working setter and getter"""
        opt = MenuOption("Howdy!",
                         width=12,
                         height=5,
                         on_select=lambda x: print("Howdy!"),
                         subtext="It says howdy",
                         pad_horizontal=1,
                         pad_vertical=1)

        # Test getter
        assert opt.text == "Howdy!"

        # Test setter
        opt.text = "Do\noo\ndy!"  # <= 12 - 1*2 wide, less than 5 - 1*2 high
        assert opt.text == "Doody!"

        # Test setter parameter checking.
        with self.assertRaises(Exception):
            opt.text = "Groooooooooooooooooooooooooooooot."  # Too long entirely

        with self.assertRaises(Exception):
            opt.text = "Mooooooood."  # Too long given horizontal padding

        with self.assertRaises(Exception):
            opt.text = "Loo\n\oo\noo\nooo\n\ooo\n\oooot\n"  # Too many lines entirely

        with self.assertRaises(Exception):
            opt.text = "Fooo\nooooo\nooooo\noooods"  # Too many lines after vertical padding

    def test_subtext(self):
        """Checks that .subtext has a working setter and getter."""
        opt = MenuOption("Howdy!",
                         width=12,
                         height=5,
                         on_select=lambda x: print("Howdy!"),
                         subtext="It says howdy",
                         pad_horizontal=1,
                         pad_vertical=1)

        assert opt.subtext == "It says howdy"

        opt.subtext = "It sure says something."
        assert opt.subtext == "It sure says something."

    def test_size(self):
        """Checks that .size has a working getter and refuses assignment."""
        opt = MenuOption("Howdy!",
                         width=12,
                         height=5,
                         on_select=lambda x: print("Howdy!"),
                         subtext="It says howdy",
                         pad_horizontal=1,
                         pad_vertical=1)

        assert opt.size == (12, 5)

        with self.assertRaises(Exception):
            opt.size = (1, 2)

    def test_color(self):
        """Tests that color has a working setter and getter."""
        opt = MenuOption("Howdy!",
                         width=12,
                         height=5,
                         on_select=lambda x: print("Howdy!"),
                         subtext="It says howdy",
                         pad_horizontal=1,
                         pad_vertical=1,
                         color=(200, 255, 200))
        assert opt.color == (200, 255, 200)

        opt.color = (155, 175, 155)
        assert opt.color == (155, 175, 155)

        with self.assertRaises(Exception):
            opt.color = (155, 22)  # Invalid tuple length

        with self.assertRaises(Exception):
            opt.color = (-32, 5, 122)  # One param below zero

        with self.assertRaises(Exception):
            opt.color = "Potatoes"  # Invalid argument type

        with self.assertRaises(Exception):
            opt.color = (1, "Onions", 35)  # One invalid param type

        with self.assertRaises(Exception):
            opt.color = None  # Assignment to None

    def test_horizontal_padding(self):
        """Tests that .horizontal_padding has working a working getter and rejects assignment."""
        opt = MenuOption("Howdy!",
                         width=12,
                         height=5,
                         on_select=lambda x: print("Howdy!"),
                         subtext="It says howdy",
                         pad_horizontal=1,
                         pad_vertical=1,
                         color=(200, 255, 200))
        assert opt.horizontal_padding == 1
        with self.assertRaises(Exception):
            opt.horizontal_padding = 4

    def test_vertical_padding(self):
        """Tests that .vertical_padding has working a working getter and setter with value checking."""
        opt = MenuOption("Howdy!",
                         width=12,
                         height=5,
                         on_select=lambda x: print("Howdy!"),
                         subtext="It says howdy",
                         pad_horizontal=1,
                         pad_vertical=1,
                         color=(200, 255, 200))

        assert opt.vertical_padding == 1
        with self.assertRaises(Exception):
            opt.vertical_padding = 2
