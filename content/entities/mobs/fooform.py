from typing import List, Tuple, Optional
from src.modifiers import Modifier, MultiplicativeModifier, AdditiveModifier, Base
from src.entity.entities import Mobile


class FooForm(Mobile):
    modifiers = {}

    def _apply_modifiers_to(self, stat: str):
        if not hasattr(self, stat):
            raise ValueError("Entity does not have a stat called '{}'!".format(stat))

        if stat not in self.modifiers.keys():
            raise ValueError("Entity's .modifiers dict has no value for key {}!".format(str(stat)))

        modifiers: List[Modifier] = self.modifiers[stat]\
            if stat in self.modifiers.keys()\
            else []

        # Separate out modifiers by additive or multiplicative
        base_adds =
        adds = [m for m in modifiers
                if isinstance(m, AdditiveModifier) or issubclass(m.__class__, AdditiveModifier)]
        mults = [m for m in modifiers
                 if isinstance(m, MultiplicativeModifier) or issubclass(m.__class__, MultiplicativeModifier)]

        # Initialize the result as the base stat
        result: float = getattr(self, name="_" + stat)

        # Apply multiplicative before additive
        for mod in mults:
            result = mod.calculate(result)
        for mod in adds:
            result = mod.calculate(result)

        return result

    def _set_base_stat(self, stat_name: str, value: float):
        if 0 <= value <= 100:
            setattr(self, "_" + stat_name, value)
        else:
            raise ValueError("Base stat {} must be a value between 0 and 100. Got {}"
                             .format(str(stat_name), str(value)))

    def on_introduce(self) -> None:
        """Overridable for logic which fires just after the object is introduced on the playfield."""
        pass

    def introduce_at(self, x, y, playfield) -> None:
        """Introduces this FooForm onto the playfield, then fires any on_create method it might have been assigned."""
        super().introduce_at(x, y, playfield)
        self.on_introduce()

    def on_destroy(self) -> None:
        """Overridable for logic which fires just before this object is destroyed."""
        pass

    def destroy(self):
        """Fires this FooForm's on_destroy method, then--as expected--destroys it."""
        self.on_destroy()
        super().destroy()

    def on_move(self,
                old_pos: Tuple[int, int],
                new_pos: Tuple[int, int]) -> None:
        """Overridable logic that fires just before this entity moves."""
        pass

    def on_just_moved(self,
                      old_pos: Tuple[int, int],
                      new_pos: Tuple[int, int]) -> None:
        """Overridable logic that fires just after this entity moves."""
        pass

    def move_to(self, x, y) -> None:
        """Fires self.on_move, then super().move_to, then self.on_just_moved."""
        old = self.position
        new = (x, y)

        self.on_move(old, new)
        super().move_to(x, y)
        self.on_just_moved(old, new)