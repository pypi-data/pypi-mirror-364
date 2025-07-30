# src\better_python_doppler\models\environment.py

from datetime import datetime as DateTime
from typing import Any

from .project import ProjectModel

class EnvironmentModel:

    def __init__(
            self,
            id: str | None = None,
            name: str | None = None,
            project: ProjectModel = ProjectModel(),
            created_at: DateTime | None = None,
            initial_fetch_at: DateTime | None = None,
        ) -> None:
        
        self._id:               str | None      = id
        self._name:             str | None      = name
        self._project:          ProjectModel         = project
        self._created_at:       DateTime | None = created_at
        self._initial_fetch_at: DateTime | None = initial_fetch_at


    @property
    def id(self) -> str | None:
        return self._id
    
    @property
    def name(self) -> str | None:
        return self._name
    
    @property
    def project(self) -> ProjectModel:
        return self._project
    
    @property
    def created_at(self) -> DateTime | None:
        return self._created_at
    
    @property
    def initial_fetch_at(self) -> DateTime | None:
        return self._initial_fetch_at
