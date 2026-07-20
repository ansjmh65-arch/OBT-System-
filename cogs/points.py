import discord
from discord.ext import commands
from services.points_service import PointsService

class Points(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="نقاطي")
    async def my_points(self, ctx):
        bonus = PointsService.calculate_bonus(5)
        await ctx.send(f"رصيد نقاط التفاعل لديك هو: {bonus} نقطة")

async def setup(bot):
    await bot.add_cog(Points(bot))
  
