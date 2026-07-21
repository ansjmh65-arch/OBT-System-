from datetime import datetime
from .base import db

class ServerConfig(db.Model):
    """جدول إعدادات السيرفر الأساسية (Guild Configuration)."""
    __tablename__ = 'server_configs'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), unique=True, nullable=False, index=True)
    guild_name = db.Column(db.String(128), nullable=True)
    prefix = db.Column(db.String(10), default="!", nullable=False)
    language = db.Column(db.String(10), default="ar", nullable=False)
    timezone = db.Column(db.String(64), default="UTC", nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class SystemSetting(db.Model):
    """إعدادات النظام العامة الخاصة بالبوت."""
    __tablename__ = 'system_settings'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False, index=True)
    value = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class FeatureFlag(db.Model):
    """أعلام الميزات (Feature Flags) لتفعيل أو تعطيل ميزات معينة عالمياً أو لسيرفرات محددة."""
    __tablename__ = 'feature_flags'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=True, index=True)  # إذا كان فارغاً فهو مطبق عالمياً
    feature_name = db.Column(db.String(64), nullable=False, index=True)
    is_enabled = db.Column(db.Boolean, default=False, nullable=False)


class BlacklistWhitelist(db.Model):
    """نظام الحظر والسماح (Blacklist / Whitelist) للمستخدمين أو السيرفرات."""
    __tablename__ = 'blacklist_whitelists'

    id = db.Column(db.Integer, primary_key=True)
    target_id = db.Column(db.String(32), nullable=False, index=True)  # User ID or Guild ID
    target_type = db.Column(db.String(16), nullable=False)  # 'user' or 'guild'
    list_type = db.Column(db.String(16), nullable=False)  # 'blacklist' or 'whitelist'
    reason = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class RateLimit(db.Model):
    """تتبع معدل الطلبات (Rate Limits) لمنع إساءة الاستخدام."""
    __tablename__ = 'rate_limits'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(128), nullable=False, index=True)
    calls = db.Column(db.Integer, default=1, nullable=False)
    reset_at = db.Column(db.DateTime, nullable=False)
  
