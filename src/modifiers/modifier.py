from typing import Optional


class Modifier:
    """Parent class for any kind of modifier to be applied to a specifiable stat."""
    def __init__(self, parent: object,
                 stat: str,
                 value: float,
                 lifespan: Optional[int] = None):
        """
        :param stat: a string corresponding to the attribute name of the stat in question.
        """
        self.stat = stat
        self.value = value
        self.lifespan = lifespan

        if not hasattr(parent, stat):
            raise ValueError("Tried to create a modifier for an object which does not have a property named {}"
                             .format(str(stat)))
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


class AdditiveModifier(Modifier):
    """A modifier which is summed with its value."""
    def __init__(self,
                 parent: object,
                 stat: str,
                 value: float,
                 lifespan: Optional[int]):
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
                 lifespan: Optional[int]):
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


class HasModifiers:
    """An optional parent class for an Entity which provides a list of modifiers."""
    pass