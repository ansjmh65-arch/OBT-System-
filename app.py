import os
import threading
import asyncio
import discord
from discord.ext import commands
from flask import Flask, render_template

# ==========================================
# 1. إعداد لوحة التحكم (الداشبورد - Flask)
# ==========================================
app = Flask(__name__, template_folder='templates')

@app.route('/')
def home():
    return "✅ OBT-System is Running Online!"

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

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

def run_flask():
    # استخراج المنفذ الصحيح من بيئة Railway لتفادي خطأ 502
    port = int(os.environ.get("PORT", 8080))
    # تشغيل الفلاسك على 0.0.0.0 إجباري في Railway
    app.run(host="0.0.0.0", port=port, use_reloader=False, debug=False)

def keep_alive():
    # تشغيل الفلاسك كخلفية (Daemon Thread) لكي لا يتعارض مع البوت
    server = threading.Thread(target=run_flask)
    server.daemon = True # مهم جداً: يضمن بقاء الداشبورد يعمل حتى لو كان هناك تأخير
    server.start()

# ==========================================
# 2. إعداد البوت (Discord.py)
# ==========================================
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"🤖 Logged in as {bot.user.name}")
    print("✅ Dashboard and Bot are fully operational!")

async def load_cogs():
    # التأكد من وجود مجلد cogs لتفادي الأخطاء إذا لم يكن موجوداً
    if not os.path.exists('./cogs'):
        os.makedirs('./cogs')
        
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f"✅ Loaded Cog: {filename}")
            except Exception as e:
                print(f"❌ Failed to load {filename}: {e}")

# ==========================================
# 3. التشغيل النهائي والآمن للمشروع
# ==========================================
async def main():
    # 1. تشغيل الداشبورد أولاً لتلبية طلب Railway للـ Port (هذا يمنع خطأ 502 نهائياً)
    keep_alive()
    
    # 2. تحميل أوامر البوت
    await load_cogs()
    
    # 3. جلب التوكن وتشغيل البوت بذكاء
    TOKEN = os.environ.get("TOKEN")
    
    if not TOKEN:
        print("❌ خطأ حرج: التوكن غير موجود في المتغيرات البيئية (Variables) في Railway!")
        # نبقي التطبيق يعمل كي لا ينهار السيرفر ويظهر خطأ 502 للداشبورد
        while True:
            await asyncio.sleep(3600)
            
    try:
        await bot.start(TOKEN)
    except discord.errors.LoginFailure:
        print("❌ خطأ: التوكن الذي أدخلته غير صحيح. تأكد منه في Railway.")
        while True:
            await asyncio.sleep(3600)
    except Exception as e:
        print(f"❌ حدث خطأ غير متوقع في البوت: {e}")
        while True:
            await asyncio.sleep(3600)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 OBT-System Shutting down...")
    
