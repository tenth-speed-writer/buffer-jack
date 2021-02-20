import unittest

from typing import List
from src.playfield import PlayField, Cell
from src.entity import Entity
from src.sigil import Sigil


class TestCell(unittest.TestCase):
    def test_sigils(self):
        # Test that .sigils returns the highest priority sigils in a cell
        pf = PlayField(4, 4)
        ent = Entity(4, Sigil("A"))
        ent2 = Entity(4, Sigil("B"))
        ent3 = Entity(4, Sigil("C", priority=2))

        # Introduce three passable entities, one with a lower priority
        ent.introduce_at(2, 2, pf)
        ent2.introduce_at(2, 2, pf)
        ent3.introduce_at(2, 2, pf)
        sigs: List[Sigil] = pf.get_cell(2, 2).sigils

        # Assert that the two highest, but not the one lowest, are returned by .sigil
        assert ent.sigil in sigs
        assert ent2.sigil in sigs
        assert ent3.sigil not in sigs

    def test_position(self):
        """.position should return an (x, y) tuple of ints and reject assignment."""
        pf = PlayField(5, 5)
        c = pf.get_cell(x=2, y=3)

        assert c.position == (2, 3)

        with self.assertRaises(Exception):
            # Should not accept reassignment of .position
            c.position = 2, 2

    def test_passable(self):
        """Should be passable if no entity in the cell has .passable=False"""
        ent1 = Entity(4, Sigil("A"))
        ent2 = Entity(3, Sigil("B"))
        ent3 = Entity(3, Sigil("C"))

        pf = PlayField(3, 3)
        ent1.introduce_at(2, 2, pf)
        ent2.introduce_at(2, 2, pf)
        ent3.introduce_at(2, 2, pf)

        c: Cell = pf.get_cell(2, 2)
        assert c.passable

        # Making any of the contents impassible should make the cell impassable
        ent2.passable = False
        assert not c.passable

        c.remove_entity(ent2)
        assert c.passable

    def test_playfield(self):
        """.playfield should return the Cell's playfield and reject assignment."""
        pf = PlayField(2, 3)
        c = pf.get_cell(1, 2)
        assert c.playfield is pf

        with self.assertRaises(Exception):
            c.playfield = PlayField(5, 5)


class TestPlayField(unittest.TestCase):
    def test_happy_path_init(self):
        pass

    def test_unhappy_path_init(self):
        pass

