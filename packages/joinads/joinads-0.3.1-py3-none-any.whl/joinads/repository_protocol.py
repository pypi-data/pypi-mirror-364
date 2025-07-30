from typing import Protocol, TypeVar, List

T = TypeVar('T')

class RepositoryProtocol(Protocol[T]):
    @classmethod
    def all(cls) -> List[T]: ...
    
    @classmethod
    def where(cls, **kwargs) -> List[T]: ...
