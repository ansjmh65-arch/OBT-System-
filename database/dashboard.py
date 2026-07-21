from datetime import datetime
from .base import db

class EmbedTemplate(db.Model):
    """قوالب الإيمبدز الجاهزة للاستخدام في السيرفر."""
    __tablename__ = 'embed_templates'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    template_name = db.Column(db.String(64), nullable=False, index=True)
    title = db.Column(db.String(256), nullable=True)
    description = db.Column(db.Text, nullable=True)
    color = db.Column(db.String(16), default="#5865F2", nullable=True)
    footer_text = db.Column(db.String(256), nullable=True)


class Form(db.Model):
    """النماذج واستطلاعات التقديم (Forms & Applications)."""
    __tablename__ = 'forms'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    title = db.Column(db.String(128), nullable=False)

    fields = db.relationship('FormField', backref='form', lazy=True, cascade="all, delete-orphan")
    submissions = db.relationship('FormSubmission', backref='form', lazy=True, cascade="all, delete-orphan")


class FormField(db.Model):
    """حقول النموذج المخصص."""
    __tablename__ = 'form_fields'

    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey('forms.id', ondelete='CASCADE'), nullable=False, index=True)
    label = db.Column(db.String(128), nullable=False)
    field_type = db.Column(db.String(32), default="text", nullable=False)
    is_required = db.Column(db.Boolean, default=True, nullable=False)


class FormSubmission(db.Model):
    """تقديمات النماذج من قبل الأعضاء."""
    __tablename__ = 'form_submissions'

    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey('forms.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.String(32), nullable=False, index=True)
    status = db.Column(db.String(32), default="pending", nullable=False)


class Notification(db.Model):
    """إشعارات لوحة التحكم للمستخدمين."""
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(32), nullable=False, index=True)
    title = db.Column(db.String(128), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class WebhookSetting(db.Model):
    """إعدادات الـ Webhooks المرتبطة بالسيرفر."""
    __tablename__ = 'webhook_settings'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False)
    url = db.Column(db.String(256), nullable=False)
    channel_id = db.Column(db.String(32), nullable=False)


class Backup(db.Model):
    """سجلات النسخ الاحتياطي الكاملة للسيرفر."""
    __tablename__ = 'backups'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    backup_code = db.Column(db.String(64), unique=True, nullable=False, index=True)
    data_json = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class BackupHistory(db.Model):
    """تاريخ عمليات النسخ والاسترجاع والحذف."""
    __tablename__ = 'backup_histories'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    action = db.Column(db.String(64), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Session(db.Model):
    """جلسات تسجيل الدخول للوحة التحكم (Web Sessions)."""
    __tablename__ = 'sessions'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(128), unique=True, nullable=False, index=True)
    user_id = db.Column(db.String(32), nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)


class APIKey(db.Model):
    """مفاتيح ربط الـ API الخاصة بالمبرمجين والمستخدمين."""
    __tablename__ = 'api_keys'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(32), nullable=False, index=True)
    api_key = db.Column(db.String(128), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class OAuthToken(db.Model):
    """رموز مصادقة Discord OAuth2."""
    __tablename__ = 'oauth_tokens'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(32), unique=True, nullable=False, index=True)
    access_token = db.Column(db.String(256), nullable=False)
    refresh_token = db.Column(db.String(256), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)


class DashboardActivity(db.Model):
    """نشاطات المستخدمين داخل لوحة التحكم."""
    __tablename__ = 'dashboard_activities'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    user_id = db.Column(db.String(32), nullable=False, index=True)
    action = db.Column(db.String(128), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
  
