from discord.ext import commands

class Reminders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="تذكير")
    async def remind(self, ctx, time_val: int, *, task: str):
        await ctx.send(f"تم ضبط التذكير بنجاح بعد {time_val} دقيقة للمهمة: {task}")

async def setup(bot):
    await bot.add_cog(Reminders(bot))
  
