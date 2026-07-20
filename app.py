import os
from threading import Thread
from flask import Flask, render_template_string, request, redirect, url_for
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
import discord
from discord.ext import commands

# --- إعداد تطبيق الـ Flask (الداشبورد) ---
app = Flask(__name__)

# --- إعداد قاعدة البيانات (SQLAlchemy) ---
database_url = os.environ.get("DATABASE_URL", "sqlite:///obt_system.db")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

engine = create_engine(database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- نماذج قاعدة البيانات (Models) تشمل كافة الأقسام ---
class GuildSettings(Base):
    __tablename__ = "guild_settings"
    id = Column(Integer, primary_key=True, index=True)
    guild_id = Column(String, unique=True, index=True)
    prefix = Column(String, default="!")
    
    # إعدادات الحماية
    anti_spam = Column(Boolean, default=True)
    anti_raid = Column(Boolean, default=True)
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
