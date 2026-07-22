-- coding: utf-8 --

import datetime

from sqlalchemy import (
Column,
Integer,
String,
Float,
Boolean,
DateTime,
BigInteger,
Text
)

from sqlalchemy.orm import declarative_base

Base = declarative_base()

==========================

Guild Settings

==========================

class GuildSettings(Base):
tablename = "guild_settings"

id = Column(Integer, primary_key=True)  

guild_id = Column(  
    BigInteger,  
    unique=True,  
    index=True,  
    nullable=False  
)  

prefix = Column(  
    String(10),  
    default="!"  
)  

language = Column(  
    String(10),  
    default="ar"  
)  

timezone = Column(  
    String(50),  
    default="UTC"  
)  

embed_color = Column(  
    String(20),  
    default="#5865F2"  
)  

owner_id = Column(  
    BigInteger,  
    nullable=True  
)  

log_channel_id = Column(  
    BigInteger,  
    nullable=True  
)  

created_at = Column(  
    DateTime,  
    default=datetime.datetime.utcnow  
)

==========================

Feature Settings

==========================

class FeatureSettings(Base):
tablename = "feature_settings"

id = Column(Integer, primary_key=True)  

guild_id = Column(  
    BigInteger,  
    unique=True,  
    nullable=False  
)  

security = Column(Boolean, default=True)  

tickets = Column(Boolean, default=True)  

economy = Column(Boolean, default=True)  

levels = Column(Boolean, default=True)  

clans = Column(Boolean, default=True)  

ai = Column(Boolean, default=False)  

created_at = Column(  
    DateTime,  
    default=datetime.datetime.utcnow  
)

==========================

Security Settings

==========================

class SecuritySettings(Base):
tablename = "security_settings"

id = Column(Integer, primary_key=True)  

guild_id = Column(  
    BigInteger,  
    unique=True,  
    index=True,  
    nullable=False  
)  

anti_spam = Column(  
    Boolean,  
    default=True  
)  

anti_raid = Column(  
    Boolean,  
    default=True  
)  

anti_link = Column(  
    Boolean,  
    default=True  
)  

anti_mention = Column(  
    Boolean,  
    default=True  
)  

anti_webhook = Column(  
    Boolean,  
    default=True  
)  

anti_bot = Column(  
    Boolean,  
    default=True  
)  

anti_channel_delete = Column(  
    Boolean,  
    default=True  
)  

anti_role_delete = Column(  
    Boolean,  
    default=True  
)  

spam_limit = Column(  
    Integer,  
    default=5  
)  

raid_limit = Column(  
    Integer,  
    default=10  
)  

punishment = Column(  
    String(30),  
    default="timeout"  
)

==========================

Security Whitelist

==========================

class SecurityWhitelist(Base):
tablename = "security_whitelist"

id = Column(  
    Integer,  
    primary_key=True  
)  

guild_id = Column(  
    BigInteger,  
    nullable=False  
)  

target_id = Column(  
    BigInteger,  
    nullable=False  
)  

target_type = Column(  
    String(20),  
    default="user"  
)  

reason = Column(  
    Text,  
    nullable=True  
)  

created_at = Column(  
    DateTime,  
    default=datetime.datetime.utcnow  
)

==========================

Security Logs

==========================

class SecurityLog(Base):
tablename = "security_logs"

id = Column(  
    Integer,  
    primary_key=True  
)  

guild_id = Column(  
    BigInteger,  
    nullable=False  
)  

user_id = Column(  
    BigInteger,  
    nullable=True  
)  

action = Column(  
    String(100)  
)  

reason = Column(  
    Text,  
    nullable=True  
)  

severity = Column(  
    String(20),  
    default="medium"  
)  

created_at = Column(  
    DateTime,  
    default=datetime.datetime.utcnow  
)

==========================

Auto Mod Rules

==========================

class AutoModRule(Base):
tablename = "automod_rules"

id = Column(  
    Integer,  
    primary_key=True  
)  

guild_id = Column(  
    BigInteger,  
    nullable=False  
)  

rule_type = Column(  
    String(50)  
)  

value = Column(  
    Text  
)  

action = Column(  
    String(30),  
    default="delete"  
)  

enabled = Column(  
    Boolean,  
    default=True  
)

==========================

Guild Settings Models

==========================

class GuildSettingsModel(db.Model):
tablename = "guild_settings"

id = db.Column(db.Integer, primary_key=True)  

guild_id = db.Column(  
    db.String(32),  
    unique=True,  
    nullable=False,  
    index=True  
)  

prefix = db.Column(  
    db.String(10),  
    default="!",  
    nullable=False  
)  

language = db.Column(  
    db.String(10),  
    default="ar",  
    nullable=False  
)  

timezone = db.Column(  
    db.String(50),  
    default="UTC",  
    nullable=False  
)  

embed_color = db.Column(  
    db.String(20),  
    default="#5865F2"  
)  

security_enabled = db.Column(  
    db.Boolean,  
    default=True  
)  

tickets_enabled = db.Column(  
    db.Boolean,  
    default=True  
)  

economy_enabled = db.Column(  
    db.Boolean,  
    default=True  
)  

levels_enabled = db.Column(  
    db.Boolean,  
    default=True  
)  

clans_enabled = db.Column(  
    db.Boolean,  
    default=True  
)  

created_at = db.Column(  
    db.DateTime,  
    default=datetime.utcnow  
)  

updated_at = db.Column(  
    db.DateTime,  
    default=datetime.utcnow,  
    onupdate=datetime.utcnow  
)

==========================

Moderation Models

==========================

class ModerationCaseModel(db.Model):
tablename = "moderation_cases"

id = db.Column(  
    db.Integer,  
    primary_key=True  
)  

guild_id = db.Column(  
    db.String(32),  
    index=True,  
    nullable=False  
)  

case_id = db.Column(  
    db.Integer,  
    nullable=False  
)  

user_id = db.Column(  
    db.String(32),  
    nullable=False  
)  

moderator_id = db.Column(  
    db.String(32),  
    nullable=False  
)  

action = db.Column(  
    db.String(50),  
    nullable=False  
)  

reason = db.Column(  
    db.Text  
)  

duration = db.Column(  
    db.Integer,  
    nullable=True  
)  

created_at = db.Column(  
    db.DateTime,  
    default=datetime.utcnow  
)

==========================

Warning System

==========================

class WarningModel(db.Model):
tablename = "warnings"

id = db.Column(  
    db.Integer,  
    primary_key=True  
)  

guild_id = db.Column(  
    db.String(32),  
    nullable=False,  
    index=True  
)  

user_id = db.Column(  
    db.String(32),  
    nullable=False  
)  

moderator_id = db.Column(  
    db.String(32),  
    nullable=False  
)  

reason = db.Column(  
    db.Text,  
    nullable=True  
)  

points = db.Column(  
    db.Integer,  
    default=1  
)  

created_at = db.Column(  
    db.DateTime,  
    default=datetime.utcnow  
)

==========================

Application System

==========================

class ApplicationModel(db.Model):
tablename = "applications"

id = db.Column(  
    db.Integer,  
    primary_key=True  
)  

guild_id = db.Column(  
    db.String(32),  
    nullable=False  
)  

user_id = db.Column(  
    db.String(32),  
    nullable=False  
)  

application_type = db.Column(  
    db.String(50),  
    nullable=False  
)  

answers = db.Column(  
    db.Text,  
    nullable=False  
)  

status = db.Column(  
    db.String(20),  
    default="pending"  
)  

reviewed_by = db.Column(  
    db.String(32),  
    nullable=True  
)  

created_at = db.Column(  
    db.DateTime,  
    default=datetime.utcnow  
)

==========================

Creator System

==========================

class CreatorProfileModel(db.Model):
tablename = "creator_profiles"

id = db.Column(  
    db.Integer,  
    primary_key=True  
)  

guild_id = db.Column(  
    db.String(32),  
    nullable=False  
)  

user_id = db.Column(  
    db.String(32),  
    nullable=False  
)  

platform = db.Column(  
    db.String(50),  
    nullable=False  
)  

username = db.Column(  
    db.String(100),  
    nullable=False  
)  

followers = db.Column(  
    db.Integer,  
    default=0  
)  

verified = db.Column(  
    db.Boolean,  
    default=False  
)  

rank = db.Column(  
    db.String(50),  
    default="Creator"  
)  

created_at = db.Column(  
    db.DateTime,  
    default=datetime.utcnow  
)

==========================

Command Statistics

==========================

class CommandStatsModel(db.Model):
tablename = "command_stats"

id = db.Column(  
    db.Integer,  
    primary_key=True  
)  

guild_id = db.Column(  
    db.String(32),  
    nullable=False  
)  

user_id = db.Column(  
    db.String(32),  
    nullable=False  
)  

command = db.Column(  
    db.String(100),  
    nullable=False  
)  

uses = db.Column(  
    db.Integer,  
    default=0  
)  

last_used = db.Column(  
    db.DateTime,  
    default=datetime.utcnow  
)

==========================

Reminder System

==========================

class ReminderModel(db.Model):
tablename = "reminders"

id = db.Column(  
    db.Integer,  
    primary_key=True  
)  

guild_id = db.Column(  
    db.String(32),  
    nullable=False  
)  

user_id = db.Column(  
    db.String(32),  
    nullable=False  
)  

message = db.Column(  
    db.Text,  
    nullable=False  
)  

remind_time = db.Column(  
    db.DateTime,  
    nullable=False  
)  

completed = db.Column(  
    db.Boolean,  
    default=False  
)  

created_at = db.Column(  
    db.DateTime,  
    default=datetime.utcnow  
)

==========================

Advanced Logs System Models

==========================

class LogSettingsModel(db.Model):
tablename = "log_settings"

id = db.Column(  
    db.Integer,  
    primary_key=True  
)  

guild_id = db.Column(  
    db.String(32),  
    unique=True,  
    nullable=False,  
    index=True  
)  

enabled = db.Column(  
    db.Boolean,  
    default=True  
)  

log_channel_id = db.Column(  
    db.String(32),  
    nullable=True  
)  

message_logs = db.Column(  
    db.Boolean,  
    default=True  
)  

member_logs = db.Column(  
    db.Boolean,  
    default=True  
)  

moderation_logs = db.Column(  
    db.Boolean,  
    default=True  
)  

role_logs = db.Column(  
    db.Boolean,  
    default=True  
)  

channel_logs = db.Column(  
    db.Boolean,  
    default=True  
)  

voice_logs = db.Column(  
    db.Boolean,  
    default=True  
)  

security_logs = db.Column(  
    db.Boolean,  
    default=True  
)  

ticket_logs = db.Column(  
    db.Boolean,  
    default=True  
)  

command_logs = db.Column(  
    db.Boolean,  
    default=True  
)

class ServerLogModel(db.Model):
tablename = "server_logs"

id = db.Column(  
    db.Integer,  
    primary_key=True  
)  

guild_id = db.Column(  
    db.String(32),  
    nullable=False,  
    index=True  
)  

user_id = db.Column(  
    db.String(32),  
    nullable=True  
)  

moderator_id = db.Column(  
    db.String(32),  
    nullable=True  
)  

log_type = db.Column(  
    db.String(50),  
    nullable=False  
)  

action = db.Column(  
    db.String(100),  
    nullable=False  
)  

target_id = db.Column(  
    db.String(32),  
    nullable=True  
)  

old_value = db.Column(  
    db.Text,  
    nullable=True  
)  

new_value = db.Column(  
    db.Text,  
    nullable=True  
)  

details = db.Column(  
    db.Text,  
    nullable=True  
)  

created_at = db.Column(  
    db.DateTime,  
    default=datetime.utcnow  
)

==========================

Message Logs

==========================

class MessageLogModel(db.Model):
tablename = "message_logs"

id = db.Column(  
    db.Integer,  
    primary_key=True  
)  

guild_id = db.Column(  
    db.String(32),  
    nullable=False  
)  

channel_id = db.Column(  
    db.String(32),  
    nullable=False  
)  

user_id = db.Column(  
    db.String(32),  
    nullable=False  
)  

message_id = db.Column(  
    db.String(32),  
    nullable=False  
)  

content = db.Column(  
    db.Text,  
    nullable=True  
)  

action = db.Column(  
    db.String(20),  
    nullable=False  
)  

created_at = db.Column(  
    db.DateTime,  
    default=datetime.utcnow  
)

==========================

Voice Logs

==========================

class VoiceLogModel(db.Model):
tablename = "voice_logs"

id = db.Column(  
    db.Integer,  
    primary_key=True  
)  

guild_id = db.Column(  
    db.String(32),  
    nullable=False  
)  

user_id = db.Column(  
    db.String(32),  
    nullable=False  
)  

channel_id = db.Column(  
    db.String(32),  
    nullable=True  
)  

action = db.Column(  
    db.String(30),  
    nullable=False  
)  

created_at = db.Column(  
    db.DateTime,  
    default=datetime.utcnow  
)

==========================

Member Logs

==========================

class MemberLogModel(db.Model):
tablename = "member_logs"

id = db.Column(  
    db.Integer,  
    primary_key=True  
)  

guild_id = db.Column(  
    db.String(32),  
    nullable=False  
)  

user_id = db.Column(  
    db.String(32),  
    nullable=False  
)  

action = db.Column(  
    db.String(50),  
    nullable=False  
)  

reason = db.Column(  
    db.Text,  
    nullable=True  
)  

created_at = db.Column(  
    db.DateTime,  
    default=datetime.utcnow  
)

==========================

Backup Full Server System

==========================

class BackupModel(db.Model):
tablename = "server_backups"

id = db.Column(  
    db.Integer,  
    primary_key=True  
)  

guild_id = db.Column(  
    db.String(32),  
    nullable=False,  
    index=True  
)  

backup_id = db.Column(  
    db.String(100),  
    unique=True,  
    nullable=False  
)  

name = db.Column(  
    db.String(100),  
    default="Full Server Backup"  
)  

created_by = db.Column(  
    db.String(32),  
    nullable=False  
)  

data = db.Column(  
    db.Text,  
    nullable=False  
)  

size = db.Column(  
    db.Integer,  
    default=0  
)  

status = db.Column(  
    db.String(20),  
    default="completed"  
)  

created_at = db.Column(  
    db.DateTime,  
    default=datetime.utcnow  
)

class BackupRestoreLogModel(db.Model):
tablename = "backup_restore_logs"

id = db.Column(  
    db.Integer,  
    primary_key=True  
)  

guild_id = db.Column(  
    db.String(32),  
    nullable=False  
)  

backup_id = db.Column(  
    db.String(100),  
    nullable=False  
)  

restored_by = db.Column(  
    db.String(32),  
    nullable=False  
)  

status = db.Column(  
    db.String(20),  
    default="success"  
)  

details = db.Column(  
    db.Text,  
    nullable=True  
)  

created_at = db.Column(  
    db.DateTime,  
    default=datetime.utcnow  
)

==========================

Welcome / Leave System

==========================

class WelcomeSettingsModel(db.Model):
tablename = "welcome_settings"

id = db.Column(  
    db.Integer,  
    primary_key=True  
)  

guild_id = db.Column(  
    db.String(32),  
    unique=True,  
    nullable=False  
)  

enabled = db.Column(  
    db.Boolean,  
    default=True  
)  

welcome_channel = db.Column(  
    db.String(32),  
    nullable=True  
)  

leave_channel = db.Column(  
    db.String(32),  
    nullable=True  
)  

welcome_message = db.Column(  
    db.Text,  
    nullable=True  
)  

leave_message = db.Column(  
    db.Text,  
    nullable=True  
)  

auto_role_id = db.Column(  
    db.String(32),  
    nullable=True  
)  

created_at = db.Column(  
    db.DateTime,  
    default=datetime.utcnow  
)

==========================

Auto Role System

==========================

class AutoRoleModel(db.Model):
tablename = "auto_roles"

id = db.Column(  
    db.Integer,  
    primary_key=True  
)  

guild_id = db.Column(  
    db.String(32),  
    nullable=False  
)  

role_id = db.Column(  
    db.String(32),  
    nullable=False  
)  

role_type = db.Column(  
    db.String(30),  
    default="join"  
)  

enabled = db.Column(  
    db.Boolean,  
    default=True  
)

==========================

Giveaway System

==========================

class GiveawayModel(db.Model):
tablename = "giveaways"

id = db.Column(  
    db.Integer,  
    primary_key=True  
)  

guild_id = db.Column(  
    db.String(32),  
    nullable=False  
)  

channel_id = db.Column(  
    db.String(32),  
    nullable=False  
)  

message_id = db.Column(  
    db.String(32),  
    nullable=False  
)  

prize = db.Column(  
    db.String(255),  
    nullable=False  
)  

winners = db.Column(  
    db.Integer,  
    default=1  
)  

ends_at = db.Column(  
    db.DateTime,  
    nullable=False  
)  

status = db.Column(  
    db.String(20),  
    default="running"  
)  

created_at = db.Column(  
    db.DateTime,  
    default=datetime.utcnow  
)

class GiveawayEntryModel(db.Model):
tablename = "giveaway_entries"

id = db.Column(  
    db.Integer,  
    primary_key=True  
)  

giveaway_id = db.Column(  
    db.Integer,  
    nullable=False  
)  

user_id = db.Column(  
    db.String(32),  
    nullable=False  
)  

joined_at = db.Column(  
    db.DateTime,  
    default=datetime.utcnow  
)

==========================

Suggestion System

==========================

class SuggestionModel(db.Model):
tablename = "suggestions"

id = db.Column(  
    db.Integer,  
    primary_key=True  
)  

guild_id = db.Column(  
    db.String(32),  
    nullable=False  
)  

user_id = db.Column(  
    db.String(32),  
    nullable=False  
)  

channel_id = db.Column(  
    db.String(32),  
    nullable=False  
)  

message_id = db.Column(  
    db.String(32),  
    nullable=False  
)  

content = db.Column(  
    db.Text,  
    nullable=False  
)  

status = db.Column(  
    db.String(30),  
    default="pending"  
)  

reviewed_by = db.Column(  
    db.String(32),  
    nullable=True  
)  

created_at = db.Column(  
    db.DateTime,  
    default=datetime.utcnow  
)

==========================

Starboard System

==========================

class StarboardSettingsModel(db.Model):
tablename = "starboard_settings"

id = db.Column(  
    db.Integer,  
    primary_key=True  
)  

guild_id = db.Column(  
    db.String(32),  
    unique=True,  
    nullable=False  
)  

enabled = db.Column(  
    db.Boolean,  
    default=True  
)  

channel_id = db.Column(  
    db.String(32),  
    nullable=True  
)  

emoji = db.Column(  
    db.String(10),  
    default="⭐"  
)  

required_stars = db.Column(  
    db.Integer,  
    default=5  
)

==========================

Shop / Inventory System

==========================

class ShopItemModel(db.Model):
tablename = "shop_items"

id = db.Column(  
    db.Integer,  
    primary_key=True  
)  

guild_id = db.Column(  
    db.String(32),  
    nullable=False  
)  

name = db.Column(  
    db.String(100),  
    nullable=False  
)  

description = db.Column(  
    db.Text,  
    nullable=True  
)  

price = db.Column(  
    db.Integer,  
    nullable=False  
)  

item_type = db.Column(  
    db.String(50),  
    nullable=False  
)  

value = db.Column(  
    db.String(255),  
    nullable=True  
)  

created_at = db.Column(  
    db.DateTime,  
    default=datetime.utcnow  
)

class InventoryModel(db.Model):
tablename = "inventory"

id = db.Column(  
    db.Integer,  
    primary_key=True  
)  

guild_id = db.Column(  
    db.String(32),  
    nullable=False  
)  

user_id = db.Column(  
    db.String(32),  
    nullable=False  
)  

item_id = db.Column(  
    db.Integer,  
    nullable=False  
)  

amount = db.Column(  
    db.Integer,  
    default=1  
)  

created_at = db.Column(  
    db.DateTime,  
    default=datetime.utcnow  
)
