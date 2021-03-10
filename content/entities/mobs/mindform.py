from src.sigil import Sigil
from src.entity.entities import Mobile


class MindForm(Mobile):
    """A coherent, sapient entity. The buffer jack, or someone that's eluded them."""
    def __init__(self, name: str, size: int,
                 sigil: Sigil, base_move_cost: int,
                 recognizance: int,
                 deconstruction: int,
                 attention: int,
                 resolution: int,
                 empathy: int):

        def __check_args():
            """Wraps up the argument tests for MindForm generation."""
            if not (1 <= recognizance <= 100):
                raise ValueError("Argument 'recognizance' must be an integer in between 1 and 100")

            elif not (1 <= deconstruction <= 100):
                raise ValueError("Argument 'deconstruction' must be an integer in between 1 and 100")

            elif not (1 <= attention <= 100):
                raise ValueError("Argument 'attention' must be an integer in between 1 and 100")

            elif not (1 <= resolution <= 100):
                raise ValueError("Argument 'resolution' must be an integer between 1 and 100")

            elif not (1 <= empathy <= 100):
                raise ValueError("Argument 'empathy' must be an integer between 1 and 100")

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

    @property
    def recognizance(self) -> int:
        """Getter for MindForm.recognizance. Override to add modifier logic."""
        return self._recognizance

    @property
    def deconstruction(self) -> int:
        """Getter for MindForm.deconstruction. Override to add modifier logic."""
        return self._deconstruction

    @property
    def attention(self) -> int:
        """Getter for MindForm.attention. Override to add modifier logic."""
        return self._attention

    @property
    def resolution(self):
        """Getter for MindForm.resolution. Override to add modifier logic."""
        return self._resolution

    @property
    def empathy(self):
        """Getter for MindForm.empathy. Override to add modifier logic."""
        return self._empathy

    @recognizance.setter
    def recognizance(self, new_recog: int) -> None:
        if not (0 <= new_recog <= 100):
            raise ValueError("Argument 'new_recog' must be between 0 and 100 inclusive.")
        self._recognizance = new_recog

    @deconstruction.setter
    def deconstruction(self, new_decon: int) -> None:
        if not (0 <= new_decon <= 100):
            raise ValueError("Argument 'new_decon' must be between 0 and 100 inclusive.")
        self._deconstruction = new_decon

    @attention.setter
    def attention(self, new_atten: int) -> None:
        if not (0 <= new_atten <= 100):
            raise ValueError("Argument 'new_atten' must be between 0 and 100 inclusive.")
        self._attention = new_atten

    @resolution.setter
    def resolution(self, new_resol: int) -> None:
        if not (0 <= new_resol <= 100):
            raise ValueError("Argument 'new_resol' must be between 0 and 100 inclusive.")
        self._resolution = new_resol

    @empathy.setter
    def empathy(self, new_empth: int) -> None:
        if not (0 <= new_empth <= 100):
            raise ValueError("Argument 'new_empth' must be between 0 and 100 inclusive.")
        self._empathy = new_empth