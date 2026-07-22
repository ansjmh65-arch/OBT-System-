# -*- coding: utf-8 -*-

import asyncio
import os
import logging

import discord
from discord.ext import commands
from quart import Quart, render_template, jsonify

from database.database import init_database


# ==========================
# Logging
# ==========================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


# ==========================
# Quart Dashboard
# ==========================

app = Quart(
    __name__,
    template_folder="templates",
    static_folder="static"
)


# ==========================
# Discord Bot
# ==========================

intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# ==========================
# Dashboard Pages
# ==========================

PAGES = [
    "index",
    "security",
    "tickets",
    "clans",
    "economy",
    "creators",
    "logs",
    "backups",
    "settings",
    "analytics"
]


@app.route("/")
async def dashboard():
    return await render_template(
        "dashboard.html",
        active_page="index"
    )


@app.route("/<page>")
async def pages(page):

    if page not in PAGES:
        return await render_template(
            "dashboard.html",
            active_page="index"
        ), 404

    return await render_template(
        "dashboard.html",
        active_page=page
    )


# ==========================
# API
# ==========================

@app.route("/api/status")
async def status():

    return jsonify({

        "bot": bot.user.name if bot.user else None,

        "online": bot.is_ready(),

        "servers":
            len(bot.guilds)
            if bot.is_ready()
            else 0,

        "ping":
            round(bot.latency * 1000)
            if bot.is_ready()
            else 0

    })


# ==========================
# Bot Events
# ==========================

@bot.event
async def on_ready():

    logging.info(
        f"Logged in as {bot.user}"
    )


# ==========================
# Load Cogs
# ==========================

async def load_extensions():

    cogs = [

        "cogs.security",
        "cogs.tickets",
        "cogs.moderation",
        "cogs.logs",
        "cogs.clans",
        "cogs.economy",
        "cogs.levels",
        "cogs.welcome"

    ]

    for cog in cogs:

        try:
            await bot.load_extension(cog)

            logging.info(
                f"Loaded {cog}"
            )

        except Exception as e:

            logging.warning(
                f"Failed {cog}: {e}"
            )


# ==========================
# Run Everything
# ==========================

async def main():

    init_database()

    await load_extensions()

    token = os.getenv(
        "DISCORD_TOKEN"
    )

    if not token:
        raise Exception(
            "DISCORD_TOKEN missing"
        )


    await asyncio.gather(

        bot.start(token),

        app.run_task(
            host="0.0.0.0",
            port=8080
        )

    )



if __name__ == "__main__":

    asyncio.run(main())
