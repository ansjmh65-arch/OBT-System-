import os
import threading
import discord
from discord.ext import commands
from flask import Flask, render_template

# ==========================================
# 1. إعداد مسارات Flask الأساسية (لحل مشكلة Railway نهائياً)
# ==========================================
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static') # إذا كان لديك ملفات CSS أو صور

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

# ==========================================
# 2. إعدادات بوت الديسكورد
# ==========================================
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True # ضروري لكي يتعرف البوت على السيرفرات
bot = commands.Bot(command_prefix="!", intents=intents)

# ==========================================
# 3. إعداد الـ 11 قسماً الخاصة بلوحة التحكم (Dashboard Sections)
# ==========================================
dashboard_sections = [
    {"id": 1, "route": "general", "name": "الإعدادات العامة", "icon": "⚙️"},
    {"id": 2, "route": "protection", "name": "الحماية (Protection)", "icon": "🛡️"},
    {"id": 3, "route": "welcomer", "name": "الترحيب والمغادرة", "icon": "👋"},
    {"id": 4, "route": "auto_responder", "name": "الردود التلقائية", "icon": "🤖"},
    {"id": 5, "route": "tickets", "name": "نظام التذاكر", "icon": "🎫"},
    {"id": 6, "route": "logs", "name": "سجل الأحداث (Logs)", "icon": "📜"},
    {"id": 7, "route": "auto_roles", "name": "الأدوار التلقائية", "icon": "🎭"},
    {"id": 8, "route": "leveling", "name": "نظام المستويات", "icon": "⭐"},
    {"id": 9, "route": "economy", "name": "الاقتصاد (Economy)", "icon": "💰"},
    {"id": 10, "route": "voice", "name": "الرومات الصوتية المؤقتة", "icon": "🎙️"},
    {"id": 11, "route": "moderation", "name": "أوامر الإدارة (Moderation)", "icon": "🔨"}
]

# ==========================================
# 4. مسارات لوحة التحكم (Flask Routes)
# ==========================================
@app.route("/")
def home():
    return "✅ النظام يعمل بنجاح! البوت ولوحة التحكم متصلان."

@app.route("/dashboard/<int:guild_id>")
def dashboard(guild_id):
    try:
        # البحث عن السيرفر للتحقق من وجود البوت فيه
        guild = bot.get_guild(guild_id)
        
        # نعرض صفحة الداشبورد ونمرر لها رقم السيرفر، بيانات السيرفر (إن وجدت)، والأقسام الـ 11
        return render_template(
            "dashboard.html", 
            guild_id=guild_id, 
            guild_name=guild.name if guild else "سيرفر غير معروف",
            sections=dashboard_sections
        )
    except Exception as e:
        # في حال حدوث أي خطأ برمجي طارئ، لا ينهار السيرفر بل يطبع الخطأ
        print(f"Error in dashboard route: {e}")
        return f"حدث خطأ داخلي: {e}", 500

# ==========================================
# 5. أحداث البوت (Bot Events)
# ==========================================
@bot.event
async def on_ready():
    print(f"🚀 Bot logged in successfully as {bot.user}")
    print(f"✅ Bot is in {len(bot.guilds)} servers.")

# ==========================================
# 6. نظام التشغيل المزدوج (فلاسك + ديسكورد)
# ==========================================
def run_flask():
    # رايلواي يتطلب استخدام البورت الخاص به من الـ Environment Variables
    port = int(os.environ.get("PORT", 8080))
    # التشغيل على 0.0.0.0 ضروري لكي يفتح من خارج السيرفر المحلي
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

if __name__ == "__main__":
    # تشغيل لوحة التحكم (Flask) في مسار (Thread) منفصل لكي لا يوقف عمل البوت
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    
    # جلب التوكن من متغيرات البيئة (يفضل وضع توكن البوت في Railway Variables)
    TOKEN = os.environ.get("DISCORD_TOKEN")
    
    # يمكنك وضع التوكن الخاص بك مباشرة هنا مؤقتاً إذا لم تكن تستخدم Railway Variables
    # TOKEN = "ضع_التوكن_هنا"
    
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ لم يتم العثور على توكن البوت! الرجاء إضافته.")
    
