import unittest as ut
from src.entity import Entity, entities, NotOnPlayFieldException, CannotMoveException
from src.playfield import PlayField, Cell
from src.sigil import Sigil

def _get_demo_entity():
    return Entity(size=5, sigil=Sigil("Q"), name="Demoboi")


class TestEntity(ut.TestCase):
    def test_create_happy_paths(self):
        test1 = Entity(size=3, sigil=Sigil("q"))
        test2 = Entity(size=9, sigil=Sigil("a"), name="Floofie")

        # DEVNOTE: We might obsolete specifying position & parents at init?
        # test_pf = PlayField(12, 12)
        # test3 = Entity(size=2, sigil=Sigil("f"), name="Leeloo",
        #                parent_cell=test_pf.get_cell(3, 2),
        #                parent_playfield=test_pf,
        #                position=(3, 2),
        #                passable=False)
        #
        # assert(test3 in test_pf.entities)

    def test_create_unhappy_paths(self):
        # Most things that go wrong here are type mismatches (which are
        # handled by explicit typing) and invalid values of size
        with self.assertRaises(Exception):
            test1 = Entity(size=34, sigil=Sigil("x"))  # Size > 10

        with self.assertRaises(Exception):
            test2 = Entity(size=-2, sigil=Sigil("z"))  # Size < 0

    def test_passable(self):
        """Test getter and setter for passable"""
        ent = Entity(size=6, sigil=Sigil("r"))
        assert ent.passable  # Entities are passable by default
        ent.passable = False
        assert not ent.passable  # Test t
        # he setter method

    def test_introduce_at(self):
        ent = _get_demo_entity()
        pf = PlayField(4, 4)
        ent.introduce_at(2, 3, pf)

        assert ent in pf.entities

    def test_position(self):
        ent = _get_demo_entity()
        pf = PlayField(4, 4)
        ent.introduce_at(2, 2, pf)

        assert ent.playfield is pf

    def test_move_to(self):
        ent = _get_demo_entity()
        pf = PlayField(4, 4)
        ent.introduce_at(2, 2, pf)
        ent.move_to(2, 3)
        assert ent.position == (2, 3)

    def test_cell(self):
        """Test getter and setter for parent cell"""
        ent = Entity(size=5, sigil=Sigil("4"))
        pf = PlayField(4, 4)
        ent.introduce_at(2, 3, pf)

        assert isinstance(ent.cell, Cell)
        assert ent in ent._parent_cell.contents

    def test_playfield(self):
        ent = Entity(size=5, sigil=Sigil("4"))
        pf = PlayField(4, 4)
        ent.introduce_at(2, 2, pf)

        assert isinstance(ent.playfield, PlayField)
        assert ent in PlayField.entities

    def test_sigil(self):
        ent = _get_demo_entity()
        assert isinstance(ent.sigil, Sigil)

        ent.sigil = Sigil("z")  # Happy path change
        assert ent.sigil.character == "z"

        with self.assertRaises(Exception):
            ent.sigil = Sigil("zz")  # Invalid sigil

    def test_size(self):
        ent = _get_demo_entity()
        assert ent.size

        ent.size = 8
        assert(ent.size == 8)

        with self.assertRaises(Exception):
            ent.size = 42  # Must be <= 10

        with self.assertRaises(Exception):
            ent.size = -3  # Must be >= 0

    def test_name(self):
        ent = _get_demo_entity()
        ent.name = "Conway Fiddy"
        assert ent.name == "Conway Fiddy"