from abc import ABC, abstractmethod
from typing import Dict, Generic, Optional, TypeVar

T = TypeVar("T")


class BaseRepository(Generic[T], ABC):
    """Abstract base repository interface."""

    @abstractmethod
    async def get(self, id: str) -> Optional[T]:
        """Get an item by ID."""
        pass

    @abstractmethod
    async def save(self, item: T) -> None:
        """Save an item."""
        pass

    @abstractmethod
    async def delete(self, id: str) -> bool:
        """Delete an item by ID."""
        pass

    @abstractmethod
    async def exists(self, id: str) -> bool:
        """Check if an item exists."""
        pass

    @abstractmethod
    async def get_all(self) -> Dict[str, T]:
        """Get all items."""
        pass
