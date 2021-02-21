import unittest
from src.menus import Menu, MenuOption
from src.menus.menu import RenderableArray, RenderableItem


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
        assert opt.text == "Do\noo\ndy!"

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

    def test_rows(self):
        """Tests that the MenuOption can render itself to a row x col 2D list of (character, (r, g, b)) tuples."""
        opt = MenuOption("AB\nCD",
                         width=6,
                         height=4,
                         on_select=lambda x: print("AB CD!"),
                         subtext="It says some letters",
                         pad_horizontal=1,
                         pad_vertical=1,
                         color=(200, 200, 200))
        rows: RenderableArray = opt.rows
        a: RenderableItem = rows[3][3]

        assert a[0] == "A"
        assert a[1] == (200, 200, 200)


class TestMenu(unittest.TestCase):
    def test_contents(self):
        """Tests getter for Menu.contents and that it rejects assignment."""
        opt = MenuOption("Howdy!",
                         width=12,
                         height=5,
                         on_select=lambda x: print("Howdy!"),
                         subtext="It says howdy",
                         pad_horizontal=1,
                         pad_vertical=1,
                         color=(200, 255, 200))
        menu = Menu(width=20, height=20,
                    has_border=True,
                    contents=[opt])

        assert opt in menu.contents

        with self.assertRaises(Exception):
            menu.contents = [opt]

    def test_add_option(self):
        """Tests that Menu.add_option() adds a valid MenuOption to Menu.contents."""
        opt = MenuOption("Howdy!",
                         width=12,
                         height=5,
                         on_select=lambda x: print("Howdy!"),
                         subtext="It says howdy",
                         pad_horizontal=1,
                         pad_vertical=1,
                         color=(200, 255, 200))
        menu = Menu(20, 20)
        menu.add_option(opt)

        assert opt in menu.contents

    def test_remove_option(self):
        """Tests that Menu.remove_option() will remove a specified MenuOption from its contents."""
        opt = MenuOption("Howdy!",
                         width=12,
                         height=5,
                         on_select=lambda x: print("Howdy!"),
                         subtext="It says howdy",
                         pad_horizontal=1,
                         pad_vertical=1,
                         color=(200, 255, 200))
        menu = Menu(20, 20, contents=[opt])
        assert opt in menu.contents

        menu.remove_option(opt)
        assert opt not in menu.contents

    def test_clear(self):
        """Tests that Menu.clear() will remove all its MenuOptions from its contents."""
        opt = MenuOption("Howdy!",
                         width=12,
                         height=5,
                         on_select=lambda x: print("Howdy!"),
                         subtext="It says howdy",
                         pad_horizontal=1,
                         pad_vertical=1,
                         color=(200, 255, 200))
        menu = Menu(20, 20, contents=[opt])
        assert opt in menu.contents

        menu.clear()
        assert opt not in menu.contents

    def test_padding(self):
        """Tests getters for each direction of padding."""
        menu = Menu(20, 20, padding=(2, 1, 3, 4))

        assert menu.pad_top == 2
        assert menu.pad_right == 1
        assert menu.pad_bottom == 3
        assert menu.pad_left == 4

        menu.padding = (2, 2, 1, 2)

        assert menu.pad_top == 2
        assert menu.pad_right == 2
        assert menu.pad_bottom == 1
        assert menu.pad_left == 2

        # Cannot directly assign new padding to their respective properties
        with self.assertRaises(Exception):
            menu.pad_top = 2
        with self.assertRaises(Exception):
            menu.pad_right = 2
        with self.assertRaises(Exception):
            menu.pad_bottom = 2
        with self.assertRaises(Exception):
            menu.pad_left = 2

        with self.assertRaises(Exception):
            menu.padding = (2, 1, 0)  # Too few params
        with self.assertRaises(Exception):
            menu.padding = (2, 5, 1, 2, 4)  # Too many params
        with self.assertRaises(Exception):
            menu.padding = (3, 5, 2, -4)  # Negative parameter
        with self.assertRaises(Exception):
            menu.padding = ("pipe", 4, 2, 1)  # Invalid parameter type

    def test_color(self):
        """Tests getter and setter for color"""
        menu = Menu(20, 20, color=(125, 125, 125))
        assert menu.color == (125, 125, 125)

        menu.color = (200, 200, 200)
        assert menu.color == (200, 200, 200)

        with self.assertRaises(Exception):
            menu.color = None  # Can't be None
        with self.assertRaises(Exception):
            menu.color = (2, 14)  # Too few args
        with self.assertRaises(Exception):
            menu.color = (2, 154, 24, 99)  # Too many args
        with self.assertRaises(Exception):
            menu.color = (4, "beef", 99)  # One invalid arg
        with self.assertRaises(Exception):
            menu.color = (-4, 192, 94)  # One negative argument