# -*- coding: utf-8 -*-

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from .models import Base


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///obt_system.db"
)


engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={
        "check_same_thread": False
    } if DATABASE_URL.startswith("sqlite") else {}
)


SessionLocal = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
)


def init_database():
    """
    إنشاء جميع جداول قاعدة البيانات
    """
    Base.metadata.create_all(
        bind=engine
    )


def get_db():
    """
    جلسة قاعدة البيانات
    """
    db = SessionLocal()

    try:
        return db

    finally:
        db.close()


def close_database():
    """
    إغلاق الاتصال
    """
    SessionLocal.remove()
