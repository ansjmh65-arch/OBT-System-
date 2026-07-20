import os
from threading import Thread
from flask import Flask
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

@app.route("/")
def index():
    return """
    <html>
        <head><title>OBT-System Dashboard</title></head>
        <body style="font-family: Arial; background: #0f172a; color: white; text-align: center; padding-top: 80px;">
            <h1>🚀 OBT-System Dashboard is Online!</h1>
            <p>لوحة التحكم تعمل بنجاح ومتصلة بقاعدة البيانات.</p>
        </body>
    </html>
    """

# إعداد بوت ديسكورد
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

def run_discord_bot():
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        print("❌ خطأ: لم يتم العثور على DISCORD_TOKEN!")
        return
    try:
        bot.run(token)
    except Exception as e:
        print(f"خطأ في تشغيل البوت: {e}")

if __name__ == "__main__":
    # تشغيل بوت ديسكورد في الخلفية
    bot_thread = Thread(target=run_discord_bot)
    bot_thread.daemon = True
    bot_thread.start()

    # تشغيل سيرفر الـ Flask على البورت المخصص من Railway
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
