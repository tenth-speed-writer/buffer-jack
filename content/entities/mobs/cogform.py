from src.sigil import Sigil
from .fooform import FooForm


class CogForm(FooForm):
    """TODO: Decide what stats these will have"""
    def __init__(self, name: str, size: int,
                 sigil: Sigil, base_move_cost: int,
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

        for stat in ("depth", "malignancy", "glimmer", "cogmass", "virality"):
            self.modifiers[stat] = []

    @property
    def base_depth(self) -> float:
        return self._depth

    @property
    def depth(self) -> float:
        return self._apply_modifiers_to("depth")

    @depth.setter
    def depth(self, new_depth: float) -> None:
        self._set_base_stat("depth", new_depth)

    @property
    def base_malignancy(self) -> float:
        return self._malignancy

    @property
    def malignancy(self) -> float:
        return self._apply_modifiers_to("malignancy")

    @malignancy.setter
    def malignancy(self, new_malig: float) -> None:
        self._set_base_stat("malignancy", new_malig)

    @property
    def base_glimmer(self) -> float:
        return self._glimmer

    @property
    def glimmer(self) -> float:
        return self._apply_modifiers_to("glimmer")

    @glimmer.setter
    def glimmer(self, new_glimm: float) -> None:
        self._set_base_stat("glimmer", new_glimm)

    @property
    def base_cogmass(self) -> float:
        return self._cogmass

    @property
    def cogmass(self) -> float:
        return self._apply_modifiers_to("cogmass")

    @cogmass.setter
    def cogmass(self, new_cmass: float) -> None:
        self._set_base_stat("cogmass", new_cmass)

    @property
    def base_virality(self) -> float:
        return self._virality
