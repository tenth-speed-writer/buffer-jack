from typing import Optional, List, Dict


class Modifier:
    """Parent class for any kind of modifier to be applied to a specifiable stat."""
    def __init__(self, parent,
                 stat: str,
                 value: float,
                 lifespan: Optional[int] = None):
        """
        :param parent: an object possessing both the specified stat as a property, as well as a .modifiers dict.
        :param stat: a string corresponding to the attribute name of the stat in question.
        :param value: a float value representing the argument operation of this modifier
        :param lifespan: in number of ticks; if None, will not expire over time.
        """
        self.stat = stat
        self.value = value
        self.lifespan = lifespan
        self._initial_lifespan = lifespan

        if not hasattr(parent, stat):
            raise ValueError("Tried to create a modifier for an object which does not have a property named {}"
                             .format(str(stat)))

        if not hasattr(parent, "modifiers") or not isinstance(getattr(parent,
                                                                      "modifiers"), dict):
            raise ValueError("The parent object {} must have an attribute 'modifiers' which must be a dict"
                             .format(str(parent)))

        else:
            self._parent = parent

    def calculate(self, modified_stat: Optional[float] = None):
        """"Calculates this stat, either by pulling it from parent or applying it to another specified value.
        Override for specific modifier types, or apply bare for a fixed value."""
        return self.value

    @property
    def parent(self):
        """Getter for self._parent, which should probably not be changed externally."""
        return self._parent

    @property
    def is_active(self):
        return (self.lifespan is None) or (self.lifespan > 0)

    def remove(self):
        mods: dict = self.parent.modifiers
        mods.pop(self.stat)

    def tick(self):
        if not (self.lifespan is None) and self.lifespan > 0:
            self.lifespan -= 1


class AdditiveModifier(Modifier):
    """A modifier which is summed with its value."""
    def __init__(self,
                 parent: object,
                 stat: str,
                 value: float,
                 lifespan: Optional[int] = None):
        Modifier.__init__(self=self,
                          parent=parent,
                          stat=stat,
                          value=value,
                          lifespan=lifespan)

    def calculate(self, modified_stat: Optional[float] = None):
        """Calculates this stat, either by pulling it from parent or applying it to another specified value.
        This one adds its value to the specified value."""
        if modified_stat is None:
            return getattr(self.parent, self.stat) + self.value
        else:
            return modified_stat + self.value


class BaseAdditiveMultiplier(Modifier):
    """Differentiated from an additive multiplier only in that it is applied *before* multiplicative modifiers."""
    def __init__(self,
                 parent: object,
                 stat: str,
                 value: float,
                 lifespan: Optional[int] = None):
        Modifier.__init__(self=self,
                          parent=parent,
                          stat=stat,
                          value=value,
                          lifespan=lifespan)

    def calculate(self, modified_stat: Optional[float] = None):
        """Calculates this stat, either by pulling it from parent or applying it to another specified value.
        This one adds its value to the specified value."""
        if modified_stat is None:
            return getattr(self.parent, self.stat) + self.value
        else:
            return modified_stat + self.value


class MultiplicativeModifier(Modifier):
    """A modifier which is applied by multiplication to its value."""
    def __init__(self,
                 parent: object,
                 stat: str,
                 value: float,
                 lifespan: Optional[int] = None):
        Modifier.__init__(self=self,
                          parent=parent,
                          stat=stat,
                          value=value,
                          lifespan=lifespan)

    def calculate(self, modified_stat: Optional[float] = None):
        """Calculates this stat, either by pulling it from parent or applying it to another specified value.
        This one multiplies by the specified value."""
        if modified_stat is None:
            return getattr(self.parent, self.stat) * self.value
        else:
            return modified_stat * self.value


# ValueDict = Dict[List[Modifier]]