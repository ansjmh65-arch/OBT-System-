import discord
from discord.ext import commands
from services.logging_service import LoggingService

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        LoggingService.log_action(f"حذف رسالة بواسطة {message.author}")

async def setup(bot):
    await bot.add_cog(Logs(bot))
  
