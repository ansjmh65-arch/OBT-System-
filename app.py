import asyncio
import os
import threading
import discord
from discord.ext import commands
from flask import Flask, render_template

from config import Config
from database.database import init_db
from utils.logger import logger

app = Flask(__name__)
app.config.from_object(Config)

init_db(app)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

initial_cogs = [
    "cogs.moderation",
    "cogs.protection",
    "cogs.tickets",
    "cogs.clans",
    "cogs.creators",
    "cogs.economy",
    "cogs.leveling",
    "cogs.auto_responder",
    "cogs.points",
    "cogs.welcome",
    "cogs.logs",
    "cogs.backups",
    "cogs.reaction_roles",
    "cogs.notifications",
    "cogs.analytics",
    "cogs.giveaways",
    "cogs.polls",
    "cogs.reminders"
]

@bot.event
async def on_ready():
    logger.info(f"تم تسجيل الدخول بنجاح باسم البوت: {bot.user}")

async def load_extensions():
    for cog in initial_cogs:
        try:
            await bot.load_extension(cog)
            logger.info(f"تم تحميل النظام الفرعي بنجاح: {cog}")
        except Exception as e:
            logger.error(f"فشل تحميل النظام الفرعي {cog}: {e}")

@app.route('/')
def index():
    return render_template('index.html', guild_name="سيرفر التجربة", guild_id="123456789")

@app.route('/tickets')
def tickets_page():
    return render_template('tickets.html')

@app.route('/security')
def security_page():
    return render_template('security.html')

@app.route('/clans')
def clans_page():
    return render_template('clans.html')

@app.route('/creators')
def creators_page():
    return render_template('creators.html')

@app.route('/economy')
def economy_page():
    return render_template('economy.html')

@app.route('/logs')
def logs_page():
    return render_template('logs.html')

@app.route('/settings')
def settings_page():
    return render_template('settings.html')

@app.route('/analytics')
def analytics_page():
    return render_template('analytics.html')

@app.route('/backups')
def backups_page():
    return render_template('backups.html')

@app.route('/notifications')
def notifications_page():
    return render_template('notifications.html')

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    async def main():
        async with bot:
            await load_extensions()
            await bot.start(app.config['DISCORD_BOT_TOKEN'])
    try:
        loop.run_until_complete(main())
    except Exception as e:
        logger.error(f"خطأ أثناء تشغيل البوت: {e}")

if __name__ == '__main__':
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    app.run(host='0.0.0.0', port=5000, debug=app.config['DEBUG'])
    
