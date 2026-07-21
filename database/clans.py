from datetime import datetime
from .base import db

class ClanSetting(db.Model):
    """إعدادات نظام الكلانات."""
    __tablename__ = 'clan_settings'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), unique=True, nullable=False, index=True)
    clans_enabled = db.Column(db.Boolean, default=True, nullable=False)
    max_members_per_clan = db.Column(db.Integer, default=10, nullable=False)
    clan_creation_cost = db.Column(db.Integer, default=1000, nullable=False)


class Clan(db.Model):
    """بيانات الكلان الأساسية."""
    __tablename__ = 'clans'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    tag = db.Column(db.String(16), nullable=False)
    owner_id = db.Column(db.String(32), nullable=False)
    level = db.Column(db.Integer, default=1, nullable=False)
    bank_balance = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    members = db.relationship('ClanMember', backref='clan', lazy=True, cascade="all, delete-orphan")
    statistics = db.relationship('ClanStatistic', backref='clan', uselist=False, cascade="all, delete-orphan")


class ClanMember(db.Model):
    """أعضاء الكلان والأدوار داخله."""
    __tablename__ = 'clan_members'

    id = db.Column(db.Integer, primary_key=True)
    clan_id = db.Column(db.Integer, db.ForeignKey('clans.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.String(32), nullable=False, index=True)
    role = db.Column(db.String(32), default="member", nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class ClanStatistic(db.Model):
    """إحصائيات الكلان (نقاط، حروب، تفاعل)."""
    __tablename__ = 'clan_statistics'

    id = db.Column(db.Integer, primary_key=True)
    clan_id = db.Column(db.Integer, db.ForeignKey('clans.id', ondelete='CASCADE'), unique=True, nullable=False, index=True)
    total_points = db.Column(db.Integer, default=0, nullable=False)
    wins = db.Column(db.Integer, default=0, nullable=False)
    losses = db.Column(db.Integer, default=0, nullable=False)


class ClanWar(db.Model):
    """سجل حروب الكلانات والتحديات."""
    __tablename__ = 'clan_wars'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    clan_one_id = db.Column(db.Integer, db.ForeignKey('clans.id', ondelete='CASCADE'), nullable=False)
    clan_two_id = db.Column(db.Integer, db.ForeignKey('clans.id', ondelete='CASCADE'), nullable=False)
    winner_clan_id = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(32), default="active", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class ClanLog(db.Model):
    """سجلات نشاطات الكلان."""
    __tablename__ = 'clan_logs'

    id = db.Column(db.Integer, primary_key=True)
    clan_id = db.Column(db.Integer, db.ForeignKey('clans.id', ondelete='CASCADE'), nullable=False, index=True)
    action = db.Column(db.String(128), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
  
