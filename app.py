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
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    logger.critical("❌ خطأ أمني حرج: متغير البيئة SECRET_KEY غير موجود!")
    raise ValueError("SECRET_KEY environment variable is missing.")

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    logger.critical("❌ خطأ أمني حرج: متغير البيئة DISCORD_TOKEN غير موجود!")
    raise ValueError("DISCORD_TOKEN environment variable is missing.")

PORT = int(os.environ.get("PORT", 8080))

# ==========================================
# 3. إعداد تطبيق Flask
# ==========================================
app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = SECRET_KEY

# ==========================================
# 4. إعداد قاعدة البيانات و SQLAlchemy 2.x
# ==========================================
database_url = os.environ.get("DATABASE_URL", "sqlite:///obt_system_master.db")
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# تحسين أداء الاتصال وقاعدة البيانات وإدارة Connection Pool
engine = create_engine(
    database_url,
    pool_pre_ping=True,  # فحص صحة الاتصال تلقائياً
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

# إدارة الجلسات بشكل آمن (Context Manager)
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"خطأ في قاعدة البيانات: {e}", exc_info=True)
        raise
    finally:
        db.close()

def log_event(guild_id: int, category: str, action_type: str, details: str, user_id: Optional[int] = None, severity: str = "INFO"):
    db = SessionLocal()
    try:
        new_log = CentralLogModel(
            guild_id=guild_id, 
            category=category, 
            action_type=action_type,
            user_id=user_id, 
            details=details, 
            severity=severity
        )
        db.add(new_log)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"فشل تسجيل الحدث في السجلات المركزية: {e}", exc_info=True)
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
# 5. إعداد بوت ديسكورد والأحداث المحسنة
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
        auto_roles = db.query(AutoRoleModel).filter_by(guild_id=member.guild.id).all()
        
        for ar in auto_roles:
            role = member.guild.get_role(ar.role_id)
            if not role:
                continue
            if ar.role_type == "bot" and not member.bot:
                continue
            if ar.role_type == "human" and member.bot:
                continue
            try:
                if member.guild.me.guild_permissions.manage_roles and member.guild.me.top_role > role:
                    await member.add_roles(role, reason="OBT System - Auto Role")
                else:
                    logger.warning(f"⚠️ صلاحيات غير كافية لتعيين الرتبة التلقائية في السيرفر {member.guild.id}")
            except discord.HTTPException as e:
                logger.error(f"فشل تعيين الرتبة التلقائية للعضو {member.id}: {e}", exc_info=True)

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
                    try:
                        await channel.send(content=member.mention, embed=embed)
                    except discord.HTTPException as e:
                        logger.error(f"فشل إرسال رسالة الترحيب (Embed): {e}", exc_info=True)
                else:
                    try:
                        await channel.send(formatted_text)
                    except discord.HTTPException as e:
                        logger.error(f"فشل إرسال رسالة الترحيب (Text): {e}", exc_info=True)
                log_event(member.guild.id, "Member", "Welcome Sent", f"ترحيب بالعضو {member}.", member.id)
    except Exception as e:
        logger.error(f"خطأ غير متوقع في معالجة دخول العضو: {e}", exc_info=True)
    finally:
        db.close()

@bot.event
async def on_member_remove(member: discord.Member):
    db = SessionLocal()
    try:
        settings = db.query(WelcomeSettingsModel).filter_by(guild_id=member.guild.id).first()
        if settings and settings.goodbye_enabled and settings.goodbye_channel_id:
            channel = member.guild.get_channel(settings.goodbye_channel_id)
            if isinstance(channel, discord.TextChannel):
                formatted_text = format_welcome_message(settings.goodbye_message, member)
                try:
                    await channel.send(formatted_text)
                except discord.HTTPException as e:
                    logger.error(f"فشل إرسال رسالة المغادرة: {e}", exc_info=True)
                log_event(member.guild.id, "Member", "Goodbye Sent", f"مغادرة العضو {member}.", member.id)
    except Exception as e:
        logger.error(f"خطأ غير متوقع في معالجة مغادرة العضو: {e}", exc_info=True)
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
        
        # نظام XP دقيق: منع تجاوز الحدود، الاحتفاظ بالخبرة الزائدة (Carry-over XP)، دعم الترقية المتعددة
        earned_xp = random.randint(15, 25)
        user_rec.xp += earned_xp
        
        leveled_up = False
        while user_rec.xp >= (user_rec.level * 100):
            user_rec.xp -= (user_rec.level * 100)
            user_rec.level += 1
            leveled_up = True
            log_event(message.guild.id, "Leveling", "Level Up", f"ترقى العضو {message.author} إلى المستوى {user_rec.level}.", message.author.id)
            
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"خطأ في نظام معالجة الخبرة XP: {e}", exc_info=True)
    finally:
        db.close()
        
    await bot.process_commands(message)

# ==========================================
# 6. أوامر السلاش المتكاملة والآمنة
# ==========================================
@bot.tree.command(name="إعداد_الترحيب", description="تحديد قناة ورسالة الترحيب الخاصة بالسيرفر")
@app_commands.describe(القناة="قناة ديسكورد المخصصة لإرسال الترحيب")
async def slash_setup_welcome(interaction: discord.Interaction, القناة: discord.TextChannel):
    if not interaction.guild or not interaction.user:
        await interaction.response.send_message("❌ هذا الأمر يستخدم داخل السيرفرات فقط.", ephemeral=True)
        return
    
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ عذراً، تتطلب صلاحية **مدير** لاستخدام هذا الأمر.", ephemeral=True)
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
        await interaction.response.send_message(f"✅ **تم تحديث قناة الترحيب بنجاح!** القناة: {القناة.mention}", ephemeral=True)
    except Exception as e:
        db.rollback()
        logger.error(f"خطأ في إعداد الترحيب: {e}", exc_info=True)
        await interaction.response.send_message("❌ حدث خطأ داخلي أثناء حفظ الإعدادات.", ephemeral=True)
    finally:
        db.close()

@bot.tree.command(name="إعداد_المغادرة", description="تحديد قناة ورسالة مغادرة الأعضاء")
@app_commands.describe(القناة="قناة ديسكورد المخصصة للمغادرة")
async def slash_setup_goodbye(interaction: discord.Interaction, القناة: discord.TextChannel):
    if not interaction.guild or not interaction.user:
        await interaction.response.send_message("❌ هذا الأمر يستخدم داخل السيرفرات فقط.", ephemeral=True)
        return
        
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ عذراً، تتطلب صلاحية **مدير** لاستخدام هذا الأمر.", ephemeral=True)
        return
        
    db = SessionLocal()
    try:
        settings = db.query(WelcomeSettingsModel).filter_by(guild_id=interaction.guild_id).first()
        if not settings:
            settings = WelcomeSettingsModel(guild_id=interaction.guild_id)
            db.add(settings)
        settings.goodbye_channel_id = القناة.id
        settings.goodbye_enabled = True
        db.commit()
        await interaction.response.send_message(f"✅ **تم تحديث قناة المغادرة بنجاح!** القناة: {القناة.mention}", ephemeral=True)
    except Exception as e:
        db.rollback()
        logger.error(f"خطأ في إعداد المغادرة: {e}", exc_info=True)
        await interaction.response.send_message("❌ حدث خطأ داخلي أثناء حفظ الإعدادات.", ephemeral=True)
    finally:
        db.close()

@bot.tree.command(name="تقديم_صانع_محتوى", description="التقديم للانضمام إلى برنامج صناع المحتوى المعتمد")
@app_commands.describe(المنصة="المنصة الأساسية لصناعة المحتوى", رابط_الملف="رابط حسابك الشخصي (URL صحيح)", المتابعون="عدد المتابعين التقريبي", التصنيف="تصنيف المحتوى")
@app_commands.choices(المنصة=[
    app_commands.Choice(name="YouTube", value="YouTube"),
    app_commands.Choice(name="TikTok", value="TikTok"),
    app_commands.Choice(name="Twitch", value="Twitch"),
    app_commands.Choice(name="Kick", value="Kick")
])
async def slash_apply_creator(interaction: discord.Interaction, المنصة: str, رابط_الملف: str, المتابعون: int, التصنيف: str):
    if not interaction.guild or not interaction.user:
        await interaction.response.send_message("❌ هذا الأمر يستخدم داخل السيرفرات فقط.", ephemeral=True)
        return

    # التحقق من صحة رابط الملف الشخصي
    url_regex = re.compile(r'^https?://[^\s/$.?#].[^\s]*$', re.IGNORECASE)
    if not url_regex.match(رابط_الملف):
        await interaction.response.send_message("❌ رابط الملف الشخصي غير صالح. يرجى إدخال رابط يبدأ بـ http:// أو https://", ephemeral=True)
        return

    if المتابعون < 0:
        await interaction.response.send_message("❌ عدد المتابعين لا يمكن أن يكون سالباً.", ephemeral=True)
        return

    db = SessionLocal()
    try:
        existing = db.query(CreatorApplicationModel).filter_by(guild_id=interaction.guild_id, user_id=interaction.user.id).first()
        if existing:
            await interaction.response.send_message("❌ لديك طلب سابق مسجل بالفعل في نظام صناع المحتوى.", ephemeral=True)
            return

        new_app = CreatorApplicationModel(
            guild_id=interaction.guild_id, 
            user_id=interaction.user.id,
            platform=المنصة, 
            profile_url=رابط_الملف, 
            followers_count=المتابعون,
            content_category=التصنيف, 
            status="PENDING"
        )
        db.add(new_app)
        db.commit()
        await interaction.response.send_message("✅ **تم إرسال طلبك بنجاح!** سيتم مراجعته من الإدارة قريباً.", ephemeral=True)
    except Exception as e:
        db.rollback()
        logger.error(f"خطأ في تقديم صانع المحتوى: {e}", exc_info=True)
        await interaction.response.send_message("❌ حدث خطأ داخلي أثناء معالجة الطلب.", ephemeral=True)
    finally:
        db.close()

# ==========================================
# 7. مسارات Flask والداشبورد الآمنة (Render Template)
# ==========================================
@app.route("/dashboard/<int:guild_id>")
def master_dashboard(guild_id):
    try:
        return render_template("dashboard.html", guild_id=guild_id)
    
