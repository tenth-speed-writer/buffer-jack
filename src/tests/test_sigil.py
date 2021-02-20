import unittest
from src.sigil import Sigil


class TestSigil(unittest.TestCase):
    def test_happy_path(self):
        """Successfully creates various happy path Sigils."""
        test1 = Sigil("R")
        test2 = Sigil("$", priority=4)
        test3 = Sigil("φ", priority=2, color=(200, 225, 200))

        for t in (test1, test2, test3):
            assert isinstance(t, Sigil)

    def test_sad_paths(self):
        """Fails to create various unhappy path sigils."""
        with self.assertRaises(ValueError):
            # The hiragana 'ku' isn't in CP437
            test1 = Sigil("く")

        with self.assertRaises(ValueError):
            test2 = Sigil("F", priority=-32)

        with self.assertRaises(ValueError):
            test3 = Sigil("F2f")

        with self.assertRaises(ValueError):
            test4 = Sigil("C", color=(42, -85, 94))

    def test_color(self):
        test = Sigil("A", priority=3, color=(199, 198, 197))

        assert test.r == 199
        assert test.g == 198
        assert test.b == 197

        assert test.color == (199, 198, 197)

        test.color = (101, 102, 103)

        assert test.r == 101
        assert test.g == 102
        assert test.b == 103

        test.b = 202
        assert test.color[2] == 202

        with self.assertRaises(ValueError):
            test.g = 442

        with self.assertRaises(ValueError):
            test.g = -30

    def test_priority(self):
        """Tests getter & setter for Sigil.priority"""
        test = Sigil("R")
        test2 = Sigil("S", priority=2)
        assert test.priority > test2.priority

        test2.priority = 4
        assert test2.priority > test.priority

        with self.assertRaises(Exception):
            test.priority = 6

        with self.assertRaises(Exception):
            test.priority = -3

        with self.assertRaises(Exception):
            test.priority = "Foo"
