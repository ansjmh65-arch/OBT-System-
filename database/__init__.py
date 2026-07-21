from .base import db

# استيراد كافة الجداول لضمان اكتشافها التلقائي بواسطة Alembic & SQLAlchemy
from .settings import ServerConfig, SystemSetting, FeatureFlag, BlacklistWhitelist, RateLimit
from .users import User, GuildMember, UserSettings, ProfileSettings, UserProfileBadge
from .moderation import SecuritySetting, ModerationSetting, Warning, Punishment, Report, Appeal
from .tickets import TicketSetting, TicketPanel, Ticket, TicketMessage, TicketTranscript
from .economy import EconomySetting, EconomyUser, Item, Inventory, Transaction
from .clans import ClanSetting, Clan, ClanMember, ClanStatistic, ClanWar, ClanLog
from .creators import ContentCreatorSetting, ContentCreator, CreatorApplication, CreatorStatistic, CreatorPost
from .community import (
    WelcomeSetting, AutoRoleSetting, VerificationSetting, LevelSystem, UserLevel,
    Giveaway, GiveawayEntry, Poll, PollOption, Suggestion, Starboard, ReactionRole,
    TempVoiceChannel, Reminder, Birthday, CustomCommand, Tag, ScheduledEvent
)
from .analytics import Statistic, PerformanceMetric, BotStatistic, ErrorLog, CacheMetadata
from .logs import LogSetting, MessageLog, VoiceLog, MemberLog, AuditLog, CommandLog
from .dashboard import (
    EmbedTemplate, Form, FormField, FormSubmission, Notification, WebhookSetting,
    Backup, BackupHistory, Session, APIKey, OAuthToken, DashboardActivity
)
