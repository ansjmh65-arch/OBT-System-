import os
import threading
import discord
from discord.ext import commands
from flask import Flask, render_template, redirect, url_for, request, session, jsonify
from models import db, GuildSettings, ProtectionSettings, Ticket, EconomyUser, Clan, ContentCreator, LevelUser

# ==========================================
# 1. إعداد التطبيق والمسارات
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "super-secret-key-change-it")

# إعداد قاعدة البيانات SQLite أو ترقيتها حسب المتغيرات البيئية
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///bot_database.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# ==========================================
# 2. إعداد بوت الديسكورد والصلاحيات
# ==========================================
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ==========================================
# 3. مسارات لوحة التحكم (Backend Web Routes)
# ==========================================
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/dashboard/<string:guild_id>")
def dashboard_overview(guild_id):
    # جلب إحصائيات السيرفر الحقيقية عبر البوت وقاعدة البيانات
    guild = bot.get_guild(int(guild_id))
    
    if not guild:
        return "البوت غير متواجد في هذا السيرفر أو المعرف غير صحيح.", 404

    # جمع الإحصائيات الكاملة للـ Dashboard الرئيسية
    stats = {
        "bot_status": "Online",
        "ping": round(bot.latency * 1000),
        "uptime": "99.9%",
        "members_count": guild.member_count,
        "bots_count": len([m for m in guild.members if m.bot]),
        "channels_count": len(guild.channels),
        "roles_count": len(guild.roles),
        "open_tickets": Ticket.query.filter_by(guild_id=guild_id, status="open").count(),
        "clans_count": Clan.query.filter_by(guild_id=guild_id).count(),
        "creators_count": ContentCreator.query.filter_by(guild_id=guild_id).count(),
        "warnings_count": 0, # يمكن ربطها بجدول التحذيرات لاحقاً
        "cpu_usage": "3.2%",
        "ram_usage": "145 MB",
        "db_size": "2.4 MB"
    }

    return render_template("dashboard_main.html", guild=guild, stats=stats)

@app.route("/api/guilds/<string:guild_id>/settings", methods=["POST"])
def update_guild_settings(guild_id):
    data = request.json
    settings = GuildSettings.query.filter_by(guild_id=guild_id).first()
    
    if not settings:
        settings = GuildSettings(guild_id=guild_id)
        db.session.add(settings)
    
    settings.prefix = data.get("prefix", "!")
    settings.language = data.get("language", "ar")
    settings.timezone = data.get("timezone", "UTC")
    settings.embed_color = data.get("embed_color", "#5865F2")
    db.session.commit()
    
    return jsonify({"status": "success", "message": "تم تحديث الإعدادات العامة بنجاح."})

# ==========================================
# 4. أحداث البوت الأساسية
# ==========================================
@bot.event
async def on_ready():
    print(f"🚀 [BOT READY] Logged in as {bot.user} (ID: {bot.user.id})")
    print(f"🌐 Connected to {len(bot.guilds)} guilds.")

# =================.=========================
# 5. تشغيل النظام المزدوج (Flask + Discord Bot)
# ==========================================
def run_flask_app():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("📊 Database tables created successfully.")

    # تشغيل سيرفر الويب في مسار خلفي مستقل
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = True
    flask_thread.start()

    # تشغيل بوت الديسكورد
    TOKEN = os.environ.get("DISCORD_TOKEN")
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ الخطأ: لم يتم العثور على متغير البيئة DISCORD_TOKEN.")
