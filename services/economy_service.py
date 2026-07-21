# -*- coding: utf-8 -*-
import logging
from database.models import EconomyModel
from database import db

logger = logging.getLogger("OBT.Services")

class EconomyService:
    @staticmethod
    def get_balance(guild_id: str, user_id: str) -> int:
        account = EconomyModel.query.filter_by(guild_id=guild_id, user_id=user_id).first()
        if not account:
            account = EconomyModel(guild_id=guild_id, user_id=user_id, balance=100, bank=0)
            db.session.add(account)
            db.session.commit()
        return account.balance

    @staticmethod
    def add_balance(guild_id: str, user_id: str, amount: int) -> int:
        account = EconomyModel.query.filter_by(guild_id=guild_id, user_id=user_id).first()
        if not account:
            account = EconomyModel(guild_id=guild_id, user_id=user_id, balance=100 + amount, bank=0)
            db.session.add(account)
        else:
            account.balance += amount
        db.session.commit()
        return account.balance
        
