# -*- coding: utf-8 -*-

import asyncio
import os
import logging

import discord
from discord.ext import commands
from quart import Quart, jsonify, render_template

# قاعدة البيانات
from database.database import init_db

# ==========================
# Logging
# ==========================

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s"
)

logger = logging.getLogger("OBT-System")


# ==========================
# Quart Dashboard
# ==========================

app = Quart(
    __name__,
    template_folder="templates",
    static_folder="static"
)


# ==========================
# Discord Bot Config
# ==========================

intents = discord.Intents.default()

intents.guilds = True
intents.members = True
intents.message_content = True
intents.presences = True
intents.messages = True
intents.voice_states = True


bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# ==========================
# Dashboard Pages
# ==========================

VALID_PAGES = [
    "index",
    "dashboard",
    "analytics",
    "backups",
    "clans",
    "creators",
    "economy",
    "logs",
    "notifications",
    "security",
    "settings",
    "tickets"
]


# ==========================
# Dashboard Routes
# ==========================


@app.route("/")
async def home():

    return await render_template(
        "dashboard.html",
        active_page="index"
    )



@app.route("/<page_name>")
async def dashboard_page(page_name):

    if page_name not in VALID_PAGES:

        return await render_template(
            "dashboard.html",
            active_page="index"
        ), 404


    return await render_template(
        "dashboard.html",
        active_page=page_name
    )



# ==========================
# API
# ==========================


@app.route("/api/status")
async def api_status():

    return jsonify({

        "status": "online",

        "bot_ready": bot.is_ready(),

        "bot_name":
            str(bot.user)
            if bot.user
            else None,

        "guilds":
            len(bot.guilds)
            if bot.is_ready()
            else 0,

        "users":
            sum(
                guild.member_count or 0
                for guild in bot.guilds
            )
            if bot.is_ready()
            else 0,

        "ping":
            round(bot.latency * 1000)
            if bot.is_ready()
            else 0,

        "database": "connected"

    })



# ==========================
# Discord Events
# ==========================


@bot.event
async def on_ready():

    logger.info(
        f"Bot Started: {bot.user} | ID: {bot.user.id}"
    )


    try:

        synced = await bot.tree.sync()

        logger.info(
            f"Synced {len(synced)} slash commands"
        )

    except Exception as error:

        logger.error(
            f"Slash sync error: {error}"
        )



# ==========================
# Load Cogs
# ==========================


async def load_cogs():

    folder = "cogs"


    if not os.path.exists(folder):

        logger.warning(
            "Cogs folder not found"
        )

        return


    for file in os.listdir(folder):

        if file.endswith(".py"):

            extension = f"{folder}.{file[:-3]}"

            try:

                await bot.load_extension(
                    extension
                )

                logger.info(
                    f"Loaded {extension}"
                )


            except Exception as error:

                logger.error(
                    f"Failed loading {extension}: {error}"
                )



# ==========================
# Startup
# ==========================


@app.before_serving
async def startup():

    logger.info(
        "Starting OBT-System..."
    )


    # Database

    try:

        init_db(app)

        logger.info(
            "Database initialized"
        )


    except Exception as error:

        logger.error(
            f"Database error: {error}"
        )


    # Cogs

    await load_cogs()


    # Bot

    token = os.getenv(
        "DISCORD_TOKEN"
    )


    if not token:

        logger.error(
            "DISCORD_TOKEN missing"
        )

        return


    asyncio.create_task(
        bot.start(token)
    )



# ==========================
# Shutdown
# ==========================


@app.after_serving
async def shutdown():

    if not bot.is_closed():

        await bot.close()


    logger.info(
        "OBT-System stopped"
    )



# ==========================
# Run
# ==========================


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8080
    )
