import unittest

from typing import List
from src.playfield import PlayField, Cell
from src.entity import Entity
from src.entity.entities import Mobile, Static
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
        pf = PlayField(5, 7)

        assert pf.width == 5
        assert pf.height == 7

    def test_unhappy_path_init(self):
        # Make sure it raises exceptions when given invalid arguments
        with self.assertRaises(Exception):
            sad = PlayField(2, -5)

    def test_entities(self):
        """Tests .entities, which returns a list of all entities in the field."""
        e1 = Mobile(4, Sigil("A"))
        e2 = Entity(4, Sigil("B"))
        e3 = Static(4, Sigil("C"))
        pf = PlayField(10, 10)

        e1.introduce_at(1, 2, pf)
        e2.introduce_at(5, 3, pf)
        e3.introduce_at(9, 5, pf)

        assert e1 in pf.entities
        assert e2 in pf.entities
        assert e3 in pf.entities

        with self.assertRaises(Exception):
            # Rejects assignment.
            pf.entities = [e2]

    def test_shape(self):
        """Getter should return (width, height) and .shape should reject assignment."""
        pf = PlayField(width=9, height=4)
        assert pf.shape == (9, 4)

        with self.assertRaises(Exception):
            pf.width = 2

        with self.assertRaises(Exception):
            pf.height = 3

        with self.assertRaises(Exception):
            pf.shape = (2, 3)

    def test_get_cells(self):
        """Method should return a List of Cell objects, and if a range,
        is specified, should only return the specified selection."""
        pf = PlayField(5, 5)

        # Total cells in a 5x5 field should be 25
        all_cells = pf.get_cells()
        assert len(all_cells) == 25

        assert len(pf.get_cells([(2, 4), (1, 1), (2, 3)])) == 3
        assert sum(map(lambda x: isinstance(x, Cell),
                       pf.get_cells([(2, 4), (1, 1), (2, 3)])))


    def test_mobiles(self):
        pass

    def test_statics(self):
        pass

    def test_drawables(self):
        pass