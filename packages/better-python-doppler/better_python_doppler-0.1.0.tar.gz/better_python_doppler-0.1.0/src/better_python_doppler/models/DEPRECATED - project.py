# src\better_python_doppler\models\project.py

from datetime import datetime as DateTime

class ProjectModel:

    def __init__(
            self,
            id: str | None = None,
            name: str | None = None,
            description: str | None = None,
            created_at: DateTime | None = None,
        ) -> None:
        
        self._id:           str | None         = id
        self._name:         str | None         = name
        self._description:  str | None         = description
        self._created_at:   DateTime | None    = created_at

    @property
    def id(self) -> str | None:
        return self._id
    
    @property
    def name(self) -> str | None:
        return self._name
    
    @property
    def description(self) -> str | None:
        return self._description
    
    @property
    def created_at(self) -> DateTime | None:
        return self._created_at