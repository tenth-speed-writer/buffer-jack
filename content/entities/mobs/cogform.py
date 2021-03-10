from src.entity.entities import Mobile
from src.sigil import Sigil


class CogForm(Mobile):
    """TODO: Decide what stats these will have"""
    def __init__(self, name: str, size: int,
                 sigil: Sigil, base_move_cost: int,):
        super().__init__(name=name,
                         size=size,
                         sigil=sigil,
                         base_move_cost=base_move_cost)