import asyncio
import os
import discord
from discord.ext import commands
from quart import Quart, jsonify, render_template

# تهيئة تطبيق الويب Quart
app = Quart(__name__)

# إعدادات بوت الديسكورد
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# قائمة الأقسام المعتمدة لتجنب أخطاء 404
VALID_PAGES = [
    'index', 'dashboard', 'analytics', 'backups', 'clans', 
    'creators', 'economy', 'logs', 'notifications', 'security', 'settings', 'tickets'
]

@app.route('/')
async def home():
    return await render_template('dashboard.html', active_page='index')

@app.route('/<page_name>')
async def render_section(page_name):
    if page_name not in VALID_PAGES:
        return await render_template('dashboard.html', active_page='index'), 404
    return await render_template('dashboard.html', active_page=page_name)

@app.route('/api/status')
async def api_status():
    try:
        guilds_count = len(bot.guilds) if bot.is_ready() else 0
        ping = round(bot.latency * 1000) if bot.is_ready() and bot.latency else 0
        return jsonify({
            "bot_ready": bot.is_ready(),
            "guilds": guilds_count,
            "ping_ms": ping,
            "database": "متصل"
        })
    except Exception as e:
        return jsonify({
            "bot_ready": False,
            "guilds": 0,
            "ping_ms": 0,
            "database": "خطأ بالاتصال"
        })

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

@app.before_serving
async def startup():
    token = os.getenv("DISCORD_TOKEN")
    if token:
        asyncio.create_task(bot.start(token))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
