import discord
from discord.ext import commands

class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="رتب_التفاعل")
    async def reaction_roles(self, ctx):
        await ctx.send("تم إرسال رسالة رتب التفاعل بنجاح.")

async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))
  
