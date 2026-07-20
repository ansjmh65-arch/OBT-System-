from models import EconomyUser
from database.database import db

class EconomyService:
    @staticmethod
    def get_balance(user_id: int, guild_id: int):
        user = EconomyUser.query.filter_by(user_id=user_id, guild_id=guild_id).first()
        if not user:
            user = EconomyUser(user_id=user_id, guild_id=guild_id, balance=1000)
            db.session.add(user)
            db.session.commit()
        return user.balance

    @staticmethod
    def update_balance(user_id: int, guild_id: int, amount: int):
        user = EconomyUser.query.filter_by(user_id=user_id, guild_id=guild_id).first()
        if not user:
            user = EconomyUser(user_id=user_id, guild_id=guild_id, balance=1000 + amount)
            db.session.add(user)
        else:
            user.balance += amount
        db.session.commit()
        return user.balance
      
