# -*- coding: utf-8 -*-
"""
Database Lifecycle Manager (Quart Native Async)
---------------------------------------------
إدارة الجداول واتصالات قاعدة البيانات متوافقة 100% مع Quart و Asyncio.
"""

import logging
from . import db

logger = logging.getLogger("OBT.Database")

class DatabaseManager:
    """مدير قاعدة البيانات المتوافق مع Quart."""

    @staticmethod
    async def initialize_database(app) -> None:
        """إنشاء الجداول باستخدام سياق تطبيق Quart غير المتزامن."""
        try:
            async with app.app_context():
                db.create_all()
            logger.info("Database schemas initialized and verified successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise e
            
