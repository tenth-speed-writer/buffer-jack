from typing import List
from src.modifiers import Modifier, MultiplicativeModifier, AdditiveModifier
from src.entity.entities import Mobile


class FooForm(Mobile):
    modifiers = {}

    def _apply_modifiers_to(self, stat: str):
        if not hasattr(self, stat):
            raise ValueError("Entity does not have a stat called '{}'!".format(stat))

        if stat not in self.modifiers.keys():
            raise ValueError("Entity's .modifiers dict has no value for key {}!".format(str(stat)))

        modifiers: List[Modifier] = self.modifiers[stat] if stat in self.modifiers.keys() else []

        # Separate out modifiers by additive or multiplicative
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