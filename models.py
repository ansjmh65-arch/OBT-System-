# -*- coding: utf-8 -*-
"""
OBT-System Database Models
--------------------------
Defines all SQLAlchemy database models used across Cogs and Services.
"""

import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, BigInteger, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class EconomyUser(Base):
    __tablename__ = 'economy_users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, unique=True, index=True, nullable=False)
    guild_id = Column(BigInteger, index=True, nullable=False)
    balance = Column(Float, default=0.0)
    bank = Column(Float, default=0.0)
    last_daily = Column(DateTime, nullable=True)


class LevelUser(Base):
    __tablename__ = 'level_users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, index=True, nullable=False)
    guild_id = Column(BigInteger, index=True, nullable=False)
    xp = Column(Integer, default=0)
    level = Column(Integer, default=0)
    total_messages = Column(Integer, default=0)


class Clan(Base):
    __tablename__ = 'clans'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    owner_id = Column(BigInteger, nullable=False)
    level = Column(Integer, default=1)
    xp = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class ProtectionSettings(Base):
    __tablename__ = 'protection_settings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, unique=True, index=True, nullable=False)
    anti_spam = Column(Boolean, default=True)
    anti_link = Column(Boolean, default=False)
    anti_bot = Column(Boolean, default=True)
    anti_raid = Column(Boolean, default=False)
    max_mentions = Column(Integer, default=5)


class Ticket(Base):
    __tablename__ = 'tickets'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(String(50), unique=True, index=True, nullable=False)
    guild_id = Column(BigInteger, index=True, nullable=False)
    channel_id = Column(BigInteger, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    status = Column(String(20), default="open")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class ContentCreator(Base):
    __tablename__ = 'content_creators'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, unique=True, index=True, nullable=False)
    guild_id = Column(BigInteger, index=True, nullable=False)
    platform = Column(String(50), nullable=False) # e.g., YouTube, Twitch, TikTok
    channel_url = Column(String(255), nullable=False)
    verified = Column(Boolean, default=False)
    added_at = Column(DateTime, default=datetime.datetime.utcnow)
    
