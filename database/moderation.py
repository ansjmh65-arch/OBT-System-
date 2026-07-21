from datetime import datetime
from .base import db

class SecuritySetting(db.Model):
    """إعدادات الحماية والأمان العامة للسيرفر."""
    __tablename__ = 'security_settings'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), unique=True, nullable=False, index=True)
    anti_spam = db.Column(db.Boolean, default=True, nullable=False)
    anti_link = db.Column(db.Boolean, default=True, nullable=False)
    anti_invite = db.Column(db.Boolean, default=True, nullable=False)
    anti_raid = db.Column(db.Boolean, default=False, nullable=False)
    max_mentions = db.Column(db.Integer, default=5, nullable=False)
    punishment_duration = db.Column(db.Integer, default=600, nullable=False)


class ModerationSetting(db.Model):
    """إعدادات المشرفين والعقوبات."""
    __tablename__ = 'moderation_settings'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), unique=True, nullable=False, index=True)
    mute_role_id = db.Column(db.String(32), nullable=True)
    max_warnings = db.Column(db.Integer, default=3, nullable=False)
    warning_action = db.Column(db.String(32), default="mute", nullable=False)
    mod_logs_channel_id = db.Column(db.String(32), nullable=True)


class Warning(db.Model):
    """سجل التحذيرات الموجهة للأعضاء."""
    __tablename__ = 'warnings'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    user_id = db.Column(db.String(32), nullable=False, index=True)
    moderator_id = db.Column(db.String(32), nullable=False)
    reason = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Punishment(db.Model):
    """العقوبات الفعالة أو السابقة (Mute, Ban, Timeout)."""
    __tablename__ = 'punishments'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    user_id = db.Column(db.String(32), nullable=False, index=True)
    action_type = db.Column(db.String(32), nullable=False)
    reason = db.Column(db.Text, nullable=True)
    moderator_id = db.Column(db.String(32), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Report(db.Model):
    """البلاغات المقدمة من الأعضاء ضد بعضهم البعض."""
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    reporter_id = db.Column(db.String(32), nullable=False, index=True)
    target_id = db.Column(db.String(32), nullable=False, index=True)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(32), default="pending", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Appeal(db.Model):
    """الطعون أو طلبات رفع العقوبات."""
    __tablename__ = 'appeals'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    user_id = db.Column(db.String(32), nullable=False, index=True)
    punishment_id = db.Column(db.Integer, db.ForeignKey('punishments.id', ondelete='CASCADE'), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(32), default="pending", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
                        
