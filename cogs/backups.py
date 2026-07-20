from discord.ext import commands
from utils.permissions import is_guild_admin

class Backups(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="نسخة_احتياطية")
    @is_guild_admin()
    async def backup_server(self, ctx):
        await ctx.send("تم إنشاء نسخة احتياطية لإعدادات السيرفر بنجاح.")

async def setup(bot):
    await bot.add_cog(Backups(bot))
  
