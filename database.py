from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    BigInteger, Boolean, Column, DateTime, Float, ForeignKey, Integer, 
    String, Text, JSON, UniqueConstraint, Index, func
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.declarative import declared_attr

class Base(DeclarativeBase):
    """القاعدة الأساسية لنماذج SQLAlchemy 2.x"""
    pass

# ==========================================================
# 1. GuildSettings (إعدادات السيرفر)
# ==========================================================
class GuildSettings(Base):
    __tablename__ = "guild_settings"

    guild_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    prefix: Mapped[str] = mapped_column(String(10), default="!")
    language: Mapped[str] = mapped_column(String(10), default="ar")
    timezone: Mapped[str] = mapped_column(String(50), default="UTC")
    embed_color: Mapped[str] = mapped_column(String(20), default="#5865F2")
    dashboard_theme: Mapped[str] = mapped_column(String(20), default="dark")
    
    # Module Toggles
    security_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    moderation_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    tickets_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    logs_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    points_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    clans_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    creators_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    economy_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    leveling_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    welcome_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    automod_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    backup_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    security: Mapped["SecuritySettings"] = relationship(back_populates="guild", uselist=False, cascade="all, delete-orphan")
    logs: Mapped["LogSettings"] = relationship(back_populates="guild", uselist=False, cascade="all, delete-orphan")
    welcome: Mapped["WelcomeSettings"] = relationship(back_populates="guild", uselist=False, cascade="all, delete-orphan")
    tickets: Mapped[List["Ticket"]] = relationship(back_populates="guild", cascade="all, delete-orphan")
    ticket_panels: Mapped[List["TicketPanel"]] = relationship(back_populates="guild", cascade="all, delete-orphan")
    moderation_cases: Mapped[List["ModerationCase"]] = relationship(back_populates="guild", cascade="all, delete-orphan")
    backups: Mapped[List["Backup"]] = relationship(back_populates="guild", cascade="all, delete-orphan")
    audit_logs: Mapped[List["DashboardAuditLog"]] = relationship(back_populates="guild", cascade="all, delete-orphan")
    scheduled_backups: Mapped[List["ScheduledBackup"]] = relationship(back_populates="guild", cascade="all, delete-orphan")
    economy_points: Mapped[List["EconomyPoint"]] = relationship(back_populates="guild", cascade="all, delete-orphan")
    clans: Mapped[List["Clan"]] = relationship(back_populates="guild", cascade="all, delete-orphan")


# ==========================================================
# 2. SecuritySettings (إعدادات الأمان والحماية)
# ==========================================================
class SecuritySettings(Base):
    __tablename__ = "security_settings"

    guild_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("guild_settings.guild_id", ondelete="CASCADE"), primary_key=True)
    anti_spam: Mapped[bool] = mapped_column(Boolean, default=True)
    anti_spam_limit: Mapped[int] = mapped_column(Integer, default=5)
    anti_duplicate_messages: Mapped[bool] = mapped_column(Boolean, default=True)
    anti_caps: Mapped[bool] = mapped_column(Boolean, default=False)
    anti_mass_mentions: Mapped[bool] = mapped_column(Boolean, default=True)
    anti_links: Mapped[bool] = mapped_column(Boolean, default=False)
    anti_invites: Mapped[bool] = mapped_column(Boolean, default=True)
    anti_bots: Mapped[bool] = mapped_column(Boolean, default=True)
    anti_webhooks: Mapped[bool] = mapped_column(Boolean, default=True)
    anti_scam: Mapped[bool] = mapped_column(Boolean, default=True)
    anti_phishing: Mapped[bool] = mapped_column(Boolean, default=True)
    anti_raid: Mapped[bool] = mapped_column(Boolean, default=True)
    anti_mass_join: Mapped[bool] = mapped_column(Boolean, default=True)
    anti_bad_words: Mapped[bool] = mapped_column(Boolean, default=True)
    verification_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    punishment_type: Mapped[str] = mapped_column(String(30), default="timeout") # timeout, kick, ban
    
    automod_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    whitelist: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    blacklist: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    guild: Mapped["GuildSettings"] = relationship(back_populates="security")


# ==========================================================
# 3. ModerationCases (سجلات الإشراف والعقوبات)
# ==========================================================
class ModerationCase(Base):
    __tablename__ = "moderation_cases"

    case_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("guild_settings.guild_id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    moderator_id: Mapped[int] = mapped_column(BigInteger)
    action: Mapped[str] = mapped_column(String(50)) # warn, mute, kick, ban
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True) # بالثواني
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    guild: Mapped["GuildSettings"] = relationship(back_populates="moderation_cases")


# ==========================================================
# 4. TicketPanels (لوحات التذاكر)
# ==========================================================
class TicketPanel(Base):
    __tablename__ = "ticket_panels"

    panel_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("guild_settings.guild_id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    channel_id: Mapped[int] = mapped_column(BigInteger)
    category_id: Mapped[int] = mapped_column(BigInteger)
    transcript_channel: Mapped[int] = mapped_column(BigInteger)
    
    support_roles: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    questions: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    auto_close: Mapped[bool] = mapped_column(Boolean, default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    guild: Mapped["GuildSettings"] = relationship(back_populates="ticket_panels")
    tickets: Mapped[List["Ticket"]] = relationship(back_populates="panel", cascade="all, delete-orphan")


# ==========================================================
# 5. Tickets (التذاكر النشطة)
# ==========================================================
class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("guild_settings.guild_id", ondelete="CASCADE"), index=True)
    panel_id: Mapped[int] = mapped_column(Integer, ForeignKey("ticket_panels.panel_id", ondelete="CASCADE"))
    creator_id: Mapped[int] = mapped_column(BigInteger, index=True)
    channel_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    claimed_by: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="open") # open, closed, archived
    rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    guild: Mapped["GuildSettings"] = relationship(back_populates="tickets")
    panel: Mapped["TicketPanel"] = relationship(back_populates="panel")


# ==========================================================
# 6. EconomyPoints (نقاط الاقتصاد والعملات)
# ==========================================================
class EconomyPoint(Base):
    __tablename__ = "economy_points"
    __table_args__ = (UniqueConstraint("guild_id", "user_id", name="uq_guild_user_economy"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("guild_settings.guild_id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    points: Mapped[float] = mapped_column(Float, default=0.0)
    total_earned: Mapped[float] = mapped_column(Float, default=0.0)
    total_spent: Mapped[float] = mapped_column(Float, default=0.0)
    season_id: Mapped[str] = mapped_column(String(50), default="season_1")
    last_daily: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    guild: Mapped["GuildSettings"] = relationship(back_populates="economy_points")


# ==========================================================
# 7 & 8. ClanSystem & ClanMembers (نظام العشائر والكلانات)
# ==========================================================
class Clan(Base):
    __tablename__ = "clans"

    clan_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("guild_settings.guild_id", ondelete="CASCADE"), index=True)
    owner_id: Mapped[int] = mapped_column(BigInteger)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    logo: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    total_points: Mapped[float] = mapped_column(Float, default=0.0)
    level: Mapped[int] = mapped_column(Integer, default=1)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    guild: Mapped["GuildSettings"] = relationship(back_populates="clans")
    members: Mapped[List["ClanMember"]] = relationship(back_populates="clan", cascade="all, delete-orphan")


class ClanMember(Base):
    __tablename__ = "clan_members"
    __table_args__ = (UniqueConstraint("clan_id", "user_id", name="uq_clan_user"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    clan_id: Mapped[int] = mapped_column(Integer, ForeignKey("clans.clan_id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    role: Mapped[str] = mapped_column(String(20), default="member") # owner, admin, member
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    clan: Mapped["Clan"] = relationship(back_populates="members")


# ==========================================================
# 9. CreatorProgram (برنامج صناع المحتوى)
# ==========================================================
class CreatorProgram(Base):
    __tablename__ = "creator_program"
    __table_args__ = (UniqueConstraint("guild_id", "user_id", name="uq_guild_creator"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("guild_settings.guild_id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    platform: Mapped[str] = mapped_column(String(50)) # YouTube, Twitch, TikTok, etc.
    channel_url: Mapped[str] = mapped_column(String(255))
    followers: Mapped[int] = mapped_column(Integer, default=0)
    approved: Mapped[bool] = mapped_column(Boolean, default=False)
    
    applied_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ==========================================================
# 10. WelcomeSettings (إعدادات الترحيب والوداع)
# ==========================================================
class WelcomeSettings(Base):
    __tablename__ = "welcome_settings"

    guild_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("guild_settings.guild_id", ondelete="CASCADE"), primary_key=True)
    welcome_channel: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    goodbye_channel: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    auto_role: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    
    welcome_embed: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    goodbye_embed: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    guild: Mapped["GuildSettings"] = relationship(back_populates="welcome")


# ==========================================================
# 11. LogSettings (قنوات السجلات الموحدة)
# ==========================================================
class LogSettings(Base):
    __tablename__ = "log_settings"

    guild_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("guild_settings.guild_id", ondelete="CASCADE"), primary_key=True)
    
    member_logs: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    message_logs: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    voice_logs: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    moderation_logs: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    role_logs: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    channel_logs: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    emoji_logs: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    sticker_logs: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    invite_logs: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    webhook_logs: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    server_logs: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    ticket_logs: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    security_logs: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    points_logs: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    clan_logs: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    creator_logs: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    backup_logs: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    dashboard_logs: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    command_logs: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    error_logs: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    guild: Mapped["GuildSettings"] = relationship(back_populates="logs")


# ==========================================================
# 12. DashboardAuditLogs (سجلات تدقيق لوحة التحكم)
# ==========================================================
class DashboardAuditLog(Base):
    __tablename__ = "dashboard_audit_logs"

    log_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("guild_settings.guild_id", ondelete="CASCADE"), index=True)
    admin_id: Mapped[int] = mapped_column(BigInteger)
    action_type: Mapped[str] = mapped_column(String(100))
    page: Mapped[str] = mapped_column(String(100))
    old_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    new_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    guild: Mapped["GuildSettings"] = relationship(back_populates="audit_logs")


# ==========================================================
# 13. Backups (النسخ الاحتياطي)
# ==========================================================
class Backup(Base):
    __tablename__ = "backups"

    backup_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("guild_settings.guild_id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    file_name: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(500))
    file_size: Mapped[int] = mapped_column(Integer, default=0) # بالبايت
    created_by: Mapped[int] = mapped_column(BigInteger)
    automatic_backup: Mapped[bool] = mapped_column(Boolean, default=False)
    version: Mapped[str] = mapped_column(String(20), default="1.0")
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    guild: Mapped["GuildSettings"] = relationship(back_populates="backups")


# ==========================================================
# 14. ScheduledBackups (النسخ الاحتياطي المجدول)
# ==========================================================
class ScheduledBackup(Base):
    __tablename__ = "scheduled_backups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("guild_settings.guild_id", ondelete="CASCADE"), index=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    interval: Mapped[str] = mapped_column(String(20), default="daily") # daily, weekly
    last_backup: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    next_backup: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    keep_last_backups: Mapped[int] = mapped_column(Integer, default=5)

    guild: Mapped["GuildSettings"] = relationship(back_populates="scheduled_backups")


# ==========================================================
# 15. LevelSystem (نظام المستويات والـ XP)
# ==========================================================
class LevelSystem(Base):
    __tablename__ = "level_system"
    __table_args__ = (UniqueConstraint("guild_id", "user_id", name="uq_guild_user_level"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    xp: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[int] = mapped_column(Integer, default=0)
    total_messages: Mapped[int] = mapped_column(Integer, default=0)


# ==========================================================
# 16. ReactionRoles (رتب التفاعل)
# ==========================================================
class ReactionRole(Base):
    __tablename__ = "reaction_roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, index=True)
    message_id: Mapped[int] = mapped_column(BigInteger, index=True)
    emoji: Mapped[str] = mapped_column(String(100))
    role_id: Mapped[int] = mapped_column(BigInteger)

# =======================================    welcome_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    automod_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    backup_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    security: Mapped["SecuritySettings"] = relationship(back_populates="guild", uselist=False, cascade="all, delete-orphan")
    logs: Mapped["LogSettings"] = relationship(back_populates="guild", uselist=False, cascade="all, delete-orphan")
    welcome: Mapped["WelcomeSettings"] = relationship(back_populates="guild", uselist=False, cascade="all, delete-orphan")
    tickets: Mapped[List["Ticket"]] = relationship(back_populates="guild", cascade="all, delete-orphan")
    ticket_panels: Mapped[List["TicketPanel"]] = relationship(back_populates="guild", cascade="all, delete-orphan")
    moderation_cases: Mapped[List["ModerationCase"]] = relationship(back_populates="guild", cascade="all, delete-orphan")
    backups: Mapped[List["Backup"]] = relationship(back_populates="guild", cascade="all, delete-orphan")
    audit_logs: Mapped[List["DashboardAuditLog"]] = relationship(back_populates="guild", cascade="all, delete-orphan")
    scheduled_backups: Mapped[List["ScheduledBackup"]] = relationship(back_populates="guild", cascade="all, delete-orphan")
    economy_points: Mapped[List["EconomyPoint"]] = relationship(back_populates="guild", cascade="all, delete-orphan")
    clans: Mapped[List["Clan"]] = relationship(back_populates="guild", cascade="all, delete-orphan")


# ==========================================================
# 2. SecuritySettings (إعدادات الأمان والحماية)
# ==========================================================
class SecuritySettings(Base):
    __tablename__ = "security_settings"

    guild_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("guild_settings.guild_id", ondelete="CASCADE"), primary_key=True)
    anti_spam: Mapped[bool] = mapped_column(Boolean, default=True)
    anti_spam_limit: Mapped[int] = mapped_column(Integer, default=5)
    anti_duplicate_messages: Mapped[bool] = mapped_column(Boolean, default=True)
    anti_caps: Mapped[bool] = mapped_column(Boolean, default=False)
    anti_mass_mentions: Mapped[bool] = mapped_column(Boolean, default=True)
    anti_links: Mapped[bool] = mapped_column(Boolean, default=False)
    anti_invites: Mapped[bool] = mapped_column(Boolean, default=True)
    anti_bots: Mapped[bool] = mapped_column(Boolean, default=True)
    anti_webhooks: Mapped[bool] = mapped_column(Boolean, default=True)
    anti_scam: Mapped[bool] = mapped_column(Boolean, default=True)
    anti_phishing: Mapped[bool] = mapped_column(Boolean, default=True)
    anti_raid: Mapped[bool] = mapped_column(Boolean, default=True)
    anti_mass_join: Mapped[bool] = mapped_column(Boolean, default=True)
    anti_bad_words: Mapped[bool] = mapped_column(Boolean, default=True)
    verification_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    punishment_type: Mapped[str] = mapped_column(String(30), default="timeout") # timeout, kick, ban
    
    automod_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    whitelist: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    blacklist: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    guild: Mapped["GuildSettings"] = relationship(back_populates="security")


# ==========================================================
# 3. ModerationCases (سجلات الإشراف والعقوبات)
# ==========================================================
class ModerationCase(Base):
    __tablename__ = "moderation_cases"

    case_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("guild_settings.guild_id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    moderator_id: Mapped[int] = mapped_column(BigInteger)
    action: Mapped[str] = mapped_column(String(50)) # warn, mute, kick, ban
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True) # بالثواني
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    guild: Mapped["GuildSettings"] = relationship(back_populates="moderation_cases")


# ==========================================================
# 4. TicketPanels (لوحات التذاكر)
# ==========================================================
class TicketPanel(Base):
    __tablename__ = "ticket_panels"

    panel_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("guild_settings.guild_id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    channel_id: Mapped[int] = mapped_column(BigInteger)
    category_id: Mapped[int] = mapped_column(BigInteger)
    transcript_channel: Mapped[int] = mapped_column(BigInteger)
    
    support_roles: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    questions: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    auto_close: Mapped[bool] = mapped_column(Boolean, default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    guild: Mapped["GuildSettings"] = relationship(back_populates="ticket_panels")
    tickets: Mapped[List["Ticket"]] = relationship(back_populates="panel", cascade="all, delete-orphan")


# ==========================================================
# 5. Tickets (التذاكر النشطة)
# ==========================================================
class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("guild_settings.guild_id", ondelete="CASCADE"), index=True)
    panel_id: Mapped[int] = mapped_column(Integer, ForeignKey("ticket_panels.panel_id", ondelete="CASCADE"))
    creator_id: Mapped[int] = mapped_column(BigInteger, index=True)
    channel_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    claimed_by: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="open") # open, closed, archived
    rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    guild: Mapped["GuildSettings"] = relationship(back_populates="tickets")
    panel: Mapped["TicketPanel"] = relationship(back_populates="tickets")


# ==========================================================
# 6. EconomyPoints (نقاط الاقتصاد والعملات)
# ==========================================================
class EconomyPoint(Base):
    __tablename__ = "economy_points"
    __table_args__ = (UniqueConstraint("guild_id", "user_id", name="uq_guild_user_economy"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("guild_settings.guild_id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    points: Mapped[float] = mapped_column(Float, default=0.0)
    total_earned: Mapped[float] = mapped_column(Float, default=0.0)
    total_spent: Mapped[float] = mapped_column(Float, default=0.0)
    season_id: Mapped[str] = mapped_column(String(50), default="season_1")
    last_daily: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    guild: Mapped["GuildSettings"] = relationship(back_populates="economy_points")


# ==========================================================
# 7 & 8. ClanSystem & ClanMembers (نظام العشائر والكلانات)
# ==========================================================
class Clan(Base):
    __tablename__ = "clans"

    clan_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("guild_settings.guild_id", ondelete="CASCADE"), index=True)
    owner_id: Mapped[int] = mapped_column(BigInteger)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    logo: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    total_points: Mapped[float] = mapped_column(Float, default=0.0)
    level: Mapped[int] = mapped_column(Integer, default=1)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    guild: Mapped["GuildSettings"] = relationship(back_populates="clans")
    members: Mapped[List["ClanMember"]] = relationship(back_populates="clan", cascade="all, delete-orphan")


class ClanMember(Base):
    __tablename__ = "clan_members"
    __table_args__ = (UniqueConstraint("clan_id", "user_id", name="uq_clan_user"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    clan_id: Mapped[int] = mapped_column(Integer, ForeignKey("clans.clan_id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    role: Mapped[str] = mapped_column(String(20), default="member") # owner, admin, member
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    clan: Mapped["Clan"] = relationship(back_populates="members")


# ==========================================================
# 9. CreatorProgram (برنامج صناع المحتوى)
# ==========================================================
class CreatorProgram(Base):
    __tablename__ = "creator_program"
    __table_args__ = (UniqueConstraint("guild_id", "user_id", name="uq_guild_creator"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("guild_settings.guild_id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    platform: Mapped[str] = mapped_column(String(50)) # YouTube, Twitch, TikTok, etc.
    channel_url: Mapped[str] = mapped_column(String(255))
    followers: Mapped[int] = mapped_column(Integer, default=0)
    approved: Mapped[bool] = mapped_column(Boolean, default=False)
    
    applied_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ==========================================================
# 10. WelcomeSettings (إعدادات الترحيب والوداع)
# ==========================================================
class WelcomeSettings(Base):
    __tablename__ = "welcome_settings"

    guild_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("guild_settings.guild_id", ondelete="CASCADE"), primary_key=True)
    welcome_channel: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    goodbye_channel: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    auto_role: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    
    welcome_embed: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    goodbye_embed: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    guild: Mapped["GuildSettings"] = relationship(back_populates="welcome")


# ==========================================================
# 11. LogSettings (قنوات السجلات الموحدة)
# ==========================================================
class LogSettings(Base):
    __tablename__ = "log_settings"

    guild_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("guild_settings.guild_id", ondelete="CASCADE"), primary_key=True)
    
    member_logs: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    message_logs: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    voice_logs: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    moderation_logs: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    role_logs: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    channel_logs: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    emoji_logs: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    sticker_logs: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    invite_logs: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    webhook_logs: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    server_logs: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    ticket_logs: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    security_logs: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    points_logs: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    clan_logs: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    creator_logs: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    backup_logs: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    dashboard_logs: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    command_logs: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    error_logs: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    guild: Mapped["GuildSettings"] = relationship(back_populates="logs")


# ==========================================================
# 12. DashboardAuditLogs (سجلات تدقيق لوحة التحكم)
# ==========================================================
class DashboardAuditLog(Base):
    __tablename__ = "dashboard_audit_logs"

    log_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("guild_settings.guild_id", ondelete="CASCADE"), index=True)
    admin_id: Mapped[int] = mapped_column(BigInteger)
    action_type: Mapped[str] = mapped_column(String(100))
    page: Mapped[str] = mapped_column(String(100))
    old_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    new_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    guild: Mapped["GuildSettings"] = relationship(back_populates="audit_logs")


# ==========================================================
# 13. Backups (النسخ الاحتياطي)
# ==========================================================
class Backup(Base):
    __tablename__ = "backups"

    backup_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("guild_settings.guild_id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    file_name: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(500))
    file_size: Mapped[int] = mapped_column(Integer, default=0) # بالبايت
    created_by: Mapped[int] = mapped_column(BigInteger)
    automatic_backup: Mapped[bool] = mapped_column(Boolean, default=False)
    version: Mapped[str] = mapped_column(String(20), default="1.0")
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    guild: Mapped["GuildSettings"] = relationship(back_populates="backups")


# ==========================================================
# 14. ScheduledBackups (النسخ الاحتياطي المجدول)
# ==========================================================
class ScheduledBackup(Base):
    __tablename__ = "scheduled_backups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("guild_settings.guild_id", ondelete="CASCADE"), index=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    interval: Mapped[str] = mapped_column(String(20), default="daily") # daily, weekly
    last_backup: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    next_backup: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    keep_last_backups: Mapped[int] = mapped_column(Integer, default=5)

    guild: Mapped["GuildSettings"] = relationship(back_populates="scheduled_backups")


# ==========================================================
# 15. LevelSystem (نظام المستويات والـ XP)
# ==========================================================
class LevelSystem(Base):
    __tablename__ = "level_system"
    __table_args__ = (UniqueConstraint("guild_id", "user_id", name="uq_guild_user_level"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    xp: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[int] = mapped_column(Integer, default=0)
    total_messages: Mapped[int] = mapped_column(Integer, default=0)


# ==========================================================
# 16. ReactionRoles (رتب التفاعل)
# ==========================================================
class ReactionRole(Base):
    __tablename__ = "reaction_roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, index=True)
    message_id: Mapped[int] = mapped_column(BigInteger, index=True)
    emoji: Mapped[str] = mapped_column(String(100))
    role_id: Mapped[int] = mapped_column(BigInteger)


# ====================================
class TicketPanels(Base, TimestampMixin):
    __tablename__ = 'ticket_panels'

    panel_id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(String(32), ForeignKey('guild_settings.guild_id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(64), nullable=False)
    channel_id = Column(String(32), nullable=False)
    category_id = Column(String(32), nullable=False)
    transcript_channel = Column(String(32), nullable=True)
    support_roles = Column(Text, default="[]", nullable=False)
    questions = Column(Text, default="[]", nullable=False)
    auto_close = Column(Boolean, default=False, nullable=False)

    guild = relationship("GuildSettings", back_populates="ticket_panels")
    tickets = relationship("Tickets", back_populates="panel", cascade="all, delete-orphan")


class Tickets(Base, TimestampMixin):
    __tablename__ = 'tickets'

    ticket_id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(String(32), ForeignKey('guild_settings.guild_id', ondelete='CASCADE'), nullable=False, index=True)
    panel_id = Column(Integer, ForeignKey('ticket_panels.panel_id', ondelete='CASCADE'), nullable=False)
    creator_id = Column(String(32), nullable=False, index=True)
    channel_id = Column(String(32), nullable=False, unique=True)
    claimed_by = Column(String(32), nullable=True)
    status = Column(String(32), default="open", nullable=False)
    rating = Column(Integer, nullable=True)
    closed_at = Column(DateTime, nullable=True)

    guild = relationship("GuildSettings", back_populates="tickets")
    panel = relationship("TicketPanels", back_populates="tickets")


class EconomyPoints(Base, TimestampMixin):
    __tablename__ = 'economy_points'

    guild_id = Column(String(32), ForeignKey('guild_settings.guild_id', ondelete='CASCADE'), primary_key=True)
    user_id = Column(String(32), primary_key=True, index=True)
    points = Column(Integer, default=0, nullable=False)
    total_earned = Column(Integer, default=0, nullable=False)
    total_spent = Column(Integer, default=0, nullable=False)
    season_id = Column(String(32), default="default", nullable=False)
    last_daily = Column(DateTime, nullable=True)

    guild = relationship("GuildSettings", back_populates="economy_points")


class ClanSystem(Base, TimestampMixin):
    __tablename__ = 'clan_system'

    clan_id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(String(32), ForeignKey('guild_settings.guild_id', ondelete='CASCADE'), nullable=False, index=True)
    owner_id = Column(String(32), nullable=False)
    name = Column(String(64), nullable=False)
    description = Column(Text, nullable=True)
    logo = Column(String(255), nullable=True)
    total_points = Column(Integer, default=0, nullable=False)
    level = Column(Integer, default=1, nullable=False)

    guild = relationship("GuildSettings", back_populates="clans")
    members = relationship("ClanMembers", back_populates="clan", cascade="all, delete-orphan")


class ClanMembers(Base):
    __tablename__ = 'clan_members'

    clan_id = Column(Integer, ForeignKey('clan_system.clan_id', ondelete='CASCADE'), primary_key=True)
    user_id = Column(String(32), primary_key=True, index=True)
    role = Column(String(32), default="member", nullable=False)
    joined_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    clan = relationship("ClanSystem", back_populates="members")


class CreatorProgram(Base, TimestampMixin):
    __tablename__ = 'creator_program'

    guild_id = Column(String(32), ForeignKey('guild_settings.guild_id', ondelete='CASCADE'), primary_key=True)
    user_id = Column(String(32), primary_key=True, index=True)
    platform = Column(String(32), nullable=False)
    channel_url = Column(String(255), nullable=False)
    followers = Column(Integer, default=0, nullable=False)
    approved = Column(Boolean, default=False, nullable=False)
    applied_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    guild = relationship("GuildSettings", back_populates="creator_programs")


class WelcomeSettings(Base, TimestampMixin):
    __tablename__ = 'welcome_settings'

    guild_id = Column(String(32), ForeignKey('guild_settings.guild_id', ondelete='CASCADE'), primary_key=True)
    welcome_channel = Column(String(32), nullable=True)
    goodbye_channel = Column(String(32), nullable=True)
    auto_role = Column(String(32), nullable=True)
    welcome_embed = Column(Text, default="{}", nullable=False)
    goodbye_embed = Column(Text, default="{}", nullable=False)

    guild = relationship("GuildSettings", back_populates="welcome_settings")


class LogSettings(Base, TimestampMixin):
    __tablename__ = 'log_settings'

    guild_id = Column(String(32), ForeignKey('guild_settings.guild_id', ondelete='CASCADE'), primary_key=True)
    member_logs = Column(String(32), nullable=True)
    message_logs = Column(String(32), nullable=True)
    voice_logs = Column(String(32), nullable=True)
    moderation_logs = Column(String(32), nullable=True)
    role_logs = Column(String(32), nullable=True)
    channel_logs = Column(String(32), nullable=True)
    emoji_logs = Column(String(32), nullable=True)
    sticker_logs = Column(String(32), nullable=True)
    invite_logs = Column(String(32), nullable=True)
    webhook_logs = Column(String(32), nullable=True)
    server_logs = Column(String(32), nullable=True)
    ticket_logs = Column(String(32), nullable=True)
    security_logs = Column(String(32), nullable=True)
    points_logs = Column(String(32), nullable=True)
    clan_logs = Column(String(32), nullable=True)
    creator_logs = Column(String(32), nullable=True)
    backup_logs = Column(String(32), nullable=True)
    dashboard_logs = Column(String(32), nullable=True)
    command_logs = Column(String(32), nullable=True)
    error_logs = Column(String(32), nullable=True)

    guild = relationship("GuildSettings", back_populates="log_settings")


class DashboardAuditLogs(Base):
    __tablename__ = 'dashboard_audit_logs'

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(String(32), ForeignKey('guild_settings.guild_id', ondelete='CASCADE'), nullable=False, index=True)
    admin_id = Column(String(32), nullable=False)
    action_type = Column(String(64), nullable=False)
    page = Column(String(64), nullable=False)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    guild = relationship("GuildSettings", back_populates="audit_logs")


class Backups(Base, TimestampMixin):
    __tablename__ = 'backups'

    backup_id = Column(String(64), primary_key=True)
    guild_id = Column(String(32), ForeignKey('guild_settings.guild_id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(64), nullable=False)
    description = Column(Text, nullable=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size = Column(Integer, nullable=False)
    created_by = Column(String(32), nullable=False)
    automatic_backup = Column(Boolean, default=False, nullable=False)
    version = Column(String(16), default="1.0", nullable=False)

    guild = relationship("GuildSettings", back_populates="backups")


class ScheduledBackups(Base, TimestampMixin):
    __tablename__ = 'scheduled_backups'

    guild_id = Column(String(32), ForeignKey('guild_settings.guild_id', ondelete='CASCADE'), primary_key=True)
    enabled = Column(Boolean, default=False, nullable=False)
    interval = Column(String(32), default="daily", nullable=False)
    last_backup = Column(DateTime, nullable=True)
    next_backup = Column(DateTime, nullable=True)
    keep_last_backups = Column(Integer, default=5, nullable=False)

    guild = relationship("GuildSettings", back_populates="scheduled_backups")


class LevelSystem(Base, TimestampMixin):
    __tablename__ = 'level_system'

    guild_id = Column(String(32), ForeignKey('guild_settings.guild_id', ondelete='CASCADE'), primary_key=True)
    user_id = Column(String(32), primary_key=True, index=True)
    xp = Column(Integer, default=0, nullable=False)
    level = Column(Integer, default=0, nullable=False)
    total_messages = Column(Integer, default=0, nullable=False)

    guild = relationship("GuildSettings", back_populates="level_systems")


class ReactionRoles(Base):
    __tablename__ = 'reaction_roles'

    guild_id = Column(String(32), ForeignKey('guild_settings.guild_id', ondelete='CASCADE'), primary_key=True)
    message_id = Column(String(32), primary_key=True, index=True)
    emoji = Column(String(64), primary_key=True)
    role_id = Column(String(32), nullable=False)

    guild = relationship("GuildSettings", back_populates="reaction_roles")


class AutoRoles(Base):
    __tablename__ = 'auto_roles'

    guild_id = Column(String(32), ForeignKey('guild_settings.guild_id', ondelete='CASCADE'), primary_key=True)
    role_id = Column(String(32), primary_key=True)
    bot_role = Column(Boolean, default=False, nullable=False)
    human_role = Column(Boolean, default=True, nullable=False)

    guild = relationship("GuildSettings", back_populates="auto_roles")


class DashboardNotifications(Base, TimestampMixin):
    __tablename__ = 'dashboard_notifications'

    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(String(32), ForeignKey('guild_settings.guild_id', ondelete='CASCADE'), nullable=False, index=True)
    title = Column(String(128), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(32), default="info", nullable=False)
    read = Column(Boolean, default=False, nullable=False)

    guild = relationship("GuildSettings", back_populates="notifications")
mestampMixin):
    __tablename__ = 'welcome_settings'

    guild_id = Column(String(32), ForeignKey('guild_settings.guild_id', ondelete='CASCADE'), primary_key=True)
    welcome_channel = Column(String(32), nullable=True)
    goodbye_channel = Column(String(32), nullable=True)
    auto_role = Column(String(32), nullable=True)
    welcome_embed = Column(Text, default="{}", nullable=False)
    goodbye_embed = Column(Text, default="{}", nullable=False)

    guild = relationship("GuildSettings", back_populates="welcome_settings")


class LogSettings(Base, TimestampMixin):
    __tablename__ = 'log_settings'

    guild_id = Column(String(32), ForeignKey('guild_settings.guild_id', ondelete='CASCADE'), primary_key=True)
    member_logs = Column(String(32), nullable=True)
    message_logs = Column(String(32), nullable=True)
    voice_logs = Column(String(32), nullable=True)
    moderation_logs = Column(String(32), nullable=True)
    role_logs = Column(String(32), nullable=True)
    channel_logs = Column(String(32), nullable=True)
    emoji_logs = Column(String(32), nullable=True)
    sticker_logs = Column(String(32), nullable=True)
    invite_logs = Column(String(32), nullable=True)
    webhook_logs = Column(String(32), nullable=True)
    server_logs = Column(String(32), nullable=True)
    ticket_logs = Column(String(32), nullable=True)
    security_logs = Column(String(32), nullable=True)
    points_logs = Column(String(32), nullable=True)
    clan_logs = Column(String(32), nullable=True)
    creator_logs = Column(String(32), nullable=True)
    backup_logs = Column(String(32), nullable=True)
    dashboard_logs = Column(String(32), nullable=True)
    command_logs = Column(String(32), nullable=True)
    error_logs = Column(String(32), nullable=True)

    guild = relationship("GuildSettings", back_populates="log_settings")


class DashboardAuditLogs(Base):
    __tablename__ = 'dashboard_audit_logs'

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(String(32), ForeignKey('guild_settings.guild_id', ondelete='CASCADE'), nullable=False, index=True)
    admin_id = Column(String(32), nullable=False)
    action_type = Column(String(64), nullable=False)
    page = Column(String(64), nullable=False)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    guild = relationship("GuildSettings", back_populates="audit_logs")


class Backups(Base, TimestampMixin):
    __tablename__ = 'backups'

    backup_id = Column(String(64), primary_key=True)
    guild_id = Column(String(32), ForeignKey('guild_settings.guild_id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(64), nullable=False)
    description = Column(Text, nullable=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size = Column(Integer, nullable=False)
    created_by = Column(String(32), nullable=False)
    automatic_backup = Column(Boolean, default=False, nullable=False)
    version = Column(String(16), default="1.0", nullable=False)

    guild = relationship("GuildSettings", back_populates="backups")


class ScheduledBackups(Base, TimestampMixin):
    __tablename__ = 'scheduled_backups'

    guild_id = Column(String(32), ForeignKey('guild_settings.guild_id', ondelete='CASCADE'), primary_key=True)
    enabled = Column(Boolean, default=False, nullable=False)
    interval = Column(String(32), default="daily", nullable=False)
    last_backup = Column(DateTime, nullable=True)
    next_backup = Column(DateTime, nullable=True)
    keep_last_backups = Column(Integer, default=5, nullable=False)

    guild = relationship("GuildSettings", back_populates="scheduled_backups")


class LevelSystem(Base, TimestampMixin):
    __tablename__ = 'level_system'

    guild_id = Column(String(32), ForeignKey('guild_settings.guild_id', ondelete='CASCADE'), primary_key=True)
    user_id = Column(String(32), primary_key=True, index=True)
    xp = Column(Integer, default=0, nullable=False)
    level = Column(Integer, default=0, nullable=False)
    total_messages = Column(Integer, default=0, nullable=False)

    guild = relationship("GuildSettings", back_populates="level_systems")


class ReactionRoles(Base):
    __tablename__ = 'reaction_roles'

    guild_id = Column(String(32), ForeignKey('guild_settings.guild_id', ondelete='CASCADE'), primary_key=True)
    message_id = Column(String(32), primary_key=True, index=True)
    emoji = Column(String(64), primary_key=True)
    role_id = Column(String(32), nullable=False)

    guild = relationship("GuildSettings", back_populates="reaction_roles")


class AutoRoles(Base):
    __tablename__ = 'auto_roles'

    guild_id = Column(String(32), ForeignKey('guild_settings.guild_id', ondelete='CASCADE'), primary_key=True)
    role_id = Column(String(32), primary_key=True)
    bot_role = Column(Boolean, default=False, nullable=False)
    human_role = Column(Boolean, default=True, nullable=False)

    guild = relationship("GuildSettings", back_populates="auto_roles")


class DashboardNotifications(Base, TimestampMixin):
    __tablename__ = 'dashboard_notifications'

    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(String(32), ForeignKey('guild_settings.guild_id', ondelete='CASCADE'), nullable=False, index=True)
    title = Column(String(128), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(32), default="info", nullable=False)
    read = Column(Boolean, default=False, nullable=False)

    guild = relationship("GuildSettings", back_populates="notifications")
    anti_bots = Column(Boolean, default=False, nullable=False)
    anti_webhooks = Column(Boolean, default=False, nullable=False)
    anti_scam = Column(Boolean, default=True, nullable=False)
    anti_phishing = Column(Boolean, default=True, nullable=False)
    anti_raid = Column(Boolean, default=False, nullable=False)
    anti_mass_join = Column(Boolean, default=False, nullable=False)
    anti_bad_words = Column(Boolean, default=False, nullable=False)
    verification_enabled = Column(Boolean, default=False, nullable=False)
    punishment_type = Column(String(32), default="timeout", nullable=False)
    automod_config = Column(Text, default="{}", nullable=False)  # JSON stored as text for sqlite/postgres compatibility
    whitelist = Column(Text, default="[]", nullable=False)
    blacklist = Column(Text, default="[]", nullable=False)

    guild = relationship("GuildSettings", back_populates="security_settings")


class ModerationCases(Base, TimestampMixin):
    __tablename__ = 'moderation_cases'

    case_id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(String(32), ForeignKey('guild_settings.guild_id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(String(32), nullable=False, index=True)
    moderator_id = Column(String(32), nullable=False)
    action = Column(String(32), nullable=False)  # ban, kick, timeout, warn
    reason = Column(Text, nullable=True)
    duration = Column(Integer, nullable=True)  # in seconds
    active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime, nullable=True)

    guild = relationship("GuildSettings", back_populates="moderation_cases")


class TicketPanels(Base, TimestampMixin):
    __tablename__ = 'ticket_panels'

    panel_id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(String(32), ForeignKey('guild_settings.guild_id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(64), nullable=False)
    channel_id = Column(String(32), nullable=False)
    category_id = Column(String(32), nullable=False)
    transcript_channel = Column(String(32), nullable=True)
    support_roles = Column(Text, default="[]", nullable=False)  # JSON list of role IDs
    questions = Column(Text, default="[]", nullable=False)  # JSON questions list
    auto_close = Column(Boolean, default=False, nullable=False)

    guild = relationship("GuildSettings", back_populates="ticket_panels")
    tickets = relationship("Tickets", back_populates="panel", cascade="all, delete-orphan")


class Tickets(Base, TimestampMixin):
    __tablename__ = 'tickets'

    ticket_id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(String(32), ForeignKey('guild_settings.guild_id', ondelete='CASCADE'), nullable=False, index=True)
    panel_id = Column(Integer, ForeignKey('ticket_panels.panel_id', ondelete='CASCADE'), nullable=False)
    creator_id = Column(String(32), nullable=False, index=True)
    channel_id = Column(String(32), nullable=False, unique=True)
    claimed_by = Column(String(32), nullable=True)
    status = Column(String(32), default="open", nullable=False)  # open, closed, claimed
    rating = Column(Integer, nullable=True)
    closed_at = Column(DateTime, nullable=True)

    guild = relationship("GuildSettings", back_populates="tickets")
    panel = relationship("TicketPanels", back_populates="tickets")


class EconomyPoints(Base, TimestampMixin):
    __tablename__ = 'economy_points'

    guild_id = Column(String(32), ForeignKey('guild_settings.guild_id', ondelete='CASCADE'), primary_key=True)
    user_id = Column(String(32), primary_key=True, index=True)
    points = Column(Integer, default=0, nullable=False)
    total_earned = Column(Integer, default=0, nullable=False)
    total_spent = Column(Integer, default=0, nullable=False)
    season_id = Column(String(32), default="default", nullable=False)
    last_daily = Column(DateTime, nullable=True)

    guild = relationship("GuildSettings", back_populates="economy_points")


class ClanSystem(Base, TimestampMixin):
    __tablename__ = 'clan_system'

    clan_id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(String(32), ForeignKey('guild_settings.guild_id', ondelete='CASCADE'), nullable=False, index=True)
    owner_id = Column(String(32), nullable=False)
    name = Column(String(64), nullable=False)
    description = Column(Text, nullable=True)
    logo = Column(String(255), nullable=True)
    total_points = Column(Integer, default=0, nullable=False)
    level = Column(Integer, default=1, nullable=False)

    guild = relationship("GuildSettings", back_populates="clans")
    members = relationship("ClanMembers", back_populates="clan", cascade="all, delete-orphan")


class ClanMembers(Base):
    __tablename__ = 'clan_members'

    clan_id = Column(Integer, ForeignKey('clan_system.clan_id', ondelete='CASCADE'), primary_key=True)
    user_id = Column(String(32), primary_key=True, index=True)
    role = Column(String(32), default="member", nullable=False)  # owner, admin, member
    joined_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    clan = relationship("ClanSystem", back_populates="members")


class CreatorProgram(Base, TimestampMixin):
    __tablename__ = 'creator_program'

    guild_id = Column(String(32), ForeignKey('guild_settings.guild_id', ondelete='CASCADE'), primary_key=True)
    user_id = Column(String(32), primary_key=True, index=True)
    platform = Column(String(32), nullable=False)  # youtube, twitch, tiktok, kick
    channel_url = Column(String(255), nullable=False)
    followers = Column(Integer, default=0, nullable=False)
    approved = Column(Boolean, default=False, nullable=False)
    applied_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    guild = relationship("GuildSettings", back_populates="creator_programs")


class WelcomeSettings(Base, TimestampMixin):
    __tablename__ = 'welcome_settings'

    guild_id = Column(String(32), ForeignKey('guild_settings.guild_id', ondelete='CASCADE'), primary_key=True)
    welcome_channel = Column(String(32), nullable=True)
    goodbye_channel = Column(String(32), nullable=True)
    auto_role = Column(String(32), nullable=True)
    welcome_embed = Column(Text, default="{}", nullable=False)  # JSON text
    goodbye_embed = Column(Text, default="{}", nullable=False)  # JSON text

    guild = relationship("GuildSettings", back_populates="welcome_settings")


class LogSettings(Base, TimestampMixin):
    __tablename__ = 'log_settings'

    guild_id = Column(String(32), ForeignKey('guild_settings.guild_id', ondelete='CASCADE'), primary_key=True)
    member_logs = Column(String(32), nullable=True)
    message_logs = Column(String(32), nullable=True)
    voice_logs = Column(String(32), nullable=True)
    moderation_logs = Column(String(32), nullable=True)
    role_logs = Column(String(32), nullable=True)
    channel_logs = Column(String(32), nullable=True)
    emoji_logs = Column(String(32), nullable=True)
    sticker_logs = Column(String(32), nullable=True)
    invite_logs = Column(String(32), nullable=True)
    webhook_logs = Column(String(32), nullable=True)
    server_logs = Column(String(32), nullable=True)
    ticket_logs = Column(String(32), nullable=True)
    security_logs = Column(String(32), nullable=True)
    points_logs = Column(String(32), nullable=True)
    clan_logs = Column(String(32), nullable=True)
    creator_logs = Column(String(32), nullable=True)
    backup_logs = Column(String(32), nullable=True)
    dashboard_logs = Column(String(32), nullable=True)
    command_logs = Column(String(32), nullable=True)
    error_logs = Column(String(32), nullable=True)

    guild = relationship("GuildSettings", back_populates="log_settings")


class DashboardAuditLogs(Base):
    __tablename__ = 'dashboard_audit_logs'

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(String(32), ForeignKey('guild_settings.guild_id', ondelete='CASCADE'), nullable=False, index=True)
    admin_id = Column(String(32), nullable=False)
    action_type = Column(String(64), nullable=False)
    page = Column(String(64), nullable=False)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    guild = relationship("GuildSettings", back_populates="audit_logs")


class Backups(Base, TimestampMixin):
    __tablename__ = 'backups'

    backup_id = Column(String(64), primary_key=True)
    guild_id = Column(String(32), ForeignKey('guild_settings.guild_id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(64), nullable=False)
    description = Column(Text, nullable=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    created_by = Column(String(32), nullable=False)
    automatic_backup = Column(Boolean, default=False, nullable=False)
    version = Column(String(16), default="1.0", nullable=False)

    guild = relationship("GuildSettings", back_populates="backups")


class ScheduledBackups(Base, TimestampMixin):
    __tablename__ = 'scheduled_backups'

    guild_id = Column(String(32), ForeignKey('guild_settings.guild_id', ondelete='CASCADE'), primary_key=True)
    enabled = Column(Boolean, default=False, nullable=False)
    interval = Column(String(32), default="daily", nullable=False)  # daily, weekly
    last_backup = Column(DateTime, nullable=True)
    next_backup = Column(DateTime, nullable=True)
    keep_last_backups = Column(Integer, default=5, nullable=False)

    guild = relationship("GuildSettings", back_populates="scheduled_backups")


class LevelSystem(Base, TimestampMixin):
    __tablename__ = 'level_system'

    guild_id = Column(String(32), ForeignKey('guild_settings.guild_id', ondelete='CASCADE'), primary_key=True)
    user_id = Column(String(32), primary_key=True, index=True)
    xp = Column(Integer, default=0, nullable=False)
    level = Column(Integer, default=0, nullable=False)
    total_messages = Column(Integer, default=0, nullable=False)

    guild = relationship("GuildSettings", back_populates="level_systems")


class ReactionRoles(Base):
    __tablename__ = 'reaction_roles'

    guild_id = Column(String(32), ForeignKey('guild_settings.guild_id', ondelete='CASCADE'), primary_key=True)
    message_id = Column(String(32), primary_key=True, index=True)
    emoji = Column(String(64), primary_key=True)
    role_id = Column(String(32), nullable=False)

    guild = relationship("GuildSettings", back_populates="reaction_roles")


class AutoRoles(Base):
    __tablename__ = 'auto_roles'

    guild_id = Column(String(32), ForeignKey('guild_settings.guild_id', ondelete='CASCADE'), primary_key=True)
    role_id = Column(String(32), primary_key=True)
    bot_role = Column(Boolean, default=False, nullable=False)
    human_role = Column(Boolean, default=True, nullable=False)

    guild = relationship("GuildSettings", back_populates="auto_roles")


class DashboardNotifications(Base, TimestampMixin):
    __tablename__ = 'dashboard_notifications'

    id = Column(Integer, primary_key=Test := None or True, autoincrement=True) # or standard autoincrement int
    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(String(32), ForeignKey('guild_settings.guild_id', ondelete='CASCADE'), nullable=False, index=True)
    title = Column(String(128), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(32), default="info", nullable=False)  # info, warning, success, error
    read = Column(Boolean, default=False, nullable=False)

    guild = relationship("GuildSettings", back_populates="notifications")
                welcome_image INTEGER DEFAULT 1,
                goodbye_channel INTEGER,
                goodbye_message TEXT,
                goodbye_image INTEGER DEFAULT 1,
                verify_channel INTEGER,
                verify_role INTEGER,
                auto_role INTEGER,
                mute_role INTEGER,
                member_counter_channel INTEGER,
                bot_counter_channel INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )""",

            # Warnings
            """CREATE TABLE IF NOT EXISTS warnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                user_id INTEGER,
                moderator_id INTEGER,
                reason TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )""",

            # Mutes
            """CREATE TABLE IF NOT EXISTS mutes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                user_id INTEGER,
                moderator_id INTEGER,
                reason TEXT,
                duration INTEGER,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                unmute_at TEXT
            )""",

            # Logs configuration
            """CREATE TABLE IF NOT EXISTS logs_config (
                guild_id INTEGER PRIMARY KEY,
                ban_log INTEGER,
                kick_log INTEGER,
                delete_log INTEGER,
                edit_log INTEGER,
                channel_log INTEGER,
                role_log INTEGER,
                member_log INTEGER,
                name_log INTEGER,
                mute_log INTEGER,
                ticket_log INTEGER,
                command_log INTEGER,
                invite_log INTEGER
            )""",

            # Protection configuration
            """CREATE TABLE IF NOT EXISTS protection_config (
                guild_id INTEGER PRIMARY KEY,
                anti_spam INTEGER DEFAULT 0,
                spam_limit INTEGER DEFAULT 5,
                anti_links INTEGER DEFAULT 0,
                anti_mention INTEGER DEFAULT 0,
                mention_limit INTEGER DEFAULT 5,
                anti_invites INTEGER DEFAULT 0,
                anti_bots INTEGER DEFAULT 0,
                anti_channel_create INTEGER DEFAULT 0,
                anti_role_create INTEGER DEFAULT 0,
                anti_channel_delete INTEGER DEFAULT 0,
                anti_role_delete INTEGER DEFAULT 0,
                anti_bad_words INTEGER DEFAULT 0,
                warn_limit INTEGER DEFAULT 3,
                warn_action TEXT DEFAULT 'mute',
                whitelist_roles TEXT DEFAULT '[]',
                whitelist_channels TEXT DEFAULT '[]'
            )""",

            # Spam tracking
            """CREATE TABLE IF NOT EXISTS spam_tracker (
                guild_id INTEGER,
                user_id INTEGER,
                message_count INTEGER DEFAULT 0,
                last_message TEXT,
                PRIMARY KEY (guild_id, user_id)
            )""",

            # Bad words list
            """CREATE TABLE IF NOT EXISTS bad_words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                word TEXT,
                UNIQUE(guild_id, word)
            )""",

            # Tickets
            """CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                user_id INTEGER,
                channel_id INTEGER,
                status TEXT DEFAULT 'open',
                department TEXT DEFAULT 'عام',
                rating INTEGER,
                transcript TEXT,
                ticket_number INTEGER,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                closed_at TEXT
            )""",

            # Ticket configuration
            """CREATE TABLE IF NOT EXISTS ticket_config (
                guild_id INTEGER PRIMARY KEY,
                category_id INTEGER,
                log_channel INTEGER,
                support_role INTEGER,
                auto_close INTEGER DEFAULT 0,
                rating_enabled INTEGER DEFAULT 1,
                panel_channel INTEGER,
                panel_message_id INTEGER,
                ticket_counter INTEGER DEFAULT 0,
                departments TEXT DEFAULT '["عام","فني","إداري","شكاوى"]'
            )""",

            # Points system
            """CREATE TABLE IF NOT EXISTS points (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                user_id INTEGER,
                points INTEGER DEFAULT 0,
                point_type TEXT DEFAULT 'member',
                UNIQUE(guild_id, user_id, point_type)
            )""",

            # Points rewards
            """CREATE TABLE IF NOT EXISTS point_rewards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                required_points INTEGER,
                reward_role INTEGER,
                point_type TEXT DEFAULT 'member'
            )""",

            # ── XP / Leveling ──────────────────────────────────────────────────

            """CREATE TABLE IF NOT EXISTS xp_data (
                guild_id INTEGER,
                user_id INTEGER,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 0,
                PRIMARY KEY (guild_id, user_id)
            )""",

            """CREATE TABLE IF NOT EXISTS xp_config (
                guild_id INTEGER PRIMARY KEY,
                enabled INTEGER DEFAULT 1,
                xp_min INTEGER DEFAULT 5,
                xp_max INTEGER DEFAULT 15,
                cooldown INTEGER DEFAULT 60,
                announce_channel INTEGER,
                announce_type TEXT DEFAULT 'current',
                stack_roles INTEGER DEFAULT 0
            )""",

            """CREATE TABLE IF NOT EXISTS level_roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                level INTEGER,
                role_id INTEGER,
                UNIQUE(guild_id, level)
            )""",

            # ── Economy ────────────────────────────────────────────────────────

            """CREATE TABLE IF NOT EXISTS economy (
                guild_id INTEGER,
                user_id INTEGER,
                credits INTEGER DEFAULT 0,
                PRIMARY KEY (guild_id, user_id)
            )""",

            """CREATE TABLE IF NOT EXISTS daily_cooldowns (
                guild_id INTEGER,
                user_id INTEGER,
                last_daily TEXT,
                PRIMARY KEY (guild_id, user_id)
            )""",

            """CREATE TABLE IF NOT EXISTS economy_config (
                guild_id INTEGER PRIMARY KEY,
                daily_amount INTEGER DEFAULT 100,
                currency_name TEXT DEFAULT 'كريدت',
                currency_emoji TEXT DEFAULT '💰'
            )""",

            """CREATE TABLE IF NOT EXISTS shop_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                name TEXT,
                description TEXT DEFAULT '',
                price INTEGER,
                role_id INTEGER,
                stock INTEGER DEFAULT -1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )""",

            # ── Anti-Raid ──────────────────────────────────────────────────────

            """CREATE TABLE IF NOT EXISTS anti_raid_config (
                guild_id INTEGER PRIMARY KEY,
                enabled INTEGER DEFAULT 1,
                action_limit INTEGER DEFAULT 3,
                time_window INTEGER DEFAULT 300,
                security_log_channel INTEGER
            )""",

            # ── Staff roles config ─────────────────────────────────────────────

            """CREATE TABLE IF NOT EXISTS staff_config (
                guild_id INTEGER PRIMARY KEY,
                moderator_roles TEXT DEFAULT '[]',
                admin_roles TEXT DEFAULT '[]'
            )""",

            # Clans
            """CREATE TABLE IF NOT EXISTS clans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                name TEXT,
                owner_id INTEGER,
                points INTEGER DEFAULT 0,
                description TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(guild_id, name)
            )""",

            """CREATE TABLE IF NOT EXISTS clan_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                clan_id INTEGER,
                user_id INTEGER,
                role TEXT DEFAULT 'member',
                joined_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(clan_id, user_id)
            )""",

            """CREATE TABLE IF NOT EXISTS clan_challenges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                title TEXT,
                description TEXT,
                reward_points INTEGER,
                status TEXT DEFAULT 'active',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                ends_at TEXT
            )""",

            # Content creators
            """CREATE TABLE IF NOT EXISTS content_creators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                user_id INTEGER,
                youtube_channel_id TEXT,
                youtube_name TEXT,
                last_video_id TEXT,
                announce_channel INTEGER,
                subscriber_count INTEGER DEFAULT 0,
                creator_role INTEGER,
                UNIQUE(guild_id, user_id)
            )""",

            # Suggestions
            """CREATE TABLE IF NOT EXISTS suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                user_id INTEGER,
                message_id INTEGER,
                channel_id INTEGER,
                content TEXT,
                status TEXT DEFAULT 'pending',
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )""",

            # Reports
            """CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                reporter_id INTEGER,
                reported_id INTEGER,
                reason TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )""",

            # Action logs
            """CREATE TABLE IF NOT EXISTS action_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                moderator_id INTEGER,
                target_id INTEGER,
                action TEXT,
                reason TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )""",

            # Reaction roles
            """CREATE TABLE IF NOT EXISTS reaction_roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                message_id INTEGER,
                emoji TEXT,
                role_id INTEGER
            )""",
        ]

        for query in queries:
            await self._conn.execute(query)
        await self._conn.commit()

        # Migrations — add new columns to existing tables if missing
        await self._migrate()

    async def _migrate(self):
        """Add new columns to existing tables for backwards compatibility."""
        migrations = [
            "ALTER TABLE guilds ADD COLUMN welcome_image INTEGER DEFAULT 1",
            "ALTER TABLE guilds ADD COLUMN goodbye_image INTEGER DEFAULT 1",
            "ALTER TABLE protection_config ADD COLUMN anti_bad_words INTEGER DEFAULT 0",
        ]
        for sql in migrations:
            try:
                await self._conn.execute(sql)
            except Exception:
                pass  # Column already exists
        await self._conn.commit()

    # ── Guild Methods ──────────────────────────────────────────────────────────

    async def ensure_guild(self, guild_id: int):
        await self._conn.execute(
            "INSERT OR IGNORE INTO guilds (guild_id) VALUES (?)",
            (guild_id,)
        )
        await self._conn.commit()

    async def get_guild(self, guild_id: int):
        await self.ensure_guild(guild_id)
        async with self._conn.execute(
            "SELECT * FROM guilds WHERE guild_id = ?", (guild_id,)
        ) as cur:
            return await cur.fetchone()

    async def update_guild(self, guild_id: int, **kwargs):
        await self.ensure_guild(guild_id)
        sets = ', '.join(f"{k} = ?" for k in kwargs)
        vals = list(kwargs.values()) + [guild_id]
        await self._conn.execute(f"UPDATE guilds SET {sets} WHERE guild_id = ?", vals)
        await self._conn.commit()

    async def get_prefix(self, guild_id: int) -> str:
        async with self._conn.execute(
            "SELECT prefix FROM guilds WHERE guild_id = ?", (guild_id,)
        ) as cur:
            row = await cur.fetchone()
            return row['prefix'] if row else '!'

    # ── Warning Methods ────────────────────────────────────────────────────────

    async def add_warning(self, guild_id, user_id, moderator_id, reason):
        await self._conn.execute(
            "INSERT INTO warnings (guild_id, user_id, moderator_id, reason) VALUES (?, ?, ?, ?)",
            (guild_id, user_id, moderator_id, reason)
        )
        await self._conn.commit()
        return await self.get_warning_count(guild_id, user_id)

    async def get_warnings(self, guild_id, user_id):
        async with self._conn.execute(
            "SELECT * FROM warnings WHERE guild_id = ? AND user_id = ? ORDER BY timestamp DESC",
            (guild_id, user_id)
        ) as cur:
            return await cur.fetchall()

    async def get_warning_count(self, guild_id, user_id):
        async with self._conn.execute(
            "SELECT COUNT(*) as cnt FROM warnings WHERE guild_id = ? AND user_id = ?",
            (guild_id, user_id)
        ) as cur:
            row = await cur.fetchone()
            return row['cnt'] if row else 0

    async def remove_warning(self, warning_id, guild_id):
        await self._conn.execute(
            "DELETE FROM warnings WHERE id = ? AND guild_id = ?",
            (warning_id, guild_id)
        )
        await self._conn.commit()

    async def clear_warnings(self, guild_id, user_id):
        await self._conn.execute(
            "DELETE FROM warnings WHERE guild_id = ? AND user_id = ?",
            (guild_id, user_id)
        )
        await self._conn.commit()

    # ── Log Config Methods ─────────────────────────────────────────────────────

    async def get_log_config(self, guild_id):
        async with self._conn.execute(
            "SELECT * FROM logs_config WHERE guild_id = ?", (guild_id,)
        ) as cur:
            return await cur.fetchone()

    async def set_log_channel(self, guild_id, log_type, channel_id):
        await self._conn.execute(
            f"INSERT INTO logs_config (guild_id, {log_type}) VALUES (?, ?) "
            f"ON CONFLICT(guild_id) DO UPDATE SET {log_type} = ?",
            (guild_id, channel_id, channel_id)
        )
        await self._conn.commit()

    # ── Protection Config ──────────────────────────────────────────────────────

    async def get_protection(self, guild_id):
        async with self._conn.execute(
            "SELECT * FROM protection_config WHERE guild_id = ?", (guild_id,)
        ) as cur:
            row = await cur.fetchone()
        if not row:
            await self._conn.execute(
                "INSERT OR IGNORE INTO protection_config (guild_id) VALUES (?)",
                (guild_id,)
            )
            await self._conn.commit()
            async with self._conn.execute(
                "SELECT * FROM protection_config WHERE guild_id = ?", (guild_id,)
            ) as cur:
                row = await cur.fetchone()
        return row

    async def update_protection(self, guild_id, **kwargs):
        await self.get_protection(guild_id)
        sets = ', '.join(f"{k} = ?" for k in kwargs)
        vals = list(kwargs.values()) + [guild_id]
        await self._conn.execute(
            f"UPDATE protection_config SET {sets} WHERE guild_id = ?", vals
        )
        await self._conn.commit()

    # ── Bad Words ──────────────────────────────────────────────────────────────

    async def get_bad_words(self, guild_id):
        async with self._conn.execute(
            "SELECT word FROM bad_words WHERE guild_id = ?", (guild_id,)
        ) as cur:
            rows = await cur.fetchall()
        return [r['word'] for r in rows]

    async def add_bad_word(self, guild_id, word):
        try:
            await self._conn.execute(
                "INSERT OR IGNORE INTO bad_words (guild_id, word) VALUES (?, ?)",
                (guild_id, word.lower())
            )
            await self._conn.commit()
            return True
        except Exception:
            return False

    async def remove_bad_word(self, guild_id, word):
        await self._conn.execute(
            "DELETE FROM bad_words WHERE guild_id = ? AND word = ?",
            (guild_id, word.lower())
        )
        await self._conn.commit()

    async def clear_bad_words(self, guild_id):
        await self._conn.execute("DELETE FROM bad_words WHERE guild_id = ?", (guild_id,))
        await self._conn.commit()

    # ── Spam Tracker ───────────────────────────────────────────────────────────

    async def increment_spam(self, guild_id, user_id):
        now = datetime.utcnow().isoformat()
        await self._conn.execute(
            """INSERT INTO spam_tracker (guild_id, user_id, message_count, last_message)
               VALUES (?, ?, 1, ?)
               ON CONFLICT(guild_id, user_id) DO UPDATE SET
               message_count = message_count + 1, last_message = ?""",
            (guild_id, user_id, now, now)
        )
        await self._conn.commit()
        async with self._conn.execute(
            "SELECT message_count FROM spam_tracker WHERE guild_id = ? AND user_id = ?",
            (guild_id, user_id)
        ) as cur:
            row = await cur.fetchone()
        return row['message_count'] if row else 0

    async def reset_spam(self, guild_id, user_id):
        await self._conn.execute(
            "UPDATE spam_tracker SET message_count = 0 WHERE guild_id = ? AND user_id = ?",
            (guild_id, user_id)
        )
        await self._conn.commit()

    # ── Ticket Methods ─────────────────────────────────────────────────────────

    async def get_ticket_config(self, guild_id):
        async with self._conn.execute(
            "SELECT * FROM ticket_config WHERE guild_id = ?", (guild_id,)
        ) as cur:
            row = await cur.fetchone()
        if not row:
            await self._conn.execute(
                "INSERT OR IGNORE INTO ticket_config (guild_id) VALUES (?)",
                (guild_id,)
            )
            await self._conn.commit()
            async with self._conn.execute(
                "SELECT * FROM ticket_config WHERE guild_id = ?", (guild_id,)
            ) as cur:
                row = await cur.fetchone()
        return row

    async def update_ticket_config(self, guild_id, **kwargs):
        await self.get_ticket_config(guild_id)
        sets = ', '.join(f"{k} = ?" for k in kwargs)
        vals = list(kwargs.values()) + [guild_id]
        await self._conn.execute(
            f"UPDATE ticket_config SET {sets} WHERE guild_id = ?", vals
        )
        await self._conn.commit()

    async def create_ticket(self, guild_id, user_id, channel_id, department):
        config = await self.get_ticket_config(guild_id)
        counter = (config['ticket_counter'] or 0) + 1
        await self._conn.execute(
            "UPDATE ticket_config SET ticket_counter = ? WHERE guild_id = ?",
            (counter, guild_id)
        )
        await self._conn.execute(
            """INSERT INTO tickets (guild_id, user_id, channel_id, department, ticket_number)
               VALUES (?, ?, ?, ?, ?)""",
            (guild_id, user_id, channel_id, department, counter)
        )
        await self._conn.commit()
        return counter

    async def get_ticket(self, channel_id):
        async with self._conn.execute(
            "SELECT * FROM tickets WHERE channel_id = ?", (channel_id,)
        ) as cur:
            return await cur.fetchone()

    async def update_ticket(self, channel_id, **kwargs):
        sets = ', '.join(f"{k} = ?" for k in kwargs)
        vals = list(kwargs.values()) + [channel_id]
        await self._conn.execute(
            f"UPDATE tickets SET {sets} WHERE channel_id = ?", vals
        )
        await self._conn.commit()

    async def update_ticket_by_number(self, ticket_number, guild_id, **kwargs):
        sets = ', '.join(f"{k} = ?" for k in kwargs)
        vals = list(kwargs.values()) + [ticket_number, guild_id]
        await self._conn.execute(
            f"UPDATE tickets SET {sets} WHERE ticket_number = ? AND guild_id = ?", vals
        )
        await self._conn.commit()

    async def get_user_tickets(self, guild_id, user_id):
        async with self._conn.execute(
            "SELECT * FROM tickets WHERE guild_id = ? AND user_id = ? ORDER BY timestamp DESC",
            (guild_id, user_id)
        ) as cur:
            return await cur.fetchall()

    # ── Points Methods ─────────────────────────────────────────────────────────

    async def get_points(self, guild_id, user_id, point_type='member'):
        async with self._conn.execute(
            "SELECT points FROM points WHERE guild_id = ? AND user_id = ? AND point_type = ?",
            (guild_id, user_id, point_type)
        ) as cur:
            row = await cur.fetchone()
        return row['points'] if row else 0

    async def add_points(self, guild_id, user_id, amount, point_type='member'):
        await self._conn.execute(
            """INSERT INTO points (guild_id, user_id, points, point_type) VALUES (?, ?, ?, ?)
               ON CONFLICT(guild_id, user_id, point_type) DO UPDATE SET points = points + ?""",
            (guild_id, user_id, amount, point_type, amount)
        )
        await self._conn.commit()
        return await self.get_points(guild_id, user_id, point_type)

    async def remove_points(self, guild_id, user_id, amount, point_type='member'):
        current = await self.get_points(guild_id, user_id, point_type)
        new_points = max(0, current - amount)
        await self._conn.execute(
            """INSERT INTO points (guild_id, user_id, points, point_type) VALUES (?, ?, ?, ?)
               ON CONFLICT(guild_id, user_id, point_type) DO UPDATE SET points = ?""",
            (guild_id, user_id, new_points, point_type, new_points)
        )
        await self._conn.commit()
        return new_points

    async def get_leaderboard(self, guild_id, point_type='member', limit=10):
        async with self._conn.execute(
            """SELECT user_id, points FROM points
               WHERE guild_id = ? AND point_type = ?
               ORDER BY points DESC LIMIT ?""",
            (guild_id, point_type, limit)
        ) as cur:
            return await cur.fetchall()

    async def get_point_rewards(self, guild_id, point_type='member'):
        async with self._conn.execute(
            """SELECT * FROM point_rewards WHERE guild_id = ? AND point_type = ?
               ORDER BY required_points ASC""",
            (guild_id, point_type)
        ) as cur:
            return await cur.fetchall()

    # ── XP / Leveling Methods ──────────────────────────────────────────────────

    async def get_xp_config(self, guild_id):
        async with self._conn.execute(
            "SELECT * FROM xp_config WHERE guild_id = ?", (guild_id,)
        ) as cur:
            row = await cur.fetchone()
        if not row:
            await self._conn.execute(
                "INSERT OR IGNORE INTO xp_config (guild_id) VALUES (?)", (guild_id,)
            )
            await self._conn.commit()
            async with self._conn.execute(
                "SELECT * FROM xp_config WHERE guild_id = ?", (guild_id,)
            ) as cur:
                row = await cur.fetchone()
        return row

    async def update_xp_config(self, guild_id, **kwargs):
        await self.get_xp_config(guild_id)
        sets = ', '.join(f"{k} = ?" for k in kwargs)
        vals = list(kwargs.values()) + [guild_id]
        await self._conn.execute(
            f"UPDATE xp_config SET {sets} WHERE guild_id = ?", vals
        )
        await self._conn.commit()

    async def get_user_xp(self, guild_id, user_id):
        async with self._conn.execute(
            "SELECT * FROM xp_data WHERE guild_id = ? AND user_id = ?",
            (guild_id, user_id)
        ) as cur:
            return await cur.fetchone()

    async def add_xp(self, guild_id, user_id, amount):
        """Add XP, recalculate level. Returns (new_xp, new_level, leveled_up)."""
        row = await self.get_user_xp(guild_id, user_id)
        if row:
            new_xp = row['xp'] + amount
            old_level = row['level']
        else:
            new_xp = amount
            old_level = 0

        # Level formula: xp needed for level L = L^2 * 50
        new_level = int((new_xp / 50) ** 0.5)
        leveled_up = new_level > old_level

        await self._conn.execute(
            """INSERT INTO xp_data (guild_id, user_id, xp, level) VALUES (?, ?, ?, ?)
               ON CONFLICT(guild_id, user_id) DO UPDATE SET xp = ?, level = ?""",
            (guild_id, user_id, new_xp, new_level, new_xp, new_level)
        )
        await self._conn.commit()
        return new_xp, new_level, leveled_up

    async def get_xp_leaderboard(self, guild_id, limit=10):
        async with self._conn.execute(
            """SELECT user_id, xp, level FROM xp_data
               WHERE guild_id = ? ORDER BY xp DESC LIMIT ?""",
            (guild_id, limit)
        ) as cur:
            return await cur.fetchall()

    async def get_xp_rank(self, guild_id, user_id):
        async with self._conn.execute(
            """SELECT COUNT(*) + 1 as rank FROM xp_data
               WHERE guild_id = ? AND xp > (SELECT xp FROM xp_data WHERE guild_id = ? AND user_id = ?)""",
            (guild_id, guild_id, user_id)
        ) as cur:
            row = await cur.fetchone()
        return row['rank'] if row else 1

    async def set_xp(self, guild_id, user_id, xp, level):
        await self._conn.execute(
            """INSERT INTO xp_data (guild_id, user_id, xp, level) VALUES (?, ?, ?, ?)
               ON CONFLICT(guild_id, user_id) DO UPDATE SET xp = ?, level = ?""",
            (guild_id, user_id, xp, level, xp, level)
        )
        await self._conn.commit()

    async def get_level_roles(self, guild_id):
        async with self._conn.execute(
            "SELECT * FROM level_roles WHERE guild_id = ? ORDER BY level ASC",
            (guild_id,)
        ) as cur:
            return await cur.fetchall()

    async def set_level_role(self, guild_id, level, role_id):
        await self._conn.execute(
            """INSERT INTO level_roles (guild_id, level, role_id) VALUES (?, ?, ?)
               ON CONFLICT(guild_id, level) DO UPDATE SET role_id = ?""",
            (guild_id, level, role_id, role_id)
        )
        await self._conn.commit()

    async def remove_level_role(self, guild_id, level):
        await self._conn.execute(
            "DELETE FROM level_roles WHERE guild_id = ? AND level = ?",
            (guild_id, level)
        )
        await self._conn.commit()

    # ── Economy Methods ────────────────────────────────────────────────────────

    async def get_economy_config(self, guild_id):
        async with self._conn.execute(
            "SELECT * FROM economy_config WHERE guild_id = ?", (guild_id,)
        ) as cur:
            row = await cur.fetchone()
        if not row:
            await self._conn.execute(
                "INSERT OR IGNORE INTO economy_config (guild_id) VALUES (?)", (guild_id,)
            )
            await self._conn.commit()
            async with self._conn.execute(
                "SELECT * FROM economy_config WHERE guild_id = ?", (guild_id,)
            ) as cur:
                row = await cur.fetchone()
        return row

    async def update_economy_config(self, guild_id, **kwargs):
        await self.get_economy_config(guild_id)
        sets = ', '.join(f"{k} = ?" for k in kwargs)
        vals = list(kwargs.values()) + [guild_id]
        await self._conn.execute(
            f"UPDATE economy_config SET {sets} WHERE guild_id = ?", vals
        )
        await self._conn.commit()

    async def get_credits(self, guild_id, user_id):
        async with self._conn.execute(
            "SELECT credits FROM economy WHERE guild_id = ? AND user_id = ?",
            (guild_id, user_id)
        ) as cur:
            row = await cur.fetchone()
        return row['credits'] if row else 0

    async def add_credits(self, guild_id, user_id, amount):
        await self._conn.execute(
            """INSERT INTO economy (guild_id, user_id, credits) VALUES (?, ?, ?)
               ON CONFLICT(guild_id, user_id) DO UPDATE SET credits = credits + ?""",
            (guild_id, user_id, amount, amount)
        )
        await self._conn.commit()
        return await self.get_credits(guild_id, user_id)

    async def remove_credits(self, guild_id, user_id, amount):
        current = await self.get_credits(guild_id, user_id)
        if current < amount:
            return False
        await self._conn.execute(
            "UPDATE economy SET credits = credits - ? WHERE guild_id = ? AND user_id = ?",
            (amount, guild_id, user_id)
        )
        await self._conn.commit()
        return True

    async def transfer_credits(self, guild_id, from_id, to_id, amount):
        success = await self.remove_credits(guild_id, from_id, amount)
        if not success:
            return False
        await self.add_credits(guild_id, to_id, amount)
        return True

    async def get_daily_cooldown(self, guild_id, user_id):
        async with self._conn.execute(
            "SELECT last_daily FROM daily_cooldowns WHERE guild_id = ? AND user_id = ?",
            (guild_id, user_id)
        ) as cur:
            row = await cur.fetchone()
        return row['last_daily'] if row else None

    async def set_daily_cooldown(self, guild_id, user_id):
        now = datetime.utcnow().isoformat()
        await self._conn.execute(
            """INSERT INTO daily_cooldowns (guild_id, user_id, last_daily) VALUES (?, ?, ?)
               ON CONFLICT(guild_id, user_id) DO UPDATE SET last_daily = ?""",
            (guild_id, user_id, now, now)
        )
        await self._conn.commit()

    async def get_credits_leaderboard(self, guild_id, limit=10):
        async with self._conn.execute(
            "SELECT user_id, credits FROM economy WHERE guild_id = ? ORDER BY credits DESC LIMIT ?",
            (guild_id, limit)
        ) as cur:
            return await cur.fetchall()

    # Shop methods
    async def get_shop_items(self, guild_id):
        async with self._conn.execute(
            "SELECT * FROM shop_items WHERE guild_id = ? ORDER BY price ASC",
            (guild_id,)
        ) as cur:
            return await cur.fetchall()

    async def get_shop_item(self, item_id):
        async with self._conn.execute(
            "SELECT * FROM shop_items WHERE id = ?", (item_id,)
        ) as cur:
            return await cur.fetchone()

    async def add_shop_item(self, guild_id, name, description, price, role_id, stock=-1):
        await self._conn.execute(
            """INSERT INTO shop_items (guild_id, name, description, price, role_id, stock)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (guild_id, name, description, price, role_id, stock)
        )
        await self._conn.commit()

    async def remove_shop_item(self, item_id, guild_id):
        await self._conn.execute(
            "DELETE FROM shop_items WHERE id = ? AND guild_id = ?",
            (item_id, guild_id)
        )
        await self._conn.commit()

    async def decrement_stock(self, item_id):
        await self._conn.execute(
            "UPDATE shop_items SET stock = stock - 1 WHERE id = ? AND stock > 0",
            (item_id,)
        )
        await self._conn.commit()

    # ── Anti-Raid Config ───────────────────────────────────────────────────────

    async def get_anti_raid_config(self, guild_id):
        async with self._conn.execute(
            "SELECT * FROM anti_raid_config WHERE guild_id = ?", (guild_id,)
        ) as cur:
            row = await cur.fetchone()
        if not row:
            await self._conn.execute(
                "INSERT OR IGNORE INTO anti_raid_config (guild_id) VALUES (?)", (guild_id,)
            )
            await self._conn.commit()
            async with self._conn.execute(
                "SELECT * FROM anti_raid_config WHERE guild_id = ?", (guild_id,)
            ) as cur:
                row = await cur.fetchone()
        return row

    async def update_anti_raid_config(self, guild_id, **kwargs):
        await self.get_anti_raid_config(guild_id)
        sets = ', '.join(f"{k} = ?" for k in kwargs)
        vals = list(kwargs.values()) + [guild_id]
        await self._conn.execute(
            f"UPDATE anti_raid_config SET {sets} WHERE guild_id = ?", vals
        )
        await self._conn.commit()

    # ── Staff Config ───────────────────────────────────────────────────────────

    async def get_staff_config(self, guild_id):
        async with self._conn.execute(
            "SELECT * FROM staff_config WHERE guild_id = ?", (guild_id,)
        ) as cur:
            row = await cur.fetchone()
        if not row:
            await self._conn.execute(
                "INSERT OR IGNORE INTO staff_config (guild_id) VALUES (?)", (guild_id,)
            )
            await self._conn.commit()
            async with self._conn.execute(
                "SELECT * FROM staff_config WHERE guild_id = ?", (guild_id,)
            ) as cur:
                row = await cur.fetchone()
        return row

    async def update_staff_config(self, guild_id, **kwargs):
        await self.get_staff_config(guild_id)
        sets = ', '.join(f"{k} = ?" for k in kwargs)
        vals = list(kwargs.values()) + [guild_id]
        await self._conn.execute(
            f"UPDATE staff_config SET {sets} WHERE guild_id = ?", vals
        )
        await self._conn.commit()

    # ── Clan Methods ───────────────────────────────────────────────────────────

    async def create_clan(self, guild_id, name, owner_id, description=''):
        await self._conn.execute(
            "INSERT INTO clans (guild_id, name, owner_id, description) VALUES (?, ?, ?, ?)",
            (guild_id, name, owner_id, description)
        )
        await self._conn.commit()
        async with self._conn.execute(
            "SELECT id FROM clans WHERE guild_id = ? AND name = ?",
            (guild_id, name)
        ) as cur:
            row = await cur.fetchone()
        clan_id = row['id']
        await self._conn.execute(
            "INSERT INTO clan_members (clan_id, user_id, role) VALUES (?, ?, 'owner')",
            (clan_id, owner_id)
        )
        await self._conn.commit()
        return clan_id

    async def get_clan(self, guild_id, name=None, clan_id=None):
        if name:
            async with self._conn.execute(
                "SELECT * FROM clans WHERE guild_id = ? AND name = ?", (guild_id, name)
            ) as cur:
                return await cur.fetchone()
        else:
            async with self._conn.execute(
                "SELECT * FROM clans WHERE id = ?", (clan_id,)
            ) as cur:
                return await cur.fetchone()

    async def get_user_clan(self, guild_id, user_id):
        async with self._conn.execute(
            """SELECT c.*, cm.role as member_role FROM clans c
               JOIN clan_members cm ON c.id = cm.clan_id
               WHERE c.guild_id = ? AND cm.user_id = ?""",
            (guild_id, user_id)
        ) as cur:
            return await cur.fetchone()

    async def get_clan_members(self, clan_id):
        async with self._conn.execute(
            "SELECT * FROM clan_members WHERE clan_id = ?", (clan_id,)
        ) as cur:
            return await cur.fetchall()

    async def add_clan_member(self, clan_id, user_id):
        await self._conn.execute(
            "INSERT OR IGNORE INTO clan_members (clan_id, user_id) VALUES (?, ?)",
            (clan_id, user_id)
        )
        await self._conn.commit()

    async def remove_clan_member(self, clan_id, user_id):
        await self._conn.execute(
            "DELETE FROM clan_members WHERE clan_id = ? AND user_id = ?",
            (clan_id, user_id)
        )
        await self._conn.commit()

    async def add_clan_points(self, clan_id, amount):
        await self._conn.execute(
            "UPDATE clans SET points = points + ? WHERE id = ?",
            (amount, clan_id)
        )
        await self._conn.commit()

    async def get_clan_leaderboard(self, guild_id, limit=10):
        async with self._conn.execute(
            "SELECT * FROM clans WHERE guild_id = ? ORDER BY points DESC LIMIT ?",
            (guild_id, limit)
        ) as cur:
            return await cur.fetchall()

    async def delete_clan(self, clan_id):
        await self._conn.execute("DELETE FROM clan_members WHERE clan_id = ?", (clan_id,))
        await self._conn.execute("DELETE FROM clans WHERE id = ?", (clan_id,))
        await self._conn.commit()

    # ── Content Creator Methods ────────────────────────────────────────────────

    async def add_creator(self, guild_id, user_id, yt_channel_id, yt_name, announce_channel):
        await self._conn.execute(
            """INSERT INTO content_creators
               (guild_id, user_id, youtube_channel_id, youtube_name, announce_channel)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(guild_id, user_id) DO UPDATE SET
               youtube_channel_id = ?, youtube_name = ?, announce_channel = ?""",
            (guild_id, user_id, yt_channel_id, yt_name, announce_channel,
             yt_channel_id, yt_name, announce_channel)
        )
        await self._conn.commit()

    async def get_creators(self, guild_id):
        async with self._conn.execute(
            "SELECT * FROM content_creators WHERE guild_id = ?", (guild_id,)
        ) as cur:
            return await cur.fetchall()

    async def get_creator(self, guild_id, user_id):
        async with self._conn.execute(
            "SELECT * FROM content_creators WHERE guild_id = ? AND user_id = ?",
            (guild_id, user_id)
        ) as cur:
            return await cur.fetchone()

    async def update_creator(self, guild_id, user_id, **kwargs):
        sets = ', '.join(f"{k} = ?" for k in kwargs)
        vals = list(kwargs.values()) + [guild_id, user_id]
        await self._conn.execute(
            f"UPDATE content_creators SET {sets} WHERE guild_id = ? AND user_id = ?",
            vals
        )
        await self._conn.commit()

    async def remove_creator(self, guild_id, user_id):
        await self._conn.execute(
            "DELETE FROM content_creators WHERE guild_id = ? AND user_id = ?",
            (guild_id, user_id)
        )
        await self._conn.commit()

    # ── Action Log Methods ─────────────────────────────────────────────────────

    async def log_action(self, guild_id, moderator_id, target_id, action, reason):
        await self._conn.execute(
            """INSERT INTO action_logs (guild_id, moderator_id, target_id, action, reason)
               VALUES (?, ?, ?, ?, ?)""",
            (guild_id, moderator_id, target_id, action, reason)
        )
        await self._conn.commit()

    async def get_action_logs(self, guild_id, target_id=None, limit=10):
        if target_id:
            async with self._conn.execute(
                """SELECT * FROM action_logs WHERE guild_id = ? AND target_id = ?
                   ORDER BY timestamp DESC LIMIT ?""",
                (guild_id, target_id, limit)
            ) as cur:
                return await cur.fetchall()
        else:
            async with self._conn.execute(
                "SELECT * FROM action_logs WHERE guild_id = ? ORDER BY timestamp DESC LIMIT ?",
                (guild_id, limit)
            ) as cur:
                return await cur.fetchall()

    # ── Suggestion Methods ─────────────────────────────────────────────────────

    async def add_suggestion(self, guild_id, user_id, message_id, channel_id, content):
        await self._conn.execute(
            """INSERT INTO suggestions (guild_id, user_id, message_id, channel_id, content)
               VALUES (?, ?, ?, ?, ?)""",
            (guild_id, user_id, message_id, channel_id, content)
        )
        await self._conn.commit()

    async def get_suggestion(self, message_id):
        async with self._conn.execute(
            "SELECT * FROM suggestions WHERE message_id = ?", (message_id,)
        ) as cur:
            return await cur.fetchone()

    async def update_suggestion(self, message_id, status):
        await self._conn.execute(
            "UPDATE suggestions SET status = ? WHERE message_id = ?",
            (status, message_id)
        )
        await self._conn.commit()

    # ── Reaction Roles ─────────────────────────────────────────────────────────

    async def add_reaction_role(self, guild_id, message_id, emoji, role_id):
        await self._conn.execute(
            """INSERT INTO reaction_roles (guild_id, message_id, emoji, role_id)
               VALUES (?, ?, ?, ?)""",
            (guild_id, message_id, emoji, role_id)
        )
        await self._conn.commit()

    async def get_reaction_role(self, message_id, emoji):
        async with self._conn.execute(
            "SELECT * FROM reaction_roles WHERE message_id = ? AND emoji = ?",
            (message_id, emoji)
        ) as cur:
            return await cur.fetchone()

    async def get_message_reaction_roles(self, message_id):
        async with self._conn.execute(
            "SELECT * FROM reaction_roles WHERE message_id = ?", (message_id,)
        ) as cur:
            return await cur.fetchall()

    async def close(self):
        if self._conn:
            await self._conn.close()
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# استخدام SQLite المتوافقة مع ملف obt_system.db الموجود لديك
DATABASE_URL = "sqlite+aiosqlite:///obt_system.db"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

class GuildSettings(Base):
    __tablename__ = "guild_settings"

    guild_id: Mapped[int] = mapped_column(primary_key=True)
    prefix: Mapped[str] = mapped_column(default="!")
    
    # إعدادات الحماية
    anti_spam: Mapped[bool] = mapped_column(default=True)
    anti_raid: Mapped[bool] = mapped_column(default=True)
    anti_link: Mapped[bool] = mapped_column(default=False)
    anti_scam: Mapped[bool] = mapped_column(default=True)
    
    # الإشراف والتذاكر
    ticket_category_id: Mapped[int] = mapped_column(nullable=True)
    welcome_message: Mapped[str] = mapped_column(default="أهلاً بك في السيرفر!")

class UserEconomy(Base):
    __tablename__ = "user_economy"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column()
    user_id: Mapped[int] = mapped_column()
    points: Mapped[int] = mapped_column(default=0)
    level: Mapped[int] = mapped_column(default=1)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column()
    channel_id: Mapped[int] = mapped_column()
    user_id: Mapped[int] = mapped_column()
    status: Mapped[str] = mapped_column(default="مفتوحة") # مفتوحة، مغلقة، قيد المتابعة
    category: Mapped[str] = mapped_column(default="الدعم العام")
    claimed_by: Mapped[int] = mapped_column(nullable=True)
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>OBT System - لوحة التحكم الإدارية</title>
    <style>
        :root {
            --bg: #0f172a;
            --card: #1e293b;
            --accent: #6366f1;
            --text: #f8fafc;
            --muted: #94a3b8;
            --success: #22c55e;
            --danger: #ef4444;
            --warning: #f59e0b;
        }
        body { margin: 0; font-family: 'Segoe UI', Tahoma, sans-serif; background: var(--bg); color: var(--text); display: flex; min-height: 100vh; }
        .sidebar { width: 280px; background: #090d16; border-left: 1px solid #334155; padding: 20px; display: flex; flex-direction: column; }
        .sidebar h2 { font-size: 22px; color: var(--accent); margin-bottom: 30px; text-align: center; }
        .sidebar a { color: var(--muted); text-decoration: none; padding: 12px 15px; border-radius: 8px; margin-bottom: 8px; display: block; font-weight: 500; transition: 0.2s; }
        .sidebar a:hover, .sidebar a.active { background: var(--accent); color: white; }
        .main { flex: 1; padding: 40px; box-sizing: border-box; overflow-y: auto; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; background: var(--card); padding: 20px; border-radius: 12px; border: 1px solid #334155; }
        .card { background: var(--card); padding: 25px; border-radius: 12px; border: 1px solid #334155; margin-bottom: 20px; }
        .card h3 { margin-top: 0; color: var(--text); border-bottom: 1px solid #334155; padding-bottom: 10px; }
        .form-group { margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between; }
        .form-control { width: 100%; padding: 10px; background: #0f172a; border: 1px solid #334155; color: var(--text); border-radius: 8px; margin-top: 5px; box-sizing: border-box; }
        .switch { position: relative; display: inline-block; width: 50px; height: 26px; }
        .switch input { opacity: 0; width: 0; height: 0; }
        .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background: #475569; transition: .3s; border-radius: 26px; }
        .slider:before { position: absolute; content: ""; height: 20px; width: 20px; left: 3px; bottom: 3px; background: white; transition: .3s; border-radius: 50%; }
        input:checked + .slider { background: var(--success); }
        input:checked + .slider:before { transform: translateX(24px); }
        .btn { background: var(--accent); color: white; border: none; padding: 12px 25px; border-radius: 8px; font-weight: bold; cursor: pointer; transition: 0.2s; }
        .btn:hover { opacity: 0.9; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: var(--card); padding: 20px; border-radius: 12px; border: 1px solid #334155; text-align: center; }
        .stat-card span { color: var(--muted); font-size: 14px; }
        .stat-card h2 { margin: 10px 0 0 0; color: var(--success); }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 12px; text-align: right; border-bottom: 1px solid #334155; font-size: 14px; }
        th { color: var(--muted); }
    </style>
</head>
<body>

    <div class="sidebar">
        <h2>🚀 OBT System</h2>
        <a href="/?tab=overview">📊 نظرة عامة</a>
        <a href="/?tab=security">🛡️ نظام الحماية</a>
        <a href="/?tab=tickets" class="active">🎫 نظام التذاكر</a>
        <a href="/?tab=economy">💰 الاقتصاد والنقاط</a>
        <a href="#" style="color: var(--danger); margin-top: auto;">🚪 تسجيل الخروج</a>
    </div>

    <div class="main">
        <div class="header">
            <h2 style="margin:0;">إدارة نظام التذاكر المتقدم</h2>
            <span style="background: rgba(34, 197, 94, 0.1); color: var(--success); padding: 6px 15px; border-radius: 20px; font-weight: bold;">● النظام يعمل بكفاءة</span>
        </div>

        {% if tab == 'tickets' %}
        <div class="card">
            <h3>لوحات التذاكر النشطة</h3>
            <p style="color: var(--muted); font-size: 13px;">إخصاص رتب الدعم الفني وتصنيفات التذاكر التلقائية.</p>
            
            <form method="POST">
                <div style="margin-bottom: 15px;">
                    <label><strong>رتبة الإشراف والدعم الفني</strong></label>
                    <input type="text" class="form-control" value="مشرف الدعم الفني" name="support_role">
                </div>
                <div style="margin-bottom: 15px;">
                    <label><strong>رسالة الترحيب داخل التذكرة</strong></label>
                    <textarea class="form-control" rows="3" name="ticket_welcome">مرحباً بك! يرجى توضيح مشكلتك وسيقوم فريق الدعم بالرد عليك في أقرب وقت.</textarea>
                </div>
                <button type="submit" class="btn">حفظ إعدادات التذاكر</button>
            </form>
        </div>

        <div class="card">
            <h3>سجل التذاكر الحالية</h3>
            <table>
                <thead>
                    <tr>
                        <th>رقم التذكرة</th>
                        <th>صاحب التذكرة</th>
                        <th>القسم</th>
                        <th>الحالة</th>
                        <th>المسؤول</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>#1042</td>
                        <td>أحمد محمد</td>
                        <td>الدعم الفني العام</td>
                        <td><span style="color: var(--success);">مفتوحة</span></td>
                        <td>غير مسند</td>
                    </tr>
                    <tr>
                        <td>#1041</td>
                        <td>سارة خالد</td>
                        <td>شكاوى الإدارة</td>
                        <td><span style="color: var(--warning);">قيد المتابعة</span></td>
                        <td>مشرف الأمان</td>
                    </tr>
                </tbody>
            </table>
        </div>
        {% else %}
        <div class="grid">
            <div class="stat-card">
                <span>التذاكر المفتوحة حالياً</span>
                <h2 style="color: var(--warning);">12 تذكرة</h2>
            </div>
            <div class="stat-card">
                <span>متوسط وقت الرد</span>
                <h2 style="color: var(--success);">1.4 دقيقة</h2>
            </div>
            <div class="stat-card">
                <span>إجمالي التذاكر المغلقة</span>
                <h2 style="color: var(--accent);">1,420</h2>
            </div>
        </div>

        <div class="card">
            <h3>نظرة سريعة على أداء السيرفر</h3>
            <p style="color: var(--muted);">انتقل إلى تبويب التذاكر من القائمة الجانبية لإدارة اللوحات والصلاحيات بشكل كامل.</p>
        </div>
        {% endif %}
    </div>

</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def dashboard():
    tab = request.args.get('tab', 'overview')
    if request.method == "POST":
        return redirect(url_for("dashboard", tab=tab))
    return render_template_string(DASHBOARD_TEMPLATE, tab=tab)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
    
