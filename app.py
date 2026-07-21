# -*- coding: utf-8 -*-
"""
OBT-System Production Engine
----------------------------
The ultimate, stable, single-file orchestrator for Discord & Quart Dashboard.
Strictly compliant with Pylance/Ruff. Optimized for memory and concurrency.
"""

import asyncio
import logging
import os
import signal
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional

import discord
from discord.ext import commands
from quart import Quart, jsonify, render_template, request
from werkzeug.exceptions import HTTPException

# استيراد إعدادات المشروع وقاعدة البيانات من الملفات الحالية
from config import Config
from database.database import DatabaseManager

# ==================== 1. نظام السجلات (Logging Setup) ====================
os.makedirs("logs", exist_ok=True)
log_format = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

file_log_handler = RotatingFileHandler(
    "logs/app.log", maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
)
file_log_handler.setFormatter(log_format)

console_log_handler = logging.StreamHandler(sys.stdout)
console_log_handler.setFormatter(log_format)

logging.basicConfig(level=logging.INFO, handlers=[file_log_handler, console_log_handler])
logger = logging.getLogger("OBT.Engine")

# ==================== 2. المتغيرات العامة وتهيئة التطبيقات ====================
db_connection_status: str = "Disconnected"
shutdown_event = asyncio.Event()

# تحسين الأداء: تعريف الصفحات المسموحة مسبقاً لمنع استهلاك الذاكرة مع كل طلب
VALID_PAGES: frozenset[str] = frozenset({
    "analytics", "backups", "clans", "creators", "dashboard", 
    "economy", "index", "logs", "notifications", "security", 
    "settings", "tickets"
})

bot_prefix: str = getattr(Config, "BOT_PREFIX", "!")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix=bot_prefix, intents=intents)

app = Quart(__name__, template_folder="templates", static_folder="static")
app.secret_key = getattr(Config, "SECRET_KEY", os.environ.get("SECRET_KEY", "obt_production_secret_2026"))

# ==================== 3. معالجة أخطاء الويب (Quart Error Handlers) ====================
@app.errorhandler(404)
async def handle_404(_error: Optional[Exception]):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Endpoint not found", "status": 404}), 404
    try:
        return await render_template("404.html"), 404
    except Exception:
        return "<div style='color:#f8fafc;background:#0f172a;padding:40px;font-family:sans-serif;'><h1>404 - Not Found</h1></div>", 404

@app.errorhandler(500)
async def handle_500(error: Optional[Exception]):
    if error and not isinstance(error, HTTPException):
        logger.error(f"Internal server error on {request.path}: {error}", exc_info=True)
    if request.path.startswith("/api/"):
        return jsonify({"error": "Internal server error", "status": 500}), 500
    try:
        return await render_template("500.html"), 500
    except Exception:
        return "<div style='color:#f8fafc;background:#0f172a;padding:40px;font-family:sans-serif;'><h1>500 - Server Error</h1></div>", 500

# ==================== 4. مسارات لوحة التحكم (Dashboard Routes) ====================
@app.route('/')
async def index():
    guilds_count = len(bot.guilds) if bot.is_ready() else 0
    ping = round(bot.latency * 1000) if bot.latency and bot.is_ready() else 0
    try:
        return await render_template('index.html', guilds=guilds_count, ping=ping, status="Online")
    except Exception:
        return await render_template('dashboard.html', guilds=guilds_count, ping=ping, status="Online")

@app.route('/<page_name>')
async def render_dashboard_pages(page_name: str):
    if page_name in VALID_PAGES:
        try:
            return await render_template(f"{page_name}.html")
        except Exception as e:
            logger.error(f"Failed to render template {page_name}.html: {e}")
            return await handle_500(e)
            
    return await handle_404(None)

@app.route('/api/status')
async def health_check_api():
    return jsonify({
        "status": "online",
        "bot_ready": bot.is_ready(),
        "bot_user": str(bot.user) if bot.is_ready() else None,
        "guilds": len(bot.guilds) if bot.is_ready() else 0,
        "ping_ms": round(bot.latency * 1000) if bot.latency and bot.is_ready() else 0,
        "database": db_connection_status
    })

# ==================== 5. معالجة أخطاء البوت (Discord Event & Error Handlers) ====================
@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError) -> None:
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ لا تمتلك الصلاحيات الكافية لتنفيذ هذا الأمر.")
        return
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ هناك وسيط مفقود! الاستخدام الصحيح: `{ctx.prefix}{ctx.command.name} {ctx.command.signature}`")
        return
        
    logger.error(f"Error executing command [{ctx.command}]: {error}", exc_info=True)

@bot.event
async def on_ready() -> None:
    logger.info(f"Discord Bot online as: {bot.user} (ID: {bot.user.id if bot.user else 'Unknown'})")

# ==================== 6. محرك التشغيل الديناميكي والإيقاف الطبيعي ====================
async def load_all_cogs() -> int:
    loaded_count = 0
    cogs_dir = "cogs"
    
    if not os.path.exists(cogs_dir):
        logger.warning(f"Directory '{cogs_dir}' not found. Skipping cog loading.")
        return 0

    for filename in os.listdir(cogs_dir):
        if filename.endswith(".py") and not filename.startswith("_"):
            cog_name = filename[:-3]
            try:
                await bot.load_extension(f"cogs.{cog_name}")
                logger.info(f"✔ Loaded Cog: {cog_name}")
                loaded_count += 1
            except Exception as e:
                logger.error(f"❌ Failed to load Cog [{cog_name}]: {e}")
    return loaded_count

async def graceful_shutdown(signal_name: Optional[str] = None) -> None:
    if shutdown_event.is_set():
        return
        
    if signal_name:
        logger.info(f"Received signal ({signal_name}). Shutting down gracefully...")
    else:
        logger.info("Initiating Graceful Shutdown...")

    # 1. إرسال إشارة الإغلاق للداشبورد (Quart) ليتوقف بشكل آمن
    shutdown_event.set()

    # 2. إغلاق اتصال البوت
    if not bot.is_closed():
        logger.info("Closing Discord connection...")
        await bot.close()
        logger.info("Discord connection closed cleanly.")

# ==================== 7. دالة الإقلاع المتزامن (Main Entrypoint) ====================
async def main() -> None:
    global db_connection_status
    
    logger.info("==================================================")
    logger.info("       🚀 Starting OBT-Enterprise Core 🚀        ")
    logger.info("==================================================")
    
    # 1. التحقق من الإعدادات
    if hasattr(Config, "validate"):
        Config.validate()
    
    # 2. تهيئة قاعدة البيانات وفحص الاتصال
    try:
        await DatabaseManager.initialize_database(app)
        db_connection_status = "Connected"
        logger.info("✔ Database initialized successfully.")
    except Exception as e:
        db_connection_status = "Connection Failed"
        logger.error(f"❌ Database initialization failed: {e}")

    # 3. تحميل الأوامر
    cogs_loaded = await load_all_cogs()

    # 4. إعداد معالجات إشارات الإيقاف الآمن
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(graceful_shutdown(s.name)))
        except NotImplementedError:
            pass # لتجاوز الخطأ في أنظمة التشغيل التي لا تدعم إشارات معينة

    # 5. عرض ملخص الحالة في الـ Terminal
    port = int(os.environ.get("PORT", 8080))
    logger.info("--------------------------------------------------")
    logger.info(f" 🗄️ Database Status  : {db_connection_status}")
    logger.info(f" 🧩 Loaded Cogs      : {cogs_loaded} module(s)")
    logger.info(f" 🌐 Dashboard URL    : http://0.0.0.0:{port}")
    logger.info(f" 🤖 Bot Prefix       : {bot_prefix}")
    logger.info("--------------------------------------------------")

    # 6. التشغيل المتزامن بدون تعارض
    bot_token = os.environ.get("DISCORD_BOT_TOKEN")
    if not bot_token:
        logger.critical("❌ Missing DISCORD_BOT_TOKEN in environment variables!")
        return

    try:
        # تم إزالة use_reloader الغير مدعومة في Quart لتجنب الـ TypeError
        await asyncio.gather(
            app.run_task(host="0.0.0.0", port=port, shutdown_trigger=shutdown_event.wait),
            bot.start(bot_token)
        )
    except asyncio.CancelledError:
        pass
    finally:
        await graceful_shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.critical(f"Fatal application error: {e}", exc_info=True)
