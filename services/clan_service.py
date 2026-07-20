from models import Clan
from database.database import db

class ClanService:
    @staticmethod
    def create_clan(guild_id: int, name: str, owner_id: int):
        clan = Clan(guild_id=guild_id, name=name, owner_id=owner_id, points=0)
        db.session.add(clan)
        db.session.commit()
        return clan
      
