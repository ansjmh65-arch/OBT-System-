import os
import random
import logging
import re
from threading import Thread
from datetime import datetime, timezone
from typing import Optional, Generator

from flask import Flask, render_template, abort
from sqlalchemy import (
    BigInteger, Boolean, DateTime, ForeignKey, Integer, 
    String, Text, create_engine, UniqueConstraint, Index
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, relationship
from sqlalchemy.exc import SQLAlchemyError

import discord
from discord.ext import commands
from discord import app_commands

# ==========================================
# 1. إعداد نظام التسجيل (Logging Configuration)
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("OBT-System")

# ==========================================
# 2. التحقق من متغيرات البيئة والأمان (Security & Validation)
# ==========================================
SECRET_KEY = os.environ.get("SECRET_KEY", "obt_secure_key_2026")
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    logger.critical("❌ خطأ أمني حرج: متغير البيئة DISCORD_TOKEN غير موجود!")
    raise ValueError("DISCORD_TOKEN environment variable is missing.")

PORT = int(os.environ.get("PORT", 8080))

# ==========================================
# 3. إعداد تطبيق Flask (ربطه بمجلد القوالب العربي لديك)
# ==========================================
app = Flask(__name__, template_folder="القوالب", static_folder="static")
app.secret_key = SECRET_KEY

# ==========================================
# 4. إعداد قاعدة البيانات و SQLAlchemy 2.x
# ==========================================
database_url = os.environ.get("DATABASE_URL", "sqlite:///obt_system_master.db")
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_recycle=3600,
    future=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

class UserModel(Base, TimestampMixin):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    balance: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    bank_balance: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    points: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    xp: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    clan_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("clans.id", ondelete="SET NULL"), nullable=True)

    clan = relationship("ClanModel", back_populates="members")

    __table_args__ = (
        UniqueConstraint("guild_id", "user_id", name="uq_guild_user"),
        Index("idx_guild_user", "guild_id", "user_id"),
    )

class ClanModel(Base, TimestampMixin):
    __tablename__ = "clans"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    owner_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    points: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)

    members = relationship("UserModel", back_populates="clan")

    __table_args__ = (
        UniqueConstraint("guild_id", "name", name="uq_guild_clan_name"),
        Index("idx_guild_clan", "guild_id", "name"),
    )

class WelcomeSettingsModel(Base, TimestampMixin):
    __tablename__ = "welcome_settings"
    
    guild_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False)
    welcome_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    welcome_channel_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    welcome_message: Mapped[str] = mapped_column(Text, default="أهلاً بك {member_mention} في سيرفر {server_name}! أنت العضو رقم #{member_count}.", nullable=False)
    use_embed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    embed_color: Mapped[str] = mapped_column(String(10), default="#6366f1", nullable=False)

    goodbye_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    goodbye_channel_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    goodbye_message: Mapped[str] = mapped_column(Text, default="غادر العضو {member_name} السيرفر. نتمنى له التوفيق!", nullable=False)

class AutoRoleModel(Base, TimestampMixin):
    __tablename__ = "auto_roles"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    role_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    role_type: Mapped[str] = mapped_column(String(20), default="human", nullable=False)

    __table_args__ = (
        UniqueConstraint("guild_id", "role_id", name="uq_guild_role"),
    )

class CreatorApplicationModel(Base, TimestampMixin):
    __tablename__ = "creator_applications"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    profile_url: Mapped[str] = mapped_column(String(500), nullable=False)
    followers_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    content_category: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False)
    creator_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    total_rewards_claimed: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)

    __table_args__ = (
        UniqueConstraint("guild_id", "user_id", name="uq_creator_guild_user"),
    )

class CentralLogModel(Base):
    __tablename__ = "central_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    action_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    details: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="INFO", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

Base.metadata.create_all(bind=engine)

def log_event(guild_id: int, category: str, action_type: str, details: str, user_id: Optional[int] = None, severity: str = "INFO"):
    db = SessionLocal()
    try:
        new_log = CentralLogModel(
            guild_id=guild_id, category=category, action_type=action_type,
            user_id=user_id, details=details, severity=severity
        )
        db.add(new_log)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"فشل تسجيل الحدث: {e}", exc_info=True)
    finally:
        db.close()

def format_welcome_message(template: str, member: discord.Member) -> str:
    created_at_str = member.created_at.strftime('%Y-%m-%d')
    return (
        template
        .replace("{member_name}", member.name)
        .replace("{member_mention}", member.mention)
        .replace("{server_name}", member.guild.name)
        .replace("{member_count}", str(member.guild.member_count))
        .replace("{account_created}", created_at_str)
    )

# ==========================================
# 5. إعداد بوت ديسكورد والأحداث
# ==========================================
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    logger.info(f'✅ OBT System متصل بنجاح كـ {bot.user}')
    try:
        synced = await bot.tree.sync()
        logger.info(f"🔄 تم مزامنة {len(synced)} أمر سلاش بنجاح.")
    except Exception as e:
        logger.error(f"خطأ في مزامنة الأوامر: {e}", exc_info=True)

@bot.event
async def on_member_join(member: discord.Member):
    db = SessionLocal()
    try:
        settings = db.query(WelcomeSettingsModel).filter_by(guild_id=member.guild.id).first()
        if settings and settings.welcome_enabled and settings.welcome_channel_id:
            channel = member.guild.get_channel(settings.welcome_channel_id)
            if isinstance(channel, discord.TextChannel):
                formatted_text = format_welcome_message(settings.welcome_message, member)
                if settings.use_embed:
                    try:
                        color_val = int(settings.embed_color.lstrip('#'), 16)
                    except ValueError:
                        color_val = 0x6366f1
                    embed = discord.Embed(title="🎉 أهلاً بك في السيرفر!", description=formatted_text, color=color_val)
                    embed.set_thumbnail(url=member.display_avatar.url)
                    await channel.send(content=member.mention, embed=embed)
                else:
                    await channel.send(formatted_text)
                log_event(member.guild.id, "Member", "Welcome Sent", f"ترحيب بالعضو {member}.", member.id)
    except Exception as e:
        logger.error(f"خطأ في دخول العضو: {e}", exc_info=True)
    finally:
        db.close()

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return
    
    db = SessionLocal()
    try:
        user_rec = db.query(UserModel).filter_by(guild_id=message.guild.id, user_id=message.author.id).first()
        if not user_rec:
            user_rec = UserModel(guild_id=message.guild.id, user_id=message.author.id, xp=0, level=1)
            db.add(user_rec)
        
        earned_xp = random.randint(15, 25)
        user_rec.xp += earned_xp
        
        while user_rec.xp >= (user_rec.level * 100):
            user_rec.xp -= (user_rec.level * 100)
            user_rec.level += 1
            log_event(message.guild.id, "Leveling", "Level Up", f"ترقى العضو {message.author} إلى المستوى {user_rec.level}.", message.author.id)
            
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"خطأ في نظام XP: {e}", exc_info=True)
    finally:
        db.close()
        
    await bot.process_commands(message)

# ==========================================
# 6. أوامر السلاش
# ==========================================
@bot.tree.command(name="إعداد_الترحيب", description="تحديد قناة الترحيب")
@app_commands.describe(القناة="قناة ديسكورد للترحيب")
async def slash_setup_welcome(interaction: discord.Interaction, القناة: discord.TextChannel):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ يتطلب صلاحية مدير.", ephemeral=True)
        return
    db = SessionLocal()
    try:
        settings = db.query(WelcomeSettingsModel).filter_by(guild_id=interaction.guild_id).first()
        if not settings:
            settings = WelcomeSettingsModel(guild_id=interaction.guild_id)
            db.add(settings)
        settings.welcome_channel_id = القناة.id
        settings.welcome_enabled = True
        db.commit()
        await interaction.response.send_message(f"✅ تم تحديث قناة الترحيب إلى {القناة.mention}", ephemeral=True)
    finally:
        db.close()

# ==========================================
# 7. مسارات Flask والداشبورد
# ==========================================
@app.route("/dashboard/<int:guild_id>")
def master_dashboard(guild_id):
    try:
        return render_template("dashboard.html", guild_id=guild_id)
    except Exception as e:
        logger.error(f"خطأ في عرض الداشبورد: {e}", exc_info=True)
        abort(500)

# ==========================================
# 8. التشغيل المتوازي
# ==========================================
def run_discord_bot():
    try:
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        logger.critical(f"❌ فشل تشغيل البوت: {e}", exc_info=True)

if __name__ == "__main__":
    bot_thread = Thread(target=run_discord_bot, daemon=True)
    bot_thread.start()

    logger.info(f"🚀 بدء تشغيل خادم Flask على المنفذ {PORT}...")
    app.run(host="0.0.0.0", port=PORT)
    
