from models import ContentCreator
from database.database import db

class CreatorService:
    @staticmethod
    def register_creator(guild_id: int, user_id: int, platform: str):
        creator = ContentCreator(guild_id=guild_id, user_id=user_id, platform=platform)
        db.session.add(creator)
        db.session.commit()
        return creator
      
