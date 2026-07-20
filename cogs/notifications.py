from discord.ext import commands

class Notifications(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="تنبيه")
    async def notify(self, ctx, *, text: str):
        await ctx.send(f"إشعار عام: {text}")

async def setup(bot):
    await bot.add_cog(Notifications(bot))
  
