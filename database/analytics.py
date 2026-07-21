from datetime import datetime
from .base import db

class Statistic(db.Model):
    """إحصائيات السيرفر العامة الحالية."""
    __tablename__ = 'statistics'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), unique=True, nullable=False, index=True)
    total_messages = db.Column(db.Integer, default=0, nullable=False)
    total_commands_used = db.Column(db.Integer, default=0, nullable=False)
    active_voice_members = db.Column(db.Integer, default=0, nullable=False)


class PerformanceMetric(db.Model):
    """مقاييس الأداء واستجابة البوت (Performance Metrics)."""
    __tablename__ = 'performance_metrics'

    id = db.Column(db.Integer, primary_key=True)
    shard_id = db.Column(db.Integer, default=0, nullable=False)
    latency_ms = db.Column(db.Float, nullable=False)
    cpu_usage = db.Column(db.Float, nullable=True)
    ram_usage = db.Column(db.Float, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class BotStatistic(db.Model):
    """إحصائيات البوت الكلية على مستوى جميع السيرفرات."""
    __tablename__ = 'bot_statistics'

    id = db.Column(db.Integer, primary_key=True)
    total_guilds = db.Column(db.Integer, default=0, nullable=False)
    total_users = db.Column(db.Integer, default=0, nullable=False)
    total_channels = db.Column(db.Integer, default=0, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class ErrorLog(db.Model):
    """سجلات أخطاء النظام والاستثناءات (Error Logs)."""
    __tablename__ = 'error_logs'

    id = db.Column(db.Integer, primary_key=True)
    error_message = db.Column(db.Text, nullable=False)
    traceback_text = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class CacheMetadata(db.Model):
    """بيانات التخزين المؤقت وتتبع الـ Cache."""
    __tablename__ = 'cache_metadata'

    id = db.Column(db.Integer, primary_key=True)
    cache_key = db.Column(db.String(128), unique=True, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
  
