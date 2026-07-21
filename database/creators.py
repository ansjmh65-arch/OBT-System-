from datetime import datetime
from .base import db

class ContentCreatorSetting(db.Model):
    """إعدادات نظام صناع المحتوى."""
    __tablename__ = 'content_creator_settings'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), unique=True, nullable=False, index=True)
    is_enabled = db.Column(db.Boolean, default=True, nullable=False)
    notification_channel_id = db.Column(db.String(32), nullable=True)


class ContentCreator(db.Model):
    """سجل صناع المحتوى المعتمدين."""
    __tablename__ = 'content_creators'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    user_id = db.Column(db.String(32), nullable=False, index=True)
    platform = db.Column(db.String(32), nullable=False)
    channel_url = db.Column(db.String(256), nullable=False)
    is_approved = db.Column(db.Boolean, default=False, nullable=False)

    statistics = db.relationship('CreatorStatistic', backref='creator', uselist=False, cascade="all, delete-orphan")
    posts = db.relationship('CreatorPost', backref='creator', lazy=True, cascade="all, delete-orphan")


class CreatorApplication(db.Model):
    """طلبات الانضمام لصناع المحتوى."""
    __tablename__ = 'creator_applications'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    user_id = db.Column(db.String(32), nullable=False, index=True)
    platform = db.Column(db.String(32), nullable=False)
    profile_link = db.Column(db.String(256), nullable=False)
    status = db.Column(db.String(32), default="pending", nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class CreatorStatistic(db.Model):
    """إحصائيات صانع المحتوى (منشورات، مشاهدات افتراضية)."""
    __tablename__ = 'creator_statistics'

    id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('content_creators.id', ondelete='CASCADE'), unique=True, nullable=False, index=True)
    total_posts = db.Column(db.Integer, default=0, nullable=False)
    total_notifications_sent = db.Column(db.Integer, default=0, nullable=False)


class CreatorPost(db.Model):
    """منشورات صناع المحتوى التي تم إرسال إشعارات لها."""
    __tablename__ = 'creator_posts'

    id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('content_creators.id', ondelete='CASCADE'), nullable=False, index=True)
    post_url = db.Column(db.String(256), nullable=False)
    notified_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
