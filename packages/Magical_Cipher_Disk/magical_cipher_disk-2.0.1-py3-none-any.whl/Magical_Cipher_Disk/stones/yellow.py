from .base import BaseStone

class YellowStone(BaseStone):
    def __init__(self, value):
        self._modifier_limit = 4
        super().__init__("YELLOW", value%self._modifier_limit)

    def __add__(self,other:BaseStone) -> "YellowStone":
        """
        Las piedras de este color Yellow deben tener un maximo de valor de 4, por lo que cada suma se calculara usando el modulo con 4.
        """
        if isinstance(other,BaseStone) and self == other:
            new_value = (self._value+other._value)%self._modifier_limit
            return YellowStone(new_value)
        return NotImplementedError