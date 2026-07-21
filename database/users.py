from datetime import datetime
from .base import db

class User(db.Model):
    """جدول المستخدمين العالمي في البوت."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(32), unique=True, nullable=False, index=True)
    username = db.Column(db.String(128), nullable=False)
    discriminator = db.Column(db.String(8), nullable=True)
    avatar_url = db.Column(db.String(256), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    settings = db.relationship('UserSettings', backref='user', uselist=False, cascade="all, delete-orphan")
    profile = db.relationship('ProfileSettings', backref='user', uselist=False, cascade="all, delete-orphan")


class GuildMember(db.Model):
    """تفاصيل العضو داخل كل سيرفر."""
    __tablename__ = 'guild_members'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    user_id = db.Column(db.String(32), db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    nickname = db.Column(db.String(128), nullable=True)
    joined_at = db.Column(db.DateTime, nullable=True)
    is_muted = db.Column(db.Boolean, default=False, nullable=False)
    is_banned = db.Column(db.Boolean, default=False, nullable=False)

    __table_args__ = (db.UniqueConstraint('guild_id', 'user_id', name='_guild_member_uc'),)


class UserSettings(db.Model):
    """إعدادات المستخدم الشخصية."""
    __tablename__ = 'user_settings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(32), db.ForeignKey('users.user_id', ondelete='CASCADE'), unique=True, nullable=False, index=True)
    preferred_language = db.Column(db.String(10), default="ar", nullable=False)
    dark_mode = db.Column(db.Boolean, default=True, nullable=False)
    notifications_enabled = db.Column(db.Boolean, default=True, nullable=False)


class ProfileSettings(db.Model):
    """الملف الشخصي وأوسمة المستخدم."""
    __tablename__ = 'profile_settings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(32), db.ForeignKey('users.user_id', ondelete='CASCADE'), unique=True, nullable=False, index=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    bio = db.Column(db.Text, default="لا توجد نبذة تعريفية.", nullable=False)
    reputation_points = db.Column(db.Integer, default=0, nullable=False)
    custom_color = db.Column(db.String(16), default="#5865F2", nullable=False)
    background_image = db.Column(db.String(256), nullable=True)

    badges = db.relationship('UserProfileBadge', backref='profile', lazy=True, cascade="all, delete-orphan")


class UserProfileBadge(db.Model):
    """أوسمة الملف الشخصي المستقلة."""
    __tablename__ = 'user_profile_badges'

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profile_settings.id', ondelete='CASCADE'), nullable=False, index=True)
    badge_name = db.Column(db.String(64), nullable=False)
    badge_icon = db.Column(db.String(256), nullable=True)
  
