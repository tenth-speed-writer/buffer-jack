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