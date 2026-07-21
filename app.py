# -*- coding: utf-8 -*-
"""
OBT-System Main Application
---------------------------
نقطة الإدخال الرئيسية لتشغيل البوت ولوحة التحكم معاً.
"""

import asyncio
import logging
import os
import discord
from discord.ext import commands
from quart import Quart

# استيراد الملفات الخاصة بالمشروع
from config import Config
from database.database import DatabaseManager

# إعداد سجلات النظام
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("OBT.Main")

# تهيئة تطبيق Quart للوحة التحكم
app = Quart(__name__)

# تهيئة بوت ديسكورد
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@app.route('/')
async def index():
    return "OBT-System Dashboard is running!"

async def load_cogs():
    """تحميل ملفات الأوامر (Cogs) للبوت."""
    # يمكنك إضافة الكوجز الخاصة بك هنا مستقبلاً
    # await bot.load_extension("cogs.general")
    pass

async def run_bot():
    """مهمة تشغيل البوت."""
    token = os.environ.get("DISCORD_BOT_TOKEN")
    if not token:
        logger.error("Discord Token is missing!")
        return
    await bot.start(token)

async def run_dashboard():
    """مهمة تشغيل لوحة التحكم (Quart)."""
    port = int(os.environ.get("PORT", 8080))
    await app.run_task(host="0.0.0.0", port=port)

async def main() -> None:
    """الدالة الرئيسية لإدارة الإقلاع والتشغيل المتزامن."""
    logger.info("Initializing OBT-System...")
    
    # 1. التحقق من الإعدادات والمتغيرات
    Config.validate()
    
    # 2. تهيئة قاعدة البيانات (مع ضبط كلمة await والمسافات 100%)
    await DatabaseManager.initialize_database(app)
    
    # 3. تحميل أوامر البوت
    await load_cogs()
    
    # 4. تشغيل الداشبورد والبوت في نفس الوقت
    logger.info("Starting Bot and Dashboard concurrently...")
    await asyncio.gather(
        run_dashboard(),
        run_bot()
    )

if __name__ == "__main__":
    try:
        # الإقلاع الرئيسي
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("System shutting down gracefully.")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        
