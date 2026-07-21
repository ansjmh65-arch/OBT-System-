import os
import threading
import asyncio
import discord
from discord.ext import commands
from flask import Flask, render_template

# ==========================================
# 1. إعداد لوحة التحكم (الداشبورد - Flask)
# ==========================================
# نقوم بتعريف الفلاسك وربطه بمجلد templates الموجود لديك
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

# دالة تشغيل السيرفر (تحل مشكلة 502 في Railway جذرياً)
def run_flask():
    port = int(os.environ.get("PORT", 5000))
    # يجب أن يكون use_reloader=False لكي لا يتعارض مع البوت
    app.run(host="0.0.0.0", port=port, use_reloader=False)

# دالة لوضع السيرفر في الخلفية (Thread) لكي لا يوقف عمل البوت
def keep_alive():
    server = threading.Thread(target=run_flask)
    server.start()


# ==========================================
# 2. إعداد البوت (Discord.py)
# ==========================================
intents = discord.Intents.default()
intents.message_content = True
# يمكنك إضافة أي Intents أخرى تحتاجها هنا لاحقاً

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"🤖 Logged in as {bot.user.name}")
    print("✅ Dashboard and Bot are fully operational!")
    
# دالة ذكية لتحميل جميع ملفاتك الموجودة في مجلد cogs تلقائياً
async def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                # نحذف آخر 3 حروف (.py) عند التحميل
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f"✅ Loaded Cog: {filename}")
            except Exception as e:
                print(f"❌ Failed to load {filename}: {e}")

# ==========================================
# 3. التشغيل النهائي والآمن للمشروع
# ==========================================
async def main():
    # 1. نشغل الداشبورد في الخلفية أولاً
    keep_alive()
    
    # 2. نحمل ملفات البوت الأساسية (Cogs)
    await load_cogs()
    
    # 3. نشغل البوت
    # ملاحظة هامة: يجب أن تضع توكن البوت في Railway في قسم Variables باسم TOKEN
    TOKEN = os.environ.get("TOKEN") 
    
    if not TOKEN:
        print("❌ خطأ: لم يتم العثور على توكن البوت (TOKEN) في المتغيرات البيئية!")
        return
        
    await bot.start(TOKEN)

if __name__ == '__main__':
    # تشغيل الدالة الرئيسية بأمان تام
    asyncio.run(main())
    
