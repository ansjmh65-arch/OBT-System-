from discord.ext import commands

class Polls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="تصويت")
    async def poll(self, ctx, *, question: str):
        msg = await ctx.send(f"📊 **تصويت جديد:** {question}")
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")

async def setup(bot):
    await bot.add_cog(Polls(bot))
  
