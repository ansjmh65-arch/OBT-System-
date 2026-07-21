# -*- coding: utf-8 -*-
from datetime import datetime
from . import db

class ServerConfigModel(db.Model):
    __tablename__ = 'server_configs'
    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), unique=True, nullable=False, index=True)
    prefix = db.Column(db.String(10), default="!", nullable=False)
    language = db.Column(db.String(10), default="ar", nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class UserModel(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(32), unique=True, nullable=False, index=True)
    username = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class EconomyModel(db.Model):
    __tablename__ = 'economy'
    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    user_id = db.Column(db.String(32), nullable=False, index=True)
    balance = db.Column(db.Integer, default=100, nullable=False)
    bank = db.Column(db.Integer, default=0, nullable=False)
    __table_args__ = (db.UniqueConstraint('guild_id', 'user_id', name='_guild_user_economy_uc'),)

class AuditLogModel(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    action = db.Column(db.String(128), nullable=False)
    executor_id = db.Column(db.String(32), nullable=False)
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
  
