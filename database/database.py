# -*- coding: utf-8 -*-
"""
Database Lifecycle Manager (Quart Compatible)
-------------------------------------------
إدارة الجداول بمرونة تامة وتوافق كامل مع Quart.
"""

import logging
from sqlalchemy import create_engine
from . import db

logger = logging.getLogger("OBT.Database")

class DatabaseManager:
    """مدير قاعدة البيانات المتوافق مع Quart و SQLAlchemy."""

    @staticmethod
    async def initialize_database(app) -> None:
        """إنشاء الجداول مباشرة لتفادي مشاكل السياق مع Quart."""
        try:
            # 1. جلب رابط قاعدة البيانات من إعدادات التطبيق أو ملف Config
            db_uri = app.config.get("SQLALCHEMY_DATABASE_URI") or "sqlite:///obt.db"
            
            # 2. إنشاء محرك الاتصال بـ SQLAlchemy وبناء الجداول مباشرة
            engine = create_engine(db_uri)
            db.metadata.create_all(bind=engine)
            
            logger.info("Database schemas initialized and verified successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise e
            
