import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index

db = SQLAlchemy()

class GuildSettings(db.Model):
    __tablename__ = 'guild_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), unique=True, nullable=False, index=True)
    prefix = db.Column(db.String(10), default="!", nullable=False)
    language = db.Column(db.String(5), default="ar", nullable=False)
    timezone = db.Column(db.String(50), default="UTC", nullable=False)
    embed_color = db.Column(db.String(10), default="#5865F2", nullable=False)
    modules_toggle = db.Column(db.JSON, default={}, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ProtectionSettings(db.Model):
    __tablename__ = 'protection_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), unique=True, nullable=False, index=True)
    anti_spam = db.Column(db.Boolean, default=True)
    anti_links = db.Column(db.Boolean, default=True)
    anti_raid = db.Column(db.Boolean, default=False)
    anti_nuke = db.Column(db.Boolean, default=True)
    punishment = db.Column(db.String(20), default="timeout") # timeout, kick, ban

class Ticket(db.Model):
    __tablename__ = 'tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    channel_id = db.Column(db.String(32), unique=True, nullable=False)
    user_id = db.Column(db.String(32), nullable=False, index=True)
    status = db.Column(db.String(20), default="open", index=True) # open, closed, claimed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class EconomyUser(db.Model):
    __tablename__ = 'economy_users'
    
    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    user_id = db.Column(db.String(32), nullable=False, index=True)
    wallet = db.Column(db.BigInteger, default=0, nullable=False)
    bank = db.Column(db.BigInteger, default=0, nullable=False)
    last_daily = db.Column(db.DateTime, nullable=True)
    
    __table_args__ = (
        Index('idx_guild_user_eco', 'guild_id', 'user_id', unique=True),
    )

class Clan(db.Model):
    __tablename__ = 'clans'
    
    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    name = db.Column(db.String(50), nullable=False)
    tag = db.Column(db.String(10), nullable=False)
    owner_id = db.Column(db.String(32), nullable=False)
    level = db.Column(db.Integer, default=1, nullable=False)
    points = db.Column(db.BigInteger, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ContentCreator(db.Model):
    __tablename__ = 'content_creators'
    
    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    user_id = db.Column(db.String(32), nullable=False, index=True)
    platform = db.Column(db.String(30), nullable=False) # youtube, twitch, tiktok
    channel_url = db.Column(db.String(255), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class LevelUser(db.Model):
    __tablename__ = 'level_users'
    
    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    user_id = db.Column(db.String(32), nullable=False, index=True)
    xp = db.Column(db.BigInteger, default=0, nullable=False)
    level = db.Column(db.Integer, default=0, nullable=False)
    
    __table_args__ = (
        Index('idx_guild_user_lvl', 'guild_id', 'user_id', unique=True),
    )
    
