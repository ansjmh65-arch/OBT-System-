# ==========================
# Security Models
# ==========================


class SecuritySettingsModel(db.Model):
    __tablename__ = "security_settings"

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


    # تفعيل الحمايات
    anti_spam = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    anti_raid = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    anti_link = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    anti_mention = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    anti_webhook = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    anti_bot = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    anti_mass_role = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    anti_channel_delete = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    anti_role_delete = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )


    # إعدادات السبام
    spam_limit = db.Column(
        db.Integer,
        default=5,
        nullable=False
    )

    spam_interval = db.Column(
        db.Integer,
        default=5,
        nullable=False
    )


    # إعدادات الرايد
    raid_join_limit = db.Column(
        db.Integer,
        default=10,
        nullable=False
    )

    raid_time = db.Column(
        db.Integer,
        default=10,
        nullable=False
    )


    # العقوبات
    punishment_type = db.Column(
        db.String(30),
        default="timeout",
        nullable=False
    )


    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )



class SecurityWhitelistModel(db.Model):
    __tablename__ = "security_whitelist"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    guild_id = db.Column(
        db.String(32),
        nullable=False,
        index=True
    )

    target_id = db.Column(
        db.String(32),
        nullable=False
    )

    target_type = db.Column(
        db.String(20),
        default="user",
        nullable=False
    )

    reason = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )


    __table_args__ = (
        db.UniqueConstraint(
            "guild_id",
            "target_id",
            name="security_whitelist_unique"
        ),
    )



class SecurityLogModel(db.Model):
    __tablename__ = "security_logs"

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

    action = db.Column(
        db.String(100),
        nullable=False
    )

    reason = db.Column(
        db.Text,
        nullable=True
    )

    details = db.Column(
        db.Text,
        nullable=True
    )

    severity = db.Column(
        db.String(20),
        default="medium",
        nullable=False
    )

    timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )



class AutoModRuleModel(db.Model):
    __tablename__ = "automod_rules"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    guild_id = db.Column(
        db.String(32),
        nullable=False,
        index=True
    )

    rule_type = db.Column(
        db.String(50),
        nullable=False
    )

    value = db.Column(
        db.Text,
        nullable=False
    )

    enabled = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    action = db.Column(
        db.String(30),
        default="delete",
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )
# ==========================
# Ticket System Models
# ==========================


class TicketSettingsModel(db.Model):
    __tablename__ = "ticket_settings"

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
        default=True,
        nullable=False
    )

    ticket_category_id = db.Column(
        db.String(32),
        nullable=True
    )

    closed_category_id = db.Column(
        db.String(32),
        nullable=True
    )

    transcript_channel_id = db.Column(
        db.String(32),
        nullable=True
    )

    support_roles = db.Column(
        db.Text,
        nullable=True
    )

    max_tickets_per_user = db.Column(
        db.Integer,
        default=1,
        nullable=False
    )

    auto_close_time = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )



class TicketPanelModel(db.Model):
    __tablename__ = "ticket_panels"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    guild_id = db.Column(
        db.String(32),
        nullable=False,
        index=True
    )

    channel_id = db.Column(
        db.String(32),
        nullable=False
    )

    message_id = db.Column(
        db.String(32),
        nullable=False
    )

    title = db.Column(
        db.String(100),
        default="Support Ticket"
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    button_text = db.Column(
        db.String(50),
        default="Create Ticket"
    )

    button_emoji = db.Column(
        db.String(20),
        nullable=True
    )

    enabled = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )



class TicketCategoryModel(db.Model):
    __tablename__ = "ticket_categories"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    guild_id = db.Column(
        db.String(32),
        nullable=False,
        index=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    category_id = db.Column(
        db.String(32),
        nullable=False
    )

    support_roles = db.Column(
        db.Text,
        nullable=True
    )

    emoji = db.Column(
        db.String(20),
        nullable=True
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    enabled = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )



class TicketModel(db.Model):
    __tablename__ = "tickets"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    guild_id = db.Column(
        db.String(32),
        nullable=False,
        index=True
    )

    ticket_number = db.Column(
        db.Integer,
        nullable=False
    )

    channel_id = db.Column(
        db.String(32),
        unique=True,
        nullable=False
    )

    owner_id = db.Column(
        db.String(32),
        nullable=False,
        index=True
    )

    category_id = db.Column(
        db.Integer,
        nullable=True
    )

    status = db.Column(
        db.String(20),
        default="open",
        nullable=False
    )

    claimed_by = db.Column(
        db.String(32),
        nullable=True
    )

    closed_by = db.Column(
        db.String(32),
        nullable=True
    )

    close_reason = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    closed_at = db.Column(
        db.DateTime,
        nullable=True
    )



class TicketMemberModel(db.Model):
    __tablename__ = "ticket_members"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    ticket_id = db.Column(
        db.Integer,
        nullable=False,
        index=True
    )

    user_id = db.Column(
        db.String(32),
        nullable=False
    )

    added_by = db.Column(
        db.String(32),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )



class TicketMessageModel(db.Model):
    __tablename__ = "ticket_messages"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    ticket_id = db.Column(
        db.Integer,
        nullable=False,
        index=True
    )

    user_id = db.Column(
        db.String(32),
        nullable=False
    )

    message = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )



class TicketTranscriptModel(db.Model):
    __tablename__ = "ticket_transcripts"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    ticket_id = db.Column(
        db.Integer,
        nullable=False
    )

    file_name = db.Column(
        db.String(255),
        nullable=False
    )

    file_url = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )



class TicketRatingModel(db.Model):
    __tablename__ = "ticket_ratings"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    ticket_id = db.Column(
        db.Integer,
        nullable=False
    )

    user_id = db.Column(
        db.String(32),
        nullable=False
    )

    rating = db.Column(
        db.Integer,
        nullable=False
    )

    feedback = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )
# ==========================
# Clan System Models
# ==========================


class ClanModel(db.Model):
    __tablename__ = "clans"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    guild_id = db.Column(
        db.String(32),
        nullable=False,
        index=True
    )

    clan_id = db.Column(
        db.String(32),
        unique=True,
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

    owner_id = db.Column(
        db.String(32),
        nullable=False
    )

    icon = db.Column(
        db.String(255),
        nullable=True
    )


    # نظام التقدم
    level = db.Column(
        db.Integer,
        default=1,
        nullable=False
    )

    points = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    members_limit = db.Column(
        db.Integer,
        default=10,
        nullable=False
    )


    status = db.Column(
        db.String(20),
        default="active",
        nullable=False
    )


    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )



class ClanMemberModel(db.Model):
    __tablename__ = "clan_members"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    clan_id = db.Column(
        db.String(32),
        nullable=False,
        index=True
    )

    user_id = db.Column(
        db.String(32),
        nullable=False,
        index=True
    )


    role = db.Column(
        db.String(30),
        default="member",
        nullable=False
    )


    points = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )


    joined_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )


    __table_args__ = (
        db.UniqueConstraint(
            "clan_id",
            "user_id",
            name="clan_member_unique"
        ),
    )



class ClanPointsLogModel(db.Model):
    __tablename__ = "clan_points_logs"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    clan_id = db.Column(
        db.String(32),
        nullable=False,
        index=True
    )

    user_id = db.Column(
        db.String(32),
        nullable=True
    )


    points = db.Column(
        db.Integer,
        nullable=False
    )


    reason = db.Column(
        db.Text,
        nullable=True
    )


    action_type = db.Column(
        db.String(30),
        default="add",
        nullable=False
    )


    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )



class ClanRankModel(db.Model):
    __tablename__ = "clan_ranks"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    clan_id = db.Column(
        db.String(32),
        nullable=False
    )


    name = db.Column(
        db.String(50),
        nullable=False
    )


    permissions = db.Column(
        db.Text,
        nullable=True
    )


    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )



class ClanRewardModel(db.Model):
    __tablename__ = "clan_rewards"

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    guild_id = db.Column(
        db.String(32),
        nullable=False
    )


    required_points = db.Column(
        db.Integer,
        nullable=False
    )


    reward_type = db.Column(
        db.String(50),
        nullable=False
    )


    reward_value = db.Column(
        db.String(255),
        nullable=False
    )


    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )
# ==========================
# Economy & Level System Models
# ==========================


class EconomyModel(db.Model):
    __tablename__ = "economy"

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
        nullable=False,
        index=True
    )


    balance = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )


    bank = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )


    daily_claimed = db.Column(
        db.DateTime,
        nullable=True
    )


    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )


    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )


    __table_args__ = (
        db.UniqueConstraint(
            "guild_id",
            "user_id",
            name="economy_guild_user_unique"
        ),
    )



class TransactionModel(db.Model):
    __tablename__ = "economy_transactions"

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


    amount = db.Column(
        db.Integer,
        nullable=False
    )


    transaction_type = db.Column(
        db.String(50),
        nullable=False
    )


    reason = db.Column(
        db.Text,
        nullable=True
    )


    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )



class LevelSettingsModel(db.Model):
    __tablename__ = "level_settings"

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
        default=True,
        nullable=False
    )


    xp_per_message = db.Column(
        db.Integer,
        default=10,
        nullable=False
    )


    cooldown = db.Column(
        db.Integer,
        default=60,
        nullable=False
    )


    level_up_channel = db.Column(
        db.String(32),
        nullable=True
    )


    level_up_message = db.Column(
        db.Text,
        nullable=True
    )



class UserLevelModel(db.Model):
    __tablename__ = "user_levels"

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
        nullable=False,
        index=True
    )


    xp = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )


    level = db.Column(
        db.Integer,
        default=1,
        nullable=False
    )


    messages = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )


    last_message = db.Column(
        db.DateTime,
        nullable=True
    )


    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )


    __table_args__ = (
        db.UniqueConstraint(
            "guild_id",
            "user_id",
            name="level_user_unique"
        ),
    )



class LevelRewardModel(db.Model):
    __tablename__ = "level_rewards"

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    guild_id = db.Column(
        db.String(32),
        nullable=False
    )


    level = db.Column(
        db.Integer,
        nullable=False
    )


    role_id = db.Column(
        db.String(32),
        nullable=False
    )


    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )



class LeaderboardModel(db.Model):
    __tablename__ = "leaderboards"

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


    category = db.Column(
        db.String(30),
        nullable=False
    )


    value = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )


    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
# ==========================
# AI System Models
# ==========================


class AISettingsModel(db.Model):
    __tablename__ = "ai_settings"

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
        default=False,
        nullable=False
    )

    allowed_channels = db.Column(
        db.Text,
        nullable=True
    )

    personality = db.Column(
        db.Text,
        nullable=True
    )

    system_prompt = db.Column(
        db.Text,
        nullable=True
    )

    memory_limit = db.Column(
        db.Integer,
        default=20,
        nullable=False
    )

    cooldown = db.Column(
        db.Integer,
        default=5,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )



class AIConversationModel(db.Model):
    __tablename__ = "ai_conversations"

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
        nullable=False,
        index=True
    )

    message = db.Column(
        db.Text,
        nullable=False
    )

    response = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )



class AutoResponseModel(db.Model):
    __tablename__ = "auto_responses"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    guild_id = db.Column(
        db.String(32),
        nullable=False,
        index=True
    )

    trigger = db.Column(
        db.String(255),
        nullable=False
    )

    response = db.Column(
        db.Text,
        nullable=False
    )

    match_type = db.Column(
        db.String(30),
        default="contains",
        nullable=False
    )

    enabled = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )
# ==========================
# Command System Models
# ==========================


class CommandSettingsModel(db.Model):
    __tablename__ = "command_settings"

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

    prefix = db.Column(
        db.String(10),
        default="!",
        nullable=False
    )

    slash_commands_enabled = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    commands_enabled = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    disabled_commands = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )



class CustomCommandModel(db.Model):
    __tablename__ = "custom_commands"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    guild_id = db.Column(
        db.String(32),
        nullable=False,
        index=True
    )

    command_name = db.Column(
        db.String(100),
        nullable=False
    )

    response = db.Column(
        db.Text,
        nullable=False
    )

    command_type = db.Column(
        db.String(30),
        default="text",
        nullable=False
    )

    required_role_id = db.Column(
        db.String(32),
        nullable=True
    )

    cooldown = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    enabled = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )



class CommandUsageLogModel(db.Model):
    __tablename__ = "command_usage_logs"

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

    command = db.Column(
        db.String(100),
        nullable=False
    )

    channel_id = db.Column(
        db.String(32),
        nullable=False
    )

    success = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )
# ==========================
# Moderation System Models
# ==========================


class ModerationSettingsModel(db.Model):
    __tablename__ = "moderation_settings"

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

    warn_enabled = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    mute_enabled = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    kick_enabled = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    ban_enabled = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    auto_punishment = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    max_warnings = db.Column(
        db.Integer,
        default=3,
        nullable=False
    )

    punishment_after_limit = db.Column(
        db.String(30),
        default="mute",
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )



class WarningModel(db.Model):
    __tablename__ = "warnings"

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
        nullable=False,
        index=True
    )

    moderator_id = db.Column(
        db.String(32),
        nullable=False
    )

    reason = db.Column(
        db.Text,
        nullable=True
    )

    status = db.Column(
        db.String(20),
        default="active",
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )



class PunishmentModel(db.Model):
    __tablename__ = "punishments"

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

    punishment_type = db.Column(
        db.String(30),
        nullable=False
    )

    reason = db.Column(
        db.Text,
        nullable=True
    )

    duration = db.Column(
        db.Integer,
        nullable=True
    )

    expires_at = db.Column(
        db.DateTime,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )



class ModerationLogModel(db.Model):
    __tablename__ = "moderation_logs"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    guild_id = db.Column(
        db.String(32),
        nullable=False
    )

    moderator_id = db.Column(
        db.String(32),
        nullable=False
    )

    target_id = db.Column(
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
        default=datetime.utcnow,
        nullable=False
    )
# ==========================
# Advanced Discord Logs Models
# ==========================


class LogSettingsModel(db.Model):
    __tablename__ = "log_settings"

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
        default=True,
        nullable=False
    )

    log_channel_id = db.Column(
        db.String(32),
        nullable=True
    )

    # تشغيل أنواع اللوقات

    message_logs = db.Column(
        db.Boolean,
        default=True
    )

    member_logs = db.Column(
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

    moderation_logs = db.Column(
        db.Boolean,
        default=True
    )

    invite_logs = db.Column(
        db.Boolean,
        default=True
    )

    bot_logs = db.Column(
        db.Boolean,
        default=True
    )

    webhook_logs = db.Column(
        db.Boolean,
        default=True
    )

    server_logs = db.Column(
        db.Boolean,
        default=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )



class DiscordLogModel(db.Model):
    __tablename__ = "discord_logs"

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

    executor_id = db.Column(
        db.String(32),
        nullable=True
    )


    # نوع الحدث
    event_type = db.Column(
        db.String(50),
        nullable=False
    )


    # معلومات الحدث
    target_id = db.Column(
        db.String(32),
        nullable=True
    )

    title = db.Column(
        db.String(255),
        nullable=True
    )

    description = db.Column(
        db.Text,
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


    extra_data = db.Column(
        db.Text,
        nullable=True
    )


    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )



# رسائل خاصة بالرسائل
class MessageLogModel(db.Model):
    __tablename__ = "message_logs"

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

    action = db.Column(
        db.String(30),
        nullable=False
    )

    old_content = db.Column(
        db.Text,
        nullable=True
    )

    new_content = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )



# لوقات الفويس
class VoiceLogModel(db.Model):
    __tablename__ = "voice_logs"

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
# ==========================
# Backup System Models
# ==========================

from datetime import datetime
from . import db


# النسخ الرئيسية
class BackupModel(db.Model):
    __tablename__ = "backups"

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
        default="Server Backup"
    )

    description = db.Column(
        db.Text,
        nullable=True
    )


    # حجم النسخة
    size = db.Column(
        db.Integer,
        default=0
    )


    # حالة النسخة
    status = db.Column(
        db.String(20),
        default="completed"
    )


    # من قام بالنسخ
    created_by = db.Column(
        db.String(32),
        nullable=False
    )


    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )



# ==========================
# Server Settings Backup
# ==========================

class BackupGuildSettingsModel(db.Model):
    __tablename__ = "backup_guild_settings"


    id = db.Column(
        db.Integer,
        primary_key=True
    )


    backup_id = db.Column(
        db.String(100),
        nullable=False,
        index=True
    )


    guild_name = db.Column(
        db.String(100)
    )


    icon_url = db.Column(
        db.Text,
        nullable=True
    )


    verification_level = db.Column(
        db.String(50),
        nullable=True
    )


    default_notifications = db.Column(
        db.String(50),
        nullable=True
    )


    data = db.Column(
        db.Text,
        nullable=False
    )



# ==========================
# Roles Backup
# ==========================

class BackupRoleModel(db.Model):
    __tablename__ = "backup_roles"


    id = db.Column(
        db.Integer,
        primary_key=True
    )


    backup_id = db.Column(
        db.String(100),
        nullable=False,
        index=True
    )


    role_id = db.Column(
        db.String(32),
        nullable=False
    )


    name = db.Column(
        db.String(100),
        nullable=False
    )


    color = db.Column(
        db.String(20),
        nullable=True
    )


    position = db.Column(
        db.Integer,
        default=0
    )


    permissions = db.Column(
        db.Text,
        nullable=False
    )


    hoist = db.Column(
        db.Boolean,
        default=False
    )


    mentionable = db.Column(
        db.Boolean,
        default=False
    )



# ==========================
# Channels Backup
# ==========================

class BackupChannelModel(db.Model):
    __tablename__ = "backup_channels"


    id = db.Column(
        db.Integer,
        primary_key=True
    )


    backup_id = db.Column(
        db.String(100),
        nullable=False,
        index=True
    )


    channel_id = db.Column(
        db.String(32),
        nullable=False
    )


    name = db.Column(
        db.String(100)
    )


    channel_type = db.Column(
        db.String(30)
    )


    position = db.Column(
        db.Integer,
        default=0
    )


    parent_id = db.Column(
        db.String(32),
        nullable=True
    )


    topic = db.Column(
        db.Text,
        nullable=True
    )


    nsfw = db.Column(
        db.Boolean,
        default=False
    )


    slowmode = db.Column(
        db.Integer,
        default=0
    )



# ==========================
# Channel Permissions Backup
# ==========================

class BackupPermissionModel(db.Model):
    __tablename__ = "backup_permissions"


    id = db.Column(
        db.Integer,
        primary_key=True
    )


    backup_id = db.Column(
        db.String(100),
        nullable=False
    )


    channel_id = db.Column(
        db.String(32),
        nullable=False
    )


    target_id = db.Column(
        db.String(32),
        nullable=False
    )


    target_type = db.Column(
        db.String(20),
        default="role"
    )


    allow_permissions = db.Column(
        db.Text,
        nullable=True
    )


    deny_permissions = db.Column(
        db.Text,
        nullable=True
    )



# ==========================
# Members Backup
# ==========================

class BackupMemberModel(db.Model):
    __tablename__ = "backup_members"


    id = db.Column(
        db.Integer,
        primary_key=True
    )


    backup_id = db.Column(
        db.String(100),
        nullable=False
    )


    user_id = db.Column(
        db.String(32),
        nullable=False
    )


    nickname = db.Column(
        db.String(100),
        nullable=True
    )


    roles = db.Column(
        db.Text,
        nullable=True
    )



# ==========================
# Emoji Backup
# ==========================

class BackupEmojiModel(db.Model):
    __tablename__ = "backup_emojis"


    id = db.Column(
        db.Integer,
        primary_key=True
    )


    backup_id = db.Column(
        db.String(100),
        nullable=False
    )


    emoji_id = db.Column(
        db.String(32)
    )


    name = db.Column(
        db.String(100)
    )


    url = db.Column(
        db.Text
    )



# ==========================
# Webhook Backup
# ==========================

class BackupWebhookModel(db.Model):
    __tablename__ = "backup_webhooks"


    id = db.Column(
        db.Integer,
        primary_key=True
    )


    backup_id = db.Column(
        db.String(100),
        nullable=False
    )


    webhook_id = db.Column(
        db.String(32)
    )


    name = db.Column(
        db.String(100)
    )


    channel_id = db.Column(
        db.String(32)
    )



# ==========================
# Restore History
# ==========================

class RestoreHistoryModel(db.Model):
    __tablename__ = "restore_history"


    id = db.Column(
        db.Integer,
        primary_key=True
    )


    backup_id = db.Column(
        db.String(100),
        nullable=False
    )


    guild_id = db.Column(
        db.String(32),
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
