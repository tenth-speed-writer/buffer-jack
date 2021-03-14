from typing import Dict, List, Type
import src.modifiers.modifier as mod
from content.entities.mobs import MindForm, CogForm
from content.entities.mobs.fooform import FooForm


class Ability:
    def __init__(self,
                 user: FooForm,
                 stats: Dict):
        """
        Create an instance of an Ability.
        The user in question must possess the specified stats as attributes, unless this behavior is overridden.

        :param user: The entity which manifested this ability.
        :param stats: A dict with stats and their relative proportions (0.0->1.0) in stat value calculation."""
        self.user = user
        self.stats = stats

    @staticmethod
    def is_or_is_child(a: object, b: Type) -> bool:
        return isinstance(a, b) or issubclass(a.__class__, b)

    @classmethod
    def _apply_mods_to_stat(cls,
                            base_stat: float,
                            modifiers: List[mod.Modifier]) -> float:
        def is_base_additive(a: mod.Modifier) -> bool:
            return cls.is_or_is_child(a, mod.BaseAdditiveModifier)\
                   or cls.is_or_is_child(a, mod.BlindBaseAdditiveModifier)

        def is_multiplicative(a: mod.Modifier) -> bool:
            return cls.is_or_is_child(a, mod.MultiplicativeModifier)\
                   or cls.is_or_is_child(a, mod.BlindMultiplicativeModifier)

        def is_additive(a: mod.Modifier) -> bool:
            return cls.is_or_is_child(a, mod.AdditiveModifier)\
                   or cls.is_or_is_child(a, mod.BlindAdditiveModifier)

        base_additives = [m for m in modifiers if is_base_additive(m)]
        multiplicatives = [m for m in modifiers if is_multiplicative(m)]
        additives = [m for m in modifiers if is_additive(m)]

        result = base_stat
        for m in base_additives:
            result = m.calculate(result)
        for m in multiplicatives:
            result = m.calculate(result)
        for m in additives:
            result = m.calculate(result)

        return result

    def _calculated_stats(self):
        """Multiplies the given multipliers by their co-named attributes from the User object."""
        calculated = {}
        for stat, multiplier in self.stats.items():
            calculated[stat] = multiplier * getattr(self.user, stat)
        return calculated

    def vs_cogform(self, target) -> None:
        """Override with logic describing what happens when this ability is used against a cogform."""
        pass

    def vs_mindform(self, target) -> None:
        """Override with logic describing what happens when this ability is used against a mindform."""
        pass

    def vs_self(self):
        """Override with logic describing what happens when this ability is used against the fooform that used it."""
        pass

    def use_on(self, target: FooForm):
        """Selects and calls the appropriate vs_ method based on the target."""
        if target is self.user:
            self.vs_self()
        elif self.is_or_is_child(target, CogForm):
            self.vs_cogform(target)
        elif self.is_or_is_child(target, MindForm):
            self.vs_mindform(target)
        else:
            raise ValueError("Target ({}) must be a MindForm, a CogForm, or the user of this ability!")