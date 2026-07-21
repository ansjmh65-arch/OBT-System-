from datetime import datetime
from .base import db

class LogSetting(db.Model):
    """إعدادات قنوات تفعيل السجلات بأنواعها."""
    __tablename__ = 'log_settings'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), unique=True, nullable=False, index=True)
    general_log_channel_id = db.Column(db.String(32), nullable=True)
    message_logs_enabled = db.Column(db.Boolean, default=True, nullable=False)
    voice_logs_enabled = db.Column(db.Boolean, default=True, nullable=False)
    member_logs_enabled = db.Column(db.Boolean, default=True, nullable=False)
    audit_logs_enabled = db.Column(db.Boolean, default=True, nullable=False)


class MessageLog(db.Model):
    """سجلات تعديل وحذف الرسائل."""
    __tablename__ = 'message_logs'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    message_id = db.Column(db.String(32), nullable=False, index=True)
    user_id = db.Column(db.String(32), nullable=False, index=True)
    channel_id = db.Column(db.String(32), nullable=False)
    content = db.Column(db.Text, nullable=True)
    action = db.Column(db.String(32), nullable=False)  # edit or delete
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class VoiceLog(db.Model):
    """سجلات الدخول والخروج من الرومات الصوتية."""
    __tablename__ = 'voice_logs'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    user_id = db.Column(db.String(32), nullable=False, index=True)
    channel_id = db.Column(db.String(32), nullable=True)
    action = db.Column(db.String(32), nullable=False)  # join, leave, move
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class MemberLog(db.Model):
    """سجلات تعديل الأسماء والألقاب."""
    __tablename__ = 'member_logs'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    user_id = db.Column(db.String(32), nullable=False, index=True)
    action = db.Column(db.String(64), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class AuditLog(db.Model):
    """سجلات الأحداث الإدارية الهامة (Audit Logs)."""
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    action_type = db.Column(db.String(64), nullable=False)
    executor_id = db.Column(db.String(32), nullable=False)
    target_id = db.Column(db.String(32), nullable=True)
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class CommandLog(db.Model):
    """سجل استخدام الأوامر وتتبع تفاعل المستخدمين."""
    __tablename__ = 'command_logs'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    user_id = db.Column(db.String(32), nullable=False, index=True)
    command_name = db.Column(db.String(64), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
  
