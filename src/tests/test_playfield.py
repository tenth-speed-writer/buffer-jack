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

        ent.introduce_at(2, 2, pf)
        ent2.introduce_at(2, 2, pf)
        ent3.introduce_at(2, 2, pf)
        sigs: List[Sigil] = pf.get_cell(2, 2).sigils

        assert ent.sigil in sigs
        assert ent2.sigil in sigs
        assert ent3.sigil not in sigs

    def test_position(self):
        pass

    def test_add_entity(self):
        pass

    def test_remove_entity(self):
        pass

    def test_passable(self):
        pass

    def test_playfield(self):
        pass


class TestPlayField(unittest.TestCase):
    def test_happy_path_init(self):
        pass

    def test_unhappy_path_init(self):
        pass

