from src.sigil import Sigil
from .fooform import FooForm


class CogForm(FooForm):
    """Represents a CogForm--an enemy or a non-sapient NPC."""
    def __init__(self, name: str, size: int,
                 sigil: Sigil, base_move_cost: int,
                 base_coherency: float,
                 depth: float,  # A character attribute, rather than a mechanical one.
                 malignancy: float,
                 glimmer: float,
                 cogmass: float,
                 virality: float):
        super().__init__(name=name,
                         size=size,
                         sigil=sigil,
                         base_move_cost=base_move_cost)

        # Test that all provided base stats are valid.
        if not sum([0 <= val <= 100 for val in (depth, malignancy, glimmer, cogmass, virality)]) == 5:
            raise ValueError("All base attributes must be between 0 and 100 (inclusive)")

        self._depth = depth            # Cognitive depth. How deeply seated is it? How overwhelmingly fractal?
        self._malignancy = malignancy  # How inherently bitter, painful, or toxic this cogform is
        self._glimmer = glimmer        # How subtly or immediately fascinating this cogform is.
        self._cogmass = cogmass        # "That's some heavy s***."
        self._virality = virality      # Propensity to spread or stick with someone.

        self._coherency = base_coherency

        for stat in ("depth",
                     "malignancy",
                     "glimmer",
                     "cogmass",
                     "virality",
                     "coherency_gain",
                     "coherency_loss"):
            self.modifiers[stat] = []

    # Depth
    @property
    def base_depth(self) -> float:
        return self._depth

    @property
    def depth(self) -> float:
        return self._apply_modifiers_to("depth")

    @depth.setter
    def depth(self, new_depth: float) -> None:
        self._set_base_stat("depth", new_depth)

    # Malignancy
    @property
    def base_malignancy(self) -> float:
        return self._malignancy

    @property
    def malignancy(self) -> float:
        return self._apply_modifiers_to("malignancy")

    @malignancy.setter
    def malignancy(self, new_malig: float) -> None:
        self._set_base_stat("malignancy", new_malig)

    # Glimmer
    @property
    def base_glimmer(self) -> float:
        return self._glimmer

    @property
    def glimmer(self) -> float:
        return self._apply_modifiers_to("glimmer")

    @glimmer.setter
    def glimmer(self, new_glimm: float) -> None:
        self._set_base_stat("glimmer", new_glimm)

    # Cognitive Mass
    @property
    def base_cogmass(self) -> float:
        return self._cogmass

    @property
    def cogmass(self) -> float:
        return self._apply_modifiers_to("cogmass")

    @cogmass.setter
    def cogmass(self, new_cmass: float) -> None:
        self._set_base_stat("cogmass", new_cmass)

    # Virality
    @property
    def base_virality(self) -> float:
        return self._virality

    @property
    def virality(self) -> float:
        return self._apply_modifiers_to("virality")

    @virality.setter
    def virality(self, new_viral: float) -> None:
        self._set_base_stat("virality", new_viral)

    # Coherency
    @property
    def coherency(self) -> float:
        return self._coherency

    @coherency.setter
    def coherency(self, new_c: float):
        if new_c >= 0:
            self._coherency = new_c
        else:
            raise ValueError("new_c must be a float greater than or equal to zero. Got {}"
                             .format(str(new_c)))

    def coherency_delta(self, change_in_coherency: float) -> None:
        """Apply mods based on the sign of the delta, and floor coherency at 0."""
        if change_in_coherency < 0:
            delta = self._apply_blind_modifiers_to(stat="coherency_loss",
                                                   initial_val=change_in_coherency)
        else:
            delta = self._apply_blind_modifiers_to(stat="coherency_gain",
                                                   initial_val=change_in_coherency)

        if self.coherency + delta <= 0:
            # Floor coherency then call .on_zero_coherency()
            self._coherency = 0
            self.on_zero_coherency()
        else:
            # Apply the delta
            self._coherency += delta

    # Event-based methods
    def on_zero_coherency(self) -> None:
        """Overridable. Logic to be run just after this cogform's coherency is reduced to zero."""
        pass
