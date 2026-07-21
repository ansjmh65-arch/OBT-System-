# -*- coding: utf-8 -*-
import logging
from sqlalchemy import create_engine
from . import db

logger = logging.getLogger("OBT.Database")

class DatabaseManager:
    @staticmethod
    async def initialize_database(app) -> None:
        """تهيئة قاعدة البيانات بشكل مباشر لتفادي أخطاء الـ Context"""
        try:
            # إنشاء اتصال مباشر بقاعدة البيانات (يفضل استخدام مسار ملفك الفعلي)
            # إذا كان لديك مسار مختلف ضعه هنا بدلاً من sqlite:///database.db
            engine = create_engine("sqlite:///database.db")
            
            # بناء الجداول مباشرة باستخدام المحرك متجاهلين Flask تماماً
            db.metadata.create_all(engine)
            
            logger.info("Database schemas initialized successfully without Flask context!")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            
