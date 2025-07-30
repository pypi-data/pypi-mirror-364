# src\better_python_doppler\models\config.py

from datetime import datetime as DateTime

from .project import ProjectModel
from .environment import EnvironmentModel

class ConfigModel:

    def __init__(
            self,
            name: str | None = None,
            project: ProjectModel = ProjectModel(),
            environment: EnvironmentModel = EnvironmentModel(),
            created_at: DateTime | None = None,
            initial_fetch_at: DateTime | None = None,
            last_fetch_at: DateTime | None = None,
            root: bool | None = None,
            locked: bool | None = None
        ) -> None:
        
        self._name:             str | None      = name 
        self._project:          ProjectModel         = project
        self._environment:      EnvironmentModel     = environment
        self._created_at:       DateTime | None = created_at
        self._initial_fetch_at: DateTime | None = initial_fetch_at
        self._last_fetch_at:    DateTime | None = last_fetch_at
        self._root:             bool | None     = root
        self._locked:           bool | None     = locked
    
    @property
    def name(self) -> str | None:
        return self._name
    
    @property
    def project(self) -> ProjectModel:
        return self._project
    
    @property
    def environment(self) -> EnvironmentModel:
        return self._environment
    
    @property
    def created_at(self) -> DateTime | None:
        return self._created_at
    
    @property
    def initial_fetch_at(self) -> DateTime | None:
        return self._initial_fetch_at
    
    @property
    def last_fetch_at(self) -> DateTime | None:
        return self._last_fetch_at
    
    @property
    def root(self) -> bool | None:
        return self._root
    
    @property
    def locked(self) -> bool | None:
        return self._locked