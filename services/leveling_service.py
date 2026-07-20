from models import LevelUser
from database.database import db

class LevelingService:
    @staticmethod
    def add_xp(user_id: int, guild_id: int, xp_amount: int = 20):
        user = LevelUser.query.filter_by(user_id=user_id, guild_id=guild_id).first()
        if not user:
            user = LevelUser(user_id=user_id, guild_id=guild_id, xp=xp_amount, level=1)
            db.session.add(user)
        else:
            user.xp += xp_amount
            next_level_xp = user.level * 100
            if user.xp >= next_level_xp:
                user.level += 1
                user.xp = 0
        db.session.commit()
        return user.level
      
