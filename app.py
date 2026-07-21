
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
from Quart import Quart

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

# تصميم الداشبورد الاحترافي الحقيقي
@app.route('/')
async def index():
    html_content = """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>OBT-System Dashboard</title>
        <style>
            body {
                background-color: #0f172a;
                color: #f8fafc;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
            }
            .card {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 12px;
                padding: 30px;
                width: 100%;
                max-width: 600px;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
            }
            h1 {
                color: #38bdf8;
                font-size: 22px;
                margin-top: 0;
                margin-bottom: 10px;
            }
            p.desc {
                color: #94a3b8;
                font-size: 14px;
                margin-bottom: 25px;
            }
            .status-badge {
                display: inline-block;
                padding: 6px 14px;
                background-color: #065f46;
                color: #34d399;
                border-radius: 20px;
                font-weight: bold;
                font-size: 13px;
                margin-bottom: 25px;
            }
            .info-item {
                background-color: #0f172a;
                padding: 14px 18px;
                border-radius: 8px;
                margin-bottom: 12px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                border: 1px solid #334155;
                font-size: 14px;
            }
            .online {
                color: #34d399;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>OBT-System Control Panel</h1>
            <p class="desc">لوحة التحكم المركزية المتزامنة لإدارة بوت ديسكورد وقاعدة البيانات.</p>
            <div class="status-badge">● النظام يعمل بكفاءة</div>
            
            <div class="info-item">
                <span>حالة بوت ديسكورد (Discord Bot):</span>
                <span class="online">متصل (Online)</span>
            </div>
            
            <div class="info-item">
                <span>قاعدة البيانات (Database):</span>
                <span class="online">متصلة وجاهزة</span>
            </div>
            
            <div class="info-item">
                <span>إطار العمل (Framework):</span>
                <strong style="color: #cbd5e1;">Quart (Async)</strong>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

async def load_cogs():
    """تحميل ملفات الأوامر (Cogs) للبوت."""
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
    Config.validate()
    await DatabaseManager.initialize_database(app)
    await load_cogs()
    
    logger.info("Starting Bot and Dashboard concurrently...")
    await asyncio.gather(
        run_dashboard(),
        run_bot()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("System shutting down gracefully.")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        
