from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar, Any
from uuid import UUID

T = TypeVar("T")

class BaseRepository(ABC, Generic[T]):
    """
    Abstract base class for all repositories.
    """
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        """Persist a new entity."""
        pass

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[T]:
        """Retrieve an entity by its unique ID."""
        pass

    @abstractmethod
    async def update(self, id: UUID, entity: T) -> T:
        """Update an existing entity."""
        pass

    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        """Remove an entity from persistence."""
        pass

    @abstractmethod
    async def list_all(self) -> List[T]:
        """Retrieve all entities."""
        pass
