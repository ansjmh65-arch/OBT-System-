from discord.ext import commands

class Giveaways(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="سحب")
    async def giveaway(self, ctx, prize: str):
        await ctx.send(f"🎉 تم بدء مسابقة على الجائزة: {prize}!")

async def setup(bot):
    await bot.add_cog(Giveaways(bot))
  
