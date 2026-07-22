# ==========================
# Imports & Setup
# ==========================
import json
from datetime import datetime, timezone
from database import db
from sqlalchemy.types import TypeDecorator, TEXT

# Helper function for UTC datetime
def current_utc():
    return datetime.now(timezone.utc)

# ==========================
# SQLite JSON Compatibility Fix
# ==========================
class JSONEncoded(TypeDecorator):
    """
    TypeDecorator لتوافق JSON مع SQLite بمرونة وبدون مشاكل تسلسل.
    يتعامل مع القيم الفارغة والقواميس والمصفوفات بشكل آمن تماماً.
    """
    impl = TEXT
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, str):
            return value
        try:
            return json.dumps(value)
        except (ValueError, TypeError):
            return "{}"

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, (dict, list)):
            return value
        try:
            return json.loads(value)
        except (ValueError, TypeError):
            return value


# ==========================
# Core Guild Settings Models
# ==========================
class GuildSettingsModel(db.Model):
    __tablename__ = "guild_settings"

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), unique=True, nullable=False, index=True)
    
    prefix = db.Column(db.String(10), default="!", nullable=False)
    language = db.Column(db.String(10), default="en", nullable=False)
    
    log_channel_id = db.Column(db.String(32), nullable=True)
    welcome_channel_id = db.Column(db.String(32), nullable=True)
    leave_channel_id = db.Column(db.String(32), nullable=True)
    
    created_at = db.Column(db.DateTime, default=current_utc, nullable=False)
    updated_at = db.Column(db.DateTime, default=current_utc, onupdate=current_utc, nullable=False)


# ==========================
# Dashboard Models
# ==========================
class DashboardStatsModel(db.Model):
    __tablename__ = "dashboard_stats"

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), unique=True, nullable=False, index=True)
    
    total_tickets = db.Column(db.Integer, default=0, nullable=False)
    total_clans = db.Column(db.Integer, default=0, nullable=False)
    total_members = db.Column(db.Integer, default=0, nullable=False)
    security_actions = db.Column(db.Integer, default=0, nullable=False)
    
    last_updated = db.Column(db.DateTime, default=current_utc, onupdate=current_utc, nullable=False)


# ==========================
# Backup System Models
# ==========================
class BackupModel(db.Model):
    __tablename__ = "backups"

    id = db.Column(db.Integer, primary_key=True)
    backup_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    
    data_type = db.Column(db.String(50), nullable=False, default="full")
    file_name = db.Column(db.String(255), nullable=True)
    file_path = db.Column(db.String(255), nullable=True)
    file_size = db.Column(db.Integer, nullable=False, default=0)
    backup_data = db.Column(JSONEncoded, nullable=True)
    
    created_by = db.Column(db.String(32), nullable=False)
    created_at = db.Column(db.DateTime, default=current_utc, nullable=False)


# ==========================
# Content Creator System Models
# ==========================
class CreatorSettingsModel(db.Model):
    __tablename__ = "creator_settings"

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), unique=True, nullable=False, index=True)
    
    enabled = db.Column(db.Boolean, default=True, nullable=False)
    announce_channel_id = db.Column(db.String(32), nullable=True)
    ping_role_id = db.Column(db.String(32), nullable=True)
    creator_role_id = db.Column(db.String(32), nullable=True)
    
    youtube_message = db.Column(db.Text, default="Hey! {creator} uploaded a new video: {link}")
    twitch_message = db.Column(db.Text, default="Hey! {creator} is now live on Twitch: {link}")
    tiktok_message = db.Column(db.Text, default="Hey! {creator} posted a new TikTok: {link}")
    
    created_at = db.Column(db.DateTime, default=current_utc, nullable=False)


class ContentCreatorModel(db.Model):
    __tablename__ = "content_creators"

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    user_id = db.Column(db.String(32), nullable=False, index=True)
    
    platform = db.Column(db.String(20), nullable=False)
    platform_channel_id = db.Column(db.String(255), nullable=False)
    platform_username = db.Column(db.String(100), nullable=True)
    
    last_notified = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    created_at = db.Column(db.DateTime, default=current_utc, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("guild_id", "platform", "platform_channel_id", name="creator_platform_unique"),
    )


# ==========================
# Security Models
# ==========================
class SecuritySettingsModel(db.Model):
    __tablename__ = "security_settings"

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), unique=True, nullable=False, index=True)

    anti_spam = db.Column(db.Boolean, default=True, nullable=False)
    anti_raid = db.Column(db.Boolean, default=True, nullable=False)
    anti_link = db.Column(db.Boolean, default=True, nullable=False)
    anti_mention = db.Column(db.Boolean, default=True, nullable=False)
    anti_mass_mention = db.Column(db.Boolean, default=True, nullable=False)
    anti_webhook = db.Column(db.Boolean, default=True, nullable=False)
    anti_bot = db.Column(db.Boolean, default=True, nullable=False)
    anti_mass_role = db.Column(db.Boolean, default=True, nullable=False)
    anti_channel_delete = db.Column(db.Boolean, default=True, nullable=False)
    anti_role_delete = db.Column(db.Boolean, default=True, nullable=False)

    anti_caps = db.Column(db.Boolean, default=False, nullable=False)
    anti_bad_words = db.Column(db.Boolean, default=True, nullable=False)
    anti_invite = db.Column(db.Boolean, default=True, nullable=False)
    anti_new_accounts = db.Column(db.Boolean, default=False, nullable=False)
    anti_nuke = db.Column(db.Boolean, default=True, nullable=False)
    anti_join_spam = db.Column(db.Boolean, default=True, nullable=False)

    whitelisted_roles = db.Column(JSONEncoded, default=list, nullable=False)
    whitelisted_channels = db.Column(JSONEncoded, default=list, nullable=False)
    whitelisted_bots = db.Column(JSONEncoded, default=list, nullable=False)
    whitelisted_users = db.Column(JSONEncoded, default=list, nullable=False)

    spam_limit = db.Column(db.Integer, default=5, nullable=False)
    spam_interval = db.Column(db.Integer, default=5, nullable=False)

    raid_join_limit = db.Column(db.Integer, default=10, nullable=False)
    raid_time = db.Column(db.Integer, default=10, nullable=False)

    punishment_type = db.Column(db.String(30), default="timeout", nullable=False)

    created_at = db.Column(db.DateTime, default=current_utc, nullable=False)
    updated_at = db.Column(db.DateTime, default=current_utc, onupdate=current_utc, nullable=False)


class SecurityWhitelistModel(db.Model):
    __tablename__ = "security_whitelist"

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    target_id = db.Column(db.String(32), nullable=False)
    target_type = db.Column(db.String(20), default="user", nullable=False)
    reason = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=current_utc, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("guild_id", "target_id", name="security_whitelist_unique"),
    )


class SecurityLogModel(db.Model):
    __tablename__ = "security_logs"

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    user_id = db.Column(db.String(32), nullable=True)
    channel_id = db.Column(db.String(32), nullable=True)
    moderator_id = db.Column(db.String(32), nullable=True)
    
    action = db.Column(db.String(100), nullable=False)
    action_type = db.Column(db.String(50), nullable=True)
    reason = db.Column(db.Text, nullable=True)
    details = db.Column(db.Text, nullable=True)
    
    log_metadata = db.Column(JSONEncoded, nullable=True)
    severity = db.Column(db.String(20), default="medium", nullable=False)
    
    timestamp = db.Column(db.DateTime, default=current_utc, nullable=False)
    created_at = db.Column(db.DateTime, default=current_utc, nullable=False)


class AutoModRuleModel(db.Model):
    __tablename__ = "automod_rules"

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    rule_type = db.Column(db.String(50), nullable=False)
    value = db.Column(db.Text, nullable=False)
    enabled = db.Column(db.Boolean, default=True, nullable=False)
    action = db.Column(db.String(30), default="delete", nullable=False)
    created_at = db.Column(db.DateTime, default=current_utc, nullable=False)


# ==========================
# Ticket System Models
# ==========================
class TicketSettingsModel(db.Model):
    __tablename__ = "ticket_settings"

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), unique=True, nullable=False, index=True)
    enabled = db.Column(db.Boolean, default=True, nullable=False)
    ticket_category_id = db.Column(db.String(32), nullable=True)
    closed_category_id = db.Column(db.String(32), nullable=True)
    transcript_channel_id = db.Column(db.String(32), nullable=True)
    support_roles = db.Column(db.Text, nullable=True)
    max_tickets_per_user = db.Column(db.Integer, default=1, nullable=False)
    auto_close_time = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=current_utc, nullable=False)
    updated_at = db.Column(db.DateTime, default=current_utc, onupdate=current_utc, nullable=False)


class TicketPanelModel(db.Model):
    __tablename__ = "ticket_panels"

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    channel_id = db.Column(db.String(32), nullable=False)
    message_id = db.Column(db.String(32), nullable=False)
    title = db.Column(db.String(100), default="Support Ticket")
    description = db.Column(db.Text, nullable=True)
    button_text = db.Column(db.String(50), default="Create Ticket")
    button_emoji = db.Column(db.String(20), nullable=True)
    enabled = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=current_utc, nullable=False)


class TicketCategoryModel(db.Model):
    __tablename__ = "ticket_categories"

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.String(32), nullable=False)
    support_roles = db.Column(db.Text, nullable=True)
    emoji = db.Column(db.String(20), nullable=True)
    description = db.Column(db.Text, nullable=True)
    enabled = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=current_utc, nullable=False)


class TicketModel(db.Model):
    __tablename__ = "tickets"

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    ticket_number = db.Column(db.Integer, nullable=False)
    channel_id = db.Column(db.String(32), unique=True, nullable=False)
    owner_id = db.Column(db.String(32), nullable=False, index=True)
    category_id = db.Column(db.Integer, nullable=True)
    
    status = db.Column(db.String(20), default="open", nullable=False)
    priority = db.Column(db.String(20), default="normal", nullable=False)
    
    claimed_by = db.Column(db.String(32), nullable=True)
    claimed_time = db.Column(db.DateTime, nullable=True)
    first_response_time = db.Column(db.DateTime, nullable=True)
    
    closed_by = db.Column(db.String(32), nullable=True)
    close_reason = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=current_utc, nullable=False)
    closed_at = db.Column(db.DateTime, nullable=True)

    members = db.relationship('TicketMemberModel', backref='ticket', cascade='all, delete-orphan', lazy=True)
    messages = db.relationship('TicketMessageModel', backref='ticket', cascade='all, delete-orphan', lazy=True)
    transcript = db.relationship('TicketTranscriptModel', backref='ticket', uselist=False, cascade='all, delete-orphan')
    rating = db.relationship('TicketRatingModel', backref='ticket', uselist=False, cascade='all, delete-orphan')


class TicketMemberModel(db.Model):
    __tablename__ = "ticket_members"

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.String(32), nullable=False)
    added_by = db.Column(db.String(32), nullable=True)
    created_at = db.Column(db.DateTime, default=current_utc, nullable=False)


class TicketMessageModel(db.Model):
    __tablename__ = "ticket_messages"

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.String(32), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=current_utc, nullable=False)


class TicketTranscriptModel(db.Model):
    __tablename__ = "ticket_transcripts"

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id', ondelete='CASCADE'), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_url = db.Column(db.Text, nullable=True)
    transcript_text = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=current_utc, nullable=False)


class TicketRatingModel(db.Model):
    __tablename__ = "ticket_ratings"

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.String(32), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    feedback = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=current_utc, nullable=False)


# ==========================
# Clan System Models
# ==========================
class ClanModel(db.Model):
    __tablename__ = "clans"

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    clan_id = db.Column(db.String(32), unique=True, nullable=False)
    clan_tag = db.Column(db.String(10), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    owner_id = db.Column(db.String(32), nullable=False)
    icon = db.Column(db.String(255), nullable=True)
    banner = db.Column(db.String(255), nullable=True)

    level = db.Column(db.Integer, default=1, nullable=False)
    points = db.Column(db.Integer, default=0, nullable=False)
    season_points = db.Column(db.Integer, default=0, nullable=False)
    season = db.Column(db.Integer, default=1, nullable=False)
    members_limit = db.Column(db.Integer, default=10, nullable=False)
    member_count = db.Column(db.Integer, default=1, nullable=False)
    
    wins = db.Column(db.Integer, default=0, nullable=False)
    losses = db.Column(db.Integer, default=0, nullable=False)
    clan_rank = db.Column(db.Integer, nullable=True)
    achievements = db.Column(JSONEncoded, default=list, nullable=False)

    status = db.Column(db.String(20), default="active", nullable=False)
    created_at = db.Column(db.DateTime, default=current_utc, nullable=False)
    updated_at = db.Column(db.DateTime, default=current_utc, onupdate=current_utc, nullable=False)

    members = db.relationship('ClanMemberModel', backref='clan', cascade='all, delete-orphan', lazy=True)
    ranks = db.relationship('ClanRankModel', backref='clan', cascade='all, delete-orphan', lazy=True)


class ClanMemberModel(db.Model):
    __tablename__ = "clan_members"

    id = db.Column(db.Integer, primary_key=True)
    clan_id = db.Column(db.String(32), db.ForeignKey('clans.clan_id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.String(32), nullable=False, index=True)
    role = db.Column(db.String(30), default="member", nullable=False)
    points = db.Column(db.Integer, default=0, nullable=False)
    joined_at = db.Column(db.DateTime, default=current_utc, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("clan_id", "user_id", name="clan_member_unique"),
    )


class ClanPointsLogModel(db.Model):
    __tablename__ = "clan_points_logs"

    id = db.Column(db.Integer, primary_key=True)
    clan_id = db.Column(db.String(32), nullable=False, index=True)
    user_id = db.Column(db.String(32), nullable=True)
    points = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.Text, nullable=True)
    action_type = db.Column(db.String(30), default="add", nullable=False)
    created_at = db.Column(db.DateTime, default=current_utc, nullable=False)


class ClanRankModel(db.Model):
    __tablename__ = "clan_ranks"

    id = db.Column(db.Integer, primary_key=True)
    clan_id = db.Column(db.String(32), db.ForeignKey('clans.clan_id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    permissions = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=current_utc, nullable=False)


class ClanRewardModel(db.Model):
    __tablename__ = "clan_rewards"

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False)
    required_points = db.Column(db.Integer, nullable=False)
    reward_type = db.Column(db.String(50), nullable=False)
    reward_value = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=current_utc, nullable=False)


# ==========================
# Economy System Models
# ==========================
class EconomySettingsModel(db.Model):
    __tablename__ = "economy_settings"

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), unique=True, nullable=False, index=True)
    currency_name = db.Column(db.String(50), default="Coins", nullable=False)
    enabled = db.Column(db.Boolean, default=True, nullable=False)
    daily_amount = db.Column(db.Integer, default=100, nullable=False)


class EconomyModel(db.Model):
    __tablename__ = "economy"

    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(32), nullable=False, index=True)
    user_id = db.Column(db.String(32), nullable=False, index=True)
    
    balance = db.Column(db.Integer, default=0, nullable=False)
    bank = db.Column(db.Integer, default=0, nullable=False)
    inventory = db.Column(JSONEncoded, default=dict, nullable=False)
    
    daily_claimed = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=current_utc, nullable=False)
    updated_at = db.Column(db.DateTime, default=current_utc, onupdate=current_utc, nullable=False)


# ==========================================
# Moderation System Models
# ==========================================
class InfractionModel(db.Model):
    __tablename__ = "infractions"

    id = db.Column(db.I
