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
    from flask import render_template

@app.route('/dashboard')
def dashboard():
    # يمكنك تمرير اسم السيرفر والأيدي الحقيقيين هنا لاحقاً
    return render_template('dashboard.html', guild_name="OBT System", guild_id="123456789")
from flask import Flask, render_template, redirect

# (تأكد أن تعريف app موجود لديك مسبقاً مثل: app = Flask(__name__))

@app.route('/dashboard')
def dashboard_page():
    return render_template('dashboard.html', guild_name="OBT System", guild_id="123456789")
    from flask import render_template

# مسار الصفحة الرئيسية للداشبورد (الأوامر العامة)
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# مسارات بقية الأقسام بناءً على ملفات الـ html الموجودة عندك
@app.route('/dashboard/analytics')
def dashboard_analytics():
    return render_template('analytics.html')

@app.route('/dashboard/economy')
def dashboard_economy():
    return render_template('economy.html')

@app.route('/dashboard/moderation')
def dashboard_moderation():
    return render_template('moderation.html')

@app.route('/dashboard/tickets')
def dashboard_tickets():
    return render_template('tickets.html')

@app.route('/dashboard/logs')
def dashboard_logs():
    return render_template('logs.html')

@app.route('/dashboard/settings')
def dashboard_settings():
    return render_template('settings.html')
                                  
