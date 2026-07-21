# -*- coding: utf-8 -*-
import logging
from . import db

logger = logging.getLogger("OBT.Database")

class DatabaseManager:
    @staticmethod
    def initialize_database(app) -> None:
        with app.app_context():
            db.create_all()
            logger.info("Database schemas initialized and verified successfully.")
            
