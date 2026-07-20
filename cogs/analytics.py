from discord.ext import commands

class Analytics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="احصائيات")
    async def analytics(self, ctx):
        await ctx.send(f"إجمالي الأعضاء في السيرفر: {ctx.guild.member_count}")

async def setup(bot):
    await bot.add_cog(Analytics(bot))
  
