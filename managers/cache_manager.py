# -*- coding: utf-8 -*-
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("OBT.Managers")

class CacheManager:
    def __init__(self) -> None:
        self._store: Dict[str, Any] = {}
        logger.info("Hybrid CacheManager initialized.")

    async def get(self, key: str) -> Optional[Any]:
        return self._store.get(key)

    async def set(self, key: str, value: Any, ttl: int = 300) -> None:
        self._store[key] = value
      
