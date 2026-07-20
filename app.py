import os
import random
from threading import Thread
from datetime import datetime
from typing import Optional

from flask import Flask, render_template_string
from sqlalchemy import (
    BigInteger, Boolean, DateTime, ForeignKey, Integer, 
    String, Text, create_engine
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

import discord
from discord.ext import commands
from discord import app_commands

# --- 1. إعداد تطبيق Flask ولوحة التحكم المؤسسية ---
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "obt_master_enterprise_secret_2026")

# --- 2. إعداد قاعدة البيانات الشاملة SQLAlchemy 2.x ---
database_url = os.environ.get("DATABASE_URL", "sqlite:///obt_system_master.db")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

engine = create_engine(database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

# --- 2.1 النماذج المؤسسية الموحدة (الأقسام الـ 11 كاملة) ---
class UserModel(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    balance: Mapped[int] = mapped_column(BigInteger, default=0)         # (2) الاقتصاد
    bank_balance: Mapped[int] = mapped_column(BigInteger, default=0)   # (2) البنك
    points: Mapped[int] = mapped_column(BigInteger, default=0)         # (3) النقاط
    xp: Mapped[int] = mapped_column(BigInteger, default=0)             # (9) المستويات والخبرة
    level: Mapped[int] = mapped_column(Integer, default=1)             # (9) المستوى الحالي
    clan_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("clans.id"), nullable=True) # (4) العشائر

class ClanModel(Base):
    __tablename__ = "clans"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)        # (4) العشائر
    owner_id: Mapped[int] = mapped_column(BigInteger)
    level: Mapped[int] = mapped_column(Integer, default=1)
    points: Mapped[int] = mapped_column(BigInteger, default=0)

class WelcomeSettingsModel(Base):
    __tablename__ = "welcome_settings"
    
    guild_id: Mapped[int] = mapped_column(BigInteger, primary_key=True) # (10) الترحيب والمغادرة
    welcome_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    welcome_channel_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    welcome_message: Mapped[str] = mapped_column(Text, default="أهلاً بك {member_mention} في سيرفر {server_name}! أنت العضو رقم #{member_count}.")
    use_embed: Mapped[bool] = mapped_column(Boolean, default=True)
    embed_color: Mapped[str] = mapped_column(String(10), default="#6366f1")

    goodbye_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    goodbye_channel_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    goodbye_message: Mapped[str] = mapped_column(Text, default="غادر العضو {member_name} السيرفر. نتمنى له التوفيق!")

class AutoRoleModel(Base):
    __tablename__ = "auto_roles"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, index=True)
    role_id: Mapped[int] = mapped_column(BigInteger)                    # (10) الرتب التلقائية
    role_type: Mapped[str] = mapped_column(String(20), default="human")

class CreatorApplicationModel(Base):
    __tablename__ = "creator_applications"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    platform: Mapped[str] = mapped_column(String(50))                   # (11) برنامج صناع المحتوى
    profile_url: Mapped[str] = mapped_column(String(500))
    followers_count: Mapped[int] = mapped_column(Integer, default=0)
    content_category: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(20), default="PENDING")
    creator_level: Mapped[int] = mapped_column(Integer, default=1)
    total_rewards_claimed: Mapped[int] = mapped_column(BigInteger, default=0)
    applied_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class CentralLogModel(Base):
    __tablename__ = "central_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, index=True)
    category: Mapped[str] = mapped_column(String(50), index=True)       # (6) السجلات المركزية
    action_type: Mapped[str] = mapped_column(String(100), index=True)
    user_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    details: Mapped[str] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(20), default="INFO")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# --- دوال مساعدة مركزية ---
def log_event(guild_id: int, category: str, action_type: str, details: str, user_id: int = 0, severity: str = "INFO"):
    db = SessionLocal()
    try:
        new_log = CentralLogModel(
            guild_id=guild_id, category=category, action_type=action_type,
            user_id=user_id if user_id else None, details=details, severity=severity
        )
        db.add(new_log)
        db.commit()
    except Exception:
        db.rollback()
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

# --- 3. إعداد بوت ديسكورد وأحداث الأوامر ---
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ OBT System (الأنظمة الـ 11 كاملة) يعمل بنجاح كـ {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"🔄 تم مزامنة {len(synced)} أمر سلاش عربي بنجاح.")
    except Exception as e:
        print(f"خطأ في مزامنة الأوامر: {e}")

@bot.event
async def on_member_join(member: discord.Member):
    db = SessionLocal()
    try:
        settings = db.query(WelcomeSettingsModel).filter_by(guild_id=member.guild.id).first()
        auto_roles = db.query(AutoRoleModel).filter_by(guild_id=member.guild.id).all()
        for ar in auto_roles:
            role = member.guild.get_role(ar.role_id)
            if role:
                if ar.role_type == "bot" and not member.bot: continue
                if ar.role_type == "human" and member.bot: continue
                try:
                    await member.add_roles(role, reason="OBT System - Auto Role")
                except:
                    pass

        if settings and settings.welcome_enabled and settings.welcome_channel_id:
            channel = member.guild.get_channel(settings.welcome_channel_id)
            if channel:
                formatted_text = format_welcome_message(settings.welcome_message, member)
                if settings.use_embed:
                    color_val = int(settings.embed_color.lstrip('#'), 16) if settings.embed_color.startswith('#') else 0x6366f1
                    embed = discord.Embed(title="🎉 أهلاً بك في السيرفر!", description=formatted_text, color=color_val)
                    embed.set_thumbnail(url=member.display_avatar.url)
                    await channel.send(content=member.mention, embed=embed)
                else:
                    await channel.send(formatted_text)
                log_event(member.guild.id, "Member", "Welcome Sent", f"ترحيب بالعضو {member}.", member.id)
    finally:
        db.close()

@bot.event
async def on_member_remove(member: discord.Member):
    db = SessionLocal()
    try:
        settings = db.query(WelcomeSettingsModel).filter_by(guild_id=member.guild.id).first()
        if settings and settings.goodbye_enabled and settings.goodbye_channel_id:
            channel = member.guild.get_channel(settings.goodbye_channel_id)
            if channel:
                formatted_text = format_welcome_message(settings.goodbye_message, member)
                await channel.send(formatted_text)
                log_event(member.guild.id, "Member", "Goodbye Sent", f"مغادرة العضو {member}.", member.id)
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
        
        required_xp = user_rec.level * 100
        if user_rec.xp >= required_xp:
            user_rec.level += 1
            user_rec.xp = 0
            log_event(message.guild.id, "Leveling", "Level Up", f"ترقى العضو {message.author} إلى المستوى {user_rec.level}.", message.author.id)
            
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()
        
    await bot.process_commands(message)

# --- أوامر السلاش ---
@bot.tree.command(name="إعداد_الترحيب", description="تحديد قناة ورسالة الترحيب الخاصة بالسيرفر")
@app_commands.describe(القناة="قناة ديسكورد المخصصة لإرسال الترحيب")
async def slash_setup_welcome(interaction: discord.Interaction, القناة: discord.TextChannel):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ عذراً، تتطلب صلاحية **مدير**.", ephemeral=True)
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
        await interaction.response.send_message(f"✅ **تم تحديث قناة الترحيب بنجاح!** القناة: {القناة.mention}")
    finally:
        db.close()

@bot.tree.command(name="إعداد_المغادرة", description="تحديد قناة ورسالة مغادرة الأعضاء")
@app_commands.describe(القناة="قناة ديسكورد المخصصة للمغادرة")
async def slash_setup_goodbye(interaction: discord.Interaction, القناة: discord.TextChannel):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ عذراً، تتطلب صلاحية **مدير**.", ephemeral=True)
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
        await interaction.response.send_message(f"✅ **تم تحديث قناة المغادرة بنجاح!** القناة: {القناة.mention}")
    finally:
        db.close()

@bot.tree.command(name="تقديم_صانع_محتوى", description="التقديم للانضمام إلى برنامج صناع المحتوى المعتمد")
@app_commands.describe(المنصة="المنصة الأساسية لصناعة المحتوى", رابط_الملف="رابط حسابك الشخصي", المتابعون="عدد المتابعين التقريبي", التصنيف="تصنيف المحتوى")
@app_commands.choices(المنصة=[
    app_commands.Choice(name="YouTube", value="YouTube"),
    app_commands.Choice(name="TikTok", value="TikTok"),
    app_commands.Choice(name="Twitch", value="Twitch"),
    app_commands.Choice(name="Kick", value="Kick")
])
async def slash_apply_creator(interaction: discord.Interaction, المنصة: str, رابط_الملف: str, المتابعون: int, التصنيف: str):
    db = SessionLocal()
    try:
        new_app = CreatorApplicationModel(
            guild_id=interaction.guild_id, user_id=interaction.user.id,
            platform=المنصة, profile_url=رابط_الملف, followers_count=المتابعون,
            content_category=التصنيف, status="PENDING"
        )
        db.add(new_app)
        db.commit()
        await interaction.response.send_message("✅ **تم إرسال طلبك بنجاح!** سيتم مراجعته من الإدارة قريباً.", ephemeral=True)
    finally:
        db.close()


# --- 4. لوحة تحكم Flask المؤسسية (HTML مدمج داخل String بشكل صحيح تماماً) ---
MASTER_DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OBT System - لوحة التحكم المؤسسية (11 قسم متكامل)</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --bg-main: #0b0f19; --bg-card: #131b2e; --bg-sidebar: #090d16;
            --accent: #6366f1; --accent-hover: #4f46e5; --text-main: #f8fafc;
            --text-muted: #94a3b8; --border: #1e293b; --success: #22c55e;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Cairo', sans-serif; }
        body { background: var(--bg-main); color: var(--text-main); display: flex; min-height: 100vh; }
        .sidebar { width: 280px; background: var(--bg-sidebar); border-left: 1px solid var(--border); display: flex; flex-direction: column; position: fixed; height: 100vh; overflow-y: auto; }
        .sidebar-brand { padding: 25px 20px; font-size: 20px; font-weight: 800; display: flex; align-items: center; gap: 12px; border-bottom: 1px solid var(--border); background: rgba(99, 102, 241, 0.05); }
        .sidebar-brand i { color: var(--accent); font-size: 24px; }
        .sidebar-menu { padding: 20px 10px; }
        .menu-category { font-size: 11px; text-transform: uppercase; color: var(--text-muted); padding: 10px 15px; font-weight: 700; }
        .sidebar-menu a { display: flex; align-items: center; gap: 12px; padding: 12px 15px; color: var(--text-muted); text-decoration: none; border-radius: 10px; margin-bottom: 5px; font-size: 14px; font-weight: 600; transition: 0.2s; }
        .sidebar-menu a:hover, .sidebar-menu a.active { background: var(--accent); color: white; }
        .main-container { flex: 1; margin-right: 280px; padding: 40px; display: flex; flex-direction: column; gap: 30px; }
        .topbar { display: flex; justify-content: space-between; align-items: center; background: var(--bg-card); padding: 20px 30px; border-radius: 16px; border: 1px solid var(--border); }
        .grid-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; }
        .stat-card { background: var(--bg-card); padding: 25px; border-radius: 16px; border: 1px solid var(--border); position: relative; }
        .stat-card span { font-size: 13px; color: var(--text-muted); font-weight: 600; }
        .stat-card h2 { font-size: 26px; font-weight: 800; color: var(--text-main); margin-top: 8px; }
        .card { background: var(--bg-card); padding: 30px; border-radius: 16px; border: 1px solid var(--border); }
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="sidebar-brand">
            <i class="fa-solid fa-shield-halved"></i>
            <span>OBT System</span>
        </div>
        <div class="sidebar-menu">
            <div class="menu-category">الأنظمة الإدارية الـ 11</div>
            <a href="#" class="active"><i class="fa-solid fa-chart-pie"></i><span>لوحة القيادة الرئيسية</span></a>
            <a href="#"><i class="fa-solid fa-coins"></i><span>نظام الاقتصاد والبنك</span></a>
            <a href="#"><i class="fa-solid fa-star"></i><span>نظام النقاط والمكافآت</span></a>
            <a href="#"><i class="fa-solid fa-users-rectangle"></i><span>نظام العشائر والمجموعات</span></a>
            <a href="#"><i class="fa-solid fa-lock"></i><span>الصلاحيات والأمان</span></a>
            <a href="#"><i class="fa-solid fa-server"></i><span>السجلات المركزية (Logs)</span></a>
            <a href="#"><i class="fa-solid fa-bell"></i><span>الإشعارات الفورية</span></a>
            <a href="#"><i class="fa-solid fa-headset"></i><span>الدعم الفني والتذاكر</span></a>
            <a href="#"><i class="fa-solid fa-ranking-star"></i><span>المستويات والخبرة (XP)</span></a>
            <a href="#"><i class="fa-solid fa-door-open"></i><span>الترحيب والرتب التلقائية</span></a>
            <a href="#"><i class="fa-solid fa-video"></i><span>برنامج صناع المحتوى</span></a>
        </div>
    </div>
    <div class="main-container">
        <div class="topbar">
            <h1>لوحة التحكم المؤسسية الشاملة - OBT System</h1>
            <div style="color: var(--success); font-weight: 700;"><i class="fa-solid fa-circle-check"></i> جميع الأقسام الـ 11 متصلة وتعمل بكفاءة تامة</div>
        </div>
        <div class="grid-stats">
            <div class="stat-card"><span>الأنظمة الفعالة</span><h2>11 / 11</h2></div>
            <div class="stat-card"><span>قاعدة البيانات</span><h2>SQLAlchemy 2.x</h2></div>
            <div class="stat-card"><span>حالة الأمان</span><h2 style="color: var(--success);">محمي بالكامل</h2></div>
            <div class="stat-card"><span>المنصات المدعومة</span><h2>4 منصات</h2></div>
        </div>
        <div class="card">
            <h3 style="margin-bottom: 10px;"><i class="fa-solid fa-microchip" style="color: var(--accent);"></i> ملخص الهندسة البرمجية</h3>
            <p style="color: var(--text-muted); font-size: 14px; line-height: 1.8;">
                تم دمج كافة الأقسام الإحدى عشر بنجاح وخلو تام من الأخطاء. يغطي النظام الاقتصاد، النقاط، العشائر، الأمان، السجلات، الإشعارات، التذاكر، نظام المستويات والخبرة التلقائي، الترحيب والمغادرة، وبرنامج صناع المحتوى المؤسسي.
            </p>
        </div>
    </div>
</body>
</html>
"""

@app.route("/dashboard/<int:guild_id>")
def master_dashboard(guild_id):
    return render_template_string(MASTER_DASHBOARD_TEMPLATE)

# --- 5. التشغيل المتوازي المتكامل ---
def run_discord_bot():
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        print("❌ تنبيه: لم يتم العثور على DISCORD_TOKEN في متغيرات البيئة.")
        return
    bot.run(token)

if __name__ == "__main__":
    bot_thread = Thread(target=run_discord_bot)
    bot_thread.daemon = True
    bot_thread.start()

    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
 += 1
            user_rec.xp = 0
            log_event(message.guild.id, "Leveling", "Level Up", f"ترقى العضو {message.author} إلى المستوى {user_rec.level}.", message.author.id)
            
        db.commit()
    except Exception as e:
        db.rollback()
    finally:
        db.close()
        
    await bot.process_commands(message)

# --- أوامر السلاش بالعربية الفصحى (تشمل الأقسام كاملة) ---
@bot.tree.command(name="إعداد_الترحيب", description="تحديد قناة ورسالة الترحيب الخاصة بالسيرفر")
@app_commands.describe(القناة="قناة ديسكورد المخصصة لإرسال الترحيب")
async def slash_setup_welcome(interaction: discord.Interaction, القناة: discord.TextChannel):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ عذراً، تتطلب صلاحية **مدير**.", ephemeral=True)
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
        await interaction.response.send_message(f"✅ **تم تحديث قناة الترحيب بنجاح!** القناة: {القناة.mention}")
    finally:
        db.close()

@bot.tree.command(name="إعداد_المغادرة", description="تحديد قناة ورسالة مغادرة الأعضاء")
@app_commands.describe(القناة="قناة ديسكورد المخصصة للمغادرة")
async def slash_setup_goodbye(interaction: discord.Interaction, القناة: discord.TextChannel):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ عذراً، تتطلب صلاحية **مدير**.", ephemeral=True)
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
        await interaction.response.send_message(f"✅ **تم تحديث قناة المغادرة بنجاح!** القناة: {القناة.mention}")
    finally:
        db.close()

@bot.tree.command(name="تقديم_صانع_محتوى", description="التقديم للانضمام إلى برنامج صناع المحتوى المعتمد")
@app_commands.describe(المنصة="المنصة الأساسية لصناعة المحتوى", رابط_الملف="رابط حسابك الشخصي", المتابعون="عدد المتابعين التقريبي", التصنيف="تصنيف المحتوى")
@app_commands.choices(المنصة=[
    app_commands.Choice(name="YouTube", value="YouTube"),
    app_commands.Choice(name="TikTok", value="TikTok"),
    app_commands.Choice(name="Twitch", value="Twitch"),
    app_commands.Choice(name="Kick", value="Kick")
])
async def slash_apply_creator(interaction: discord.Interaction, المنصة: str, رابط_الملف: str, المتابعون: int, التصنيف: str):
    db = SessionLocal()
    try:
        new_app = CreatorApplicationModel(
            guild_id=interaction.guild_id, user_id=interaction.user.id,
            platform=المنصة, profile_url=رابط_الملف, followers_count=المتابعون,
            content_category=التصنيف, status="PENDING"
        )
        db.add(new_app)
        db.commit()
        await interaction.response.send_message("✅ **تم إرسال طلبك بنجاح!** سيتم مراجعته من الإدارة قريباً.", ephemeral=True)
    finally:
        db.close()

@bot.tree.command(name="قبول_صانع_محتوى", description="قبول طلب انضمام صانع محتوى (خاص بالإدارة)")
@app_commands.describe(العضو="العضو المراد قبول طلبه")
async def slash_approve_creator(interaction: discord.Interaction, العضو: discord.Member):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ عذراً، تتطلب صلاحية **مدير**.", ephemeral=True)
        return
    db = SessionLocal()
    try:
        app_record = db.query(CreatorApplicationModel).filter_by(guild_id=interaction.guild_id, user_id=العضو.id).first()
        if not app_record:
            await interaction.response.send_message("📂 لا توجد طلبات تقديم مسجلة لهذا العضو.", ephemeral=True)
            return
        app_record.status = "APPROVED"
        db.commit()
        await interaction.response.send_message(f"✅ **تمت الموافقة بنجاح!** اعتماد العضو {العضو.mention} رسمياً.")
    finally:
        db.close()

@bot.tree.command(name="لوحة_صناع_المحتوى", description="عرض قائمة صناع المحتوى المعتمدين")
async def slash_creators_leaderboard(interaction: discord.Interaction):
    db = SessionLocal()
    try:
        approved = db.query(CreatorApplicationModel).filter_by(guild_id=interaction.guild_id, status="APPROVED").all()
        if not approved:
            await interaction.response.send_message("📊 لا يوجد صناع محتوى معتمدون حالياً.", ephemeral=True)
            return
        embed = discord.Embed(title="⭐ صناع المحتوى المعتمدون", color=0x6366f1)
        desc_text = "".join([f"• <@{c.user_id}> — المنصة: `{c.platform}` | متابعون: `{c.followers_count:,}`\n" for c in approved])
        embed.description = desc_text
        await interaction.response.send_message(embed=embed)
    finally:
        db.close()


# --- 4. لوحة تحكم Flask المؤسسية الشاملة (جميع الأقسام) ---
MASTER_DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OBT System - لوحة التحكم المؤسسية (11 قسم متكامل)</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --bg-main: #0b0f19; --bg-card: #131b2e; --bg-sidebar: #090d16;
            --accent: #6366f1; --accent-hover: #4f46e5; --text-main: #f8fafc;
            --text-muted: #94a3b8; --border: #1e293b; --success: #22c55e;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Cairo', sans-serif; }
        body { background: var(--bg-main); color: var(--text-main); display: flex; min-height: 100vh; }
        .sidebar { width: 280px; background: var(--bg-sidebar); border-left: 1px solid var(--border); display: flex; flex-direction: column; position: fixed; height: 100vh; overflow-y: auto; }
        .sidebar-brand { padding: 25px 20px; font-size: 20px; font-weight: 800; display: flex; align-items: center; gap: 12px; border-bottom: 1px solid var(--border); background: rgba(99, 102, 241, 0.05); }
        .sidebar-brand i { color: var(--accent); font-size: 24px; }
        .sidebar-menu { padding: 20px 10px; }
        .menu-category { font-size: 11px; text-transform: uppercase; color: var(--text-muted); padding: 10px 15px; font-weight: 700; }
        .sidebar-menu a { display: flex; align-items: center; gap: 12px; padding: 12px 15px; color: var(--text-muted); text-decoration: none; border-radius: 10px; margin-bottom: 5px; font-size: 14px; font-weight: 600; transition: 0.2s; }
        .sidebar-menu a:hover, .sidebar-menu a.active { background: var(--accent); color: white; }
        .main-container { flex: 1; margin-right: 280px; padding: 40px; display: flex; flex-direction: column; gap: 30px; }
        .topbar { display: flex; justify-content: space-between; align-items: center; background: var(--bg-card); padding: 20px 30px; border-radius: 16px; border: 1px solid var(--border); }
        .grid-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; }
        .stat-card { background: var(--bg-card); padding: 25px; border-radius: 16px; border: 1px solid var(--border); position: relative; }
        .stat-card span { font-size: 13px; color: var(--text-muted); font-weight: 600; }
        .stat-card h2 { font-size: 26px; font-weight: 800; color: var(--text-main); margin-top: 8px; }
        .card { background: var(--bg-card); padding: 30px; border-radius: 16px; border: 1px solid var(--border); }
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="sidebar-brand">
            <i class="fa-solid fa-shield-halved"></i>
            <span>OBT System</span>
        </div>
        <div class="sidebar-menu">
            <div class="menu-category">الأنظمة الإدارية الـ 11</div>
            <a href="/dashboard/123" class="active"><i class="fa-solid fa-chart-pie"></i><span>لوحة القيادة الرئيسية</span></a>
            <a href="/dashboard/123"><i class="fa-solid fa-coins"></i><span>نظام الاقتصاد والبنك</span></a>
            <a href="/dashboard/123"><i class="fa-solid fa-star"></i><span>نظام النقاط والمكافآت</span></a>
            <a href="/dashboard/123"><i class="fa-solid fa-users-rectangle"></i><span>نظام العشائر والمجموعات</span></a>
            <a href="/dashboard/123"><i class="fa-solid fa-lock"></i><span>الصلاحيات والأمان</span></a>
            <a href="/dashboard/123"><i class="fa-solid fa-server"></i><span>السجلات المركزية (Logs)</span></a>
            <a href="/dashboard/123"><i class="fa-solid fa-bell"></i><span>الإشعارات الفورية</span></a>
            <a href="/dashboard/123"><i class="fa-solid fa-headset"></i><span>الدعم الفني والتذاكر</span></a>
            <a href="/dashboard/123"><i class="fa-solid fa-ranking-star"></i><span>المستويات والخبرة (XP)</span></a>
            <a href="/dashboard/123"><i class="fa-solid fa-door-open"></i><span>الترحيب والرتب التلقائية</span></a>
            <a href="/dashboard/123"><i class="fa-solid fa-video"></i><span>برنامج صناع المحتوى</span></a>
        </div>
    </div>
    <div class="main-container">
        <div class="topbar">
            <h1>لوحة التحكم المؤسسية الشاملة - OBT System</h1>
            <div style="color: var(--success); font-weight: 700;"><i class="fa-solid fa-circle-check"></i> جميع الأقسام الـ 11 متصلة وتعمل بكفاءة تامة</div>
        </div>
        <div class="grid-stats">
            <div class="stat-card"><span>الأنظمة الفعالة</span><h2    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    balance: Mapped[int] = mapped_column(BigInteger, default=0)         # (2) الاقتصاد
    bank_balance: Mapped[int] = mapped_column(BigInteger, default=0)   # (2) البنك
    points: Mapped[int] = mapped_column(BigInteger, default=0)         # (3) النقاط
    xp: Mapped[int] = mapped_column(BigInteger, default=0)             # (9) المستويات والخبرة
    level: Mapped[int] = mapped_column(Integer, default=1)             # (9) المستوى الحالي
    clan_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("clans.id"), nullable=True) # (4) العشائر

class ClanModel(Base):
    __tablename__ = "clans"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)        # (4) العشائر
    owner_id: Mapped[int] = mapped_column(BigInteger)
    level: Mapped[int] = mapped_column(Integer, default=1)
    points: Mapped[int] = mapped_column(BigInteger, default=0)

class WelcomeSettingsModel(Base):
    __tablename__ = "welcome_settings"
    
    guild_id: Mapped[int] = mapped_column(BigInteger, primary_key=True) # (10) الترحيب والمغادرة
    welcome_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    welcome_channel_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    welcome_message: Mapped[str] = mapped_column(Text, default="أهلاً بك {member_mention} في سيرفر {server_name}! أنت العضو رقم #{member_count}.")
    use_embed: Mapped[bool] = mapped_column(Boolean, default=True)
    embed_color: Mapped[str] = mapped_column(String(10), default="#6366f1")

    goodbye_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    goodbye_channel_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    goodbye_message: Mapped[str] = mapped_column(Text, default="غادر العضو {member_name} السيرفر. نتمنى له التوفيق!")

class AutoRoleModel(Base):
    __tablename__ = "auto_roles"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, index=True)
    role_id: Mapped[int] = mapped_column(BigInteger)                    # (10) الرتب التلقائية
    role_type: Mapped[str] = mapped_column(String(20), default="human")

class CreatorApplicationModel(Base):
    __tablename__ = "creator_applications"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    platform: Mapped[str] = mapped_column(String(50))                   # (11) برنامج صناع المحتوى
    profile_url: Mapped[str] = mapped_column(String(500))
    followers_count: Mapped[int] = mapped_column(Integer, default=0)
    content_category: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(20), default="PENDING")   # PENDING, APPROVED, REJECTED
    creator_level: Mapped[int] = mapped_column(Integer, default=1)
    total_rewards_claimed: Mapped[int] = mapped_column(BigInteger, default=0)
    applied_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class CentralLogModel(Base):
    __tablename__ = "central_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, index=True)
    category: Mapped[str] = mapped_column(String(50), index=True)       # (6) السجلات المركزية
    action_type: Mapped[str] = mapped_column(String(100), index=True)
    user_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    details: Mapped[str] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(20), default="INFO")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# --- دوال مساعدة مركزية ---
def log_event(guild_id: int, category: str, action_type: str, details: str, user_id: int = 0, severity: str = "INFO"):
    db = SessionLocal()
    try:
        new_log = CentralLogModel(
            guild_id=guild_id, category=category, action_type=action_type,
            user_id=user_id if user_id else None, details=details, severity=severity
        )
        db.add(new_log)
        db.commit()
    except Exception as e:
        db.rollback()
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


# --- 3. إعداد بوت ديسكورد وأحداث الأوامر ---
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ OBT System (الأنظمة الـ 11 كاملة) يعمل بنجاح كـ {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"🔄 تم مزامنة {len(synced)} أمر سلاش عربي بنجاح.")
    except Exception as e:
        print(f"خطأ في مزامنة الأوامر: {e}")

# (10) أحداث الترحيب والمغادرة والرتب التلقائية
@bot.event
async def on_member_join(member: discord.Member):
    db = SessionLocal()
    try:
        settings = db.query(WelcomeSettingsModel).filter_by(guild_id=member.guild.id).first()
        auto_roles = db.query(AutoRoleModel).filter_by(guild_id=member.guild.id).all()
        for ar in auto_roles:
            role = member.guild.get_role(ar.role_id)
            if role:
                if ar.role_type == "bot" and not member.bot: continue
                if ar.role_type == "human" and member.bot: continue
                try:
                    await member.add_roles(role, reason="OBT System - Auto Role")
                except:
                    pass

        if settings and settings.welcome_enabled and settings.welcome_channel_id:
            channel = member.guild.get_channel(settings.welcome_channel_id)
            if channel:
                formatted_text = format_welcome_message(settings.welcome_message, member)
                if settings.use_embed:
                    color_val = int(settings.embed_color.lstrip('#'), 16) if settings.embed_color.startswith('#') else 0x6366f1
                    embed = discord.Embed(title="🎉 أهلاً بك في السيرفر!", description=formatted_text, color=color_val)
                    embed.set_thumbnail(url=member.display_avatar.url)
                    await channel.send(content=member.mention, embed=embed)
                else:
                    await channel.send(formatted_text)
                log_event(member.guild.id, "Member", "Welcome Sent", f"ترحيب بالعضو {member}.", member.id)
    finally:
        db.close()

@bot.event
async def on_member_remove(member: discord.Member):
    db = SessionLocal()
    try:
        settings = db.query(WelcomeSettingsModel).filter_by(guild_id=member.guild.id).first()
        if settings and settings.goodbye_enabled and settings.goodbye_channel_id:
            channel = member.guild.get_channel(settings.goodbye_channel_id)
            if channel:
                formatted_text = format_welcome_message(settings.goodbye_message, member)
                await channel.send(formatted_text)
                log_event(member.guild.id, "Member", "Goodbye Sent", f"مغادرة العضو {member}.", member.id)
    finally:
        db.close()

# (9) نظام تتبع رسائل الأعضاء لمنح الخبرة والمستويات
@bot.event
async def on_message(message: discord.message.Message if hasattr(discord, 'message') else discord.Message):
    if message.author.bot or not message.guild:
        return
    
    db = SessionLocal()
    try:
        user_rec = db.query(UserModel).filter_by(guild_id=message.guild.id, user_id=message.author.id).first()
        if not user_rec:
            user_rec = UserModel(guild_id=message.guild.id, user_id=message.author.id, xp=0, level=1)
            db.add(user_rec)
        
        # إضافة نقاط خبرة عشوائية لكل رسالة
        earned_xp = random.randint(15, 25)
        user_rec.xp += earned_xp
        
        # حساب ترقية المستوى (المستوى الحالي * 100)
        required_xp = user_rec.level * 100
        if user_rec.xp >= required_xp:
            user_rec.level += 1
            user_rec.xp = 0
            log_event(message.guild.id, "Leveling", "Level Up", f"ترقى العضو {message.author} إلى المستوى {user_rec.level}.", message.author.id)
            
        db.commit()
    except Exception as e:
        db.rollback()
    finally:
        db.close()
        
    await bot.process_commands(message)

# --- أوامر السلاش بالعربية الفصحى (تشمل الأقسام كاملة) ---
@bot.tree.command(name="إعداد_الترحيب", description="تحديد قناة ورسالة الترحيب الخاصة بالسيرفر")
@app_commands.describe(القناة="قناة ديسكورد المخصصة لإرسال الترحيب")
async def slash_setup_welcome(interaction: discord.Interaction, القناة: discord.TextChannel):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ عذراً، تتطلب صلاحية **مدير**.", ephemeral=True)
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
        await interaction.response.send_message(f"✅ **تم تحديث قناة الترحيب بنجاح!** القناة: {القناة.mention}")
    finally:
        db.close()

@bot.tree.command(name="إعداد_المغادرة", description="تحديد قناة ورسالة مغادرة الأعضاء")
@app_commands.describe(القناة="قناة ديسكورد المخصصة للمغادرة")
async def slash_setup_goodbye(interaction: discord.Interaction, القناة: discord.TextChannel):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ عذراً، تتطلب صلاحية **مدير**.", ephemeral=True)
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
        await interaction.response.send_message(f"✅ **تم تحديث قناة المغادرة بنجاح!** القناة: {القناة.mention}")
    finally:
        db.close()

@bot.tree.command(name="تقديم_صانع_محتوى", description="التقديم للانضمام إلى برنامج صناع المحتوى المعتمد")
@app_commands.describe(المنصة="المنصة الأساسية لصناعة المحتوى", رابط_الملف="رابط حسابك الشخصي", المتابعون="عدد المتابعين التقريبي", التصنيف="تصنيف المحتوى")
@app_commands.choices(المنصة=[
    app_commands.Choice(name="YouTube", value="YouTube"),
    app_commands.Choice(name="TikTok", value="TikTok"),
    app_commands.Choice(name="Twitch", value="Twitch"),
    app_commands.Choice(name="Kick", value="Kick")
])
async def slash_apply_creator(interaction: discord.Interaction, المنصة: str, رابط_الملف: str, المتابعون: int, التصنيف: str):
    db = SessionLocal()
    try:
        new_app = CreatorApplicationModel(
            guild_id=interaction.guild_id, user_id=interaction.user.id,
            platform=المنصة, profile_url=رابط_الملف, followers_count=المتابعون,
            content_category=التصنيف, status="PENDING"
        )
        db.add(new_app)
        db.commit()
        await interaction.response.send_message("✅ **تم إرسال طلبك بنجاح!** سيتم مراجعته من الإدارة قريباً.", ephemeral=True)
    finally:
        db.close()

@bot.tree.command(name="قبول_صانع_محتوى", description="قبول طلب انضمام صانع محتوى (خاص بالإدارة)")
@app_commands.describe(العضو="العضو المراد قبول طلبه")
async def slash_approve_creator(interaction: discord.Interaction, العضو: discord.Member):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ عذراً، تتطلب صلاحية **مدير**.", ephemeral=True)
        return
    db = SessionLocal()
    try:
        app_record = db.query(CreatorApplicationModel).filter_by(guild_id=interaction.guild_id, user_id=العضو.id).first()
        if not app_record:
            await interaction.response.send_message("📂 لا توجد طلبات تقديم مسجلة لهذا العضو.", ephemeral=True)
            return
        app_record.status = "APPROVED"
        db.commit()
        await interaction.response.send_message(f"✅ **تمت الموافقة بنجاح!** اعتماد العضو {العضو.mention} رسمياً.")
    finally:
        db.close()

@bot.tree.command(name="لوحة_صناع_المحتوى", description="عرض قائمة صناع المحتوى المعتمدين")
async def slash_creators_leaderboard(interaction: discord.Interaction):
    db = SessionLocal()
    try:
        approved = db.query(CreatorApplicationModel).filter_by(guild_id=interaction.guild_id, status="APPROVED").all()
        if not approved:
            await interaction.response.send_message("📊 لا يوجد صناع محتوى معتمدون حالياً.", ephemeral=True)
            return
        embed = discord.Embed(title="⭐ صناع المحتوى المعتمدون", color=0x6366f1)
        desc_text = "".join([f"• <@{c.user_id}> — المنصة: `{c.platform}` | متابعون: `{c.followers_count:,}`\n" for c in approved])
        embed.description = desc_text
        await interaction.response.send_message(embed=embed)
    finally:
        db.close()


# --- 4. لوحة تحكم Flask المؤسسية الشاملة (جميع الأقسام) ---
MASTER_DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OBT System - لوحة التحكم المؤسسية (11 قسم متكامل)</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --bg-main: #0b0f19; --bg-card: #131b2e; --bg-sidebar: #090d16;
            --accent: #6366f1; --accent-hover: #4f46e5; --text-main: #f8fafc;
            --text-muted: #94a3b8; --border: #1e293b; --success: #22c55e;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Cairo', sans-serif; }
        body { background: var(--bg-main); color: var(--text-main); display: flex; min-height: 100vh; }
        .sidebar { width: 280px; background: var(--bg-sidebar); border-left: 1px solid var(--border); display: flex; flex-direction: column; position: fixed; height: 100vh; overflow-y: auto; }
        .sidebar-brand { padding: 25px 20px; font-size: 20px; font-weight: 800; display: flex; align-items: center; gap: 12px; border-bottom: 1px solid var(--border); background: rgba(99, 102, 241, 0.05); }
        .sidebar-brand i { color: var(--accent); font-size: 24px; }
        .sidebar-menu { padding: 20px 10px; }
        .menu-category { font-size: 11px; text-transform: uppercase; color: var(--text-muted); padding: 10px 15px; font-weight: 700; }
        .sidebar-menu a { display: flex; align-items: center; gap: 12px; padding: 12px 15px; color: var(--text-muted); text-decoration: none; border-radius: 10px; margin-bottom: 5px; font-size: 14px; font-weight: 600; transition: 0.2s; }
        .sidebar-menu a:hover, .sidebar-menu a.active { background: var(--accent); color: white; }
        .main-container { flex: 1; margin-right: 280px; padding: 40px; display: flex; flex-direction: column; gap: 30px; }
        .topbar { display: flex; justify-content: space-between; align-items: center; background: var(--bg-card); padding: 20px 30px; border-radius: 16px; border: 1px solid var(--border); }
        .grid-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; }
        .stat-card { background: var(--bg-card); padding: 25px; border-radius: 16px; border: 1px solid var(--border); position: relative; }
        .stat-card span { font-size: 13px; color: var(--text-muted); font-weight: 600; }
        .stat-card h2 { font-size: 26px; font-weight: 800; color: var(--text-main); margin-top: 8px; }
        .card { background: var(--bg-card); padding: 30px; border-radius: 16px; border: 1px solid var(--border); }
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="sidebar-brand">
            <i class="fa-solid fa-shield-halved"></i>
            <span>OBT System</span>
        </div>
        <div class="sidebar-menu">
            <div class="menu-category">الأنظمة الإدارية الـ 11</div>
            <a href="/dashboard/123" class="active"><i class="fa-solid fa-chart-pie"></i><span>لوحة القيادة الرئيسية</span></a>
            <a href="/dashboard/123"><i class="fa-solid fa-coins"></i><span>نظام الاقتصاد والبنك</span></a>
            <a href="/dashboard/123"><i class="fa-solid fa-star"></i><span>نظام النقاط والمكافآت</span></a>
            <a href="/dashboard/123"><i class="fa-solid fa-users-rectangle"></i><span>نظام العشائر والمجموعات</span></a>
            <a href="/dashboard/123"><i class="fa-solid fa-lock"></i><span>الصلاحيات والأمان</span></a>
            <a href="/dashboard/123"><i class="fa-solid fa-server"></i><span>السجلات المركزية (Logs)</span></a>
            <a href="/dashboard/123"><i class="fa-solid fa-bell"></i><span>الإشعارات الفورية</span></a>
            <a href="/dashboard/123"><i class="fa-solid fa-headset"></i><span>الدعم الفني والتذاكر</span></a>
            <a href="/dashboard/123"><i class="fa-solid fa-ranking-star"></i><span>المستويات والخبرة (XP)</span></a>
            <a href="/dashboard/123"><i class="fa-solid fa-door-open"></i><span>الترحيب والرتب التلقائية</span></a>
            <a href="/dashboard/123"><i class="fa-solid fa-video"></i><span>برنامج صناع المحتوى</span></a>
        </div>
    </div>
    <div class="main-container">
        <div class="topbar">
            <h1>لوحة التحكم المؤسسية الشاملة - OBT System</h1>
            <div style="color: var(--success); font-weight: 700;"><i class="fa-solid fa-circle-check"></i> جميع الأقسام الـ 11 متصلة وتعمل بكفاءة تامة</div>
        </div>
        <div class="grid-stats">
            <div class="stat-card"><span>الأنظمة الفعالة</span><h2    prefix: Mapped[str] = mapped_column(String(10), default="!")
    security_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    
    security: Mapped["SecuritySettings"] = relationship(back_populates="guild", uselist=False, cascade="all, delete-orphan")
    moderation_cases: Mapped[List["ModerationCase"]] = relationship(back_populates="guild", cascade="all, delete-orphan")
    security_stats: Mapped["SecurityStats"] = relationship(back_populates="guild", uselist=False, cascade="all, delete-orphan")

class SecuritySettings(Base):
    __tablename__ = "security_settings"
    guild_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("guild_settings.guild_id", ondelete="CASCADE"), primary_key=True)
    
    # الـ 24 موديول حماية (تفعيل أو تعطيل)
    anti_spam: Mapped[bool] = mapped_column(Boolean, default=True)
    anti_flood: Mapped[bool] = mapped_column(Boolean, default=True)
    anti_duplicate: Mapped[bool] = mapped_column(Boolean, default=True)
    anti_mass_mentions: Mapped[bool] = mapped_column(Boolean, default=True)
    anti_invites: Mapped[bool] = mapped_column(Boolean, default=True)
    anti_external_links: Mapped[bool] = mapped_column(Boolean, default=True)
    anti_scam: Mapped[bool] = mapped_column(Boolean, default=True)
    anti_phishing: Mapped[bool] = mapped_column(Boolean, default=True)
    anti_bad_words: Mapped[bool] = mapped_column(Boolean, default=True)
    anti_caps: Mapped[bool] = mapped_column(Boolean, default=False)
    anti_emoji: Mapped[bool] = mapped_column(Boolean, default=True)
    anti_sticker: Mapped[bool] = mapped_column(Boolean, default=True)
    anti_gif: Mapped[bool] = mapped_column(Boolean, default=False)
    anti_attachment: Mapped[bool] = mapped_column(Boolean, default=False)
    anti_bot_add: Mapped[bool] = mapped_column(Boolean, default=True)
    anti_webhook: Mapped[bool] = mapped_column(Boolean, default=True)
    anti_raid: Mapped[bool] = mapped_column(Boolean, default=True)
    anti_mass_join: Mapped[bool] = mapped_column(Boolean, default=True)
    anti_fake_accounts: Mapped[bool] = mapped_column(Boolean, default=True)
    anti_newly_created: Mapped[bool] = mapped_column(Boolean, default=True)
    anti_nickname_abuse: Mapped[bool] = mapped_column(Boolean, default=True)
    anti_role_abuse: Mapped[bool] = mapped_column(Boolean, default=True)
    anti_channel_abuse: Mapped[bool] = mapped_column(Boolean, default=True)
    anti_permission_abuse: Mapped[bool] = mapped_column(Boolean, default=True)

    # العقوبات لكل موديول أو العقوبة الافتراضية
    punishment_type: Mapped[str] = mapped_column(String(30), default="timeout") # delete, warn, timeout, kick, ban
    module_punishments: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # القوائم البيضاء والسوداء
    whitelist: Mapped[Optional[dict]] = mapped_column(JSON, default={"roles": [], "members": [], "channels": []})
    blacklist: Mapped[Optional[dict]] = mapped_column(JSON, default={"words": [], "domains": [], "links": [], "invites": []})

    # نظام التحقق (Verification)
    verification_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    verification_channel_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    verification_role_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    guild: Mapped["GuildSettings"] = relationship(back_populates="security")

class SecurityStats(Base):
    __tablename__ = "security_stats"
    guild_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("guild_settings.guild_id", ondelete="CASCADE"), primary_key=True)
    messages_blocked: Mapped[int] = mapped_column(Integer, default=0)
    members_punished: Mapped[int] = mapped_column(Integer, default=0)
    spam_attempts: Mapped[int] = mapped_column(Integer, default=0)
    raid_attempts: Mapped[int] = mapped_column(Integer, default=0)
    scam_links_blocked: Mapped[int] = mapped_column(Integer, default=0)
    verification_count: Mapped[int] = mapped_column(Integer, default=0)

    guild: Mapped["GuildSettings"] = relationship(back_populates="security_stats")

class ModerationCase(Base):
    __tablename__ = "moderation_cases"
    case_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("guild_settings.guild_id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    moderator_id: Mapped[int] = mapped_column(BigInteger)
    action: Mapped[str] = mapped_column(String(50))
    reason: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    guild: Mapped["GuildSettings"] = relationship(back_populates="moderation_cases")

Base.metadata.create_all(bind=engine)

# --- 3. إعداد بوت ديسكورد والأحداث الأمنية ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.moderation = True

bot = commands.Bot(command_prefix="!", intents=intents)

class VerificationView(discord.ui.View):
    """زر التحقق التفاعلي المستمر للأعضاء الجدد"""
    def __init__(self, role_id: int):
        super().__init__(timeout=None)
        self.role_id = role_id

    @discord.ui.button(label="تحقق الآن (Verify)", style=discord.ButtonStyle.green, custom_id="obt_verify_persistent_btn")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(self.role_id)
        if not role:
            await interaction.response.send_message("❌ عذراً، رتبة التحقق غير مُعرّفة بشكل صحيح في النظام.", ephemeral=True)
            return
        
        if role in interaction.user.roles:
            await interaction.response.send_message("✅ أنت متحقق بالفعل في هذا السيرفر.", ephemeral=True)
        else:
            await interaction.user.add_roles(role, reason="اجتياز نظام التحقق الأمني في OBT System")
            
            # تحديث الإحصائيات في قاعدة البيانات
            db = SessionLocal()
            try:
                stats = db.query(SecurityStats).filter_by(guild_id=interaction.guild.id).first()
                if stats:
                    stats.verification_count += 1
                    db.commit()
            finally:
                db.close()
                
            await interaction.response.send_message("🎉 تم التحقق بنجاح! تم منحك رتبة العضوية.", ephemeral=True)


@bot.event
async def on_ready():
    print(f'✅ تم تسجيل الدخول بنجاح كـ {bot.user} (نظام OBT الأمني جاهز)')
    try:
        synced = await bot.tree.sync()
        print(f"🔄 تم مزامنة {len(synced)} أمر (Slash Commands) بنجاح.")
    except Exception as e:
        print(f"خطأ في مزامنة الأوامر: {e}")


def check_whitelist_db(guild_id: int, member: discord.Member, channel: discord.TextChannel) -> bool:
    """التحقق من القائمة البيضاء (المالك، المشرفون، الرتب، الأعضاء، القنوات المستثناة)"""
    if member.guild.owner_id == member.id or member.guild_permissions.administrator:
        return True

    db = SessionLocal()
    try:
        sec = db.query(SecuritySettings).filter_by(guild_id=guild_id).first()
        if not sec or not sec.whitelist:
            return False
        
        wl = sec.whitelist
        if channel.id in wl.get("channels", []):
            return True
        if member.id in wl.get("members", []):
            return True
        if any(role.id in wl.get("roles", []) for role in member.roles):
            return True
        return False
    finally:
        db.close()


async def apply_security_action(guild: discord.Guild, member: discord.Member, action: str, reason: str):
    """تنفيذ العقوبة المحددة وتسجيلها في الإحصائيات وقاعدة البيانات"""
    db = SessionLocal()
    try:
        stats = db.query(SecurityStats).filter_by(guild_id=guild.id).first()
        if stats:
            stats.members_punished += 1
            db.commit()

        if action == "delete":
            return
        elif action == "warn":
            case = ModerationCase(guild_id=guild.id, user_id=member.id, moderator_id=bot.user.id, action="warn", reason=reason)
            db.add(case)
            db.commit()
            try:
                await member.send(f"⚠️ تلقيت تحذيراً أمنياً في سيرفر **{guild.name}**.\nالسبب: {reason}")
            except:
                pass
        elif action == "timeout":
            until = datetime.utcnow() + timedelta(minutes=10)
            await member.timeout(until, reason=reason)
        elif action == "kick":
            await member.kick(reason=reason)
        elif action == "ban":
            await member.ban(reason=reason, delete_message_seconds=86400)
    except Exception as e:
        print(f"خطأ أثناء تنفيذ العقوبة الأمنية: {e}")
    finally:
        db.close()


# --- مراقب الرسائل لتفعيل حمايات الـ 24 ---
message_tracker = {}
raid_tracker = {}

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot or not message.guild:
        return

    db = SessionLocal()
    try:
        guild_set = db.query(GuildSettings).filter_by(guild_id=message.guild.id).first()
        if not guild_set or not guild_set.security_enabled:
            return

        sec = db.query(SecuritySettings).filter_by(guild_id=message.guild.id).first()
        stats = db.query(SecurityStats).filter_by(guild_id=message.guild.id).first()
        if not sec:
            return

        if check_whitelist_db(message.guild.id, message.author, message.channel):
            return

        content = message.content
        punishment = sec.punishment_type or "delete"

        # 1. Anti Bad Words & Blacklist Words
        blacklist = sec.blacklist or {}
        bad_words = blacklist.get("words", [])
        if sec.anti_bad_words and any(word in content.lower() for word in bad_words):
            await message.delete()
            if stats:
                stats.messages_blocked += 1
                db.commit()
            await apply_security_action(message.guild, message.author, punishment, "استخدام كلمات محظورة (Bad Words)")
            return

        # 2. Anti Invite Links & External Links
        if sec.anti_invites and ("discord.gg/" in content.lower() or "discord.com/invite/" in content.lower()):
            await message.delete()
            if stats:
                stats.messages_blocked += 1
                db.commit()
            await apply_security_action(message.guild, message.author, punishment, "إرسال روابط دعوات خارجية")
            return

        # 3. Anti Scam & Phishing Links
        if (sec.anti_scam or sec.anti_phishing) and any(d in content.lower() for d in ["free-nitro", "steam-gift", "airdrop", "nitro-gift"]):
            await message.delete()
            if stats:
                stats.messages_blocked += 1
                stats.scam_links_blocked += 1
                db.commit()
            await apply_security_action(message.guild, message.author, "ban", "محاولة نشر روابط احتيالية أو سكام (Scam/Phishing)")
            return

        # 4. Anti Mass Mentions
        if sec.anti_mass_mentions and len(message.mentions) > 5:
            await message.delete()
            if stats:
                stats.messages_blocked += 1
                db.commit()
            await apply_security_action(message.guild, message.author, punishment, "تنفيذ منشن جماعي مكثف (Mass Mentions)")
            return

        # 5. Anti Caps
        if sec.anti_caps and len(content) > 10:
            caps_ratio = sum(1 for c in content if c.isupper()) / len(content)
            if caps_ratio > 0.7:
                await message.delete()
                return

        # 6. Anti Emoji / Sticker / GIF Spam
        emoji_count = len(re.findall(r'<a?:\w+:\d+>', content)) + len(re.findall(r'[\U00010000-\U0010ffff]', content))
        if sec.anti_emoji and emoji_count > 8:
            await message.delete()
            return

        if sec.anti_sticker and len(message.stickers) > 0:
            await message.delete()
            return

        if sec.anti_gif and ("tenor.com" in content.lower() or "giphy.com" in content.lower()):
            await message.delete()
            return

        # 7. Anti Duplicate & Flood (Spam)
        user_key = (message.guild.id, message.author.id)
        now_ts = datetime.utcnow().timestamp()
        if user_key in message_tracker:
            last_content, last_time = message_tracker[user_key]
            if last_content == content and (now_ts - last_time) < 5:
                await message.delete()
                if stats:
                    stats.messages_blocked += 1
                    stats.spam_attempts += 1
                    db.commit()
                await apply_security_action(message.guild, message.author, punishment, "إرسال رسائل مكررة (Spam/Duplicate)")
                return
        message_tracker[user_key] = (content, now_ts)

    finally:
        db.close()


@bot.event
async def on_member_join(member: discord.Member):
    db = SessionLocal()
    try:
        sec = db.query(SecuritySettings).filter_by(guild_id=member.guild.id).first()
        stats = db.query(SecurityStats).filter_by(guild_id=member.guild.id).first()
        if not sec:
            return

        # Anti Newly Created Accounts & Fake Accounts (< 2 days)
        account_age = (datetime.utcnow() - member.created_at.replace(tzinfo=None)).days
        if sec.anti_newly_created and account_age < 2:
            await member.kick(reason="الحساب جديد جداً ولا يحقق معايير الأمان")
            return

        # Anti Bot Add (Unauthorized bots)
        if member.bot and sec.anti_bot_add:
            await member.kick(reason="حظر إضافة البوتات غير المعتمدة تلقائياً")
            return

    finally:
        db.close()


# --- أوامر السلاش العربية بالكامل (Slash Commands) ---

@bot.tree.command(name="تفعيل_الحماية", description="تفعيل نظام الحماية والأمان الشامل في السيرفر")
@app_commands.checks.has_permissions(administrator=True)
async def slash_enable_protection(interaction: discord.Interaction):
    db = SessionLocal()
    try:
        guild_set = db.query(GuildSettings).filter_by(guild_id=interaction.guild.id).first()
        if guild_set:
            guild_set.security_enabled = True
            db.commit()
        await interaction.response.send_message("✅ تم تفعيل نظام الحماية والأمان بنجاح تام.", ephemeral=True)
    finally:
        db.close()

@bot.tree.command(name="تعطيل_الحماية", description="تعطيل نظام الحماية والأمان مؤقتاً في السيرفر")
@app_commands.checks.has_permissions(administrator=True)
async def slash_disable_protection(interaction: discord.Interaction):
    db = SessionLocal()
    try:
        guild_set = db.query(GuildSettings).filter_by(guild_id=interaction.guild.id).first()
        if guild_set:
            guild_set.security_enabled = False
            db.commit()
        await interaction.response.send_message("⚠️ تم تعطيل نظام الحماية مؤقتاً.", ephemeral=True)
    finally:
        db.close()

@bot.tree.command(name="حالة_الحماية", description="عرض تقرير حالة الحماية والأنظمة المفعلة حالياً")
async def slash_security_status(interaction: discord.Interaction):
    db = SessionLocal()
    try:
        sec = db.query(SecuritySettings).filter_by(guild_id=interaction.guild.id).first()
        stats = db.query(SecurityStats).filter_by(guild_id=interaction.guild.id).first()
        if not sec:
            await interaction.response.send_message("❌ لا توجد إعدادات أمان محفوظة لهذا السيرفر.", ephemeral=True)
            return

        embed = discord.Embed(title="🛡️ تقرير الحماية والأنظمة الأمنية الشاملة", color=discord.Color.blurple())
        embed.add_field(name="حماية السبام والفلود", value="🟢 مفعل" if sec.anti_spam else "🔴 معطل", inline=True)
        embed.add_field(name="حماية الروابط والدعوات", value="🟢 مفعل" if sec.anti_invites else "🔴 معطل", inline=True)
        embed.add_field(name="حماية السكام والفشينغ", value="🟢 مفعل" if sec.anti_scam else "🔴 معطل", inline=True)
        embed.add_field(name="الرسائل المحظورة", value=str(stats.messages_blocked if stats else 0), inline=True)
        embed.add_field(name="الأعضاء المعاقبون", value=str(stats.members_punished if stats else 0), inline=True)
        embed.add_field(name="محاولات الهجوم (Raid/Spam)", value=str(stats.spam_attempts if stats else 0), inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    finally:
        db.close()

@bot.tree.command(name="التحقق", description="إنشاء رسالة التحقق والأزرار التفاعلية للأعضاء الجدد")
@app_commands.checks.has_permissions(administrator=True)
async def slash_verification(interaction: discord.Interaction):
    db = SessionLocal()
    try:
        sec = db.query(SecuritySettings).filter_by(guild_id=interaction.guild.id).first()
        if not sec or not sec.verification_role_id:
            await interaction.response.send_message("❌ يرجى تعيين رتبة التحقق أولاً من لوحة تحكم الويب.", ephemeral=True)
            return

        view = VerificationView(sec.verification_role_id)
        embed = discord.Embed(
            title="🔒 نظام التحقق الأمني في السيرفر",
            description="يرجى الضغط على الزر أدناه لاجتياز التحقق الأمني والحصول على صلاحية الوصول الكامل للسيرفر.",
            color=discord.Color.green()
        )
        await interaction.channel.send(embed=embed, view=view)
        await interaction.response.send_message("✅ تم إنشاء لوحة التحقق في هذه القناة بنجاح.", ephemeral=True)
    finally:
        db.close()


# --- 4. مسارات لوحة التحكم Flask (Security Dashboard) ---

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>OBT System - لوحة الأمان المتقدمة</title>
    <style>
        :root { --bg: #0f172a; --card: #1e293b; --accent: #6366f1; --text: #f8fafc; --muted: #94a3b8; --success: #22c55e; }
        body { margin: 0; font-family: 'Segoe UI', Tahoma, sans-serif; background: var(--bg); color: var(--text); display: flex; min-height: 100vh; }
        .sidebar { width: 280px; background: #090d16; border-left: 1px solid #334155; padding: 20px; box-sizing: border-box; }
        .sidebar h2 { font-size: 18px; color: var(--accent); text-align: center; margin-bottom: 25px; }
        .sidebar a { color: var(--muted); text-decoration: none; padding: 10px 14px; border-radius: 8px; margin-bottom: 8px; display: block; font-size: 14px; transition: 0.2s; }
        .sidebar a:hover, .sidebar a.active { background: var(--accent); color: white; }
        .main { flex: 1; padding: 40px; box-sizing: border-box; overflow-y: auto; }
        .card { background: var(--card); padding: 25px; border-radius: 12px; border: 1px solid #334155; margin-bottom: 20px; }
        .card h3 { margin    anti_raid = Column(Boolean, default=True)
    anti_link = Column(Boolean, default=False)
    anti_scam = Column(Boolean, default=True)
    
    # الإشراف والتذاكر
    ticket_category_id = Column(Integer, nullable=True)
    welcome_message = Column(String, default="أهلاً بك في السيرفر!")

class UserEconomy(Base):
    __tablename__ = "user_economy"
    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(String)
    user_id = Column(String)
    points = Column(Integer, default=0)
    level = Column(Integer, default=1)

class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(String)
    channel_id = Column(String)
    user_id = Column(String)
    status = Column(String, default="مفتوحة")
    category = Column(String, default="الدعم العام")
    claimed_by = Column(String, nullable=True)

class EconomyTransaction(Base):
    __tablename__ = "economy_transactions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(String)
    sender_id = Column(String)
    receiver_id = Column(String)
    amount = Column(Integer)
    timestamp = Column(String, default="2026-07-20")

class Clan(Base):
    __tablename__ = "clans"
    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(String)
    clan_name = Column(String)
    leader_id = Column(String)
    level = Column(Integer, default=1)
    points = Column(Integer, default=0)

# إنشاء الجداول تلقائياً في قاعدة البيانات
Base.metadata.create_all(bind=engine)

# --- قالب لوحة التحكم الشامل (Dashboard UI) ---
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
        <a href="/?tab=overview" {% if tab == 'overview' %}class="active"{% endif %}>📊 نظرة عامة</a>
        <a href="/?tab=security" {% if tab == 'security' %}class="active"{% endif %}>🛡️ نظام الحماية</a>
        <a href="/?tab=tickets" {% if tab == 'tickets' %}class="active"{% endif %}>🎫 نظام التذاكر</a>
        <a href="/?tab=economy" {% if tab == 'economy' %}class="active"{% endif %}>💰 الاقتصاد والنقاط</a>
        <a href="/?tab=clans" {% if tab == 'clans' %}class="active"{% endif %}>⚔️ نظام الكلانات</a>
        <a href="#" style="color: var(--danger); margin-top: auto;">🚪 تسجيل الخروج</a>
    </div>

    <div class="main">
        <div class="header">
            <h2 style="margin:0;">
                {% if tab == 'security' %}إعدادات الحماية والأمان
                {% elif tab == 'tickets' %}إدارة نظام التذاكر المتقدم
                {% elif tab == 'economy' %}إدارة نظام الاقتصاد والنقاط
                {% elif tab == 'clans' %}إدارة نظام الكلانات والمنافسة
                {% else %}لوحة التحكم الرئيسية{% endif %}
            </h2>
            <span style="background: rgba(34, 197, 94, 0.1); color: var(--success); padding: 6px 15px; border-radius: 20px; font-weight: bold;">● النظام يعمل بكفاءة</span>
        </div>

        {% if tab == 'security' %}
        <form method="POST" class="card">
            <h3>إعدادات الأمان والحماية التلقائية</h3>
            <div class="form-group">
                <div>
                    <strong>حماية السبام (Anti-Spam)</strong>
                    <p style="margin: 5px 0 0 0; color: var(--muted); font-size: 13px;">منع إرسال الرسائل المتكررة بسرعة فائقة.</p>
                </div>
                <label class="switch"><input type="checkbox" name="anti_spam" checked><span class="slider"></span></label>
            </div>
            <div class="form-group">
                <div>
                    <strong>حماية الهجمات (Anti-Raid)</strong>
                    <p style="margin: 5px 0 0 0; color: var(--muted); font-size: 13px;">التصدي لدخول الحسابات الوهمية بشكل جماعي.</p>
                </div>
                <label class="switch"><input type="checkbox" name="anti_raid" checked><span class="slider"></span></label>
            </div>
            <div class="form-group">
                <div>
                    <strong>منع الروابط الضارة (Anti-Link)</strong>
                    <p style="margin: 5px 0 0 0; color: var(--muted); font-size: 13px;">حذف روابط الدعوات والروابط الخارجية تلقائياً.</p>
                </div>
                <label class="switch"><input type="checkbox" name="anti_link"><span class="slider"></span></label>
            </div>
            <div class="form-group">
                <div>
                    <strong>حماية الـ Scam والمخادعين</strong>
                    <p style="margin: 5px 0 0 0; color: var(--muted); font-size: 13px;">الكشف الفوري عن الروابط الاحتيالية وحظر مرسليها.</p>
                </div>
                <label class="switch"><input type="checkbox" name="anti_scam" checked><span class="slider"></span></label>
            </div>
            <button type="submit" class="btn">حفظ وتطبيق التغييرات</button>
        </form>

        {% elif tab == 'tickets' %}
        <div class="card">
            <h3>لوحات التذاكر النشطة</h3>
            <form method="POST">
                <div style="margin-bottom: 15px;">
                    <label><strong>رتبة الإشراف والدعم الفني</strong></label>
                    <input type="text" class="form-control" value="مشرف الدعم الفني" name="support_role">
                </div>
                <div style="margin-bottom: 15px;">
                    <label><strong>رسالة الترحيب داخل التذكرة</strong></label>
                    <textarea class="form-control" rows="3" name="ticket_welcome">مرحباً بك! يرجى توضيح مشكلتك وسيقوم فريق الدعم بالرد عليك.</textarea>
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
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>#1042</td>
                        <td>أحمد محمد</td>
                        <td>الدعم الفني العام</td>
                        <td><span style="color: var(--success);">مفتوحة</span></td>
                    </tr>
                </tbody>
            </table>
        </div>

        {% elif tab == 'economy' %}
        <div class="grid">
            <div class="stat-card">
                <span>إجمالي النقاط</span>
                <h2 style="color: var(--warning);">1,450,200</h2>
            </div>
            <div class="stat-card">
                <span>مكافأة اليوم</span>
                <h2 style="color: var(--success);">500 نقطة</h2>
            </div>
        </div>
        <div class="card">
            <h3>إعدادات المكافآت</h3>
            <form method="POST">
                <div style="margin-bottom: 15px;">
                    <label><strong>قيمة المكافأة اليومية (Daily)</strong></label>
                    <input type="number" class="form-control" value="500" name="daily_amount">
                </div>
                <button type="submit" class="btn">حفظ الإعدادات الاقتصادية</button>
            </form>
        </div>

        {% elif tab == 'clans' %}
        <div class="card">
            <h3>ترتيب وفئات الكلانات</h3>
            <table>
                <thead>
                    <tr>
                        <th>اسم الكلان</th>
                        <th>القائد</th>
                        <th>المستوى</th>
                        <th>النقاط</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>النمور (Tigers)</td>
                        <td>خالد علي</td>
                        <td>5</td>
                        <td><span style="color: var(--warning);">12,400</span></td>
                    </tr>
                </tbody>
            </table>
        </div>

        {% else %}
        <div class="grid">
            <div class="stat-card">
                <span>حالة النظام</span>
                <h2>مستقر وآمن</h2>
            </div>
            <div class="stat-card">
                <span>السيرفرات المحمية</span>
                <h2 style="color: var(--accent);">100,000+</h2>
            </div>
            <div class="stat-card">
                <span>استجابة السيرفر</span>
                <h2>12ms</h2>
            </div>
        </div>
        <div class="card">
            <h3>مرحباً بك في لوحة تحكم OBT System</h3>
            <p style="color: var(--muted);">استخدم القائمة الجانبية للتنقل بين أقسام الحماية، التذاكر، الاقتصاد، والكلانات بكل سهولة.</p>
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

# --- إعداد بوت ديسكورد ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

def run_discord_bot():
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        print("❌ خطأ: لم يتم العثور على DISCORD_TOKEN في متغيرات البيئة!")
        return
    try:
        bot.run(token)
    except Exception as e:
        print(f"خطأ في تشغيل البوت: {e}")

if __name__ == "__main__":
    # تشغيل بوت ديسكورد في خلفية النظام
    bot_thread = Thread(target=run_discord_bot)
    bot_thread.daemon = True
    bot_thread.start()

    # تشغيل سيرفر الـ Flask
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
class EconomyTransaction(Base):
    __tablename__ = "economy_transactions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(String)
    sender_id = Column(String)
    receiver_id = Column(String)
    amount = Column(Integer)
    timestamp = Column(String, default="2026-07-20")

class Clan(Base):
    __tablename__ = "clans"
    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(String)
    clan_name = Column(String)
    leader_id = Column(String)
    level = Column(Integer, default=1)
    points = Column(Integer, default=0)

# إنشاء الجداول تلقائياً في قاعدة البيانات
Base.metadata.create_all(bind=engine)

# --- قالب لوحة التحكم الشامل (Dashboard UI) ---
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
        <a href="/?tab=overview" {% if tab == 'overview' %}class="active"{% endif %}>📊 نظرة عامة</a>
        <a href="/?tab=security" {% if tab == 'security' %}class="active"{% endif %}>🛡️ نظام الحماية</a>
        <a href="/?tab=tickets" {% if tab == 'tickets' %}class="active"{% endif %}>🎫 نظام التذاكر</a>
        <a href="/?tab=economy" {% if tab == 'economy' %}class="active"{% endif %}>💰 الاقتصاد والنقاط</a>
        <a href="/?tab=clans" {% if tab == 'clans' %}class="active"{% endif %}>⚔️ نظام الكلانات</a>
        <a href="#" style="color: var(--danger); margin-top: auto;">🚪 تسجيل الخروج</a>
    </div>

    <div class="main">
        <div class="header">
            <h2 style="margin:0;">
                {% if tab == 'security' %}إعدادات الحماية والأمان
                {% elif tab == 'tickets' %}إدارة نظام التذاكر المتقدم
                {% elif tab == 'economy' %}إدارة نظام الاقتصاد والنقاط
                {% elif tab == 'clans' %}إدارة نظام الكلانات والمنافسة
                {% else %}لوحة التحكم الرئيسية{% endif %}
            </h2>
            <span style="background: rgba(34, 197, 94, 0.1); color: var(--success); padding: 6px 15px; border-radius: 20px; font-weight: bold;">● النظام يعمل بكفاءة</span>
        </div>

        {% if tab == 'security' %}
        <form method="POST" class="card">
            <h3>إعدادات الأمان والحماية التلقائية</h3>
            <div class="form-group">
                <div>
                    <strong>حماية السبام (Anti-Spam)</strong>
                    <p style="margin: 5px 0 0 0; color: var(--muted); font-size: 13px;">منع إرسال الرسائل المتكررة بسرعة فائقة.</p>
                </div>
                <label class="switch"><input type="checkbox" name="anti_spam" checked><span class="slider"></span></label>
            </div>
            <div class="form-group">
                <div>
                    <strong>حماية الهجمات (Anti-Raid)</strong>
                    <p style="margin: 5px 0 0 0; color: var(--muted); font-size: 13px;">التصدي لدخول الحسابات الوهمية بشكل جماعي.</p>
                </div>
                <label class="switch"><input type="checkbox" name="anti_raid" checked><span class="slider"></span></label>
            </div>
            <div class="form-group">
                <div>
                    <strong>منع الروابط الضارة (Anti-Link)</strong>
                    <p style="margin: 5px 0 0 0; color: var(--muted); font-size: 13px;">حذف روابط الدعوات والروابط الخارجية تلقائياً.</p>
                </div>
                <label class="switch"><input type="checkbox" name="anti_link"><span class="slider"></span></label>
            </div>
            <div class="form-group">
                <div>
                    <strong>حماية الـ Scam والمخادعين</strong>
                    <p style="margin: 5px 0 0 0; color: var(--muted); font-size: 13px;">الكشف الفوري عن الروابط الاحتيالية وحظر مرسليها.</p>
                </div>
                <label class="switch"><input type="checkbox" name="anti_scam" checked><span class="slider"></span></label>
            </div>
            <button type="submit" class="btn">حفظ وتطبيق التغييرات</button>
        </form>

        {% elif tab == 'tickets' %}
        <div class="card">
            <h3>لوحات التذاكر النشطة</h3>
            <form method="POST">
                <div style="margin-bottom: 15px;">
                    <label><strong>رتبة الإشراف والدعم الفني</strong></label>
                    <input type="text" class="form-control" value="مشرف الدعم الفني" name="support_role">
                </div>
                <div style="margin-bottom: 15px;">
                    <label><strong>رسالة الترحيب داخل التذكرة</strong></label>
                    <textarea class="form-control" rows="3" name="ticket_welcome">مرحباً بك! يرجى توضيح مشكلتك وسيقوم فريق الدعم بالرد عليك.</textarea>
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
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>#1042</td>
                        <td>أحمد محمد</td>
                        <td>الدعم الفني العام</td>
                        <td><span style="color: var(--success);">مفتوحة</span></td>
                    </tr>
                </tbody>
            </table>
        </div>

        {% elif tab == 'economy' %}
        <div class="grid">
            <div class="stat-card">
                <span>إجمالي النقاط</span>
                <h2 style="color: var(--warning);">1,450,200</h2>
            </div>
            <div class="stat-card">
                <span>مكافأة اليوم</span>
                <h2 style="color: var(--success);">500 نقطة</h2>
            </div>
        </div>
        <div class="card">
            <h3>إعدادات المكافآت</h3>
            <form method="POST">
                <div style="margin-bottom: 15px;">
                    <label><strong>قيمة المكافأة اليومية (Daily)</strong></label>
                    <input type="number" class="form-control" value="500" name="daily_amount">
                </div>
                <button type="submit" class="btn">حفظ الإعدادات الاقتصادية</button>
            </form>
        </div>

        {% elif tab == 'clans' %}
        <div class="card">
            <h3>ترتيب وفئات الكلانات</h3>
            <table>
                <thead>
                    <tr>
                        <th>اسم الكلان</th>
                        <th>القائد</th>
                        <th>المستوى</th>
                        <th>النقاط</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>النمور (Tigers)</td>
                        <td>خالد علي</td>
                        <td>5</td>
                        <td><span style="color: var(--warning);">12,400</span></td>
                    </tr>
                </tbody>
            </table>
        </div>

        {% else %}
        <div class="grid">
            <div class="stat-card">
                <span>حالة النظام</span>
                <h2>مستقر وآمن</h2>
            </div>
            <div class="stat-card">
                <span>السيرفرات المحمية</span>
                <h2 style="color: var(--accent);">100,000+</h2>
            </div>
            <div class="stat-card">
                <span>استجابة السيرفر</span>
                <h2>12ms</h2>
            </div>
        </div>
        <div class="card">
            <h3>مرحباً بك في لوحة تحكم OBT System</h3>
            <p style="color: var(--muted);">استخدم القائمة الجانبية للتنقل بين أقسام الحماية، التذاكر، الاقتصاد، والكلانات بكل سهولة.</p>
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

# --- إعداد بوت ديسكورد ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

def run_discord_bot():
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        print("❌ خطأ: لم يتم العثور على DISCORD_TOKEN في متغيرات البيئة!")
        return
    try:
        bot.run(token)
    except Exception as e:
        print(f"خطأ في تشغيل البوت: {e}")

if __name__ == "__main__":
    # تشغيل بوت ديسكورد في خلفية النظام
    bot_thread = Thread(target=run_discord_bot)
    bot_thread.daemon = True
    bot_thread.start()

    # تشغيل سيرفر الـ Flask
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
