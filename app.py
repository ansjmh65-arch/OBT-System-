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
