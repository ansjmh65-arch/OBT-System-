from datetime import datetime
from .base import db

class WelcomeSetting(db.Model):
    """إعدادات الترحيب والمغادرة."""
    __tablename__ = 'welcome_settings'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), unique=True, nullable=False, index=True)
    welcome_channel_id = db.Column(db.String(32), nullable=True)
    leave_channel_id = db.Column(db.String(32), nullable=True)
    welcome_message = db.Column(db.Text, default="أهلاً بك يا {user} في سيرفر {server}", nullable=False)
    leave_message = db.Column(db.Text, default="وداعاً {user}", nullable=False)


class AutoRoleSetting(db.Model):
    """الرتب التلقائية عند الدخول (Auto Roles)."""
    __tablename__ = 'autorole_settings'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), unique=True, nullable=False, index=True)
    role_id = db.Column(db.String(32), nullable=False)
    role_type = db.Column(db.String(16), default="human", nullable=False)  # human or bot


class VerificationSetting(db.Model):
    """إعدادات نظام التحقق للأعضاء الجدد."""
    __tablename__ = 'verification_settings'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), unique=True, nullable=False, index=True)
    is_enabled = db.Column(db.Boolean, default=False, nullable=False)
    verification_role_id = db.Column(db.String(32), nullable=True)
    channel_id = db.Column(db.String(32), nullable=True)
    method = db.Column(db.String(32), default="button", nullable=False)


class LevelSystem(db.Model):
    """نظام المستويات والخبرة (Levels & XP)."""
    __tablename__ = 'level_systems'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), unique=True, nullable=False, index=True)
    is_enabled = db.Column(db.Boolean, default=True, nullable=False)
    announcement_channel_id = db.Column(db.String(32), nullable=True)


class UserLevel(db.Model):
    """خبرة ومستوى المستخدم الحالي."""
    __tablename__ = 'user_levels'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    user_id = db.Column(db.String(32), nullable=False, index=True)
    xp = db.Column(db.Integer, default=0, nullable=False)
    level = db.Column(db.Integer, default=0, nullable=False)

    __table_args__ = (db.UniqueConstraint('guild_id', 'user_id', name='_guild_user_level_uc'),)


class Giveaway(db.Model):
    """المسابقات والهدايا (Giveaways)."""
    __tablename__ = 'giveaways'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    channel_id = db.Column(db.String(32), nullable=False)
    message_id = db.Column(db.String(32), unique=True, nullable=False, index=True)
    prize = db.Column(db.String(128), nullable=False)
    winners_count = db.Column(db.Integer, default=1, nullable=False)
    ends_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    entries = db.relationship('GiveawayEntry', backref='giveaway', lazy=True, cascade="all, delete-orphan")


class GiveawayEntry(db.Model):
    """المشاركون في المسابقات."""
    __tablename__ = 'giveaway_entries'

    id = db.Column(db.Integer, primary_key=True)
    giveaway_id = db.Column(db.Integer, db.ForeignKey('giveaways.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.String(32), nullable=False, index=True)


class Poll(db.Model):
    """استطلاعات الرأي (Polls)."""
    __tablename__ = 'polls'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    channel_id = db.Column(db.String(32), nullable=False)
    message_id = db.Column(db.String(32), unique=True, nullable=False, index=True)
    question = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    options = db.relationship('PollOption', backref='poll', lazy=True, cascade="all, delete-orphan")


class PollOption(db.Model):
    """خيارات استطلاع الرأي."""
    __tablename__ = 'poll_options'

    id = db.Column(db.Integer, primary_key=True)
    poll_id = db.Column(db.Integer, db.ForeignKey('polls.id', ondelete='CASCADE'), nullable=False, index=True)
    option_text = db.Column(db.String(256), nullable=False)
    votes_count = db.Column(db.Integer, default=0, nullable=False)


class Suggestion(db.Model):
    """نظام الاقتراحات (Suggestions)."""
    __tablename__ = 'suggestions'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    user_id = db.Column(db.String(32), nullable=False, index=True)
    message_id = db.Column(db.String(32), unique=True, nullable=True, index=True)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(32), default="pending", nullable=False)


class Starboard(db.Model):
    """نظام النجوم (Starboard)."""
    __tablename__ = 'starboards'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    original_message_id = db.Column(db.String(32), nullable=False, index=True)
    starboard_message_id = db.Column(db.String(32), nullable=False, index=True)
    stars_count = db.Column(db.Integer, default=1, nullable=False)


class ReactionRole(db.Model):
    """رتب التفاعل عبر الرموز التعبيرية (Reaction Roles)."""
    __tablename__ = 'reaction_roles'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    channel_id = db.Column(db.String(32), nullable=False)
    message_id = db.Column(db.String(32), nullable=False, index=True)
    emoji = db.Column(db.String(128), nullable=False)
    role_id = db.Column(db.String(32), nullable=False)


class TempVoiceChannel(db.Model):
    """الرومات الصوتية المؤقتة (Temporary Voice Channels)."""
    __tablename__ = 'temp_voice_channels'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    channel_id = db.Column(db.String(32), unique=True, nullable=False, index=True)
    owner_id = db.Column(db.String(32), nullable=False, index=True)


class Reminder(db.Model):
    """التذكيرات الشخصية (Reminders)."""
    __tablename__ = 'reminders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(32), nullable=False, index=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    message = db.Column(db.Text, nullable=False)
    remind_at = db.Column(db.DateTime, nullable=False)
    is_sent = db.Column(db.Boolean, default=False, nullable=False)


class Birthday(db.Model):
    """أعياد ميلاد الأعضاء."""
    __tablename__ = 'birthdays'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    user_id = db.Column(db.String(32), nullable=False, index=True)
    birth_date = db.Column(db.Date, nullable=False)


class CustomCommand(db.Model):
    """الأوامر المخصصة للسيرفر (Custom Commands)."""
    __tablename__ = 'custom_commands'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    trigger = db.Column(db.String(64), nullable=False, index=True)
    response = db.Column(db.Text, nullable=False)


class Tag(db.Model):
    """الكلمات الدلالية المحفوظة (Tags)."""
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.String(32), nullable=False)


class ScheduledEvent(db.Model):
    """المهام والفعاليات المجدولة."""
    __tablename__ = 'scheduled_events'

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    task_type = db.Column(db.String(64), nullable=False)
    target_id = db.Column(db.String(32), nullable=False)
    execute_at = db.Column(db.DateTime, nullable=False)
    is_completed = db.Column(db.Boolean, default=False, nullable=False)
  
