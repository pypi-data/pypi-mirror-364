from abc import ABC, abstractmethod
from typing import Any, final


class AbstractSerializer(ABC):
    _Instance = None

    @final
    def __new__(cls, *args, **kwargs):  # 序列器一定是单例的
        if cls._Instance is None:
            cls._Instance = super().__new__(cls, *args, **kwargs)
        return cls._Instance

    @abstractmethod
    def dumps(self, data) -> bytes:
        ...
    
    @abstractmethod
    def dump(self, fp) -> None:
        ...

    @abstractmethod
    def loads(self, data) -> Any:
        ...
    
    @abstractmethod
    def load(self, fp) -> Any:
        ...
