from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Boolean,
    ForeignKey,
    Text,
)
from .database import Base


class SecurityConfig(Base):
    __tablename__ = "security_configs"

    guild_id = Column(BigInteger, ForeignKey("guild_configs.guild_id"), primary_key=True)

    # Spam Protection
    anti_spam = Column(Boolean, default=False)
    similar_spam = Column(Boolean, default=False)
    mention_spam = Column(Boolean, default=False)
    emoji_spam = Column(Boolean, default=False)
    attachment_spam = Column(Boolean, default=False)
    caps_spam = Column(Boolean, default=False)

    # Link Protection
    link_protection = Column(Boolean, default=False)
    invite_protection = Column(Boolean, default=False)
    scam_protection = Column(Boolean, default=True)

    # Raid Protection
    raid_protection = Column(Boolean, default=False)
    bot_protection = Column(Boolean, default=False)
    webhook_protection = Column(Boolean, default=False)

    # Account Protection
    vpn_protection = Column(Boolean, default=False)
    alt_account_detection = Column(Boolean, default=False)
    new_account_protection = Column(Boolean, default=False)

    # Verification
    verification_enabled = Column(Boolean, default=False)

    # Punishments
    punishment = Column(String(30), default="timeout")
    whitelist_enabled = Column(Boolean, default=False)
    blacklist_enabled = Column(Boolean, default=False)


class BadWord(Base):
    __tablename__ = "security_bad_words"

    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey("guild_configs.guild_id"))
    word = Column(String(255), nullable=False)


class DomainWhitelist(Base):
    __tablename__ = "security_domain_whitelist"

    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey("guild_configs.guild_id"))
    domain = Column(String(255), nullable=False)


class DomainBlacklist(Base):
    __tablename__ = "security_domain_blacklist"

    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey("guild_configs.guild_id"))
    domain = Column(String(255), nullable=False)


class SecurityLog(Base):
    __tablename__ = "security_logs"

    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey("guild_configs.guild_id"))
    user_id = Column(BigInteger)
    action = Column(String(100))
    reason = Column(Text)
    timestamp = Column(String(100))
