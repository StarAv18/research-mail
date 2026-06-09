import json
import os
import portalocker
from typing import List, Optional, TypeVar, Type, Generic, Any
from uuid import UUID
from pydantic import BaseModel
from app.repository.base import BaseRepository
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)

class BaseJSONRepository(BaseRepository[T], Generic[T]):
    """
    Common logic for JSON file-based repositories.
    Provides thread-safe and process-safe file operations using portalocker.
    """

    def __init__(self, filename: str, model_class: Type[T]):
        settings = get_settings()
        self.storage_path = os.path.join(settings.DATA_DIR, filename)
        self.model_class = model_class
        self._ensure_storage_exists()

    def _ensure_storage_exists(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, 'w') as f:
                json.dump([], f)

    async def create(self, entity: T) -> T:
        with portalocker.Lock(self.storage_path, mode='r+', timeout=5) as f:
            data = json.load(f)
            data.append(json.loads(entity.model_dump_json()))
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=2)
        return entity

    async def get_by_id(self, id: UUID) -> Optional[T]:
        items = await self.list_all()
        # Note: items are already model instances
        return next((item for item in items if getattr(item, 'id', None) == id), None)

    async def update(self, id: UUID, updated_entity: T) -> T:
        with portalocker.Lock(self.storage_path, mode='r+', timeout=5) as f:
            data = json.load(f)
            found = False
            for i, item in enumerate(data):
                if item.get('id') == str(id):
                    data[i] = json.loads(updated_entity.model_dump_json())
                    found = True
                    break
            
            if not found:
                raise ValueError(f"Entity with ID {id} not found")
                
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=2)
        return updated_entity

    async def delete(self, id: UUID) -> bool:
        with portalocker.Lock(self.storage_path, mode='r+', timeout=5) as f:
            data = json.load(f)
            initial_len = len(data)
            data = [item for item in data if item.get('id') != str(id)]
            
            if len(data) < initial_len:
                f.seek(0)
                f.truncate()
                json.dump(data, f, indent=2)
                return True
        return False

    async def list_all(self) -> List[T]:
        try:
            with portalocker.Lock(self.storage_path, mode='r', timeout=5) as f:
                data = json.load(f)
                return [self.model_class(**item) for item in data]
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Error reading from {self.storage_path}: {e}")
            return []
