class BaseStone:
    def __init__(self,name:str,value:int) -> None:
        """
        Base para la creacion de mas Stones, donde debera usarse el metodo apply() para configurar su efecto.

        Args:
            name (str): Nombre de la piedra, generalmente se usa un color.
            value (int): Valor de la piedra.
        """
        self._name = name
        self._value = max(value,0)

    @property
    def name(self) -> str:
        """
        Retorna el nombre de la piedra.
        """
        return self._name.upper()
    
    @property
    def value(self) -> int:
        """
        Retorna el valor de la piedra.
        """
        return self._value
    
    def apply(self,letter:str,source_alphabet:str = None,target_alphabet:str = None,isEncrypted:bool = False) -> str:
        """
        Efecto de la Stone, donde se decidira de que manera se cambiara la letra.

        Args:
            letter (str): Letra que se cambiara.
            source_alphabet (str): El alfabeto de origen del que se tomara el indice de la letra.
            target_alphabet (str): El alfabeto objetivo del que se usara la letra para sustituir.
            isEncrypted (bool): Esta encriptada o no esta encriptada.

        Returns:
            str: Letra transformada.
        """
        return letter

    def __str__(self) -> str:
        return f"{self.name}:{self.value}"
    
    def __repr__(self) -> str:
        return f"Stone(name={self.name},value={self.value})"
    
    def __eq__(self, other:"BaseStone") -> bool:
        if isinstance(other,BaseStone):
            return self.name == other.name
        return False
    
    def __add__(self,other:"BaseStone") -> "BaseStone":
        if isinstance(other,BaseStone) and self == other:
            new_value  = self.value+other.value
            return self.__class__(new_value)
        return NotImplementedError