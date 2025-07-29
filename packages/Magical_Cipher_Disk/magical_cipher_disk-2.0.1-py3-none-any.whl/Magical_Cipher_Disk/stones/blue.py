from .base import BaseStone

class BlueStone(BaseStone):
    def __init__(self, value):
        super().__init__("BLUE", value)

    def apply(self,letter:str,source_alphabet:str = None,target_alphabet:str = None,isEncrypted:bool = False) -> str:
        """
        Aplica una transformacion a la letra, cambiando su posicion al exacto opuesto en el alfabeto.
        """
        len_alphabet = int(len(source_alphabet)/2)
        direction = -1 if isEncrypted else 1
        _index = (target_alphabet.index(str.upper(letter))+len_alphabet*direction)%len(target_alphabet)
        return str.upper(target_alphabet[_index])