import os
from threading import Thread
from flask import Flask, render_template
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
import discord
from discord.ext import commands

# إعداد تطبيق الـ Flask (الداشبورد)
app = Flask(__name__)

# إعداد قاعدة البيانات (SQLAlchemy)
database_url = os.environ.get("DATABASE_URL", "sqlite:///obt_system.db")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

engine = create_engine(database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class GuildSettings(Base):
    __tablename__ = "guild_settings"
    id = Column(Integer, primary_key=True, index=True)
    guild_id = Column(String, unique=True, index=True)
    prefix = Column(String, default="!")

Base.metadata.create_all(bind=engine)

# --- المسارات (Routes) ---

@app.route("/")
def index():
    # يعرض صفحة index.html
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    # يعرض صفحة dashboard.html
    return render_template("dashboard.html")

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
    # تشغيل بوت ديسكورد في خلفية النظام (Background Thread)
    bot_thread = Thread(target=run_discord_bot)
    bot_thread.daemon = True
    bot_thread.start()

    # تشغيل سيرفر الـ Flask واستقبال الاتصالات من Railway على البورت الصحيح
    # الكود هنا يكتشف المنفذ تلقائياً، وإذا لم يجده يستخدم 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
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
    # تشغيل بوت ديسكورد في خلفية النظام (Background Thread)
    bot_thread = Thread(target=run_discord_bot)
    bot_thread.daemon = True
    bot_thread.start()

    # تشغيل سيرفر الـ Flask واستقبال الاتصالات من Railway على البورت الصحيح
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
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
    </style>
</head>
<body>

    <div class="sidebar">
        <h2>🚀 OBT System</h2>
        <a href="#" class="active">📊 نظرة عامة</a>
        <a href="#">🛡️ نظام الحماية</a>
        <a href="#">🔨 نظام الإشراف</a>
        <a href="#">🎫 نظام التذاكر</a>
        <a href="#">💰 الاقتصاد والنقاط</a>
        <a href="#" style="color: var(--danger); margin-top: auto;">🚪 تسجيل الخروج</a>
    </div>

    <div class="main">
        <div class="header">
            <h2 style="margin:0;">لوحة التحكم الرئيسية</h2>
            <span style="background: rgba(34, 197, 94, 0.1); color: var(--success); padding: 6px 15px; border-radius: 20px; font-weight: bold;">● النظام يعمل بكفاءة</span>
        </div>

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
    </div>

</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def dashboard():
    if request.method == "POST":
        return redirect(url_for("dashboard"))
    return render_template_string(DASHBOARD_TEMPLATE)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
    
