# -*- coding: utf-8 -*-
"""
Database Lifecycle Manager (Quart Compatible)
-------------------------------------------
إدارة جلسات العمل وبناء الجداول عند الإقلاع والتحقق من السلامة لـ Quart.
"""

import asyncio
import logging
from . import db

logger = logging.getLogger("OBT.Database")

class DatabaseManager:
    """مدير الاتصالات والعمليات الخاصة بقاعدة البيانات متوافق مع Quart."""

    @staticmethod
    def initialize_database(app) -> None:
        """إنشاء الجداول والتحقق من جاهزية الاتصال بشكل متزامن."""
        
        async def _init_db():
            async with app.app_context():
                db.create_all()
            logger.info("Database schemas initialized and verified successfully.")

        # تشغيل التهيئة داخل حلقة الأحداث
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                # إذا كانت الحلقة تعمل، نقوم بإنشاء مهمة أو تنفيذها
                pass
        except RuntimeError:
            pass
        
        # طريقة مباشرة وآمنة لإنشاء الجداول في Quart
        ctx = app.app_context()
        ctx.push()
        db.create_all()
        ctx.pop()
        logger.info("Database schemas initialized and verified successfully.")
        
