import unittest as ut
from src.entity import Entity, entities, NotOnPlayFieldException, CannotMoveException
from src.playfield import PlayField
from src.sigil import Sigil


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
            test1 = Entity(size=34, sigil=Sigil("x")) # Size > 10

        with self.assertRaises(Exception):
            test2 = Entity(size=-2, sigil=Sigil("z")) # Size < 0

    def test_passable(self):
        pass

    def test_cell(self):
        pass

    def test_playfield(self):
        pass

    def test_position(self):
        pass

    def test_sigil(self):
        pass

    def test_size(self):
        pass

    def test_name(self):
        pass

    def test_introduce_at(self):
        pass

    def test_move_to(self):
        pass