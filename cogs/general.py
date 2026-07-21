# -*- coding: utf-8 -*-
import discord
from discord.ext import commands

class GeneralCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="ping", description="فحص سرعة استجابة البوت ونظامه.")
    async def ping_command(self, ctx: commands.Context) -> None:
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(
            title="pong! 🏓",
            description=f"سرعة استجابة نظام OBT الحالية: `{latency}ms`",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(GeneralCog(bot))
  
