from src.sigil import Sigil
from .fooform import FooForm


class MindForm(FooForm):
    """A coherent, sapient entity. The buffer jack, or someone that's eluded them."""

    def __init__(self, name: str, size: int,
                 sigil: Sigil, base_move_cost: int,
                 recognizance: float,
                 deconstruction: float,
                 attention: float,
                 resolution: float,
                 empathy: float):

        def __check_args():
            """Wraps up the argument tests for MindForm generation."""
            if not (1 <= recognizance <= 100):
                raise ValueError("Argument 'recognizance' must be an float in between 1 and 100")

            elif not (1 <= deconstruction <= 100):
                raise ValueError("Argument 'deconstruction' must be an float in between 1 and 100")

            elif not (1 <= attention <= 100):
                raise ValueError("Argument 'attention' must be an float in between 1 and 100")

            elif not (1 <= resolution <= 100):
                raise ValueError("Argument 'resolution' must be an float between 1 and 100")

            elif not (1 <= empathy <= 100):
                raise ValueError("Argument 'empathy' must be an float between 1 and 100")

        __check_args()
        super().__init__(name=name,
                         size=size,
                         sigil=sigil,
                         base_move_cost=base_move_cost)

        self._recognizance = recognizance
        self._deconstruction = deconstruction
        self._attention = attention
        self._resolution = resolution
        self._empathy = empathy

        self._stress = 0

        # Initialize empty lists in the .modifiers dict for each assigned stat
        for stat in ("recognizance",
                     "deconstruction",
                     "attention",
                     "resolution",
                     "empathy",

                     "max_stress",
                     "stress_gain",   # Applied to stress_delta when change is positive
                     "stress_loss"):  # Applied to stress_delta when change is negative
            self.modifiers[stat] = []

    @property
    def base_recognizance(self) -> float:
        """Getter for MindForm.recognizance. Override to add modifier logic."""
        return self._recognizance

    @property
    def recognizance(self):
        return self._apply_modifiers_to("recognizance")

    @property
    def base_deconstruction(self) -> float:
        """Getter for MindForm.deconstruction. Override to add modifier logic."""
        return self._deconstruction

    @property
    def deconstruction(self) -> float:
        return self._apply_modifiers_to("recognizance")

    @deconstruction.setter
    def deconstruction(self, new_decon: float) -> None:
        self._set_base_stat("deconstruction", new_decon)

    @property
    def base_attention(self) -> float:
        """Getter for MindForm.attention. Override to add modifier logic."""
        return self._attention

    @property
    def attention(self) -> float:
        return self._apply_modifiers_to("attention")

    @attention.setter
    def attention(self, new_atten: float) -> None:
        self._set_base_stat("attention", new_atten)

    @property
    def base_resolution(self) -> float:
        """Getter for MindForm.resolution. Override to add modifier logic."""
        return self._resolution

    @property
    def resolution(self) -> float:
        return self._apply_modifiers_to("resolution")

    @resolution.setter
    def resolution(self, new_resol: float) -> None:
        self._set_base_stat("resolution", new_resol)

    @property
    def base_empathy(self) -> float:
        """Getter for MindForm.empathy. Override to add modifier logic."""
        return self._empathy

    @property
    def empathy(self) -> float:
        return self._apply_modifiers_to("empathy")

    @empathy.setter
    def empathy(self, new_empth: float) -> None:
        self._set_base_stat("empathy", new_empth)

    def max_stress(self,
                   recog_weight: float = 0.2,
                   resol_weight: float = 0.5,
                   decon_weight: float = 0.2,
                   atten_weight: float = 0.1,
                   empth_weight: float = -0.1) -> float:
        """Calculates and returns the critical stress at which the MindForm loses cohesion.
        For the player this means a traumatic jack-out and for other things it means...

        All stats affect max stress to varying degrees.
        High resolution makes the most difference; high empathy actually hurts it."""
        stat_sum = sum((recog_weight * self.recognizance,
                        resol_weight * self.resolution,
                        decon_weight * self.deconstruction,
                        atten_weight * self.attention,
                        empth_weight * self.empathy))

        return self._apply_blind_modifiers_to(stat="max_stress",
                                              initial_val=stat_sum)

    @property
    def stress(self):
        return self._stress

    @stress.setter
    def stress(self, new_stress):
        """Sets the stress of this creature to a specified value. Use for mechanical reasons;
        for gameplay, .stress_delta() is preferred as it calls on_critical_stress."""
        self._stress = new_stress

    def on_critical_stress(self):
        """By default, remove this MindForm from the playfield and print to the gamelog about it.
        Override and call in order to add what more-or-less amounts to on-death logic."""
        self.playfield.interface.print_to_log("{} jacks out due to extreme duress!"
                                              .format(self.name))
        self.destroy()

    def stress_delta(self, change_in_stress: float):
        """Changes this MindForm's stress by some quantity, flooring it at 0
        and capping it + calling on_critical_stress at self.max_stress().

        Override and call to add behavior on stress change."""

        max_stress = self.max_stress()

        # Apply stress_gain or stress_loss modifiers, as appropriate
        if change_in_stress > 0:
            delta = self._apply_blind_modifiers_to(stat="stress_gain",
                                                   initial_val=change_in_stress)
        else:
            delta = self._apply_blind_modifiers_to(stat="stress_loss",
                                                   initial_val=change_in_stress)

        if self.stress + delta < 0:
            # Floor minimum stress at 0
            self.stress = float(0)
        elif self.stress + delta >= max_stress:
            # Cap max stress at max_stress and also call self.on_critical_stress()
            self.stress = self.max_stress()
            self.on_critical_stress()
        else:
            # Just apply the delta
            self.stress += delta
