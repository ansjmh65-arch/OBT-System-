import os
import threading
import asyncio
import discord
from discord.ext import commands
from flask import Flask, render_template, request, redirect, url_for
from models import db, ServerConfig

# إعداد تطبيق Flask
app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///obt_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# مسارات لوحة التحكم وحفظ البيانات
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard_home():
    config = ServerConfig.query.filter_by(guild_id="default_guild").first()
    if not config:
        config = ServerConfig(guild_id="default_guild")
        db.session.add(config)
        db.session.commit()

    if request.method == 'POST':
        # استقبال وتحديث حالة الأقسام من الأزرار (Checkboxes)
        config.security_enabled = 'security_enabled' in request.form
        config.moderation_enabled = 'moderation_enabled' in request.form
        config.tickets_enabled = 'tickets_enabled' in request.form
        config.clans_enabled = 'clans_enabled' in request.form
        config.economy_enabled = 'economy_enabled' in request.form
        config.content_creators_enabled = 'content_creators_enabled' in request.form
        config.welcome_enabled = 'welcome_enabled' in request.form
        config.logs_enabled = 'logs_enabled' in request.form
        config.auto_roles_enabled = 'auto_roles_enabled' in request.form
        config.backup_enabled = 'backup_enabled' in request.form
        
        # حفظ النصوص والإعدادات الأخرى إن وجدت
        config.welcome_message = request.form.get('welcome_message', '')
        
        db.session.commit()
        return redirect(url_for('dashboard_home'))

    return render_template('dashboard.html', config=config)

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, use_reloader=False, debug=False)

def keep_alive():
    server = threading.Thread(target=run_flask)
    server.daemon = True
    server.start()

# إعداد بوت ديسكورد (Discord.py)
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"🤖 Bot Logged in as {bot.user.name}")

async def main():
    keep_alive()
    TOKEN = os.environ.get("TOKEN")
    if not TOKEN:
        print("❌ تحذير: التوكن غير موجود، الداشبورد ستظل تعمل ولكن البوت توقف.")
        while True:
            await asyncio.sleep(3600)
    try:
        await bot.start(TOKEN)
    except Exception as e:
        print(f"❌ خطأ في تشغيل البوت: {e}")
        while True:
            await asyncio.sleep(3600)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Shutting down...")
        
