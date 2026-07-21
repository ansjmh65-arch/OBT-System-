# -*- coding: utf-8 -*-
"""
OBT System - Enterprise Final Unified Engine
-------------------------------------------
المحرك الرئيسي لتشغيل البوت ولوحة التحكم وقاعدة البيانات بتزامن كامل عبر asyncio.
"""

import asyncio
import logging
import os
import sys
from quart import Quart
from hypercorn.asyncio import serve
from hypercorn.config import Config as HypercornConfig

from config import Config
from database import db
from database.database import DatabaseManager
from dashboard.routes import dashboard_bp, api_bp

# إعدادات التسجيل الاحترافية
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("OBT.App")

# تهيئة تطبيق Quart
app = Quart(__name__)
app.config.from_object(Config)

# تسجيل الـ Blueprints
app.register_blueprint(dashboard_bp)
app.register_blueprint(api_bp)

# ربط قاعدة البيانات
db.init_app(app)

import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=Config.BOT_PREFIX, intents=intents)

@bot.event
async def on_ready() -> None:
    logger.info(f"Discord Bot successfully logged in as {bot.user}")

async def load_cogs() -> None:
    """تحميل الامتدادات تلقائياً."""
    if os.path.exists("cogs"):
        for filename in os.listdir("cogs"):
            if filename.endswith(".py") and not filename.startswith("_"):
                await bot.load_extension(f"cogs.{filename[:-3]}")
                logger.info(f"Loaded Cog: cogs.{filename[:-3]}")

async def main() -> None:
    """الدالة الرئيسية لإدارة الإقلاع والتشغيل المتزامن."""
    Config.validate()
    DatabaseManager.initialize_database(app)
    
    await load_cogs()

    hypercorn_config = HypercornConfig()
    hypercorn_config.bind = [f"0.0.0.0:{Config.PORT}"]
    hypercorn_config.use_reloader = False

    logger.info(f"Starting Hypercorn Web Server on port {Config.PORT} and Discord Bot concurrently...")

    await asyncio.gather(
        serve(app, hypercorn_config),
        bot.start(Config.DISCORD_BOT_TOKEN)
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("OBT Enterprise System stopped cleanly.")
