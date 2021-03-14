from src.modifiers import Modifier, MultiplicativeModifier, AdditiveModifier
from src.entity.entities import Mobile
from src.sigil import Sigil
from unittest import TestCase


class TestyBoi(Mobile):
    def __init__(self):
        super().__init__(4, Sigil("@"), "testyboi")
        self.modifiers = {}
        self.testymcstatface = 54


class TestModifiers(TestCase):
    def test_modifier(self):
        """Correctly gives a modifier to a valid entity."""
        testy_boi = TestyBoi()
        testy_boi.modifiers["testymcstatface"] = Modifier(testy_boi, "testymcstatface", 75)
        assert testy_boi.modifiers["testymcstatface"].calculate() == 75

    def test_additive_modifier(self):
        testy_boi = TestyBoi()
        testy_boi.modifiers["testymcstatface"] = AdditiveModifier(testy_boi, "testymcstatface", 15, lifespan=None)
        assert testy_boi.modifiers["testymcstatface"].calculate() == 54 + 15

    def test_multiplicative_modifier(self):
        testy_boi = TestyBoi()
        testy_boi.modifiers["testymcstatface"] = MultiplicativeModifier(testy_boi, "testymcstatface", 2, lifespan=None)
        assert testy_boi.modifiers["testymcstatface"].calculate() == 54 * 2
