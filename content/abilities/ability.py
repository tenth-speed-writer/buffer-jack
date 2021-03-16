from typing import Dict, List, Type, Optional
import src.modifiers.modifier as mod
from content.entities.mobs import MindForm, CogForm
from content.entities.mobs.fooform import FooForm
from src.pf_event_logger.logger import PFEventLogger


class Ability:
    def add_to_logger(self, logger: PFEventLogger):
        """Adds a row in a specified playfield logger for this event."""
        logger.add_ability(ability_id=self.ability_id,
                           name=self.name)

    def __init__(self,
                 name: str,
                 user: FooForm,
                 stats: Dict,
                 ability_id: Optional[str] = None):
        """
        Create an instance of an Ability.
        The user in question must possess the specified stats as attributes, unless this behavior is overridden.

        Ability ID is generated automatically based on ability name, so the same
        ability on different entities will have the same ability_id in the game logs.
        Be sure to specify a different ability_id if you want to be able to differentiate.

        :param name: A string representing the name of this ability
        :param user: The entity which manifested this ability.
        :param stats: A dict with stats and their relative proportions (0.0->1.0) in stat value calculation.
        :param ability_id: An ID by which to refer to this exact ability in the log. If none, defaults to '__name__'"""

        if name.strip(" ") != "":
            self.name = name
        else:
            raise ValueError("Attribute 'name' cannot be a blank string!")

        if ability_id:
            self.ability_id = ability_id
        else:
            self.ability_id = "__" + name + "__"

        self.user = user
        self.stats = stats

        # Log this user having an ability with this ability ID
        self.add_to_logger(user.playfield.logger)

    @staticmethod
    def _is_or_is_child(a: object, b: Type) -> bool:
        return isinstance(a, b) or issubclass(a.__class__, b)

    @classmethod
    def _apply_mods_to_stat(cls,
                            base_stat: float,
                            modifiers: List[mod.Modifier]) -> float:
        def is_base_additive(a: mod.Modifier) -> bool:
            return cls._is_or_is_child(a, mod.BaseAdditiveModifier)\
                   or cls._is_or_is_child(a, mod.BlindBaseAdditiveModifier)

        def is_multiplicative(a: mod.Modifier) -> bool:
            return cls._is_or_is_child(a, mod.MultiplicativeModifier)\
                   or cls._is_or_is_child(a, mod.BlindMultiplicativeModifier)

        def is_additive(a: mod.Modifier) -> bool:
            return cls._is_or_is_child(a, mod.AdditiveModifier)\
                   or cls._is_or_is_child(a, mod.BlindAdditiveModifier)

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
        """Override with logic describing what happens when this ability is used against the FooForm that used it."""
        pass

    def use_on(self, target: FooForm):
        """Selects and calls the appropriate vs_ method based on the target. Also logs it."""

        # Determine which vs_ method to call, then call it.
        if target is self.user:
            self.vs_self()
        elif self._is_or_is_child(target, CogForm):
            self.vs_cogform(target)
        elif self._is_or_is_child(target, MindForm):
            self.vs_mindform(target)
        else:
            raise ValueError("Target ({}) must be a MindForm, a CogForm, or the user of this ability!")

        # If nothing went wrong engine-wise, log an ability_used with the user's playfield's event logger
        self.user.playfield.logger.add_ability_used(ability_id=self.ability_id,
                                                    user_id=self.user.ent_id,
                                                    target_id=target.ent_id)
