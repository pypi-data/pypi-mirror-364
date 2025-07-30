# src\better_python_doppler\models\secret.py

class SecretValue():

    def __init__(
            self,
            raw: str | None = None,
            computed: str | None = None,
            note: str | None = None
        ) -> None:

        self._raw:      str | None = raw
        self._computed: str | None = computed 
        self._note:     str | None = note

    @property
    def raw(self) -> str | None:
        return self._raw
    
    @property
    def computed(self) -> str | None:
        return self._computed
    
    @property
    def note(self) -> str | None:
        return self._note
    
    @raw.setter
    def raw(self, raw: str) -> None:
        self._raw = raw
    
    @note.setter
    def note(self, note: str) -> None:
        self._note = note

    def __str__(self) -> str:
        temp = {'raw': self._raw, 'computed': self._computed, 'note': self._note}
        return str(temp)
    
    def dict(self)-> dict:
        return {'raw': self._raw, 'computed': self._computed, 'note': self._note}
    
    


class SecretModel():

    def __init__(
            self,
            name: str | None = None,
            value: SecretValue = SecretValue() 
        ) -> None:
        
        self._name: str | None = name
        self._value: SecretValue = value 

    @property
    def name(self) -> str | None:
        return self._name
    
    @property
    def value(self) -> SecretValue:
        return self._value
    
    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    def key_value(self) -> str:
        return f"'{self._name}': '{self._value.raw}'"