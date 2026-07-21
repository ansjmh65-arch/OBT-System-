# -*- coding: utf-8 -*-
"""
OBT System - Central Configuration Manager
------------------------------------------
مسؤول عن تحميل والتحقق من صحة جميع متغيرات البيئة وإعدادات النظام للإنتاج.
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """فئة الإعدادات العامة لجميع المكونات والبيئات."""
    ENV = os.getenv("FLASK_ENV", "production")
    DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    SECRET_KEY = os.getenv("SECRET_KEY", "obt-enterprise-ultra-secure-secret-2026-key")
    PORT = int(os.getenv("PORT", 5000))
    
    DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
    BOT_PREFIX = os.getenv("BOT_PREFIX", "!")
    
    DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///obt_system.db")
    SQLALCHEMY_DATABASE_URI = DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID", "")
    DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET", "")
    DISCORD_REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI", "http://localhost:5000/auth/callback")
    
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    USE_REDIS = os.getenv("USE_REDIS", "False").lower() in ("true", "1", "t")

    @classmethod
    def validate(cls) -> None:
        if not cls.DISCORD_BOT_TOKEN:
            raise ValueError("الحرج الأمني: متغير DISCORD_BOT_TOKEN غير موجود في ملف .env!")
            
